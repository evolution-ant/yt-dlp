# coding: utf-8


import itertools
import re
import io
import os
import errno
import traceback

from ..extractor.common import InfoExtractor, SearchInfoExtractor
from ..extractor.youtube import YoutubeBaseInfoExtractor as _YoutubeBaseInfoExtractor
from ..extractor.youtube import YoutubeIE as _YoutubeIE
from ..jsinterp import JSInterpreter
from ..compat import (
    compat_urllib_parse_unquote_plus,
    compat_urllib_parse_urlencode,
    compat_urlparse,
    compat_urllib_parse_unquote,
    compat_parse_qs,
    compat_urllib_parse_urlparse,
)

from ..utils import (
    int_or_none,
    clean_html,
    ExtractorError,
    get_element_by_attribute,
    orderedSet,
    unescapeHTML,
    uppercase_escape,
    sanitized_Request,
    parse_duration,
    expand_path,
    smuggle_url,
    unsmuggle_url,
    get_element_by_id,
    unified_strdate,
    remove_quotes,
    try_get,
    str_to_int,
    mimetype2ext,
    parse_codecs,
    float_or_none,
)

from ..compat import compat_chr
import json

class YoutubeBaseInfoExtractor(_YoutubeBaseInfoExtractor):
    def _ids_to_results(self, ids):
        from .youtubeExternallinkSite import YoutubeExternallinkSiteIE
        x = YoutubeExternallinkSiteIE()
        x.set_downloader(self._downloader)
        entries = x.getEntriesByID(ids)
        return [self.url_result(entry['id'], 'Youtube', video_id=entry['id'], video_title=entry['title'], video_duration=entry['duration'])
                    for entry in entries]


    @staticmethod
    def url_result(url, ie=None, video_id=None, video_title=None, video_duration = None):
        video_info = {'_type': 'url',
                      'url': url,
                      'ie_key': ie}
        if video_id is not None:
            video_info['id'] = video_id
        if video_title is not None:
            video_info['title'] = video_title
        if video_duration is not None:
            video_info['duration'] = video_duration
        return video_info


class YoutubeEntryListBaseInfoExtractor(YoutubeBaseInfoExtractor):
    # Extract entries from page with "Load more" button
    def _entries(self, page, playlist_id):
        more_widget_html = content_html = page
        for page_num in itertools.count(1):
            for entry in self._process_page(content_html):
                yield entry

            mobj = re.search(r'data-uix-load-more-href="/?(?P<more>[^"]+)"', more_widget_html)
            if not mobj:
                break
            if page_num > 10:
                return
            more = self._download_json(
                'https://youtube.com/%s' % mobj.group('more'), playlist_id,
                'Downloading page #%s' % page_num,
                transform_source=uppercase_escape)
            content_html = more['content_html']
            if not content_html.strip():
                # Some webpages show a "Load more" button but they don't
                # have more videos
                break
            more_widget_html = more['load_more_widget_html']


class YoutubePlaylistBaseInfoExtractor(YoutubeEntryListBaseInfoExtractor):
    def _process_page(self, content):
        for video_id, video_title, video_duration in self.extract_videos_from_page(content):
            yield self.url_result(video_id, 'Youtube', video_id, video_title, video_duration)

    def extract_videos_from_page(self, page):
        ids_in_page = []
        titles_in_page = []
        druation_in_page = []

        for mobj in re.finditer(self._VIDEO_RE, page):
            # The link with index 0 is not the first video of the playlist (not sure if still actual)
            if 'index' in mobj.groupdict() and mobj.group('id') == '0':
                continue
            video_id = mobj.group('id')
            video_title = unescapeHTML(mobj.group('title'))
            video_duration = '0'
            try:
                if mobj.group('duration'):
                    video_duration = unescapeHTML(mobj.group('duration'))
            except:
                video_duration = '0'
            if video_title:
                video_title = video_title.strip()
            try:
                idx = ids_in_page.index(video_id)
                if video_title and not titles_in_page[idx]:
                    titles_in_page[idx] = video_title
            except ValueError:
                ids_in_page.append(video_id)
                titles_in_page.append(video_title)
                druation_in_page.append(video_duration)
        return list(zip(ids_in_page, titles_in_page, druation_in_page))


class YoutubePlaylistsBaseInfoExtractor(YoutubeEntryListBaseInfoExtractor):
    def _process_page(self, content):
        for playlist_id in orderedSet(re.findall(
                r'<h3[^>]+class="[^"]*yt-lockup-title[^"]*"[^>]*><a[^>]+href="/?playlist\?list=([0-9A-Za-z-_]{10,})"',
                content)):
            yield self.url_result(
                'https://www.youtube.com/playlist?list=%s' % playlist_id, 'YoutubePlaylist')

    def _real_extract(self, url):
        playlist_id = self._match_id(url)
        webpage = self._download_webpage(url, playlist_id)
        title = self._og_search_title(webpage, fatal=False)
        return self.playlist_result(self._entries(webpage, playlist_id), playlist_id, title)

