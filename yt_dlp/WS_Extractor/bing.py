#encoding: utf-8



import json
from ..extractor.common import InfoExtractor

class BingIE(InfoExtractor):
    # https://www.bing.com/videos/search?q=youtube+supermarket+flowers&ru=%2fsearch%3fq%3dyoutube%2bsupermarket%2bflowers%26FORM%3dQSRE3&view=detail&mid=616B8E40E9346549CDBB616B8E40E9346549CDBB&&mmscn=vwrc&FORM=VDRVRV
    _VALID_URL = r'https?://(?:www\.)?bing\.com/videos/search\?q=(?P<real_url>[^/?#]+)'

    def _real_extract(self, url):
        try:
            webpage = self._download_webpage(url, url)
            pattern = r'VDMetadata=([^;]*)'
            js_str = self._search_regex(pattern, webpage, 'js_str')
            if not js_str:
                return super(BingIE, self)._real_extract(url)

            media_info = json.loads(js_str)
            if media_info and 'mediaUrl' in media_info:
                return self.url_result(media_info['mediaUrl'])

            return super(BingIE, self)._real_extract(url)
        except:
            return super(BingIE, self)._real_extract(url)