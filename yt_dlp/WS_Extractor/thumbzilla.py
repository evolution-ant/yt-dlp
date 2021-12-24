

import re
import json

from ..extractor.common import InfoExtractor
from ..utils import (
    js_to_json
)


class thumbzillaIE(InfoExtractor):
    #http://www.txxx.com/videos/2631606/stepmom-seduces-teen-babe/
    _VALID_URL = r'https?://(?:www\.)?thumbzilla\.com'

    def _real_extract(self, url):
        webpage = self._download_webpage(url, url)

        title = self._og_search_title(webpage, default=None) or self._html_search_regex(
            r'(?s)<title>(.*?)</title>', webpage, 'video title',
            default='video')

        list = re.findall(r'data-quality="(.+)">(.+)P', webpage)

        formats = [{'url': item[0], 'height': item[1], 'ext': 'mp4'} for item in list]

        thumbnail = self._search_regex(r'<img class="mainImage playVideo removeWhenPlaying" width="100%" height="100%" src="([^"]+)', webpage, 'thumbail', fatal=False) or \
                    self._og_search_thumbnail(webpage) or self._html_search_meta('thumbnailUrl', webpage)
        return  ({
                'id': '',
                'title': title,
                'thumbnail': thumbnail,
                'formats': formats,
            })

