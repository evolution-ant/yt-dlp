# encoding: utf-8



from ..utils import determine_ext
from ..utilsEX import execjs_execute
from ..extractor.common import InfoExtractor

class VjavIE(InfoExtractor):
    # https://www.vjav.com/videos/6471/natural-production-plants-shit-female-flight-principle/?source=2108980576#
    _VALID_URL = r'https?://(?:.+\.)?(?:vjav|hotmovs)\.com'

    def _real_extract(self, url):
        try:
            webpage = self._download_webpage(url, url)
            title = self._og_search_title(webpage, default=None) or self._html_search_regex(
                r'(?<=<title>)(.*)(?=</title>)', webpage, 'video title',
                default='video')
            title = title.replace(' - VJAV.com', '')
            # video_url = self._search_regex('video_url:\s*\'([^\']+)', webpage, 'src')
            video_data = self._search_regex(r'(?s)playlist:\s+\[(.*?)\]\s+};', webpage, 'video_data')
            video_data = video_data.replace('\t', '')
            #直接再正则匹配吧
            thumbnail = self._search_regex(r'image:\s*\'([^\']+)\'', video_data, 'thumbnail')
            # 验证mp4下载有网站证书信任问题，先找m3u8
            try:
                if ('"hls"' in video_data):
                    video_url = self._search_regex(r'\'file\':\s*\'([^\']+)\',\'type\':\s*"hls"', video_data, 'video url')
                    formats = [{
                        'url': video_url,
                        'protocol': 'm3u8'
                    }]
                # 否则求mp4
                else:
                    video_url = self._search_regex(r'\'file\':\s*\'([^\']+)\.mp4/.*', video_data, 'video url')
                    video_url = video_url + '.mp4'
                    formats = [{
                        'url': video_url,
                        'exe': 'mp4'
                    }]
            # 上述失败，取其页面js，解码其加密网址
            except:
                formats = self.decode_video_url(webpage)

            return {
                'id': '',
                'title': title,
                'thumbnail': thumbnail,
                'formats': formats,
            }
        except Exception as ex:
            return super(VjavIE, self)._real_extract(url)

    def decode_video_url(self, webpage):
        js = self._search_regex(r'(?s)window\.Dpww3Dw64=function\(b\){(.*?)};', webpage, 'js_code', fatal=False, default='')
        if js.strip() == '':
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
        video_url = self._search_regex(r'video_url="(.*?)"', webpage, 'video_url')
        if video_url:
            video_url = execjs_execute(js, 'Dpww3Dw64', video_url)
            formats = [{
                'url': video_url,
                'ext': determine_ext(video_url)
            }]
            return formats

        # 找m3u8 url
        m3u8_url = self._search_regex(r'm3u8_url="(.*?)"', webpage, 'm3u8_url')
        if m3u8_url:
            m3u8_url = execjs_execute(js, 'Dpww3Dw64', video_url)
            formats = [{
                'url': m3u8_url,
                'protocol': 'm3u8'
            }]
            return formats

        return []