class YoutubePlaylistIE(YoutubePlaylistBaseInfoExtractor):
    IE_DESC = 'YouTube.com playlists'
    _VALID_URL = r"""(?x)(?:
                        (?:https?://)?
                        (?:\w+\.)?
                        youtube\.com/
                        (?:
                           (?:course|view_play_list|my_playlists|artist|playlist|watch|embed/videoseries)
                           \? (?:.*?[&;])*? (?:p|a|list)=
                        |  p/
                        )
                        (
                            (?:PL|LL|EC|UU|FL|RD|UL)?[0-9A-Za-z-_]{10,}
                            # Top tracks, they can also include dots
                            |(?:MC)[\w\.]*
                        )
                        .*
                     |
                        ((?:PL|LL|EC|UU|FL|RD|UL)[0-9A-Za-z-_]{10,})
                     )"""
    _TEMPLATE_URL = 'https://www.youtube.com/playlist?list=%s'

    _VIDEO_RE = r'data-title="(?P<title>[^\"]+)(?:[\s|\S]+?)href="\s*/watch\?v=(?P<id>[0-9A-Za-z_-]{11})&amp;[^"]*?index=(?P<index>\d+)(?:[\s|\S]+?)(?:(?=data-title=)|>(?P<duration>(?:\d+\:)?\d+\:\d{2}))'
    #_VIDEO_RE = r'href="\s*/watch\?v=(?P<id>[0-9A-Za-z_-]{11})&amp;[^"]*?index=(?P<index>\d+)(?:[^>]+>(?P<title>[^<]+))?(?:[\s|\S]+?)>(?P<duration>(?:\d+\:)?\d+\:\d{2})'
    IE_NAME = 'youtube:playlist'
    _TESTS = [{
        'url': 'https://www.youtube.com/playlist?list=PLwiyx1dc3P2JR9N8gQaQN_BCvlSlap7re',
        'info_dict': {
            'title': 'ytdl test PL',
            'id': 'PLwiyx1dc3P2JR9N8gQaQN_BCvlSlap7re',
        },
        'playlist_count': 3,
    }, {
        'url': 'https://www.youtube.com/playlist?list=PLtPgu7CB4gbZDA7i_euNxn75ISqxwZPYx',
        'info_dict': {
            'id': 'PLtPgu7CB4gbZDA7i_euNxn75ISqxwZPYx',
            'title': 'YDL_Empty_List',
        },
        'playlist_count': 0,
    }, {
        'note': 'Playlist with deleted videos (#651). As a bonus, the video #51 is also twice in this list.',
        'url': 'https://www.youtube.com/playlist?list=PLwP_SiAcdui0KVebT0mU9Apz359a4ubsC',
        'info_dict': {
            'title': '29C3: Not my department',
            'id': 'PLwP_SiAcdui0KVebT0mU9Apz359a4ubsC',
        },
        'playlist_count': 95,
    }, {
        'note': 'issue #673',
        'url': 'PLBB231211A4F62143',
        'info_dict': {
            'title': '[OLD]Team Fortress 2 (Class-based LP)',
            'id': 'PLBB231211A4F62143',
        },
        'playlist_mincount': 26,
    }, {
        'note': 'Large playlist',
        'url': 'https://www.youtube.com/playlist?list=UUBABnxM4Ar9ten8Mdjj1j0Q',
        'info_dict': {
            'title': 'Uploads from Cauchemar',
            'id': 'UUBABnxM4Ar9ten8Mdjj1j0Q',
        },
        'playlist_mincount': 799,
    }, {
        'url': 'PLtPgu7CB4gbY9oDN3drwC3cMbJggS7dKl',
        'info_dict': {
            'title': 'YDL_safe_search',
            'id': 'PLtPgu7CB4gbY9oDN3drwC3cMbJggS7dKl',
        },
        'playlist_count': 2,
    }, {
        'note': 'embedded',
        'url': 'http://www.youtube.com/embed/videoseries?list=PL6IaIsEjSbf96XFRuNccS_RuEXwNdsoEu',
        'playlist_count': 4,
        'info_dict': {
            'title': 'JODA15',
            'id': 'PL6IaIsEjSbf96XFRuNccS_RuEXwNdsoEu',
        }
    }, {
        'note': 'Embedded SWF player',
        'url': 'http://www.youtube.com/p/YN5VISEtHet5D4NEvfTd0zcgFk84NqFZ?hl=en_US&fs=1&rel=0',
        'playlist_count': 4,
        'info_dict': {
            'title': 'JODA7',
            'id': 'YN5VISEtHet5D4NEvfTd0zcgFk84NqFZ',
        }
    }, {
        'note': 'Buggy playlist: the webpage has a "Load more" button but it doesn\'t have more videos',
        'url': 'https://www.youtube.com/playlist?list=UUXw-G3eDE9trcvY2sBMM_aA',
        'info_dict': {
            'title': 'Uploads from Interstellar Movie',
            'id': 'UUXw-G3eDE9trcvY2sBMM_aA',
        },
        'playlist_mincout': 21,
    }]

    def _real_initialize(self):
        self._login()

    def _extract_mix(self, playlist_id):
        # The mixes are generated from a single video
        # the id of the playlist is just 'RD' + video_id
        ids = []
        last_id = playlist_id[-11:]
        for n in itertools.count(1):
            url = 'https://youtube.com/watch?v=%s&list=%s' % (last_id, playlist_id)
            webpage = self._download_webpage(
                url, playlist_id, 'Downloading page {0} of Youtube mix'.format(n))
            new_ids = orderedSet(re.findall(
                r'''(?xs)data-video-username=".*?".*?
                           href="/watch\?v=([0-9A-Za-z_-]{11})&amp;[^"]*?list=%s''' % re.escape(playlist_id),
                webpage))
            # Fetch new pages until all the videos are repeated, it seems that
            # there are always 51 unique videos.
            new_ids = [_id for _id in new_ids if _id not in ids]
            if not new_ids:
                break
            ids.extend(new_ids)
            last_id = ids[-1]

        url_results = self._ids_to_results(ids)

        search_title = lambda class_name: get_element_by_attribute('class', class_name, webpage)
        title_span = (
            search_title('playlist-title') or
            search_title('title long-title') or
            search_title('title'))
        title = clean_html(title_span)

        return self.playlist_result(url_results, playlist_id, title)

    def _extract_playlist(self, playlist_id):
        url = self._TEMPLATE_URL % playlist_id
        page = self._download_webpage(url, playlist_id)

        for match in re.findall(r'<div class="yt-alert-message">([^<]+)</div>', page):
            match = match.strip()
            # Check if the playlist exists or is private
            if re.match(r'[^<]*(The|This) playlist (does not exist|is private)[^<]*', match):
                raise ExtractorError(
                    'The playlist doesn\'t exist or is private, use --username or '
                    '--netrc to access it.',
                    expected=True)
            elif re.match(r'[^<]*Invalid parameters[^<]*', match):
                raise ExtractorError(
                    'Invalid parameters. Maybe URL is incorrect.',
                    expected=True)
            elif re.match(r'[^<]*Choose your language[^<]*', match):
                continue
            else:
                self.report_warning('Youtube gives an alert message: ' + match)

        playlist_title = self._html_search_regex(
            r'(?s)<h1 class="pl-header-title[^"]*"[^>]*>\s*(.*?)\s*</h1>',
            page, 'title', fatal=False, default=None)
        if not playlist_title:
            playlist_title = playlist_title = self._og_search_title(page)

        return self.playlist_result(self._entries(page, playlist_id), playlist_id, playlist_title)

    def _check_download_just_video(self, url, playlist_id):
        # Check if it's a video-specific URL
        query_dict = compat_urlparse.parse_qs(compat_urlparse.urlparse(url).query)
        if 'v' in query_dict:
            video_id = query_dict['v'][0]
            if self._downloader.params.get('noplaylist'):
                self.to_screen('Downloading just video %s because of --no-playlist' % video_id)
                return self.url_result(video_id, 'Youtube', video_id=video_id)
            else:
                self.to_screen('Downloading playlist %s - add --no-playlist to just download video %s' % (playlist_id, video_id))

    def _real_extract(self, url):
        # Extract playlist id
        mobj = re.match(self._VALID_URL, url)
        if mobj is None:
            raise ExtractorError('Invalid URL: %s' % url)
        playlist_id = mobj.group(1) or mobj.group(2)

        video = self._check_download_just_video(url, playlist_id)
        if video:
            return video
        try:
            if playlist_id.startswith(('RD', 'UL', 'PU')):
                # Mixes require a custom extraction process
                return self._extract_mix(playlist_id)

            return self._extract_playlist(playlist_id)
        except Exception as e:
            query_dict = compat_urlparse.parse_qs(compat_urlparse.urlparse(url).query)
            if 'v' in query_dict:
                video_id = query_dict['v'][0]
                url_results = self._ids_to_results([video_id])
                return self.playlist_result(url_results, playlist_id, 'autoplaylist')
            else:
                raise e

