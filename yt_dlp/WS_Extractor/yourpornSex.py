

import re

from ..extractor.common import InfoExtractor
from ..utils import (
    determine_ext
)

class YourpornSexIE(InfoExtractor):
    # http://www.txxx.com/videos/2631606/stepmom-seduces-teen-babe/
    _VALID_URL = r'https?://(?:www\.)?yourporn\.sexy'

    def _real_extract(self, url):
        webpage = self._download_webpage(url, url)

        title = self._og_search_title(webpage, default=None) or self._html_search_regex(
            r'(?s)<title>(.*?)</title>', webpage, 'video title',
            default='video')

        video_url = self._search_regex('video\s*id=\'player_el\'\s*src=\'//([^\']+)', webpage, 'src', fatal=False)
        if not video_url:
            if webpage.find('<div id=\'videos_container\'>') > -1:
                ids = re.findall(r'<div class="pl_vid_el transition" data-source="blog" data-hash="([^"]+)', webpage)
                if ids:
                    entries = [self.url_result('https://yourporn.sexy/post/%s.html' % id, ie=yourpornSexIE.ie_key()) for
                               id in ids]
                    return {
                        '_type': 'playlist',
                        'id': 'x',
                        'title': '',
                        'entries': entries,
                    }
        if not 'http' in video_url:
            video_url = 'http://' + video_url
        thumbnail = self._og_search_thumbnail(webpage) or self._html_search_meta('thumbnailUrl', webpage)
        formats = [{
            'url': video_url,
            'ext': determine_ext(video_url),
        }]
        return ({
            'id': '',
            'title': title,
            'thumbnail': thumbnail,
            'formats': formats,
            'http_headers': {
                'Referer': url,
                'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36'
            }
        })