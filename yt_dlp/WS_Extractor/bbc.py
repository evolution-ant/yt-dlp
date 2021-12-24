# coding: utf-8


import re
import xml.etree.ElementTree

from ..extractor.common import InfoExtractor
from ..extractor.bbc import (
    BBCCoUkIE as OldBBCCoUkIE,
    BBCIE as OldBBCIE,
    BBCCoUkArticleIE as OldBBCCoUkArticleIE
)
from ..utils import (
    ExtractorError,
    float_or_none,
    int_or_none,
    parse_duration,
    parse_iso8601,
    remove_end,
    unescapeHTML,
)
from ..compat import (
    compat_HTTPError,
    compat_urllib_parse_urlparse,
)


class BBCCoUkIE(InfoExtractor):
    IE_NAME = 'bbc.co.uk'
    IE_DESC = 'BBC iPlayer'
    _VALID_URL = r'https?://(?:www\.)?bbc\.co\.uk/(?:(?:programmes/(?!articles/)|iplayer(?:/[^/]+)?/(?:episode/|playlist/))|music/clips[/#])(?P<id>[\da-z]{8})'

    _MEDIASELECTOR_URLS = [
        # Provides HQ HLS streams with even better quality that pc mediaset but fails
        # with geolocation in some cases when it's even not geo restricted at all (e.g.
        # http://www.bbc.co.uk/programmes/b06bp7lf)
        'http://open.live.bbc.co.uk/mediaselector/5/select/version/2.0/mediaset/iptv-all/vpid/%s',
        'http://open.live.bbc.co.uk/mediaselector/5/select/version/2.0/mediaset/pc/vpid/%s',
    ]

    _MEDIASELECTION_NS = 'http://bbc.co.uk/2008/mp/mediaselection'
    _EMP_PLAYLIST_NS = 'http://bbc.co.uk/2008/emp/playlist'

    _NAMESPACES = (
        _MEDIASELECTION_NS,
        _EMP_PLAYLIST_NS,
    )


    class MediaSelectionError(Exception):
        def __init__(self, id):
            self.id = id

    def _extract_asx_playlist(self, connection, programme_id):
        asx = self._download_xml(connection.get('href'), programme_id, 'Downloading ASX playlist')
        return [ref.get('href') for ref in asx.findall('./Entry/ref')]

    def _extract_connection(self, connection, programme_id):
        formats = []
        kind = connection.get('kind')
        protocol = connection.get('protocol')
        supplier = connection.get('supplier')
        if protocol == 'http':
            href = connection.get('href')
            transfer_format = connection.get('transferFormat')
            # ASX playlist
            if supplier == 'asx':
                for i, ref in enumerate(self._extract_asx_playlist(connection, programme_id)):
                    formats.append({
                        'url': ref,
                        'format_id': 'ref%s_%s' % (i, supplier),
                    })
            # Skip DASH until supported
            elif transfer_format == 'dash':
                pass
            elif transfer_format == 'hls':
                '''
                m3u8_formats = self._extract_m3u8_formats(
                    href, programme_id, ext='mp4', entry_protocol='m3u8_native',
                    m3u8_id=supplier)
                if m3u8_formats:
                    formats.extend(m3u8_formats)
            '''
                formats = [{
                    'format_id': '-'.join([_f for _f in [None, 'meta'] if _f]),
                    'url': href,
                    'ext': 'mp4',
                    'protocol': 'm3u8',
                }]
            # Direct link
            else:
                formats.append({
                    'url': href,
                    'format_id': supplier or kind or protocol,
                })
        elif protocol == 'rtmp':
            application = connection.get('application', 'ondemand')
            auth_string = connection.get('authString')
            identifier = connection.get('identifier')
            server = connection.get('server')
            formats.append({
                'url': '%s://%s/%s?%s' % (protocol, server, application, auth_string),
                'play_path': identifier,
                'app': '%s?%s' % (application, auth_string),
                'page_url': 'http://www.bbc.co.uk',
                'player_url': 'http://www.bbc.co.uk/emp/releases/iplayer/revisions/617463_618125_4/617463_618125_4_emp.swf',
                'rtmp_live': False,
                'ext': 'flv',
                'format_id': supplier,
            })
        return formats

    def _extract_items(self, playlist):
        return playlist.findall('./{%s}item' % self._EMP_PLAYLIST_NS)

    def _findall_ns(self, element, xpath):
        elements = []
        for ns in self._NAMESPACES:
            elements.extend(element.findall(xpath % ns))
        return elements

    def _extract_medias(self, media_selection):
        error = media_selection.find('./{%s}error' % self._MEDIASELECTION_NS)
        if error is None:
            media_selection.find('./{%s}error' % self._EMP_PLAYLIST_NS)
        if error is not None:
            raise BBCCoUkIE.MediaSelectionError(error.get('id'))
        return self._findall_ns(media_selection, './{%s}media')

    def _extract_connections(self, media):
        return self._findall_ns(media, './{%s}connection')

    def _extract_video(self, media, programme_id):
        formats = []
        vbr = int_or_none(media.get('bitrate'))
        vcodec = media.get('encoding')
        service = media.get('service')
        width = int_or_none(media.get('width'))
        height = int_or_none(media.get('height'))
        file_size = int_or_none(media.get('media_file_size'))
        for connection in self._extract_connections(media):
            conn_formats = self._extract_connection(connection, programme_id)
            for format in conn_formats:
                format.update({
                    'width': width,
                    'height': height,
                    'vbr': vbr,
                    'vcodec': vcodec,
                    'filesize': file_size,
                })
                if service:
                    format['format_id'] = '%s_%s' % (service, format['format_id'])
            formats.extend(conn_formats)
        return formats

    def _extract_audio(self, media, programme_id):
        formats = []
        abr = int_or_none(media.get('bitrate'))
        acodec = media.get('encoding')
        service = media.get('service')
        for connection in self._extract_connections(media):
            conn_formats = self._extract_connection(connection, programme_id)
            for format in conn_formats:
                format.update({
                    'format_id': '%s_%s' % (service, format['format_id']),
                    'abr': abr,
                    'acodec': acodec,
                })
            formats.extend(conn_formats)
        return formats

    def _get_subtitles(self, media, programme_id):
        subtitles = {}
        for connection in self._extract_connections(media):
            captions = self._download_xml(connection.get('href'), programme_id, 'Downloading captions')
            lang = captions.get('{http://www.w3.org/XML/1998/namespace}lang', 'en')
            subtitles[lang] = [
                {
                    'url': connection.get('href'),
                    'ext': 'ttml',
                },
            ]
        return subtitles

    def _raise_extractor_error(self, media_selection_error):
        raise ExtractorError(
            '%s returned error: %s' % (self.IE_NAME, media_selection_error.id),
            expected=True)

    def _getNewMediaSelection(self, vpid):
        #str = 'http://open.live.bbc.co.uk/mediaselector/5/select/version/2.0/mediaset/' \
        #      'mobile-phone-baseline/vpid/%s/'
        str = 'http://open.live.bbc.co.uk/mediaselector/5/select/version/2.0/mediaset/' \
              'pc/vpid/%s/'
        import hashlib;
        key = '7dff7671d0c697fedb1d905d9a121719938b92bf'
        data = key + vpid
        hashValue =  hashlib.sha1(data).hexdigest()
        return str +  ('atk/%s/asn/1/' % hashValue)

    def _download_media_selector(self, programme_id):
        last_exception = None
        for mediaselector_url in self._MEDIASELECTOR_URLS:
            try:
                formats, subtitles = self._download_media_selector_url(
                    mediaselector_url % programme_id, programme_id)
                formats = [item for item in formats if re.search(r'rtmp://|rtmpe://',formats[0]['url']) is None]
                if len(formats)>0:
                    return formats, subtitles
                else:
                    continue
            except BBCCoUkIE.MediaSelectionError as e:
                if e.id in ('notukerror', 'geolocation'):
                    last_exception = e
                    continue
                self._raise_extractor_error(e)
            except Exception as e:
                continue
        self._raise_extractor_error(last_exception)

    def _download_media_selector_url(self, url, programme_id=None):
        try:
            media_selection = self._download_xml(
                url, programme_id, 'Downloading media selection XML')
        except ExtractorError as ee:
            if isinstance(ee.cause, compat_HTTPError) and ee.cause.code == 403:
                media_selection = xml.etree.ElementTree.fromstring(ee.cause.read().decode('utf-8'))
            else:
                raise
        return self._process_media_selector(media_selection, programme_id)

    def _process_media_selector(self, media_selection, programme_id):
        formats = []
        subtitles = None

        for media in self._extract_medias(media_selection):
            kind = media.get('kind')
            if kind == 'audio':
                formats.extend(self._extract_audio(media, programme_id))
            elif kind == 'video':
                formats.extend(self._extract_video(media, programme_id))
            elif kind == 'captions':
                subtitles = self.extract_subtitles(media, programme_id)
        return formats, subtitles

    def _download_playlist(self, playlist_id):
        try:
            try:
                playlist = self._download_json(
                    'http://www.bbc.co.uk/programmes/%s/playlist.json' % playlist_id,
                    playlist_id, 'Downloading playlist JSON')
            except Exception as ex:
                #处理Cookie无效的问题
                if ex.message.find('400') > -1:
                    playlist = self._download_json(
                        'http://www.bbc.co.uk/programmes/%s/playlist.json' % playlist_id,
                        playlist_id, 'Downloading playlist JSON', headers = {'Cookies': ''})

            version = playlist.get('defaultAvailableVersion')
            if version:
                smp_config = version['smpConfig']
                title = smp_config['title']
                description = smp_config['summary']
                for item in smp_config['items']:
                    kind = item['kind']
                    if kind != 'programme' and kind != 'radioProgramme':
                        continue
                    programme_id = item.get('vpid')
                    duration = int_or_none(item.get('duration'))
                    self._MEDIASELECTOR_URLS.insert(0, self._getNewMediaSelection(programme_id))
                    formats, subtitles = self._download_media_selector(programme_id)

                return programme_id, title, description, duration, formats, subtitles
        except ExtractorError as ee:
            if not (isinstance(ee.cause, compat_HTTPError) and ee.cause.code == 404):
                raise

        # fallback to legacy playlist
        return self._process_legacy_playlist(playlist_id)

    def _process_legacy_playlist_url(self, url, display_id):
        playlist = self._download_legacy_playlist_url(url, display_id)
        return self._extract_from_legacy_playlist(playlist, display_id)

    def _process_legacy_playlist(self, playlist_id):
        return self._process_legacy_playlist_url(
            'http://www.bbc.co.uk/iplayer/playlist/%s' % playlist_id, playlist_id)

    def _download_legacy_playlist_url(self, url, playlist_id=None):
        return self._download_xml(
            url, playlist_id, 'Downloading legacy playlist XML')

    def _extract_from_legacy_playlist(self, playlist, playlist_id):
        no_items = playlist.find('./{%s}noItems' % self._EMP_PLAYLIST_NS)
        if no_items is not None:
            reason = no_items.get('reason')
            if reason == 'preAvailability':
                msg = 'Episode %s is not yet available' % playlist_id
            elif reason == 'postAvailability':
                msg = 'Episode %s is no longer available' % playlist_id
            elif reason == 'noMedia':
                msg = 'Episode %s is not currently available' % playlist_id
            else:
                msg = 'Episode %s is not available: %s' % (playlist_id, reason)
            raise ExtractorError(msg, expected=True)

        for item in self._extract_items(playlist):
            kind = item.get('kind')
            if kind != 'programme' and kind != 'radioProgramme':
                continue
            title = playlist.find('./{%s}title' % self._EMP_PLAYLIST_NS).text
            description_el = playlist.find('./{%s}summary' % self._EMP_PLAYLIST_NS)
            description = description_el.text if description_el is not None else None

            def get_programme_id(item):
                def get_from_attributes(item):
                    for p in('identifier', 'group'):
                        value = item.get(p)
                        if value and re.match(r'^[pb][\da-z]{7}$', value):
                            return value
                get_from_attributes(item)
                mediator = item.find('./{%s}mediator' % self._EMP_PLAYLIST_NS)
                if mediator is not None:
                    return get_from_attributes(mediator)

            programme_id = get_programme_id(item)
            duration = int_or_none(item.get('duration'))

            if programme_id:
                formats, subtitles = self._download_media_selector(programme_id)
            else:
                formats, subtitles = self._process_media_selector(item, playlist_id)
                programme_id = playlist_id

        return programme_id, title, description, duration, formats, subtitles

    def _sort_formats(self, formats):
        if not formats:
            raise ExtractorError('No video formats found')

        def _formats_key(f):
            # TODO remove the following workaround
            from ..utils import determine_ext
            if not f.get('ext') and 'url' in f:
                f['ext'] = determine_ext(f['url'])

            preference = f.get('preference')
            if preference is None:
                proto = f.get('protocol')
                if proto is None:
                    proto = compat_urllib_parse_urlparse(f.get('url', '')).scheme

                preference = 0 if proto in ['http', 'https'] else -0.1
                preference = preference-50 if proto in ['rtmp', 'rtmpe'] else preference
                if f.get('ext') in ['f4f', 'f4m']:  # Not yet supported
                    preference -= 0.5

            if f.get('vcodec') == 'none':  # audio only
                if self._downloader.params.get('prefer_free_formats'):
                    ORDER = ['aac', 'mp3', 'm4a', 'webm', 'ogg', 'opus']
                else:
                    ORDER = ['webm', 'opus', 'ogg', 'mp3', 'aac', 'm4a']
                ext_preference = 0
                try:
                    audio_ext_preference = ORDER.index(f['ext'])
                except ValueError:
                    audio_ext_preference = -1
            else:
                if self._downloader.params.get('prefer_free_formats'):
                    ORDER = ['flv', 'mp4', 'webm']
                else:
                    ORDER = ['webm', 'flv', 'mp4']
                try:
                    ext_preference = ORDER.index(f['ext'])
                except ValueError:
                    ext_preference = -1
                audio_ext_preference = 0

            return (
                preference,
                f.get('language_preference') if f.get('language_preference') is not None else -1,
                f.get('quality') if f.get('quality') is not None else -1,
                f.get('tbr') if f.get('tbr') is not None else -1,
                f.get('filesize') if f.get('filesize') is not None else -1,
                f.get('vbr') if f.get('vbr') is not None else -1,
                f.get('height') if f.get('height') is not None else -1,
                f.get('width') if f.get('width') is not None else -1,
                ext_preference,
                f.get('abr') if f.get('abr') is not None else -1,
                audio_ext_preference,
                f.get('fps') if f.get('fps') is not None else -1,
                f.get('filesize_approx') if f.get('filesize_approx') is not None else -1,
                f.get('source_preference') if f.get('source_preference') is not None else -1,
                f.get('format_id'),
            )
        formats.sort(key=_formats_key)


    def _real_extract(self, url):

        for i in range(2):
            self._downloader.params['listsubtitles'] = 1
            try:
                result = self.do_real_extract(url)
                if result and len(result.get('formats', []))>0:
                    return result
                else:
                    if i == 1:
                        try:
                            self._downloader.cookiejar.clear('.co.uk')
                        except:
                            pass
            except:
                pass
            finally:
                if 'listsubtitles' in self._downloader.params:
                    self._downloader.params.pop('listsubtitles')


    def do_real_extract(self, url):
        oldBBC = OldBBCCoUkIE()
        oldBBC.set_downloader(self._downloader)
        try:
            result = oldBBC._real_extract(url)
        except:
            result = None
        if result:
            return result

        group_id = self._match_id(url)

        webpage = self._download_webpage(url, group_id, 'Downloading video page')

        programme_id = None

        tviplayer = self._search_regex(
            r'mediator\.bind\(({.+?})\s*,\s*document\.getElementById',
            webpage, 'player', default=None)

        if tviplayer:
            player = self._parse_json(tviplayer, group_id).get('player', {})
            duration = int_or_none(player.get('duration'))
            programme_id = player.get('vpid')

        if not programme_id:
            programme_id = self._search_regex(
                r'"vpid"\s*:\s*"([\da-z]{8})"', webpage, 'vpid', fatal=False, default=None)

        if programme_id:
            self._MEDIASELECTOR_URLS.insert(0, self._getNewMediaSelection(programme_id))
            formats, subtitles = self._download_media_selector(programme_id)
            title = self._og_search_title(webpage)
            description = self._search_regex(
                r'<p class="[^"]*medium-description[^"]*">([^<]+)</p>',
                webpage, 'description', fatal=False, default='')
            duration = self._search_regex(r'"duration":(\d*)', webpage, 'duration', default=0)
        else:
            programme_id, title, description, duration, formats, subtitles = self._download_playlist(group_id)

        self._sort_formats(formats)

        return {
            'id': programme_id,
            'title': title,
            'description': description,
            'thumbnail': self._og_search_thumbnail(webpage, default=None),
            'duration': duration,
            'formats': formats,
            'subtitles': subtitles,
        }


