# encoding: utf-8


from ..extractor.common import InfoExtractor
import json
from ..utils import int_or_none

class HudlIE(InfoExtractor):
    # http://www.hudl.com/video/3/10371003/5a14f58c42061a246c9410fb
    # http://www2.hudl.com/v/27tN4k
    # http://www.hudl.com/v/28DQtZ
    _VALID_URL = r'https?://(?:www2?\.)?hudl\.com/'

    def _real_extract(self, url):
        webpage = self._download_webpage(url, 'video_id')
        video_js = self._search_regex(r'(?<="video":)(.+)(?=,"clientIpAddress")', webpage, 'video_data')
        video_data = json.loads(video_js)
        if video_data and 'sources' in video_data and isinstance(video_data['sources'], dict):
            # "sources": {
            #     "mobile": "https://vf.hudl.com/p-highlights/User/10371003/5a14f58c42061a246c9410fb/051ead11_360.mp4?v=308649F50832D508",
            #     "sd": "https://vf.hudl.com/p-highlights/User/10371003/5a14f58c42061a246c9410fb/051ead11_480.mp4?v=308649F50832D508",
            #     "hd": "https://vf.hudl.com/p-highlights/User/10371003/5a14f58c42061a246c9410fb/051ead11_720.mp4?v=308649F50832D508"
            # }
            formats = []
            for key, video_url in list(video_data['sources'].items()):
                height = int_or_none(self._search_regex(r'_(\d+)', video_url, 'height'))
                formats.extend([{
                    'quality': key,
                    'ext': 'mp4',
                    'height': height,
                    'url': video_url,
                }])

            title = video_data['title']
            thumbnail = video_data['thumbnailUri']
            return {
                'id': '',
                'title': title,
                'formats': formats,
                'thumbnail': thumbnail,
            }

        # 这一种，直接在canvas上画的，下不下来
        return super(HudlIE, self)._real_extract(url)