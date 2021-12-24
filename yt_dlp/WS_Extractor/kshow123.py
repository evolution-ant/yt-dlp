# encoding: utf-8


from ..extractor.common import InfoExtractor
import re
from ..utils import (
    urlencode_postdata,
    js_to_json
)
from ..utilsEX import (
    downloadWebPage_BYHeadlessBrowser,
    aes_decrypt,
)

class KShow123IE(InfoExtractor):
    # http://kshow123.net/show/morning-forum/episode-8028.html
    _VALID_URL = r'(?:https?://)?(?:www\.)?kshow123\.net/show/(?P<id>[^/]+)'

    def _real_extract(self, url):
        video_id = self._match_id(url)
        # 先走动态解析，没有结果再硬啃
        webpage, _ = downloadWebPage_BYHeadlessBrowser(url)
        title = self._og_search_title(webpage)
        thumbnail = self._og_search_thumbnail(webpage)
        description = self._og_search_description(webpage)
        video_url = self._search_regex(r'src="(.+?\.mp4)', webpage, 'video_url', fatal=False)
        if video_url:
            return {
                'id': video_id,
                'title': title,
                'thumbnail': thumbnail,
                'description': description,
                'url': video_url,
                'ext': 'mp4'
            }


        # 直接解密，硬啃
        webpage = self._download_webpage(url, video_id)
        webpage = webpage.replace('videoJson=\'\'', '')
        webpage = webpage.replace('imageCover=\'\'', '')
        video_json = self._parse_json(self._search_regex(r'videoJson\s*=\s*\'([^\']+)', webpage, 'video_json'), video_id)
        if isinstance(video_json, list):
            current_video = self._search_regex(r'currentVideo\s*=\s*\"([^\"]+)', webpage, 'current_video')
            for video in video_json:
                if video['videoId'] == int(current_video):
                    video_json = video
                    break
        link = video_json['url']
        sub_url = video_json['subUrl']
        image_cover = self._search_regex(r'imageCover\s*=\s*\'([^\']+)', webpage, 'image_cover')

        api_url = self._search_regex(r'API_URL\s*=\s*\'([^\']+)', webpage, 'api_url')
        api_url = api_url + 'proxy.php'

        post_data = urlencode_postdata({
            'link': link,
            'subUrl': sub_url,
            'imageCover': image_cover,
        })
        headers={
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'
        }
        video_src = self._download_webpage(api_url,
            video_id,
            data=post_data,
            headers=headers
        )
        # 引用其它网站的
        if '<iframe ' in video_src:
            url = self._search_regex(r'<iframe[^>]+src="([^"]+)', video_src, url)
            return self.url_result(url)

        # 解密
        def decode_file(m):
            path, key = re.findall(r'"([^"]+)",(\d+)', m.group(1))[0]
            key = 'kshow123.net' + '4590481877' + key
            # 它只支持ansi编码
            path = path.encode('ascii','ignore')
            key = key.encode('ascii','ignore')
            result = aes_decrypt(path, key)
            return '"%s"' % result

        video_src = re.sub(r'decodeLink\(([^)]+)\)', decode_file, video_src)
        js_data = self._search_regex(r'(?s)playerInstance\.setup\(({.+?})\)', video_src, 'jwplayer data')
        jwplayer_data = self._parse_json(js_data, video_id, transform_source=lambda s: js_to_json(s))

        info_dict = self._parse_jwplayer_data(
            jwplayer_data, video_id, require_title=False, m3u8_id='hls', mpd_id='dash')

        info_dict.update({
            'title': self._og_search_title(webpage),
            'description': self._og_search_description(webpage)
        })
        return info_dict