class YoutubeChannelIE(YoutubePlaylistBaseInfoExtractor):
    IE_DESC = 'YouTube.com channels'
    _VALID_URL = r'https?://(?:youtu\.be|(?:\w+\.)?youtube(?:-nocookie)?\.com)/channel/(?P<id>[0-9A-Za-z_-]+)'
    _TEMPLATE_URL = 'https://www.youtube.com/channel/%s/videos'
    _VIDEO_RE = r'channels-content-item[\s\S]+?(?P<duration>(?:\d+\:)?\d+\:\d{2})[\s\S]+?(?:title="(?P<title>[^"]+)"[^>]+)?href="/watch\?v=(?P<id>[0-9A-Za-z_-]+)&?'
    IE_NAME = 'youtube:channel'
    _TESTS = [{
        'note': 'paginated channel',
        'url': 'https://www.youtube.com/channel/UCKfVa3S1e4PHvxWcwyMMg8w',
        'playlist_mincount': 91,
        'info_dict': {
            'id': 'UUKfVa3S1e4PHvxWcwyMMg8w',
            'title': 'Uploads from lex will',
        }
    }, {
        'note': 'Age restricted channel',
        # from https://www.youtube.com/user/DeusExOfficial
        'url': 'https://www.youtube.com/channel/UCs0ifCMCm1icqRbqhUINa0w',
        'playlist_mincount': 64,
        'info_dict': {
            'id': 'UUs0ifCMCm1icqRbqhUINa0w',
            'title': 'Uploads from Deus Ex',
        },
    }]

    @classmethod
    def suitable(cls, url):
        return (False if YoutubePlaylistsIE.suitable(url)
                else super(YoutubeChannelIE, cls).suitable(url))

    def _real_extract(self, url):
        channel_id = self._match_id(url)

        url = self._TEMPLATE_URL % channel_id

        # Channel by page listing is restricted to 35 pages of 30 items, i.e. 1050 videos total (see #5778)
        # Workaround by extracting as a playlist if managed to obtain channel playlist URL
        # otherwise fallback on channel by page extraction
        channel_page = self._download_webpage(
            url + '?view=57', channel_id,
            'Downloading channel page', fatal=False)
        if channel_page is False:
            channel_playlist_id = False
        else:
            channel_playlist_id = self._html_search_meta(
                'channelId', channel_page, 'channel id', default=None)
            if not channel_playlist_id:
                channel_playlist_id = self._search_regex(
                    r'data-(?:channel-external-|yt)id="([^"]+)"',
                    channel_page, 'channel id', default=None)
        channel_page = self._download_webpage(url, channel_id, 'Downloading page #1')
        autogenerated = re.search(r'''(?x)
                class="[^"]*?(?:
                    channel-header-autogenerated-label|
                    yt-channel-title-autogenerated
                )[^"]*"''', channel_page) is not None
        if channel_page:
            channel_title = self._og_search_title(channel_page)
            if not channel_title:
                channel_title = self._html_search_meta(
                    'name', channel_page, 'channel title', default=None)
        if autogenerated:
            if channel_playlist_id and channel_playlist_id.startswith('UC'):
                return self.playlist_result(self._entries(channel_page, channel_id), channel_id, channel_title)
            # The videos are contained in a single page
            # the ajax pages can't be used, they are empty
            entries = [
                self.url_result(
                    video_id, 'Youtube', video_id=video_id,
                    video_title=video_title)
                for video_id, video_title in self.extract_videos_from_page(channel_page)]
            return self.playlist_result(entries, channel_id, channel_title)

        if channel_playlist_id and channel_playlist_id.startswith('UC'):
            playlist_id = 'UU' + channel_playlist_id[2:]
            return self.url_result(
                compat_urlparse.urljoin(url, '/playlist?list=%s' % playlist_id), 'YoutubePlaylist')
        return self.playlist_result(self._entries(channel_page, channel_id), channel_id, channel_title)


