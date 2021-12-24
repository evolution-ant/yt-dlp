

import re
import json

from ..extractor.common import InfoExtractor
from ..utils import (
    js_to_json
)


class porneqIE(InfoExtractor):
    #http://www.txxx.com/videos/2631606/stepmom-seduces-teen-babe/
    _VALID_URL = r'https?://(?:www\.)?porneq\.com'

    def _real_extract(self, url):
        webpage = self._download_webpage(url, url)

        jw_config = self._parse_json(
            self._search_regex(
                r'(?s)jwplayer\(([\'"])(?:(?!\1).)+\1\)\.setup\s*\((?P<options>.+?)\);',
                webpage, 'jw config', group='options'),
            '', transform_source=js_to_json)
        info = self._parse_jwplayer_data(
            jw_config, '123', require_title=False, m3u8_id='hls',
            base_url=url)

        title = self._og_search_title(webpage, default=None) or self._html_search_regex(
            r'(?s)<title>(.*?)</title>', webpage, 'video title',
            default='video')

        info.update({
            'title': title,
            'thumbnail': self._og_search_thumbnail(webpage),
        })
        return info

