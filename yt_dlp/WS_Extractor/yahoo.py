# coding: utf-8


import uuid
import re
import json
from ..extractor.common import InfoExtractor
from ..extractor.yahoo import YahooIE as OldYahooIE
from ..compat import (
    compat_urlparse,
    compat_urllib_parse_urlencode,
)
from ..utils import (
    int_or_none,
    ExtractorError,
    clean_html,
    unescapeHTML
)

class YahooIE(InfoExtractor):
    IE_DESC = 'Yahoo screen and movies'
    _VALID_URL = r'(?P<url>(?P<host>https?://(?:[a-zA-Z]{2}\.)?[\da-zA-Z_-]+\.yahoo\.com)/(?:[^/]+/)*(?P<display_id>.+)?-(?P<id>[0-9]+)(?:-[a-z]+)?(?:\.html)?)'

    def _real_extract(self, url):
        if OldYahooIE.suitable(url):
            old = OldYahooIE()
            old.set_downloader(self._downloader)
            try:
                result= old._real_extract(url)
                return result
            except:
                pass

        mobj = re.match(self._VALID_URL, url)
        display_id = mobj.group('display_id')
        page_id = mobj.group('id')
        url = mobj.group('url')
        host = mobj.group('host')
        webpage = self._download_webpage(url, display_id)

        externalUrl =  re.search(r'data-type\=\"videoIframe"\s*src="(.*?)"', webpage)
        if externalUrl:
            return self.url_result(externalUrl.group(1))

        # Look for iframed media first
        iframe_m = re.search(r'<iframe[^>]+src="(/video/.+?-\d+\.html\?format=embed.*?)"', webpage)

        if iframe_m:
            iframepage = self._download_webpage(
                host + iframe_m.group(1), display_id, 'Downloading iframe webpage')
            items_json = self._search_regex(
                r'mediaItems: (\[.+?\])$', iframepage, 'items', flags=re.MULTILINE, default=None)
            if items_json:
                items = json.loads(items_json)
                video_id = items[0]['id']
                return self._get_info(video_id, display_id, webpage)

        items_json = self._search_regex(
            r'mediaItems: ({.*?})$', webpage, 'items', flags=re.MULTILINE,
            default=None)
        if items_json is None:
            alias = self._search_regex(
                r'"aliases":{.*"video":"(.*?)"', webpage, 'alias', default=None)
            if alias is not None:
                alias_info = self._download_json(
                    'https://www.yahoo.com/_td/api/resource/VideoService.videos;video_aliases=["%s"]' % alias,
                    display_id, 'Downloading alias info')
                video_id = alias_info[0]['id']
            else:
                CONTENT_ID_REGEXES = [
                    r'YUI\.namespace\("Media"\)\.CONTENT_ID\s*=\s*"([^"]+)"',
                    r'root\.App\.Cache\.context\.videoCache\.curVideo = \{"([^"]+)"',
                    r'"first_videoid"\s*:\s*"([^"]+)"',
                    r'%s[^}]*"ccm_id"\s*:\s*"([^"]+)"' % re.escape(page_id),
                    r'<article[^>]data-uuid=["\']([^"\']+)',
                    r'yahoo://article/view\?.*\buuid=([^&"\']+)',
                ]
                video_id = self._search_regex(
                    CONTENT_ID_REGEXES, webpage, 'content ID')
        else:
            items = json.loads(items_json)
            info = items['mediaItems']['query']['results']['mediaObj'][0]
            # The 'meta' field is not always in the video webpage, we request it
            # from another page
            video_id = info['id']
        if video_id is None:
            try:
                html = self._download_webpage('https://video.yahoo.com/services/oembed/?site=ivy&region=US&lang=en-US&url=%s'% url, display_id)
                iframe_url = self._html_search_regex(r'src=\\"(.*?)\\"', html, '')
                iframepage = self._download_webpage(iframe_url, iframe_url)
            except:
                iframe_url = self._twitter_search_player(webpage)
                iframepage = self._download_webpage(iframe_url, iframe_url)
            items_json = self._search_regex(
                r'window.Af.bootstrap\[".*?"\]\s*=\s*(.*);', iframepage, 'items', flags=re.MULTILINE, default=None)
            if items_json:
                items = json.loads(items_json)
                try:
                    video_id = items['models']['applet_model']['data']['sapi']['query']['results']['mediaObj'][0]['id']
                except:
                    video_id = items['models']['applet_model']['data']['first_videoid']
        return self._get_info(video_id, display_id, webpage)

    def _get_info(self, video_id, display_id, webpage):
        region = self._search_regex(
            r'\\?"region\\?"\s*:\s*\\?"([^"]+?)\\?"',
            webpage, 'region', fatal=False, default='US')
        data = compat_urllib_parse_urlencode({
            'protocol': 'http',
            'region': region,
        })
        query_url = (
            'https://video.media.yql.yahoo.com/v1/video/sapi/streams/'
            '{id}?{data}'.format(id=video_id, data=data))
        query_result = self._download_json(
            query_url, display_id, 'Downloading video info')

        info = query_result['query']['results']['mediaObj'][0]
        meta = info.get('meta')

        if not meta:
            msg = info['status'].get('msg')
            if msg:
                raise ExtractorError(
                    '%s returned error: %s' % (self.IE_NAME, msg), expected=True)
            raise ExtractorError('Unable to extract media object meta')

        formats = []
        for s in info['streams']:
            format_info = {
                'width': int_or_none(s.get('width')),
                'height': int_or_none(s.get('height')),
                'tbr': int_or_none(s.get('bitrate')),
            }

            host = s['host']
            path = s['path']
            if host.startswith('rtmp'):
                format_info.update({
                    'url': host,
                    'play_path': path,
                    'ext': 'flv',
                })
            else:
                format_url = compat_urlparse.urljoin(host, path)
                format_info['url'] = format_url
            formats.append(format_info)

        self._sort_formats(formats)

        return {
            'id': video_id,
            'display_id': display_id,
            'title': unescapeHTML(meta['title']),
            'formats': formats,
            'description': clean_html(meta['description']),
            'thumbnail': meta['thumbnail'] if meta.get('thumbnail') else self._og_search_thumbnail(webpage),
            'duration': int_or_none(meta.get('duration')),
        }

    def cpp_(self, url):
        #C++
        vid = None
        webPage = self._download_webpage(url, url)
        content = self._search_regex(r'<head>(.+)</head>', webPage, 'extract head', default=None)
        if content:
            vid = self._search_regex(r'CONTENT_ID\s*=\s*\"([^"]+)"', content, 'vid', default=None )
        if not vid:
            vid = self._search_regex(r'"pstaid":"([^"]+)"', webPage, 'vid', default=None)
        #blog
        if not vid:
            link = self._search_regex(r'<p class="first">\s*<iframe[^>]+src="([^"]+)"', webPage, 'content', default=None)
            webPage2 = self._download_webpage(link, link)
            if content:
                vid = self._search_regex(r'"mediaItems[^]]+"id":"([^"]+)"', webPage2, 'content2', default=None)

        if not vid:
            vid = self._search_regex(r'Y\.Media\.InlineVideoPlayer\([^)]*[\'"]*videoId[\'"]*:\"([^\"]+)\"', webPage, 'vevo')
            link = 'http://www.vevo.com/video/%s' % vid

        if not vid:
            list =  [r'Y\.Media\.SingleVideoClip\(\[\{[^]]*"id":"([^"]+)"',
                     r'YAHOO\.Media\.CarouselDataManager\([^}]+"id":"id-([^\"]+)"',
                     r'YVIDEO_INIT_ITEMS[^}]+"id":"([^"]+)"']
            for item in list:
                vid = self._search_regex(item , webPage, 'vid', default=None)
                if vid:
                    break

        if vid:
            result = self.yql(vid)

        if result:
            return

    def yql(self, id):
        plrs = '%s' % uuid.uuid4()
        url = "https://video.query.yahoo.com/v1/public/yql?q="
        url += "SELECT%20*%20FROM%20yahoo.media.video.streams%20WHERE%20id%3D%22"
        url += id
        url += "%22%20AND%20format%3D%22mp4%2Cflv%2Cf4m%22%20AND%20protocol%3D%22rtmp%2Chttp%22%20AND%20rt%3D%22flash%22%20AND%20plrs%3D%22"
        url += plrs
        url += "%22%20AND%20acctid%3D%22762%22%20AND%20plidl%3D%22default%22%20AND%20pspid%3D%221197686338%22%20AND%20offnetwork%3D%22false%22%20AND%20site%3D%22anc%22%20AND%20lang%3D%22en-PH%22%20AND%20region%3D%22PH%22%20AND%20override%3D%22none%22%20AND%20plist%3D%22%22%20AND%20hlspre%3D%22false%22%20AND%20ssl%3D%22false%22%20AND%20synd%3D%22%22%3B&env=prod&format=json&callback=YUI.Env.JSONP.yui_3_9_1_1_1404803085999_740"
        webpage = self._download_webpage(url)