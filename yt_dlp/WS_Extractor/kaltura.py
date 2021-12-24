#encoding: utf-8


import re
import json

from ..extractor.kaltura import KalturaIE as Old
from ..compat import compat_urlparse

class KalturaIE(Old):

    def _real_extract(self, url):
        result = super(KalturaIE, self)._real_extract(url)
        self._check_formats(result['formats'], '')
        self._sort_formats(result['formats'])
        return result
