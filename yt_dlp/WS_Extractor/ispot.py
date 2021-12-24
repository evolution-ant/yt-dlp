

from ..extractor.common import InfoExtractor

class IspotIE(InfoExtractor):
    _VALID_URL = r'https?://(?:www\.)?www.ispot.tv'

    _TEST = {
        'url': 'https://www.ispot.tv/ad/ARfj/nike-unlimited-you-featuring-serena-williams-kevin-durant',
    }

    def _real_extract(self, url):
        webpage = self._download_webpage(url, url)
        video_id = self._search_regex('var\s+video_id="([^\"]+)', webpage, 'video_id', default='1')
        title = self._search_regex('<meta property="og:title" content="([^\"]+)', webpage, 'video title', default='video')
        if title == 'video':
            title =  self._search_regex(r'(?s)<title>(.*?)</title>', webpage, 'video title', default='video')
        duration = self._search_regex(r'<meta itemprop="duration" content="([^\"]+)', webpage, 'duration', default=None)
        thumbnail = self._search_regex(r'<meta itemprop="thumbnailUrl" content="([^\"]+)', webpage, 'thumbail', default=None)
        video_mp4_url = self._search_regex('data-mp4="([^\"]+)',webpage, 'video_mp4_url', default=None)
        video_webm_url = self._search_regex('data-webm="([^\"]+)',webpage, 'video_mp4_url', default=None)
        formats = []
        formats.append({
            'url': video_mp4_url,
            'width': 360,
            'ext': 'mp4',
        })

        formats.append({
            'url': video_webm_url,
            'width': 360,
            'ext': 'webM',
        })

        return {
            '_type': 'video',
            'id': video_id,
            'title':title,
            'thumbnail': thumbnail,
            'duration': duration,
            'formats': formats,
        }
