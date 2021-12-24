#encoding: utf-8

from ..extractor.common import InfoExtractor
from urllib.parse import *

class XpauIE(InfoExtractor):
    # http://xpau.se/watch/prison-break/s5/e1
    _VALID_URL = r'(?:https?://)?(?:www\.)?xpau\.se/'

    def _real_extract(self, url):
        # 求第一级iframe
        webpage = self._download_webpage(url, 'video_id')
        frmae_url = self._search_regex(r'<iframe id="\w+" src="(.[^\"]+)"', webpage, 'url1')
        if not frmae_url:
            return super(XpauIE, self)._real_extract(url)

        parts = urlparse(url)
        frmae_url = '%s://%s%s' % (parts.scheme, parts.netloc, frmae_url)
        webpage = self._download_webpage(frmae_url, 'video_id')
        frmae_url = self._search_regex(r'<iframe\s?(?:id="\w+")? src="(.[^\"]+)"', webpage, 'url2')
        if not frmae_url:
            return super(XpauIE, self)._real_extract(url)

        frmae_url = '%s://%s%s' % (parts.scheme, parts.netloc, frmae_url)
        webpage = self._download_webpage(frmae_url, 'video_id')

        video_url = self._search_regex(r'<iframe src="(.[^\"]+)"', webpage, 'video_url')
        if not video_url or not 'google' in video_url:
            return super(XpauIE, self)._real_extract(url)

        return self.url_result(video_url, 'GoogleDrive')