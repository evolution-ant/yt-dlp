
from ..extractor.dropbox import (
    DropboxIE,
)

class DropboxExIE(DropboxIE):
    def _real_extract(self, url):
        webpage = self._download_webpage(url, url, '')
        if self._search_regex(r'<div class="error-type">404</div>', webpage, '', fatal=False):
            raise Exception('404')

        return super(DropboxExIE, self)._real_extract(url)

