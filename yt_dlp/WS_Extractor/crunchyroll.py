# encoding: utf-8


import re
import json
import base64
import zlib
import xml.etree.ElementTree

from hashlib import sha1
from math import pow, sqrt, floor
from ..extractor.common import InfoExtractor
from ..extractor.crunchyroll import CrunchyrollIE as OldCrunchyrollIE
from ..compat import (
    compat_urllib_parse,
    compat_urllib_request,
)
from ..utils import (
    ExtractorError,
    bytes_to_intlist,
    intlist_to_bytes,
    unified_strdate,
    urlencode_postdata,
)
from ..aes import (
    aes_cbc_decrypt,
    inc,
)


class CrunchyrollIE(OldCrunchyrollIE):
    _VALID_URL = r'https?://(?:(?P<prefix>www|m)\.)?(?P<url>crunchyroll\.(?:com|fr)/(?:[^/]*/[^/?&]*?|media/\?id=)(?P<video_id>[0-9]+))(?:[/?&]|$)'
    _NETRC_MACHINE = 'crunchyroll'


    def extract_subtitles(self, *args, **kwargs):
        keysTranslate = {
            'deDE': 'de',
            'enUS': 'en',
            'enGB': 'en',
            'esLA': 'es',
            'esES': 'es',
            'frFR': 'fr',
            'itIT': 'it',
            'ptBR': 'pt',
            #'': 'ja',
            #'': 'hl',
            }
        result =  self._get_subtitles(*args, **kwargs)
        #return result
        if result:
            subtitles = {keysTranslate.get(key, key): [item] for key, items in list(result.items()) for item in items if item['ext'].lower() == 'srt'}
            if len(subtitles) > 0:
                subtitles['default'] = list(subtitles.values())[0]
            return subtitles

    def _real_extract(self, url):
        try:
            result= super(CrunchyrollIE, self)._real_extract(url)
            return result
        except:
            pass
        mobj = re.match(self._VALID_URL, url)
        video_id = mobj.group('video_id')

        if mobj.group('prefix') == 'm':
            mobile_webpage = self._download_webpage(url, video_id, 'Downloading mobile webpage')
            webpage_url = self._search_regex(r'<link rel="canonical" href="([^"]+)" />', mobile_webpage, 'webpage_url')
        else:
            webpage_url = 'http://www.' + mobj.group('url')

        webpage = self._download_webpage(webpage_url, video_id, 'Downloading webpage')
        note_m = self._html_search_regex(r'<div class="showmedia-trailer-notice">(.+?)</div>', webpage, 'trailer-notice', default='')
        if note_m:
            raise ExtractorError(note_m)

        mobj = re.search(r'Page\.messaging_box_controller\.addItems\(\[(?P<msg>{.+?})\]\)', webpage)
        if mobj:
            msg = json.loads(mobj.group('msg'))
            if msg.get('type') == 'error':
                raise ExtractorError('crunchyroll returned error: %s' % msg['message_body'], expected=True)

        video_title = self._html_search_regex(r'<meta name="description" content="([^\"]+)', webpage, 'video_title', flags=re.DOTALL)
        #video_title = re.sub(r' {2,}', ' ', video_title)
        video_description = self._html_search_regex(r'"description":"([^"]+)', webpage, 'video_description', default='')
        if not video_description:
            video_description = None
        video_upload_date = self._html_search_regex(r'<div>Availability for free users:(.+?)</div>', webpage, 'video_upload_date', fatal=False, flags=re.DOTALL)
        if video_upload_date:
            video_upload_date = unified_strdate(video_upload_date)
        video_uploader = self._html_search_regex(r'<div>\s*Publisher:(.+?)</div>', webpage, 'video_uploader', fatal=False, flags=re.DOTALL)

        playerdata_url = compat_urllib_parse.unquote(self._html_search_regex(r'"config_url":"([^"]+)', webpage, 'playerdata_url'))
        playerdata_req = compat_urllib_request.Request(playerdata_url)
        playerdata_req.data = compat_urllib_parse.urlencode({'current_page': webpage_url})
        playerdata_req.add_header('Content-Type', 'application/x-www-form-urlencoded')
        playerdata = self._download_webpage(playerdata_req, video_id, note='Downloading media info')

        stream_id = self._search_regex(r'<media_id>([^<]+)', playerdata, 'stream_id')
        mainifest_Url = self._search_regex(r'<file>([^<]+)', playerdata, 'mainifest_url')
        video_thumbnail = self._search_regex(r'<episode_image_url>([^<]+)', playerdata, 'thumbnail', fatal=False)

        formats = []

        for fmt in re.findall(r'showmedia\.([0-9]{3,4})p', webpage):
            stream_quality, stream_format = self._FORMAT_IDS[fmt]
            video_format = fmt + 'p'
            req_url = '%s?%s' % ('http://www.crunchyroll.com/xml/',
                                'req=RpcApiVideoPlayer_GetStandardConfig&video%5Fencode%5Fquality=' + stream_quality + '&media%5Fid=' + stream_id + '&video%5Fformat=' + stream_format)
            streamdata_req = compat_urllib_request.Request(req_url, compat_urllib_parse.urlencode({'current_page': url}))
            streamdata_req.add_header('Content-Type', 'application/x-www-form-urlencoded')
            #streamdata_req.add_header('Content-Length', str(len(streamdata_req.data)))
            streamdata = self._download_xml(
                streamdata_req, video_id,
                note='Downloading media info for %s' % video_format)
            #video_url = streamdata.find('.//host').text
            video_play_path = streamdata.find('.//file').text
            formats.append({
                'url': video_play_path,
                'ext': 'mp4',
                'format': video_format,
                'format_id': video_format,
            })

        subtitles = self.extract_subtitles(video_id, webpage)
        self._sort_formats(formats)
        return {
            'id': video_id,
            'title': video_title,
            'description': video_description,
            'thumbnail': video_thumbnail,
            'uploader': video_uploader,
            'upload_date': video_upload_date,
            'subtitles': subtitles,
            'formats': formats,
        }


class CrunchyrollShowPlaylistIE(InfoExtractor):
    IE_NAME = "crunchyroll:playlist"
    _VALID_URL = r'https?://(?:(?P<prefix>www|m)\.)?(?P<url>crunchyroll\.com/(?!(?:news|anime-news|library|forum|launchcalendar|lineup|store|comics|freetrial|login))(?P<id>[\w\-]+))/?$'

    _TESTS = [{
        'url': 'http://www.crunchyroll.com/a-bridge-to-the-starry-skies-hoshizora-e-kakaru-hashi',
        'info_dict': {
            'id': 'a-bridge-to-the-starry-skies-hoshizora-e-kakaru-hashi',
            'title': 'A Bridge to the Starry Skies - Hoshizora e Kakaru Hashi'
        },
        'playlist_count': 13,
    }]

    def _real_extract(self, url):
        show_id = self._match_id(url)

        webpage = self._download_webpage(url, show_id)
        title = self._html_search_regex(
            r'(?s)<h1[^>]*>\s*<span itemprop="name">(.*?)</span>',
            webpage, 'title')
        episode_paths = re.findall(
            r'(?s)<li id="showview_videos_media_[0-9]+"[^>]+>.*?<a href="([^"]+)"',
            webpage)
        entries = [
            self.url_result('http://www.crunchyroll.com' + ep, 'Crunchyroll')
            for ep in episode_paths
        ]
        entries.reverse()

        return {
            '_type': 'playlist',
            'id': show_id,
            'title': title,
            'entries': entries,
        }