class YoutubeUserIE(YoutubeChannelIE):
    IE_DESC = 'YouTube.com user videos (URL or "ytuser" keyword)'
    _VALID_URL = r'(?:(?:https?://(?:\w+\.)?youtube\.com/(?:user/)?(?!(?:attribution_link|watch|results)(?:$|[^a-z_A-Z0-9-])))|ytuser:)(?!feed/)(?P<id>[A-Za-z0-9_-]+)'
    _TEMPLATE_URL = 'https://www.youtube.com/user/%s/videos'
    IE_NAME = 'youtube:user'

    _TESTS = [{
        'url': 'https://www.youtube.com/user/TheLinuxFoundation',
        'playlist_mincount': 320,
        'info_dict': {
            'title': 'TheLinuxFoundation',
        }
    }, {
        'url': 'ytuser:phihag',
        'only_matching': True,
    }]

    @classmethod
    def suitable(cls, url):
        # Don't return True if the url can be extracted with other youtube
        # extractor, the regex would is too permissive and it would match.
        other_yt_ies = iter(klass for (name, klass) in list(globals().items()) if name.startswith('Youtube') and name.endswith('IE') and klass is not cls)
        if any(ie.suitable(url) for ie in other_yt_ies):
            return False
        else:
            return super(YoutubeUserIE, cls).suitable(url)


class YoutubePlaylistsIE(YoutubePlaylistsBaseInfoExtractor):
    IE_DESC = 'YouTube.com user/channel playlists'
    _VALID_URL = r'https?://(?:\w+\.)?youtube\.com/(?:user|channel)/(?P<id>[^/]+)/playlists'
    IE_NAME = 'youtube:playlists'

    _TESTS = [{
        'url': 'http://www.youtube.com/user/ThirstForScience/playlists',
        'playlist_mincount': 4,
        'info_dict': {
            'id': 'ThirstForScience',
            'title': 'Thirst for Science',
        },
    }, {
        # with "Load more" button
        'url': 'http://www.youtube.com/user/igorkle1/playlists?view=1&sort=dd',
        'playlist_mincount': 70,
        'info_dict': {
            'id': 'igorkle1',
            'title': 'Игорь Клейнер',
        },
    }, {
        'url': 'https://www.youtube.com/channel/UCiU1dHvZObB2iP6xkJ__Icw/playlists',
        'playlist_mincount': 17,
        'info_dict': {
            'id': 'UCiU1dHvZObB2iP6xkJ__Icw',
            'title': 'Chem Player',
        },
    }]


class YoutubeSearchIE(SearchInfoExtractor, YoutubePlaylistIE):
    IE_DESC = 'YouTube.com searches'
    # there doesn't appear to be a real limit, for example if you search for
    # 'python' you get more than 8.000.000 results
    _MAX_RESULTS = float('inf')
    IE_NAME = 'youtube:search'
    _SEARCH_KEY = 'ytsearch'
    _EXTRA_QUERY_ARGS = {}
    _TESTS = []

    def _get_n_results(self, query, n):
        """Get a specified number of results for a query"""

        videos = []
        limit = n

        for pagenum in itertools.count(1):
            url_query = {
                'search_query': query.encode('utf-8'),
                'page': pagenum,
                'spf': 'navigate',
            }
            url_query.update(self._EXTRA_QUERY_ARGS)
            result_url = 'https://www.youtube.com/results?' + compat_urllib_parse_urlencode(url_query)
            data = self._download_json(
                result_url, video_id='query "%s"' % query,
                note='Downloading page %s' % pagenum,
                errnote='Unable to download API page')
            html_content = data[1]['body']['content']

            if 'class="search-message' in html_content:
                raise ExtractorError(
                    '[youtube] No video results', expected=True)

            new_videos = self._ids_to_results(orderedSet(re.findall(
                r'href="/watch\?v=(.{11})', html_content)))
            videos += new_videos
            if not new_videos or len(videos) > limit:
                break

        if len(videos) > n:
            videos = videos[:n]
        return self.playlist_result(videos, query)


class YoutubeSearchDateIE(YoutubeSearchIE):
    IE_NAME = YoutubeSearchIE.IE_NAME + ':date'
    _SEARCH_KEY = 'ytsearchdate'
    IE_DESC = 'YouTube.com searches, newest videos first'
    _EXTRA_QUERY_ARGS = {'search_sort': 'video_date_uploaded'}


class YoutubeSearchURLIE(YoutubePlaylistBaseInfoExtractor):
    IE_DESC = 'YouTube.com search URLs'
    IE_NAME = 'youtube:search_url'
    _VALID_URL = r'https?://(?:www\.)?youtube\.com/results\?(.*?&)?(?:search_query|q)=(?P<query>[^&]+)(?:[&]|$)'
    _VIDEO_RE = r'href="\s*/watch\?v=(?P<id>[0-9A-Za-z_-]{11})(?:[^"]*"[^>]+\btitle="(?P<title>[^"]+))?'
    _TESTS = [{
        'url': 'https://www.youtube.com/results?baz=bar&search_query=yt-dlp+test+video&filters=video&lclk=video',
        'playlist_mincount': 5,
        'info_dict': {
            'title': 'yt-dlp test video',
        }
    }, {
        'url': 'https://www.youtube.com/results?q=test&sp=EgQIBBgB',
        'only_matching': True,
    }]

    def _real_extract(self, url):
        mobj = re.match(self._VALID_URL, url)
        query = compat_urllib_parse_unquote_plus(mobj.group('query'))
        webpage = self._download_webpage(url, query)
        return self.playlist_result(self._process_page(webpage), playlist_title=query)


