# encoding: utf-8



import re
import json
import itertools
import threading

from ..utils import (
    smuggle_url,
    determine_ext,
    int_or_none,
    sanitized_Request,
    try_get,
    parse_filesize,
    unsmuggle_url,
    std_headers,
    RegexNotFoundError,
    ExtractorError,
)

from ..compat import (
    compat_str,
    compat_urlparse,
    compat_HTTPError
)

from ..extractor.vimeo import (
    VimeoBaseInfoExtractor,
    VimeoIE,
    VimeoChannelIE
)


class VimeoBlogIE(VimeoBaseInfoExtractor):
    IE_NAME = 'vimeo:Blog'
    _VALID_URL = r'https://vimeo\.com/blog/([^/]+)'

    def _real_extract(self, url):
        html = self._download_webpage(url, None)
        vid = re.search(r'data-config-url="(.*)/config', html)
        if vid:
            playUrl = vid.group(1)
            IE = VimeoIE(self._downloader)
            ie_result = IE._real_extract(playUrl)
            formats = []
            for format in  ie_result["formats"]:
                if re.search('primaryToken=',format['url']):
                    formats.append(format)
            if formats:
                ie_result["formats"] = formats

            return ie_result

# 修正其title
class VimeoExIE(VimeoIE):
    def _real_extract(self, url):
        result = super(VimeoExIE, self)._real_extract(url)
        video_id = result['id']
        webpage = self._download_webpage(url, video_id)
        result.update({
            'title': self._og_search_title(webpage),
        })
        return result

class VimeoInfoIE(VimeoIE):

    def _parse_config(self, config, video_id):
        video_data = config['video']
        # Extract title
        video_title = video_data['title']

        # Extract video thumbnail
        video_thumbnail = video_data.get('thumbnail')
        if video_thumbnail is None:
            video_thumbs = video_data.get('thumbs')
            if video_thumbs and isinstance(video_thumbs, dict):
                _, video_thumbnail = sorted((int(width if width.isdigit() else 0), t_url) for (width, t_url) in list(video_thumbs.items()))[-1]

        # Extract video duration
        video_duration = int_or_none(video_data.get('duration'))

        return {
            'title': video_title,
            'thumbnail': video_thumbnail,
            'duration': video_duration,
        }

    def _real_extract(self, url):
        url, data = unsmuggle_url(url, {})
        headers = std_headers.copy()
        if 'http_headers' in data:
            headers.update(data['http_headers'])
        if 'Referer' not in headers:
            headers['Referer'] = url

        # Extract ID from URL
        mobj = re.match(self._VALID_URL, url)
        video_id = mobj.group('id')
        if mobj.group('pro') or mobj.group('player'):
            url = 'https://player.vimeo.com/video/' + video_id
        elif any(p in url for p in ('play_redirect_hls', 'moogaloop.swf')):
            url = 'https://vimeo.com/' + video_id

        # Retrieve video webpage to extract further information
        request = sanitized_Request(url, headers=headers)
        try:
            webpage, urlh = self._download_webpage_handle(request, video_id)
        except ExtractorError as ee:
            if isinstance(ee.cause, compat_HTTPError) and ee.cause.code == 403:
                errmsg = ee.cause.read()
                if b'Because of its privacy settings, this video cannot be played here' in errmsg:
                    raise ExtractorError(
                        'Cannot download embed-only video without embedding '
                        'URL. Please call yt-dlp with the URL of the page '
                        'that embeds this video.',
                        expected=True)
            raise

        try:
            try:
                info_dict = self._search_json_ld(webpage, '123',fatal=False)
                if info_dict:
                    info_dict.update({
                        'id': video_id,
                        'url': url,
                    })
                    return info_dict

                config_url = self._html_search_regex(
                    r' data-config-url="(.+?)"', webpage,
                    'config URL', default=None)
                if not config_url:
                    # Sometimes new react-based page is served instead of old one that require
                    # different config URL extraction approach (see
                    # https://github.com/rg3/yt-dlp/pull/7209)
                    vimeo_clip_page_config = self._search_regex(
                        r'vimeo\.clip_page_config\s*=\s*({.+?});', webpage,
                        'vimeo clip page config')
                    page_config = self._parse_json(vimeo_clip_page_config, video_id)
                    config_url = page_config['player']['config_url']

                config_json = self._download_webpage(config_url, video_id)
                config = json.loads(config_json)
            except RegexNotFoundError:
                # For pro videos or player.vimeo.com urls
                # We try to find out to which variable is assigned the config dic
                m_variable_name = re.search(r'(\w)\.video\.id', webpage)
                if m_variable_name is not None:
                    config_re = r'%s=({[^}].+?});' % re.escape(m_variable_name.group(1))
                else:
                    config_re = [r' = {config:({.+?}),assets:', r'(?:[abc])=({.+?});']
                config = self._search_regex(config_re, webpage, 'info section',
                                            flags=re.DOTALL)
                config = json.loads(config)
        except Exception as e:
            if re.search('The creator of this video has not given you permission to embed it on this domain.', webpage):
                raise ExtractorError('The author has restricted the access to this video, try with the "--referer" option')

            if re.search(r'<form[^>]+?id="pw_form"', webpage) is not None:
                if '_video_password_verified' in data:
                    raise ExtractorError('video password verification failed!')
                self._verify_video_password(url, video_id, webpage)
                return self._real_extract(
                    smuggle_url(url, {'_video_password_verified': 'verified'}))
            else:
                raise ExtractorError('Unable to extract info section',
                                     cause=e)
        else:
            if config.get('view') == 4:
                config = self._verify_player_video_password(url, video_id)


        info_dict = self._parse_config(config, video_id)

        info_dict.update({
            'id': video_id,
            'url': url,
        })

        return info_dict

