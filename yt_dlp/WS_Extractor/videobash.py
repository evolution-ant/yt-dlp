
import re

from ..extractor.common import (
    InfoExtractor,
)

from ..compat import compat_urllib_parse_unquote

class VideoBashIE(InfoExtractor):
    IE_NAME = 'VideoBash'

    _VALID_URL = r'https?://(?:www\.)?videobash\.com'

    def _real_extract(self, url):
        html = self._download_webpage(url, url)
        mobj = re.search(r'&amp;file="\s+\+\s+\'(.+)\'\s+\+\s+\'([^\']+)?', html)
        if mobj:
            url = compat_urllib_parse_unquote(mobj.group(1) + mobj.group(2))
            title = self._html_search_meta('og:title', html)
            thumbail = self._html_search_meta('og:image', html)

            return {
                'id': 'xxx',
                'title': title,
                'formats': [{'url': url}],
                'thumbnail': thumbail,
            }


        else:
            raise 'not support'
