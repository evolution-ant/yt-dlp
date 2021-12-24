# encoding: utf-8



from ..extractor.common import (
    InfoExtractor
)
from ..utils import (
    js_to_json,
)

class YesvideoIE(InfoExtractor):
    # http://share.yesvideo.com/s/aQdzgvCKvcIBAvTb/embed
    # http://share.yesvideo.com/s#/share/5962ad5b17744959bc002003
    _VALID_URL = r'https?://(?:share\.)?yesvideo\.com'

    def _real_extract(self, url):
        # 若是s#/share形式，求其原ID
        if 's#/share' in url:
            video_id = self._search_regex(r's#/share/([^/]+)', url, 'video_id')
            if video_id:
                api_url = r'http://share.yesvideo.com/api/v3/shares/' + video_id
                video_data = self._download_json(api_url, video_id)
                link_url = video_data['share']['link_url']
                if link_url:
                    return self.url_result(link_url)

        if not '/s/' in url:
            return super(YesvideoIE, self)._real_extract(url)

        if not '/embed' in url:
            url = url + '/embed'
        video_id = self._search_regex(r'/s/([^/]+)', url, 'video_id')
        webpage = self._download_webpage(url, video_id)
        title = self._search_regex(r'<title>([^<]+)</title>', webpage, 'title', fatal=False)
        thumbnail = self._search_regex(r'image:\s*"([^"]+)', webpage, 'thumbnail', fatal=False)
        video_url = self._search_regex(r'(?s)config:.*?"([^"]+)', webpage, 'video_url', fatal=False)

        return {
            'id': video_id,
            'title': title,
            'thumbnail': thumbnail,
            'url': video_url
        }