# def appendEntry(self, entries, entry):
#     #self._lock.acquire()
#     try:
#
#     finally:
#         self._lock.release()

def _title_and_entriesEx(self, list_id, base_url):

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

    def getVideoInfo(url, entries):
        try:
            ie = VimeoInfoIE()
            ie.set_downloader(self._downloader)
            info = ie._real_extract(url)
            entries.append(info)
            #self.appendEntry(entries, info)
        except Exception as ex:
            print(ex)
            pass

    def getVideoInfos(urls):
        threadList = []
        entries = []
        for url in urls:
            try:
                t = threading.Thread(target=getVideoInfo, args=(url, entries))
                threadList.append(t)
                t.setDaemon(True)
                t.start()
            except:
                pass
        for t in threadList:
            t.join()
        return entries


    all_urls = []

    # page_url = self._page_url(base_url, 1)
    # webpage = self._download_webpage(
    #     page_url, list_id,
    #     'Downloading page %s' % 1)
    # webpage = self._login_list_password(page_url, list_id, webpage)
    # page_ids = re.findall(r'data-page\="(\d+)">\1</a>',webpage)
    # if page_ids:
    #     pages = [x for x in range(1, int(page_ids[-1]))]
    # else:
    pages = itertools.count(1)

    for pagenum in pages:
        page_url = self._page_url(base_url, pagenum)
        webpage = self._download_webpage(
            page_url, list_id,
            'Downloading page %s' % pagenum)

        if pagenum == 1:
            webpage = self._login_list_password(page_url, list_id, webpage)
            yield self._extract_list_title(webpage)
        if pagenum == 20:
            break
        # Try extracting href first since not all videos are available via
        # short https://vimeo.com/id URL (e.g. https://vimeo.com/channels/tributes/6213729)
        clips = re.findall(
            r'id="clip_(\d+)"[^>]*>\s*<a[^>]+href="(/(?:[^/]+/)*\1)(?:[^>]+\btitle="([^"]+)")?', webpage)
        urls = []
        if clips:
            for video_id, video_url, video_title in clips:
                urls.append(compat_urlparse.urljoin(base_url, video_url))
        # More relaxed fallback
        else:
            for video_id in re.findall(r'id=["\']clip_(\d+)', webpage):
                urls.append('https://vimeo.com/%s' % video_id,)

            if not urls and isinstance(self, VimeoSearchIE):
                urls = ['https://vimeo.com/%s' % video_id for video_id in re.findall(r'"clip":\{"uri":"\\/videos\\/(\d+)', webpage)]
        all_urls = list(set(urls).union(set(all_urls)))

        if re.search(self._MORE_PAGES_INDICATOR, webpage, re.DOTALL) is None:
            break

    enties = getVideoInfos(all_urls)

    for entry in enties:
        yield url_result(entry['url'], 'vimeo', video_id=entry['id'], video_title=entry['title'], video_duration=entry['duration'])



VimeoChannelIE._title_and_entries = _title_and_entriesEx
# VimeoChannelIE.appendEntry = appendEntry


class VimeoSearchIE(VimeoChannelIE):

    _VALID_URL = r'https://vimeo\.com/search[/?]+'

    IE_NAME = 'vimeo:search'

    _TITLE_RE = r'<title>(.+)</title>'

    _MORE_PAGES_INDICATOR = '"paging"\:\{"next"\:"(.+)"'
    key = ''


    def _page_url(self, base_url, pagenum):
        return '%s/page:%d/?q=%s' % (base_url, pagenum, self.key)


    def _real_extract(self, url):
        self.key = self._search_regex(r'\?q=(.+)', url, '', '')

        return self._extract_videos(self.key, 'https://vimeo.com/search')

VimeoChannelIE._VALID_URL = r'https://vimeo\.com/channels/(?P<id>[^/?#]+)/?(?:$|[?#]|\d+)'