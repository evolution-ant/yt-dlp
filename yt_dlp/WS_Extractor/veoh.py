

import re
import json

from ..extractor.common import InfoExtractor
from ..utils import (
    int_or_none,
    ExtractorError,
    sanitized_Request,
    UnsupportedError
)

from ..extractor.veoh import VeohIE as OldIE


class VeohIE(InfoExtractor):
    _VALID_URL = r'https?://(?:www\.)?veoh\.com/(?:watch|iphone/#_Watch)/(?P<id>(?:v|yapi-)[\da-zA-Z]+)'

    def _real_extract(self, url):

        if OldIE.suitable(url):
            old = OldIE()
            old.set_downloader(self._downloader)
            try:
                result = old._real_extract(url)
                if result:
                    real_url = result['formats'][0]['url']
                    if real_url.find('anyclip')!=-1:
                        raise UnsupportedError(real_url)
                    return result
            except UnsupportedError as e:
                raise e
            else:
                pass
