# coding: utf-8


import re
from ..extractor.discovery import DiscoveryIE as Old

class DiscoveryIE(Old):

    def _real_extract(self, url):
        try:
            result = super(DiscoveryIE, self)._real_extract(url)
            if not result or not result.get('formats', None):
                raise
            return result
        except:
            display_id = self._match_id(url)
            webpage = self._download_webpage(url, display_id)
            mobj = re.search(
                        r'window\.__reactTransmitPacket = (.*);</script>',
                        webpage)
            if mobj:
                json_string = mobj.group(1)
            mobj = re.search(
                        r'<title>(.*)</title>',
                        webpage)
            title = mobj.group(1)
            json = self._parse_json(
                        json_string, display_id, transform_source=None, fatal=True)
            id = json.get('videoPlayer').get('players').get('eos-videos-short-form-layout-video-4').get('video').get('id')
            duration = json.get('videoPlayer').get('players').get('eos-videos-short-form-layout-video-4').get('video').get('duration')
            link = 'http://api.discovery.com/v1/streaming/video/' + id + '?platform=desktop'
            loginlink = 'https://www.discovery.com/anonymous?authLink=https%3A%2F%2Flogin.discovery.com%2Fv1%2Foauth2%2Fauthorize%3Fclient_id%3D3020a40c2356a645b4b4%26redirect_uri%3Dhttps%253A%252F%252Ffusion.ddmcdn.com%252Fapp%252Fmercury-sdk%252F180%252FredirectHandler.html%253Fhttps%253A%252F%252Fwww.discovery.com%26response_type%3Danonymous%26state%3DeyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJub25jZSI6IkhEYUs3Y2owM0ZKM3BDaWtLR1U4SVpDZHV6dzllUFlKIn0.RVwDsGm4kh-M6tesveDLtynVOmGJ1FKZ6q3fssp_OoQ%26networks.code%3DDSC&client_id=3020a40c2356a645b4b4&state=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJub25jZSI6IkhEYUs3Y2owM0ZKM3BDaWtLR1U4SVpDZHV6dzllUFlKIn0.RVwDsGm4kh-M6tesveDLtynVOmGJ1FKZ6q3fssp_OoQ'
            info = self._download_json(loginlink, 'discovery')
            access_token = info.get('access_token')
            token_type = info.get('token_type')
            if token_type:
                authorization = token_type + ' ' + access_token
            else:
                authorization = access_token
            res = self._download_json(link, display_id,
                           'Downloading JSON metadata',
                           'Unable to download JSON metadata',
                           None, True, None, None, {"authorization":authorization}, {})
            streamUrl = res.get('streamUrl')
            captions = res.get('captions')
            formats = self._extract_m3u8_formats(
                streamUrl,
                'discovery', ext='mp4', m3u8_id='hls', fatal=False)
            self._sort_formats(formats)
            return {
                'id': id,
                'title': title,
                'timestamp': duration,
                'captions': captions,
                'formats': formats,
            }
