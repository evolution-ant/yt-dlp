# coding: utf-8


from ..compat import (
    compat_cookies,
)

from ..utils import (
    sanitized_Request,
)

from ..extractor.viki import (
    VikiIE as OldVikeIE,
    VikiChannelIE as OldVikiChannelIE,
)

class VikiIE(OldVikeIE):
    def _real_extract(self, url):
        webpage = self._download_webpage(url, url)
        self._token = self._search_regex(r'session\.user_token\s*=\s*"([^"]+)', webpage, 'token', fatal=False)
        return super(VikiIE, self)._real_extract(url)


class VikiChannelIE(OldVikiChannelIE):
    def _real_extract(self, url):
        webpage = self._download_webpage(url, url)
        self._token = self._search_regex(r'session\.user_token\s*=\s*"([^"]+)', webpage, 'token', fatal=False)
        return super(VikiChannelIE, self)._real_extract(url)