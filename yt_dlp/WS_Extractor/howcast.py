from ..extractor.howcast import HowcastIE as HowcastIEBase
from ..utils import parse_iso8601
from ..utilsEX import decode_html

class HowcastIE(HowcastIEBase):

    def _real_extract(self, url):
        video_id = self._match_id(url)
        webpage = self._download_webpage(url, video_id)

        try:
            embed_code = self._search_regex(
                r'<iframe[^>]+src="[^"]+\bembed_code=([^\b]+)\b',
                webpage, 'ooyala embed code')

            return {
                '_type': 'url_transparent',
                'ie_key': 'Ooyala',
                'url': 'ooyala:%s' % embed_code,
                'id': video_id,
                'timestamp': parse_iso8601(self._html_search_meta(
                    'article:published_time', webpage, 'timestamp')),
            }
        except Exception as ex:
            _url = self._search_regex(
                r'<iframe[^>]+src="([^"]+)"',
                webpage, 'youtube embed code')

            if 'youtube' in _url.lower():
                _url = decode_html(_url)
                return {
                    '_type': 'url',
                    'ie_key': 'Youtube',
                    'url': _url,
                }
            else:
                raise ex