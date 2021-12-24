#encoding: utf-8


import os
import json

from ..extractor.common import InfoExtractor
from ..extractor.googledrive import GoogleDriveIE as Old
from ..compat import compat_urlparse

# class GoogleDriverIE(InfoExtractor):
#     # https://www.bing.com/videos/search?q=youtube+supermarket+flowers&ru=%2fsearch%3fq%3dyoutube%2bsupermarket%2bflowers%26FORM%3dQSRE3&view=detail&mid=616B8E40E9346549CDBB616B8E40E9346549CDBB&&mmscn=vwrc&FORM=VDRVRV
#     _VALID_URL = r'https?://drive.google.com/(?:file/|open\?)'
#
#     def _real_extract(self, url):
#         self._downloader.cookiejar.clear()
#         webpage = self._download_webpage(url, url)
#
#         self._search_regex(r'(<meta property="og:video"|audio_favicon\.ico)', webpage, '')
#
#         title = self._search_regex(r'<meta itemprop="name"\s+content="([^"]+)', webpage, '', fatal=False)
#         # info = self._search_regex(r'_initProjector\([\s\S]+,\[null,"(.+)\[\[\["status","ok"\]', webpage, '')
#         ext = os.path.splitext(title)[-1]
#         id = self._search_regex(r'\["docid","(.+)?"\]', webpage, '', fatal=False) or self._search_regex(r'\'id\':\s+\'([^\']+)', webpage, '')
#         video_url = 'https://drive.google.com/uc?id=%s&export=download' % id
#         thumbnail = self._search_regex(r'meta property="og:image"\s+content="([^"]+)', webpage, '', fatal=False)
#
#         formats = [{
#                        'url': video_url,
#                         'ext': ext.strip('.'),
#         }]
#
#         return {
#             'id': id,
#             'title': title,
#             'formats': formats,
#             'thumbnail': thumbnail,
#         }
from ..utils import std_headers

class GoogleDriverIE(Old):
    def _real_extract(self, url):
        result = super(GoogleDriverIE, self)._real_extract(url)
        result['formats'] = [format for format in result['formats'] if format['url'].find('export=download')>-1]
        std_headers.pop('Accept-Encoding')
        self._downloader.cookiejar.clear()
        return result