

from ..extractor.common import InfoExtractor
from ..utilsEX import (
    downloadWebPage_BYHeadlessBrowser,
)
from ..utils import (
    determine_ext
)


class CamwhoresIE(InfoExtractor):
    # http://www.camwhores.tv/videos/1826836/lunaxjames-fucking-my-asian-sex-doll-premium3/
    _VALID_URL = r'https?://(?:www\.)?camwhores\.(?:org|tv)/(?:videos|embed)/(?P<id>[^/]+)'

    def _real_extract(self, url):
        video_id = self._match_id(url)
        webpage, _ = downloadWebPage_BYHeadlessBrowser(url)
        # <video class="fp-engine" src="http://www.camwhores.tv/get_file/23/f8920c78bd107adbbe6672961a3560190d7ed653dc/1826000/1826836/1826836.mp4/?rnd=1519807399739" preload="metadata" autoplay="" hola-pid="3" x-webkit-airplay="allow"></video>
        video_url = self._search_regex(r'<video\s+class="fp-engine"\s+src="([^"]+)', webpage, 'video_url')
        if not video_url:
            return super(CamwhoresIE, self)._real_extract(url)

        title = self._og_search_title(webpage, default=None) or self._html_search_regex(
            r'(?s)<title>(.*?)</title>', webpage, 'video title',
            default='video')
        thumbnail = self._search_regex('preview_url:\s*\'([^\']+)', webpage, 'thumbnail')
        formats = [{
            'url': video_url,
            'ext': determine_ext(video_url),
        }]

        return ({
            'id': video_id,
            'title': title,
            'thumbnail': thumbnail,
            'formats': formats,
        })