class BBCIE(BBCCoUkIE):
    IE_NAME = 'bbc'
    IE_DESC = 'BBC'
    _VALID_URL = r'https?://(?:www\.)?bbc\.(?:com|co\.uk)/(?:[^/]+/)+(?P<id>[^/#?]+)'

    _MEDIASELECTOR_URLS = [
        # Provides HQ HLS streams but fails with geolocation in some cases when it's
        # even not geo restricted at all
        'http://open.live.bbc.co.uk/mediaselector/5/select/version/2.0/mediaset/iptv-all/vpid/%s',
        # Provides more formats, namely direct mp4 links, but fails on some videos with
        # notukerror for non UK (?) users (e.g.
        # http://www.bbc.com/travel/story/20150625-sri-lankas-spicy-secret)
        'http://open.live.bbc.co.uk/mediaselector/4/mtis/stream/%s',
        # Provides fewer formats, but works everywhere for everybody (hopefully)
        'http://open.live.bbc.co.uk/mediaselector/5/select/version/2.0/mediaset/journalism-pc/vpid/%s',
    ]

    _TESTS = [{
        # article with multiple videos embedded with data-playable containing vpids
        'url': 'http://www.bbc.com/news/world-europe-32668511',
        'info_dict': {
            'id': 'world-europe-32668511',
            'title': 'Russia stages massive WW2 parade despite Western boycott',
            'description': 'md5:00ff61976f6081841f759a08bf78cc9c',
        },
        'playlist_count': 2,
    }, {
        # article with multiple videos embedded with data-playable (more videos)
        'url': 'http://www.bbc.com/news/business-28299555',
        'info_dict': {
            'id': 'business-28299555',
            'title': 'Farnborough Airshow: Video highlights',
            'description': 'BBC reports and video highlights at the Farnborough Airshow.',
        },
        'playlist_count': 9,
        'skip': 'Save time',
    }, {
        # article with multiple videos embedded with `new SMP()`
        # broken
        'url': 'http://www.bbc.co.uk/blogs/adamcurtis/entries/3662a707-0af9-3149-963f-47bea720b460',
        'info_dict': {
            'id': '3662a707-0af9-3149-963f-47bea720b460',
            'title': 'BBC Blogs - Adam Curtis - BUGGER',
        },
        'playlist_count': 18,
    }, {
        # single video embedded with data-playable containing vpid
        'url': 'http://www.bbc.com/news/world-europe-32041533',
        'info_dict': {
            'id': 'p02mprgb',
            'ext': 'mp4',
            'title': 'Aerial footage showed the site of the crash in the Alps - courtesy BFM TV',
            'description': 'md5:2868290467291b37feda7863f7a83f54',
            'duration': 47,
            'timestamp': 1427219242,
            'upload_date': '20150324',
        },
        'params': {
            # rtmp download
            'skip_download': True,
        }
    }, {
        # article with single video embedded with data-playable containing XML playlist
        # with direct video links as progressiveDownloadUrl (for now these are extracted)
        # and playlist with f4m and m3u8 as streamingUrl
        'url': 'http://www.bbc.com/turkce/haberler/2015/06/150615_telabyad_kentin_cogu',
        'info_dict': {
            'id': '150615_telabyad_kentin_cogu',
            'ext': 'mp4',
            'title': "YPG: Tel Abyad'ın tamamı kontrolümüzde",
            'timestamp': 1434397334,
            'upload_date': '20150615',
        },
        'params': {
            'skip_download': True,
        }
    }, {
        # single video embedded with data-playable containing XML playlists (regional section)
        'url': 'http://www.bbc.com/mundo/video_fotos/2015/06/150619_video_honduras_militares_hospitales_corrupcion_aw',
        'info_dict': {
            'id': '150619_video_honduras_militares_hospitales_corrupcion_aw',
            'ext': 'mp4',
            'title': 'Honduras militariza sus hospitales por nuevo escándalo de corrupción',
            'timestamp': 1434713142,
            'upload_date': '20150619',
        },
        'params': {
            'skip_download': True,
        }
    }, {
        # single video from video playlist embedded with vxp-playlist-data JSON
        'url': 'http://www.bbc.com/news/video_and_audio/must_see/33376376',
        'info_dict': {
            'id': 'p02w6qjc',
            'ext': 'mp4',
            'title': '''Judge Mindy Glazer: "I'm sorry to see you here... I always wondered what happened to you"''',
            'duration': 56,
        },
        'params': {
            'skip_download': True,
        }
    }, {
        # single video story with digitalData
        'url': 'http://www.bbc.com/travel/story/20150625-sri-lankas-spicy-secret',
        'info_dict': {
            'id': 'p02q6gc4',
            'ext': 'flv',
            'title': 'Sri Lanka’s spicy secret',
            'description': 'As a new train line to Jaffna opens up the country’s north, travellers can experience a truly distinct slice of Tamil culture.',
            'timestamp': 1437674293,
            'upload_date': '20150723',
        },
        'params': {
            # rtmp download
            'skip_download': True,
        }
    }, {
        # single video story without digitalData
        'url': 'http://www.bbc.com/autos/story/20130513-hyundais-rock-star',
        'info_dict': {
            'id': 'p018zqqg',
            'ext': 'mp4',
            'title': 'Hyundai Santa Fe Sport: Rock star',
            'description': 'md5:b042a26142c4154a6e472933cf20793d',
            'timestamp': 1415867444,
            'upload_date': '20141113',
        },
        'params': {
            # rtmp download
            'skip_download': True,
        }
    }, {
        # single video with playlist.sxml URL in playlist param
        'url': 'http://www.bbc.com/sport/0/football/33653409',
        'info_dict': {
            'id': 'p02xycnp',
            'ext': 'mp4',
            'title': 'Transfers: Cristiano Ronaldo to Man Utd, Arsenal to spend?',
            'description': 'BBC Sport\'s David Ornstein has the latest transfer gossip, including rumours of a Manchester United return for Cristiano Ronaldo.',
            'duration': 140,
        },
        'params': {
            # rtmp download
            'skip_download': True,
        }
    }, {
        # article with multiple videos embedded with playlist.sxml in playlist param
        'url': 'http://www.bbc.com/sport/0/football/34475836',
        'info_dict': {
            'id': '34475836',
            'title': 'What Liverpool can expect from Klopp',
        },
        'playlist_count': 3,
    }, {
        # single video with playlist URL from weather section
        'url': 'http://www.bbc.com/weather/features/33601775',
        'only_matching': True,
    }, {
        # custom redirection to www.bbc.com
        'url': 'http://www.bbc.co.uk/news/science-environment-33661876',
        'only_matching': True,
    }]

    @classmethod
    def suitable(cls, url):
        return False if BBCCoUkIE.suitable(url) or BBCCoUkArticleIE.suitable(url) else super(BBCIE, cls).suitable(url)

    def _extract_from_media_meta(self, media_meta, video_id):
        # Direct links to media in media metadata (e.g.
        # http://www.bbc.com/turkce/haberler/2015/06/150615_telabyad_kentin_cogu)
        # TODO: there are also f4m and m3u8 streams incorporated in playlist.sxml
        source_files = media_meta.get('sourceFiles')
        if source_files:
            return [{
                'url': f['url'],
                'format_id': format_id,
                'ext': f.get('encoding'),
                'tbr': float_or_none(f.get('bitrate'), 1000),
                'filesize': int_or_none(f.get('filesize')),
            } for format_id, f in list(source_files.items()) if f.get('url')], []

        programme_id = media_meta.get('externalId')
        if programme_id:
            return self._download_media_selector(programme_id)

        # Process playlist.sxml as legacy playlist
        href = media_meta.get('href')
        if href:
            playlist = self._download_legacy_playlist_url(href)
            _, _, _, _, formats, subtitles = self._extract_from_legacy_playlist(playlist, video_id)
            return formats, subtitles

        return [], []

    def _extract_from_playlist_sxml(self, url, playlist_id, timestamp):
        programme_id, title, description, duration, formats, subtitles = \
            self._process_legacy_playlist_url(url, playlist_id)
        self._sort_formats(formats)
        return {
            'id': programme_id,
            'title': title,
            'description': description,
            'duration': duration,
            'timestamp': timestamp,
            'formats': formats,
            'subtitles': subtitles,
        }

    def _real_extract(self, url):
        try:
            playlist_id = self._match_id(url)

            webpage = self._download_webpage(url, playlist_id)

            timestamp = None
            playlist_title = None
            playlist_description = None

            ld = self._parse_json(
                self._search_regex(
                    r'(?s)<script type="application/ld\+json">(.+?)</script>',
                    webpage, 'ld json', default='{}'),
                playlist_id, fatal=False)
            if ld:
                timestamp = parse_iso8601(ld.get('datePublished'))
                playlist_title = ld.get('headline')
                playlist_description = ld.get('articleBody')

            if not timestamp:
                timestamp = parse_iso8601(self._search_regex(
                    [r'<meta[^>]+property="article:published_time"[^>]+content="([^"]+)"',
                     r'itemprop="datePublished"[^>]+datetime="([^"]+)"',
                     r'"datePublished":\s*"([^"]+)'],
                    webpage, 'date', default=None))

            entries = []

            # article with multiple videos embedded with playlist.sxml (e.g.
            # http://www.bbc.com/sport/0/football/34475836)
            playlists = re.findall(r'<param[^>]+name="playlist"[^>]+value="([^"]+)"', webpage)
            if playlists:
                entries = [
                    self._extract_from_playlist_sxml(playlists[0], playlist_id, timestamp)]
                    #for playlist_url in playlists]

            # news article with multiple videos embedded with data-playable
            data_playables = re.findall(r'data-playable=(["\'])({.+?})\1', webpage)
            if data_playables:
                for _, data_playable_json in data_playables:
                    data_playable = self._parse_json(
                        unescapeHTML(data_playable_json), playlist_id, fatal=False)
                    if not data_playable:
                        continue
                    settings = data_playable.get('settings', {})
                    if settings:
                        # data-playable with video vpid in settings.playlistObject.items (e.g.
                        # http://www.bbc.com/news/world-us-canada-34473351)
                        playlist_object = settings.get('playlistObject', {})
                        if playlist_object:
                            items = playlist_object.get('items')
                            if items and isinstance(items, list):
                                title = playlist_object['title']
                                description = playlist_object.get('summary')
                                duration = int_or_none(items[0].get('duration'))
                                programme_id = items[0].get('vpid')
                                formats, subtitles = self._download_media_selector(programme_id)
                                self._sort_formats(formats)
                                entries.append({
                                    'id': programme_id,
                                    'title': title,
                                    'description': description,
                                    'timestamp': timestamp,
                                    'duration': duration,
                                    'formats': formats,
                                    'subtitles': subtitles,
                                })
                        else:
                            # data-playable without vpid but with a playlist.sxml URLs
                            # in otherSettings.playlist (e.g.
                            # http://www.bbc.com/turkce/multimedya/2015/10/151010_vid_ankara_patlama_ani)
                            playlist = data_playable.get('otherSettings', {}).get('playlist', {})
                            if playlist:
                                entries.append(self._extract_from_playlist_sxml(
                                    playlist.get('progressiveDownloadUrl'), playlist_id, timestamp))

            if entries:
                playlist_title = playlist_title or remove_end(self._og_search_title(webpage), ' - BBC News')
                playlist_description = playlist_description or self._og_search_description(webpage, default=None)
                return self.playlist_result(entries, playlist_id, playlist_title, playlist_description)

            # single video story (e.g. http://www.bbc.com/travel/story/20150625-sri-lankas-spicy-secret)
            programme_id = self._search_regex(
                [r'data-video-player-vpid="([\da-z]{8})"',
                 r'<param[^>]+name="externalIdentifier"[^>]+value="([\da-z]{8})"',
                 r'"vpid"\s*:\s*"([\da-z]{8})"'],
                webpage, 'vpid', default=None)

            if programme_id:
                formats, subtitles = self._download_media_selector(programme_id)
                self._sort_formats(formats)
                # digitalData may be missing (e.g. http://www.bbc.com/autos/story/20130513-hyundais-rock-star)
                digital_data = self._parse_json(
                    self._search_regex(
                        r'var\s+digitalData\s*=\s*({.+?});?\n', webpage, 'digital data', default='{}'),
                    programme_id, fatal=False)
                page_info = digital_data.get('page', {}).get('pageInfo', {})
                title = page_info.get('pageName') or self._og_search_title(webpage)
                description = page_info.get('description') or self._og_search_description(webpage)
                timestamp = parse_iso8601(page_info.get('publicationDate')) or timestamp
                return {
                    'id': programme_id,
                    'title': title,
                    'description': description,
                    'timestamp': timestamp,
                    'formats': formats,
                    'subtitles': subtitles,
                }

            playlist_title = self._html_search_regex(
                r'<title>(.*?)(?:\s*-\s*BBC [^ ]+)?</title>', webpage, 'playlist title')
            playlist_description = self._og_search_description(webpage, default=None)

            def extract_all(pattern):
                return list([_f for _f in [self._parse_json(s, playlist_id, fatal=False) for s in re.findall(pattern, webpage)] if _f])

            # Multiple video article (e.g.
            # http://www.bbc.co.uk/blogs/adamcurtis/entries/3662a707-0af9-3149-963f-47bea720b460)
            EMBED_URL = r'https?://(?:www\.)?bbc\.co\.uk/(?:[^/]+/)+[\da-z]{8}(?:\b[^"]+)?'
            entries = []
            for match in extract_all(r'new\s+SMP\(({.+?})\)'):
                embed_url = match.get('playerSettings', {}).get('externalEmbedUrl')
                if embed_url and re.match(EMBED_URL, embed_url):
                    entries.append(embed_url)
            entries.extend(re.findall(
                r'setPlaylist\("(%s)"\)' % EMBED_URL, webpage))
            if entries:
                return self.playlist_result(
                    [self.url_result(entry, 'BBCCoUk') for entry in entries],
                    playlist_id, playlist_title, playlist_description)

            # Multiple video article (e.g. http://www.bbc.com/news/world-europe-32668511)
            medias = extract_all(r"data-media-meta='({[^']+})'")

            if not medias:
                # Single video article (e.g. http://www.bbc.com/news/video_and_audio/international)
                media_asset = self._search_regex(
                    r'mediaAssetPage\.init\(\s*({.+?}), "/',
                    webpage, 'media asset', default=None)
                if media_asset:
                    media_asset_page = self._parse_json(media_asset, playlist_id, fatal=False)
                    medias = []
                    for video in list(media_asset_page.get('videos', {}).values()):
                        medias.extend(list(video.values()))

            if not medias:
                # Multiple video playlist with single `now playing` entry (e.g.
                # http://www.bbc.com/news/video_and_audio/must_see/33767813)
                vxp_playlist = self._parse_json(
                    self._search_regex(
                        r'<script[^>]+class="vxp-playlist-data"[^>]+type="application/json"[^>]*>([^<]+)</script>',
                        webpage, 'playlist data'),
                    playlist_id)
                playlist_medias = []
                for item in vxp_playlist:
                    media = item.get('media')
                    if not media:
                        continue
                    playlist_medias.append(media)
                    # Download single video if found media with asset id matching the video id from URL
                    if item.get('advert', {}).get('assetId') == playlist_id:
                        medias = [media]
                        break
                # Fallback to the whole playlist
                if not medias:
                    medias = playlist_medias

            entries = []
            for num, media_meta in enumerate(medias, start=1):
                formats, subtitles = self._extract_from_media_meta(media_meta, playlist_id)
                if not formats:
                    continue
                self._sort_formats(formats)

                video_id = media_meta.get('externalId')
                if not video_id:
                    video_id = playlist_id if len(medias) == 1 else '%s-%s' % (playlist_id, num)

                title = media_meta.get('caption')
                if not title:
                    title = playlist_title if len(medias) == 1 else '%s - Video %s' % (playlist_title, num)

                duration = int_or_none(media_meta.get('durationInSeconds')) or parse_duration(media_meta.get('duration'))

                images = []
                for image in list(media_meta.get('images', {}).values()):
                    images.extend(list(image.values()))
                if 'image' in media_meta:
                    images.append(media_meta['image'])

                thumbnails = [{
                    'url': image.get('href'),
                    'width': int_or_none(image.get('width')),
                    'height': int_or_none(image.get('height')),
                } for image in images]

                entries.append({
                    'id': video_id,
                    'title': title,
                    'thumbnails': thumbnails,
                    'duration': duration,
                    'timestamp': timestamp,
                    'formats': formats,
                    'subtitles': subtitles,
                })

            return self.playlist_result(entries, playlist_id, playlist_title, playlist_description)
        except:
            result = self._try_newVersion_extract(webpage)
            if result:
                return result
            if OldBBCIE.suitable(url):
                old = OldBBCIE()
                old.set_downloader(self._downloader)
                try:
                    result= old._real_extract(url)
                    return result
                except:
                    pass

    def _try_newVersion_extract(self, webpage):
            programme_id = self._search_regex(
                [r'&quot;vpid&quot;:&quot;(.+?)&quot;,'],
                webpage, 'vpid', default=None)
            if programme_id:
                formats, subtitles = self._download_media_selector(programme_id)
                self._sort_formats(formats)
                # digitalData may be missing (e.g. http://www.bbc.com/autos/story/20130513-hyundais-rock-star)
                title = self._og_search_title(webpage)
                thumbnail = self._og_search_thumbnail(webpage)

                return {
                    'id': programme_id,
                    'title': title,
                    'thumbnail': thumbnail,
                    'formats': formats,
                    'subtitles': subtitles,
                }
            else:
                playlist_id = self._search_regex(
                    [r'<div class="video" data-pid="([^"]+)'],
                    webpage, 'vpid', default=None)
                programme_id, title, description, duration, formats, subtitles = self._download_playlist(playlist_id)

                self._sort_formats(formats)
                return {
                    'id': programme_id,
                    'title': title,
                    'description': description,
                    'thumbnail': self._og_search_thumbnail(webpage, default=None),
                    'duration': duration,
                    'formats': formats,
                    'subtitles': subtitles,
                }