class YoutubeShowIE(YoutubePlaylistsBaseInfoExtractor):
    IE_DESC = 'YouTube.com (multi-season) shows'
    _VALID_URL = r'https?://www\.youtube\.com/show/(?P<id>[^?#]*)'
    IE_NAME = 'youtube:show'
    _TESTS = [{
        'url': 'https://www.youtube.com/show/airdisasters',
        'playlist_mincount': 5,
        'info_dict': {
            'id': 'airdisasters',
            'title': 'Air Disasters',
        }
    }]

    def _real_extract(self, url):
        playlist_id = self._match_id(url)
        return super(YoutubeShowIE, self)._real_extract(
            'https://www.youtube.com/show/%s/playlists' % playlist_id)


class YoutubeFeedsInfoExtractor(YoutubeBaseInfoExtractor):
    """
    Base class for feed extractors
    Subclasses must define the _FEED_NAME and _PLAYLIST_TITLE properties.
    """
    _LOGIN_REQUIRED = True

    @property
    def IE_NAME(self):
        return 'youtube:%s' % self._FEED_NAME

    def _real_initialize(self):
        self._login()

    def _real_extract(self, url):
        page = self._download_webpage(
            'https://www.youtube.com/feed/%s' % self._FEED_NAME, self._PLAYLIST_TITLE)

        # The extraction process is the same as for playlists, but the regex
        # for the video ids doesn't contain an index
        ids = []
        more_widget_html = content_html = page
        for page_num in itertools.count(1):
            matches = re.findall(r'href="\s*/watch\?v=([0-9A-Za-z_-]{11})', content_html)

            # 'recommended' feed has infinite 'load more' and each new portion spins
            # the same videos in (sometimes) slightly different order, so we'll check
            # for unicity and break when portion has no new videos
            new_ids = [video_id for video_id in orderedSet(matches) if video_id not in ids]
            if not new_ids:
                break

            ids.extend(new_ids)

            mobj = re.search(r'data-uix-load-more-href="/?(?P<more>[^"]+)"', more_widget_html)
            if not mobj:
                break

            more = self._download_json(
                'https://youtube.com/%s' % mobj.group('more'), self._PLAYLIST_TITLE,
                'Downloading page #%s' % page_num,
                transform_source=uppercase_escape)
            content_html = more['content_html']
            more_widget_html = more['load_more_widget_html']

        return self.playlist_result(
            self._ids_to_results(ids), playlist_title=self._PLAYLIST_TITLE)


class YoutubeWatchLaterIE(YoutubePlaylistIE):
    IE_NAME = 'youtube:watchlater'
    IE_DESC = 'Youtube watch later list, ":ytwatchlater" for short (requires authentication)'
    _VALID_URL = r'https?://www\.youtube\.com/(?:feed/watch_later|(?:playlist|watch)\?(?:.+&)?list=WL)|:ytwatchlater'

    _TESTS = [{
        'url': 'https://www.youtube.com/playlist?list=WL',
        'only_matching': True,
    }, {
        'url': 'https://www.youtube.com/watch?v=bCNU9TrbiRk&index=1&list=WL',
        'only_matching': True,
    }]

    def _real_extract(self, url):
        video = self._check_download_just_video(url, 'WL')
        if video:
            return video
        return self._extract_playlist('WL')


class YoutubeFavouritesIE(YoutubeBaseInfoExtractor):
    IE_NAME = 'youtube:favorites'
    IE_DESC = 'YouTube.com favourite videos, ":ytfav" for short (requires authentication)'
    _VALID_URL = r'https?://www\.youtube\.com/my_favorites|:ytfav(?:ou?rites)?'
    _LOGIN_REQUIRED = True

    def _real_extract(self, url):
        webpage = self._download_webpage('https://www.youtube.com/my_favorites', 'Youtube Favourites videos')
        playlist_id = self._search_regex(r'list=(.+?)["&]', webpage, 'favourites playlist id')
        return self.url_result(playlist_id, 'YoutubePlaylist')


class YoutubeRecommendedIE(YoutubeFeedsInfoExtractor):
    IE_DESC = 'YouTube.com recommended videos, ":ytrec" for short (requires authentication)'
    _VALID_URL = r'https?://www\.youtube\.com/feed/recommended|:ytrec(?:ommended)?'
    _FEED_NAME = 'recommended'
    _PLAYLIST_TITLE = 'Youtube Recommended videos'


class YoutubeSubscriptionsIE(YoutubeFeedsInfoExtractor):
    IE_DESC = 'YouTube.com subscriptions feed, "ytsubs" keyword (requires authentication)'
    _VALID_URL = r'https?://www\.youtube\.com/feed/subscriptions|:ytsubs(?:criptions)?'
    _FEED_NAME = 'subscriptions'
    _PLAYLIST_TITLE = 'Youtube Subscriptions'


class YoutubeHistoryIE(YoutubeFeedsInfoExtractor):
    IE_DESC = 'Youtube watch history, ":ythistory" for short (requires authentication)'
    _VALID_URL = 'https?://www\.youtube\.com/feed/history|:ythistory'
    _FEED_NAME = 'history'
    _PLAYLIST_TITLE = 'Youtube History'


