

import re
import json

from ..extractor.common import InfoExtractor
from ..utils import (
    js_to_json
)


class hqcollectTVIE(InfoExtractor):
    #http://www.txxx.com/videos/2631606/stepmom-seduces-teen-babe/
    _VALID_URL = r'https?://(?:www\.)?hqcollect\.tv'

    def _real_extract(self, url):
        webpage = self._download_webpage(url, url)
        title = self._og_search_title(webpage, default=None) or self._html_search_regex(
            r'(?s)<title>(.*?)</title>', webpage, 'video title',
            default='video')
        video_url = self._search_regex('<source src="(.+)" type="video/mp4"', webpage, 'src')
        thumbnail = self._search_regex(r'<video class="u-full-width" controls poster="([^"])', webpage, 'thumbail', fatal=False) or \
                    self._og_search_thumbnail(webpage) or self._html_search_meta('thumbnailUrl', webpage)
        formats = [{
                       'url': video_url,
                        'ext': 'mp4',
        }]
        return  ({
                'id': '',
                'title': title,
                'thumbnail': thumbnail,
                'formats': formats,
            })

