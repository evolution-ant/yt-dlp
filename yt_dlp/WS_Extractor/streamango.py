# coding: utf-8


from ..extractor.streamango import StreamangoIE as StreamangoBase
# 这个函数，解不了此页面上的packer加密，格式不对
from ..utils import decode_packed_codes
from ..utilsEX import execjs_execute
import re

class StreamangoIE(StreamangoBase):
    # 解密视频地址，反替换回去
    def _download_webpage(self, url_or_request, video_id, note=None, errnote=None, fatal=True, tries=1, timeout=5,
                          encoding=None, data=None, headers={}, query={}):
        webpage = super(StreamangoIE, self)._download_webpage(url_or_request, video_id, note, errnote, fatal, tries, timeout,
                                                              encoding, data, headers, query)
        # 解出加密代码
        pattern = r'eval\((.+)\)'
        packed_js = self._search_regex(pattern, webpage, 'js_code')

        import execjs
        js = execjs.eval(packed_js)
        js = js.replace('window.d=function', 'function f')
        # src:d('guDNKZ3bNKLfQ6jRg6zRQODKgqwRN6HPNqHTJ57SNp7PO53RPpIPaN8Lat4QZ9wNM98LZeIOad4SZeIQM63KLanIOMvngt0Ma=AA',174)
        m = re.search(r"src:d\('([^']+)',(\d+)\)", webpage)
        arg1 = m.group(1)
        arg2 = m.group(2)
        video_src = execjs_execute(js, 'f', arg1, arg2)
        webpage = re.sub(r"d\('[^']+',\d+\)", '"%s"' % video_src, webpage)
        return webpage