class YoutubeTruncatedURLIE(InfoExtractor):
    IE_NAME = 'youtube:truncated_url'
    IE_DESC = False  # Do not list
    _VALID_URL = r'''(?x)
        (?:https?://)?
        (?:\w+\.)?[yY][oO][uU][tT][uU][bB][eE](?:-nocookie)?\.com/
        (?:watch\?(?:
            feature=[a-z_]+|
            annotation_id=annotation_[^&]+|
            x-yt-cl=[0-9]+|
            hl=[^&]*|
            t=[0-9]+
        )?
        |
            attribution_link\?a=[^&]+
        )
        $
    '''

    _TESTS = [{
        'url': 'http://www.youtube.com/watch?annotation_id=annotation_3951667041',
        'only_matching': True,
    }, {
        'url': 'http://www.youtube.com/watch?',
        'only_matching': True,
    }, {
        'url': 'https://www.youtube.com/watch?x-yt-cl=84503534',
        'only_matching': True,
    }, {
        'url': 'https://www.youtube.com/watch?feature=foo',
        'only_matching': True,
    }, {
        'url': 'https://www.youtube.com/watch?hl=en-GB',
        'only_matching': True,
    }, {
        'url': 'https://www.youtube.com/watch?t=2372',
        'only_matching': True,
    }]

    def _real_extract(self, url):
        raise ExtractorError(
            'Did you forget to quote the URL? Remember that & is a meta '
            'character in most shells, so you want to put the URL in quotes, '
            'like  yt-dlp '
            '"http://www.youtube.com/watch?feature=foo&v=BaW_jenozKc" '
            ' or simply  yt-dlp BaW_jenozKc  .',
            expected=True)


class YoutubeTruncatedIDIE(InfoExtractor):
    IE_NAME = 'youtube:truncated_id'
    IE_DESC = False  # Do not list
    _VALID_URL = r'https?://(?:www\.)?youtube\.com/watch\?v=(?P<id>[0-9A-Za-z_-]{1,10})$'

    _TESTS = [{
        'url': 'https://www.youtube.com/watch?v=N_708QY7Ob',
        'only_matching': True,
    }]

    def _real_extract(self, url):
        video_id = self._match_id(url)
        raise ExtractorError(
            'Incomplete YouTube ID %s. URL %s looks truncated.' % (video_id, url),
            expected=True)