class BBCCoUkArticleIE(InfoExtractor):
    _VALID_URL = 'http://www.bbc.co.uk/programmes/articles/(?P<id>[a-zA-Z0-9]+)'
    IE_NAME = 'bbc.co.uk:article'
    IE_DESC = 'BBC articles'

    _TEST = {
        'url': 'http://www.bbc.co.uk/programmes/articles/3jNQLTMrPlYGTBn0WV6M2MS/not-your-typical-role-model-ada-lovelace-the-19th-century-programmer',
        'info_dict': {
            'id': '3jNQLTMrPlYGTBn0WV6M2MS',
            'title': 'Calculating Ada: The Countess of Computing - Not your typical role model: Ada Lovelace the 19th century programmer - BBC Four',
            'description': 'Hannah Fry reveals some of her surprising discoveries about Ada Lovelace during filming.',
        },
        'playlist_count': 4,
        'add_ie': ['BBCCoUk'],
    }

    def _real_extract(self, url):
        if OldBBCCoUkArticleIE.suitable(url):
            old = OldBBCCoUkArticleIE()
            old.set_downloader(self._downloader)
            try:
                result= old._real_extract(url)
                return result
            except:
                pass

        playlist_id = self._match_id(url)

        webpage = self._download_webpage(url, playlist_id)

        title = self._og_search_title(webpage)
        description = self._og_search_description(webpage).strip()

        entries = [self.url_result(programme_url) for programme_url in re.findall(
            r'<div[^>]+typeof="Clip"[^>]+resource="([^"]+)"', webpage)]

        return self.playlist_result(entries, playlist_id, title, description)
