# encoding: utf-8



from ..extractor.common import InfoExtractor
from ..utils import (
    js_to_json,
    determine_ext,
)
from ..utilsEX import execjs_execute

class HclipsIE(InfoExtractor):
    # https://www.hclips.com/videos/fucking-and-then-shooting-a-priceless-load-on-to-her-snatch
    # https://m.hclips.com/videos/fucking-and-then-shooting-a-priceless-load-on-to-her-snatch
    # https://m.hclips.com/embed/871839
    _VALID_URL = r'https?://(?:(www|m)\.)?hclips\.com'

    def _real_extract(self, url):
        webpage = self._download_webpage(url, url)

        try:
            jw_config = self._parse_json(
                self._search_regex(
                    r'jwsettings=([\s\S]+?);',
                    webpage, 'jw config'),
                '', transform_source=js_to_json)
            info = self._parse_jwplayer_data(
                jw_config, '123', require_title=False, m3u8_id='hls',
                base_url=url)

            title = self._og_search_title(webpage, default=None) or self._html_search_regex(
                r'(?s)<title>(.*?)</title>', webpage, 'video title',
                default='video')

            info.update({
                'title': title,
                'thumbnail': self._og_search_thumbnail(webpage),
            })
            return info
        # 抠代码，直解加密视频字串
        except:
            js = self._search_regex(r'(?s)window\.Dpww3Dw64=function\(b\){(.*?)};', webpage, 'js_code', fatal=False)
            if not js or js.strip() == '':
                js = '''
                    var c = "",
                        d = 0;
                    /[^АВСЕМA-Za-z0-9\.\,\~]/g.exec(b) && console.log("error decoding url");
                    b = b.replace(/[^АВСЕМA-Za-z0-9\.\,\~]/g, "");
                    do {
                        var f = "АВСDЕFGHIJKLМNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789.,~".indexOf(b.charAt(d++)),
                            e = "АВСDЕFGHIJKLМNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789.,~".indexOf(b.charAt(d++)),
                            g = "АВСDЕFGHIJKLМNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789.,~".indexOf(b.charAt(d++)),
                            h = "АВСDЕFGHIJKLМNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789.,~".indexOf(b.charAt(d++)),
                            f = f << 2 | e >> 4,
                            e = (e & 15) << 4 | g >> 2,
                            k = (g & 3) << 6 | h,
                            c = c + String.fromCharCode(f);
                        64 != g && (c += String.fromCharCode(e));
                        64 != h && (c += String.fromCharCode(k))
                    } while (d < b.length);
                    return unescape(c)
                '''

            js = 'function Dpww3Dw64(b){%s}' % js
            # 用utilsEx中的JSInterpreter，win下用MSScriptControl.ScriptControl遭遇编码问题，故用pyexecjs，并改其源码，隐藏win下subprocess.Popen() cmd窗口
            # 找mp4 url
            video_url = self._search_regex(r'video_url=Dpww3Dw64\("([^"]*?)"\)', webpage, 'video_url', fatal=False)
            if not video_url:
                video_url = self._search_regex(r'var\svideo_url="([^"]*?)"', webpage, 'video_url')
            if video_url:
                video_url = execjs_execute(js, 'Dpww3Dw64', video_url)
                formats = [{
                    'url': video_url,
                    'ext': determine_ext(video_url)
                }]

                title = self._search_regex(r'video_title="([^"]*?)"', webpage, 'video_title', fatal=False) or \
                        self._search_regex(r'title: "([^"]*?)"', webpage, 'video_title', fatal=False, default='no title')
                thumbnail = self._search_regex(r'image: \'([^\']*?)\'', webpage, 'thumbnail', fatal=False)
                return {
                    'id': '',
                    'title': title,
                    'thumbnail': thumbnail,
                    'formats': formats,
                }