class YoutubeIE(_YoutubeIE):
    _CreateExtractor = None

    def extract_subtitles(self, *args, **kwargs):
        return self._get_subtitles(*args, **kwargs)

    def extract_automatic_captions(self, *args, **kwargs):
        return self._get_automatic_captions(*args, **kwargs)

    def __getSignaturePattern__(self):
        #提取CBS上提取表达式
        raise Exception('todo')

        content = self._download_webpage(
            'http://api.wondershare.com/interface.php?m=online_res&mode=res_list&product_id=0&category_id=114',
            'update config')
        updateUrl = self._search_regex(r'name="youtube"[\S\s]*?<src>\s*(.*?)\s*</src>', content, 'updateUrl',
                                       '')
        return self._download_webpage(updateUrl, 'signature code url')

    def _extract_signature_function(self, video_id, player_url, example_sig):
        try:
            return super(YoutubeIE, self)._extract_signature_function( video_id, player_url, example_sig)
        except:
            pass
        id_m = re.match(
            r'.*?-(?P<id>[a-zA-Z0-9_-]+)(?:/watch_as3|/html5player(?:-new)?|(?:/\w+)/base)?\.(?P<ext>[a-z]+)$',
            player_url)
        if not id_m:
            raise ExtractorError('Cannot identify player %r' % player_url)
        player_type = id_m.group('ext')
        player_id = id_m.group('id')

        # Read from filesystem cache
        func_id = '%s_%s_%s' % (
            player_type, player_id, self._signature_cache_id(example_sig))
        assert os.path.basename(func_id) == func_id

        cache_spec = self._downloader.cache.load('youtube-sigfuncs', func_id)
        if cache_spec is not None:
            return lambda s: ''.join(s[i] for i in cache_spec)

        download_note = (
            'Downloading player %s' % player_url
            if self._downloader.params.get('verbose') else
            'Downloading %s player %s' % (player_type, player_id)
        )
        if player_type == 'js':
            code = self._download_webpage(
                player_url, video_id,
                note=download_note,
                errnote='Download of %s failed' % player_url)
            res = self._parse_sig_js(code)
        elif player_type == 'swf':
            urlh = self._request_webpage(
                player_url, video_id,
                note=download_note,
                errnote='Download of %s failed' % player_url)
            code = urlh.read()
            res = self._parse_sig_swf(code)
        else:
            assert False, 'Invalid player type %r' % player_type

        test_string = ''.join(map(compat_chr, list(range(len(example_sig)))))
        cache_res = res(test_string)
        cache_spec = [ord(c) for c in cache_res]

        self._downloader.cache.store('youtube-sigfuncs', func_id, cache_spec)
        return res

    def _parse_sig_js(self, jscode):
        try:
            return super(YoutubeIE, self)._parse_sig_js(jscode)
        except:
            signature_code = self.__getSignaturePattern__()
            funcname = self._search_regex(
                signature_code,
                jscode, 'Initial JS player signature function name', group='sig')
            jsi = JSInterpreter(jscode)
            initial_function = jsi.extract_function(funcname)
            return lambda s: initial_function([s])


    def get_formatsList(self):
        return self._formats



    def _real_extract(self, url):
        try:
            self._CreateExtractor, localFrist = self.getCBS_YoutubeExctractorEx()
        except:
            print(traceback.format_exc())
            localFrist = True

        funcArray = [self._my_real_extract, self.requestByCBSVersion, self.old_RequestByCBSVersion, self.requstKeepVid]
        if not localFrist:
            funcArray = [self.requestByCBSVersion, self._my_real_extract, self.old_RequestByCBSVersion, self.requstKeepVid]
        error = None
        for func in funcArray:
            self.to_screen('--------------------Begin safe_call_%s--------------------' % func.__name__)
            try:
                result = func(url)
                if result:
                    break
            except:
                print(traceback.format_exc())
                if func == self._my_real_extract:
                    error = traceback.format_exc()
            finally:
                self.to_screen('--------------------End safe_call_%s--------------------' % func.__name__)

        if result:
            return result
        else:
            raise Exception(error)


    def _my_real_extract(self, url):
        from .youtubeCore import CreateExtractor
        ie = CreateExtractor(YoutubeIE,
            try_get,
            clean_html,
            str_to_int,
            smuggle_url,
            int_or_none,
            unescapeHTML,
            mimetype2ext,
            parse_codecs,
            float_or_none,
            remove_quotes,
            unsmuggle_url,
            ExtractorError,
            compat_parse_qs,
            parse_duration,
            unified_strdate,
            get_element_by_id,
            compat_urllib_parse_unquote,
            compat_urllib_parse_urlparse,
            compat_urllib_parse_urlencode,
            compat_urllib_parse_unquote_plus
        )

        ie.set_downloader(self._downloader)
        return ie._real_extract(url)


    def getCBS_YoutubeExctractorEx(self):
        GA = self._downloader.params.get('GA', None)
        content = self._download_webpage(
            'http://api.wondershare.com/interface.php?m=online_res&mode=res_list&product_id=0&category_id=114',
            'update config', fatal=False)
        if GA:
            GA.send('event', 'requestCBS', 'request CBS Fail' if not content else 'request CBS Sucess')
        updateUrl = self._search_regex(r'name="youtube_test"[\S\s]*?<src>\s*(.*?)\s*</src>', content, 'updateUrl','')
        #updateUrl = 'http://cbs.wondershare.cn/resource/001/335/youtube_auto_201705221.py'
        fileName= self._search_regex('(youtube_auto_.+)', updateUrl, updateUrl)

        download_Path  = expand_path(os.path.join('~/.cache', 'yt-dlp'))
        fn = os.path.join(download_Path, fileName)
        code = None
        try:
            if not os.path.exists(fn):
                print('begin save %s to disk %s' % (fileName, download_Path))
                try:
                    try:
                        os.makedirs(os.path.dirname(fn))
                    except OSError as ose:
                        if ose.errno != errno.EEXIST:
                            raise
                    code = self._download_webpage(updateUrl, 'signature code url')
                    if GA:
                        GA.send('event', 'requestCBS', 'request %s Sucess' % updateUrl)
                    with io.open(fn, 'w', encoding='utf-8') as f:
                        f.write(code)
                    return code
                except Exception:
                    if GA:
                        GA.send('event', 'requestCBS', 'request %s Fail' % updateUrl)
                    tb = traceback.format_exc()
                    self._ydl.report_warning(
                        'Writing CBS youtube extractor to %r failed: %s' % (fn, tb))
            else:
                print('load %s from disk %s' % (fileName, download_Path))
                with io.open(fn, 'r', encoding='utf-8') as f:
                    code = f.read()
        finally:
            if not code:
               code = open(fn, 'r').read()
            a = compile(code, '', 'exec')
            exec(a)
            return CreateExtractor, localFrist(),
            # if code:
            #     return code

    def requestByCBSVersion(self, url):
        print('------------------Begin requestByCBSVersion-----------------------')
        try:
            ie = self._CreateExtractor(YoutubeIE,
                try_get,
                clean_html,
                str_to_int,
                smuggle_url,
                int_or_none,
                unescapeHTML,
                mimetype2ext,
                parse_codecs,
                float_or_none,
                remove_quotes,
                unsmuggle_url,
                ExtractorError,
                compat_parse_qs,
                parse_duration,
                unified_strdate,
                get_element_by_id,
                compat_urllib_parse_unquote,
                compat_urllib_parse_urlparse,
                compat_urllib_parse_urlencode,
                compat_urllib_parse_unquote_plus
            )

            ie.set_downloader(self._downloader)
            ie.initialize()
            return ie._real_extract(url)

        except Exception as e:
            print('------------------end requestByCBSVersion fail-----------------------: Exception:')
            print(e)


    def requstKeepVid(self, url):
        import hashlib
        from urllib.parse import quote, urlencode
        print('Begin requstKeepVid')
        host = 'http://srv1.keepvid.com/api/v2.php'
        try:
            data = compat_urllib_parse_urlencode({'url': url})
        except Exception as e:
            print(e)
        mobj = re.search(r'url=(.+)', data)
        gethash = hashlib.md5((('%s_keepvid' % mobj.group(1))).encode('utf-8')).hexdigest()
        reqUrl = '%s?%s' % (host, urlencode({'url': url, 'gethash': gethash}))
        req = sanitized_Request(reqUrl,  headers={'Referer': 'http://www.keepvid.com/'})
        html = self._download_webpage(req, reqUrl)

        data = json.loads(html)
        if not data:
            return
        formats = []
        print(data['error'])
        for value in list(data['download_links'].values()):
            try:
                if value['type'].find('WEBM') != -1:
                    continue

                if value['type'].find('M4A') != -1:
                    fmt = 'm4a'
                    format_note = 'DASH audio'
                    bitrate = 128000
                    quality = 0
                    if value['quality'].find('128 kbps') != -1:
                        bitrate = 128000
                    if value['quality'].find('256 kbps') != -1:
                        bitrate = 256000
                    acodec = 'aac'
                    print('.......................................................m4a', value['url'])
                else:
                    bitrate = 0
                    if value['quality'].find('144p') != -1:
                       quality = 144
                    elif value['quality'].find('240p') != -1:
                       quality = 240
                    elif value['quality'].find('360p') != -1:
                        quality = 360
                    elif value['quality'].find('480p') != -1:
                        quality = 480
                    elif value['quality'].find('720p') != -1:
                        quality = 720
                    elif value['quality'].find('1080p') != -1:
                        quality = 1080
                    elif value['quality'].find('1440p') != -1:
                        quality = 1440
                    elif value['quality'].find('2160p') != -1:
                        quality = 2160
                    elif value['quality'].find('3072p') != -1:
                        quality = 3072
                    else:
                        continue
                    print('.......................................................', value['quality'])
                    if value['type'].find('FLV') != -1:
                        fmt = 'flv'
                        format_note = '%dp' % quality
                        acodec = 'aac'
                    elif value['type'].find('3GP') != -1:
                        fmt = '3gp'
                        format_note = '%dp' % quality
                        acodec = 'aac'
                    else:
                        if value['type'].find('MP4') != -1:
                            fmt = 'mp4'
                            format_note = '%dp' % quality
                            acodec = 'aac'
                            if value['quality'].find('(Video Only)') != -1:
                                format_note = 'DASH video'
                                acodec = 'none'
                        else:
                            continue
                try:
                    formats.append({
                        'url': value['url'],
                        'height': quality,
                        'ext': fmt,
                        'format_note': format_note,
                        'acodec': acodec
                    })
                except Exception as e:
                    print(e)
            except Exception as e:
                print(e)
        title = data['info']['title']
        if not title:
            title = self._og_search_title(
                html, default=None) or self._html_search_regex(
                r'(?s)<title>(.*?)</title>', html, 'video title',
                default='video')
        thumbnail = data['info']['image']
        if not thumbnail:
            thumbnail = self._og_search_thumbnail(html, default=None)
        duration = parse_duration(data['info']['duration'])
        self._check_formats(formats, '')
        if formats and len(formats) > 0 :
            return {
                'id': id,
                'title': title,
                'thumbnail': thumbnail,
                'formats': formats,
                'duration': duration,
                'subExtract': 'KeepVid'
            }
        else:
            raise Exception('KeepVid Return result can\'t connect')


