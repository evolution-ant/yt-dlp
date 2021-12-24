# encoding: utf-8


import re
from ..compat import compat_urllib_parse
from ..extractor.common import InfoExtractor
from ..extractor.vshare import VShareIE as OldVShareIE


class VShareIE(OldVShareIE):
    # http://yespornplease.com/view/353285165 这个链接，所求下载居然是个vob连接，鬼！神器整它
    # https://vshare.io/v/fccdbc4/width-750/height-400/1
    def _real_extract(self, url):
        # 先走官方解析
        try:
            return super(VShareIE, self)._real_extract(url)
        except:
            pass

        # 旧版解析title异常，弃旧版方式
        video_id = self._match_id(url)
        # 取缩略图
        webpage = self._download_webpage(url, video_id)
        # 直解加密的js代码，取其中视频信息
        formats = self.get_formats(webpage)
        if len(formats) == 0:
            return super(VShareIE, self)._real_extract(url)

        title = self._html_search_regex(
            r'(?<=<title>)(.*)(?=</title>)', webpage, 'video title',
            default='video')
        ridx = title.rfind(' - ')
        if ridx != -1:
            title = title[0:ridx]
        description = self._og_search_description(webpage)
        thumbnail = self._html_search_regex(
            r'poster="([^"]+)"', webpage, 'thumbnail')
        thumbnail = thumbnail if thumbnail.startswith('http') else 'https:' + thumbnail
        # 取实际视频内容...此处vshare改版，不再放其下载url，直解其packed js代码
        # webpage = self._download_webpage(
        #     'https://vshare.io/d/%s' % video_id, video_id)

        # title = self._html_search_regex(
        #     r'(?s)<div id="root-container">\s+<[^\n]*\s+(.+?)<br\s?/>', webpage, 'title')
        # video_url = self._search_regex(
        #     r'<a[^>]+href=(["\'])(?P<url>(?:https?:)?//.+?)\1[^>]*>[Cc]lick\s+here',
        #     webpage, 'video url', group='url')

        return {
            'id': video_id,
            'title': title,
            'thumbnail': thumbnail,
            'formats': formats,
            'description': description
        }

    def get_formats(self, webpage):
        import re
        from ..utils import decode_packed_codes
        from ..utilsEX import execjs_execute

        # 找出eval执行体
        # pattern = r'eval\((.+)\)'
        # packed_js = self._search_regex(pattern, webpage, 'js_code')
        # js = execjs.eval(packed_js)
        # 原来，有直接可用函数！
        js = decode_packed_codes(webpage)

        # 处理为可解析格式
        base = self._search_regex(r'-(\d+)\)', js, 'base')
        args =self._search_regex(r'(\[[^\]]+\])', js, 'args')
        js = '''
            function f(){
                var v = %s;
                length = v.length;
                var r = '';
                for (var k = 0; k < length; k++) {
                    r += String.fromCharCode(parseInt(v[k]) - %s);
                }
                return r;
            }
        ''' % (args, base)
        source = execjs_execute(js, 'f')
        pattern = r'src="([^"]+)"[^>]type="([^"]+)"[^>]label="([^"]+)"[^>]res="([^"]+)"'
        formats = []
        for url, ext, format_id, height in re.findall(pattern, source):
            formats.append({
                'url': url,
                'ext': ext.replace('video/', ''),
                'format_id': format_id,
                'height': height,
            }
        )

        self._sort_formats(formats)
        return formats

class VShare_euIE(InfoExtractor):

    _VALID_URL = r'https?://(?:www\.)?vshare\.eu/'

    def _real_extract(self, url):
        self._downloader.cookiejar.clear()
        headers = {}#{'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36', 'cookie': ''}
        webpage = self._download_webpage(url, url, headers=headers)
        params = re.findall(r'name="(.+)?".+?value="(.+)?">', webpage)
        data = {param[0] : param[1] for param in params if param[1]!=''}
        data = compat_urllib_parse.urlencode(data)
        webpage = self._download_webpage(url, url, data=data, headers=headers)
        title = self._og_search_title(webpage, default=None) or self._html_search_regex(
            r'(?s)<Title>(.*?)</Title>', webpage, 'video title',
            default='video')
        video_url = self._search_regex(r'source\s+src="([^"]+)', webpage, '')
        thumbnail = self._search_regex(r'poster="([^"]+)', webpage, '', fatal=False)
        formats = [{
                       'url': video_url,
                       'ext': 'mp4',
        }]
        return  ({
                'id': '',
                'title': title,
                'thumbnail': thumbnail,
                'formats': formats,
            })