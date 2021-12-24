# encoding: utf-8



from ..extractor.common import InfoExtractor
from ..utils import urlencode_postdata
from ..utilsEX import execjs_execute

class PutStreamIE(InfoExtractor):
    IE_NAME = 'putstream'
    _VALID_URL = r'https?://(?:www\.)?putstream\.com/'

    def _real_extract(self, url):
        video_id = self._search_regex(r'watching=(\w+)', url, 'video_id')
        webpage = self._download_webpage(url, video_id)

        title = self._og_search_title(webpage)
        ridx = title.rfind(' - ')
        if ridx != -1:
            title = title[0:ridx]
        thumbnail = self._og_search_thumbnail(webpage)
        description = self._og_search_description(webpage)
        video_url = self.get_video_url(webpage, url)

        return {
            'id': video_id,
            'title': title,
            'url': video_url,
            'thumbnail': thumbnail,
            'description': description,
        }

    def get_video_url(self, webpage, url):
        # 解析其中js代码
        tc = self._search_regex(r'var\s+tc\s+=\s+\'([^\']+)', webpage, 'tc')
        js = self._search_regex(r'(function _t_t[^<]+)', webpage, 'js')
        x_token = execjs_execute(js, '_t_t', tc)
        token = self._search_regex(r'"_token":\s+"([^\"]+)', webpage, 'token')

        # 构建ajax请求所需数据队列
        post_data = urlencode_postdata({
            'tokenCode': tc,
            '_token': token,
        })
        headers = {
            'x-token': x_token,
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        }
        post_url = 'https://putstream.com/decode-link'
        video_urls = self._download_json(post_url, 'video_id', data=post_data, headers=headers)
        return video_urls[0]