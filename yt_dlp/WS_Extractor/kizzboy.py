# encoding: utf-8



from ..extractor.common import (
    InfoExtractor
)
from ..utils import (
    js_to_json,
)

class KizzboyIE(InfoExtractor):
    # http://www.kizzboy.com/2018/02/02/tricked-str8-18-year-old-from-poland-on-cam/
    _VALID_URL = r'https?://(?:www\.)?kizzboy\.com/(?:[\d{2,4}/]+)(?P<id>[^/]+)'

    def _real_extract(self, url):
        video_id = self._match_id(url)
        # 求其frmae url
        webpage = self._download_webpage(url, video_id)
        frame_url = self._search_regex(r'<iframe[^>]+src="([^"]+")', webpage, 'frame_url')
        if not frame_url:
            return super(KizzboyIE, self)._real_extract(url)

        title = self._og_search_title(webpage)
        title = title[0:title.index(' - GayBoysTube')]
        thumbnail = self._og_search_thumbnail(webpage)
        formats = self._get_formats(frame_url, video_id)

        return {
            'id': video_id,
            'title': title,
            'thumbnail': thumbnail,
            'formats': formats,
        }

    def _get_formats(self, url, video_id):
        webpage = self._download_webpage(url, '')
        jd = self._extract_jwplayer_data(webpage, video_id, require_title=False)
        return jd['formats']