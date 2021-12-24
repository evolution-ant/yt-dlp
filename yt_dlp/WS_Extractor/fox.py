#encoding: utf-8


import re
import json

from ..extractor.fox import FOXIE as Old
from ..utilsEX import download_webPage_by_PYCURL

class FoxIE(Old):
    def _download_webpage(self, url_or_request, video_id, note=None, errnote=None, fatal=True, tries=1, timeout=5, encoding=None, data=None, headers={}, query={}):
        try:
            return super(FoxIE, self)._download_webpage(url_or_request, video_id, note, errnote, fatal, tries, timeout, encoding, data, headers, query)
        except:
            return download_webPage_by_PYCURL(self, url_or_request, timeout, data, headers, query)