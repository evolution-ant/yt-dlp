

import re
import json

from ..extractor.common import InfoExtractor
from ..utils import (
    int_or_none,
    ExtractorError,
    sanitized_Request,
    UnsupportedError,
    urlencode_postdata
)
from ..compat import compat_urlparse

class ancensoredIE(InfoExtractor):
    #http://www.txxx.com/videos/2631606/stepmom-seduces-teen-babe/
    _VALID_URL = r'https?://(?:www\.)?ancensored\.com'

    def _real_extract(self, url):
        webpage = self._download_webpage(url, url)

        title = self._og_search_title(webpage, default=None) or self._html_search_regex(
            r'(?s)<title>(.*?)</title>', webpage, 'video title',
            default='video')

        thumbnail = self._search_regex(r'background-image: url\((.+)', webpage, 'background', fatal=False)
        if thumbnail:
            thumbnail = compat_urlparse.urljoin(url, thumbnail)
        else:
            thumbnail = self._og_search_thumbnail(webpage) or self._html_search_meta('thumbnailUrl', webpage)
        csrf = self._search_regex(r'<meta name="csrf-token"\s*content="([^"]+)', webpage, 'csrf')
        hash = self._search_regex('{hash:\s*\'([^\']+)', webpage, 'hash')
        queryUrl = 'http://ancensored.com/video/get-link'
        request = sanitized_Request(
            queryUrl, urlencode_postdata({'hash': hash}))

        webpage = self._download_webpage(request, None, '', headers={'X-Requested-With': 'XMLHttpRequest', 'X-CSRF-Token': csrf, 'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'})
        video_url = self._search_regex(r'"src":"([^"]+)', webpage, 'src')

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