#-----------------------------------------------------
    def getCBS_YoutubeExctractor(self, url):
        content = self._download_webpage(
            'http://api.wondershare.com/interface.php?m=online_res&mode=res_list&product_id=0&category_id=114',
            'update config')
        updateUrl = self._search_regex(r'name="youtube_dev"[\S\s]*?<src>\s*(.*?)\s*</src>', content, 'updateUrl','')
        #updateUrl = 'http://cbs.wondershare.cn/resource/001/335/youtube_auto_201705221.py'
        fileName= self._search_regex('(youtube_auto_.+)', updateUrl, updateUrl)

        download_Path  = expand_path(os.path.join('~/.cache', 'yt-dlp'))
        fn = os.path.join(download_Path, fileName)
        code = None
        try:
            if not os.path.exists(fn):
                try:
                    try:
                        os.makedirs(os.path.dirname(fn))
                    except OSError as ose:
                        if ose.errno != errno.EEXIST:
                            raise
                    code = self._download_webpage(updateUrl, 'signature code url')
                    with io.open(fn, 'w', encoding='utf-8') as f:
                        f.write(code)
                    return code
                except Exception:
                    tb = traceback.format_exc()
                    self._ydl.report_warning(
                        'Writing CBS youtube extractor to %r failed: %s' % (fn, tb))
            else:
                with io.open(fn, 'r', encoding='utf-8') as f:
                    code = f.read()
        finally:
            if not code:
                code = open(fn, 'r').read()
            a = compile(code, '', 'exec')
            exec(a)
            return getSniffer(url, None)
            # if code:
            #     return code

    def old_RequestByCBSVersion(self, url):
        print('------------------Begin Old_requestByCBSVersion-----------------------')
        try:
            obj = self.getCBS_YoutubeExctractor(url)
            if not obj:
                return
            try:
                obj.start()
                title = obj.getTitle()
                duration = obj.getDuration()
                thumbnail = obj.getPic()
                list = obj.getList()
                formats = []
                for item in list:
                    try:
                        if item.isValid() == 1:
                            format = item.getFormat()
                            quality = int_or_none(item.getQuality(), default=360)
                            videoUrl = item.getUrl()
                            fileSize = int_or_none(item.getSize(), default=0)
                            if not videoUrl or not quality or not format:
                                continue

                            if quality > 1440:
                                quality = 2160
                            elif quality > 1080:
                                quality = 1440
                            elif quality > 720:
                                quality = 1080
                            elif quality > 540:
                                quality = 720
                            elif quality > 480:
                                quality = 480
                            elif quality > 360:
                                quality = 360
                            elif quality > 240:
                                quality = 240
                            else:
                                continue

                            format_note = None
                            acodec = 'aac'
                            Lformat = format.lower()
                            if Lformat.find('flv') > -1:
                                ext = 'flv'
                            elif Lformat.find('mp4') > -1:
                                ext = 'mp4'
                            elif Lformat.find('webm') > -1:
                                ext = 'webm'
                            elif Lformat.find('3gp') > -1:
                                ext = '3gp'
                            elif Lformat.find('m3u8') > -1:
                                ext = 'm3u8'
                            elif Lformat.find('mp4v') > -1:
                                ext = 'mp4'
                                format_note = 'DASH video'
                                acodec = 'none'
                            elif Lformat.find('mp4a') > -1:
                                ext = 'm4a'
                                format_note = 'DASH audio'
                                acodec = 'aac'
                            else:
                                continue
                            formats.append({
                                'url': videoUrl,
                                'height': quality,
                                'ext': ext,
                                'filesize': fileSize,
                                'format_note': format_note if format_note else '%dp' % quality,
                                'acodec': acodec
                            })
                    except Exception as e:
                        print(e)

                duration = parse_duration(duration)
                self._check_formats(formats, '')
                if formats and len(formats) > 0 :
                    print('------------------end requestByCBSVersion Sucess-----------------------')
                    return {
                        'id': id,
                        'title': title,
                        'thumbnail': thumbnail,
                        'formats': formats,
                        'duration': duration,
                        'subExtract': 'CBSYoutubeExtract'
                    }
                else:
                    raise Exception('CBS Youtube Extractor no result')
            except Exception as e:
                print(e)
        except Exception as e:
            print('------------------end Old_requestByCBSVersion fail-----------------------: Exception:')
            print(e)