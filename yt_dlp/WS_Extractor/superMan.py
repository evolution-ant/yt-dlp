#encoding: utf-8

from ..extractor.common import InfoExtractor
import re
import time
import json
from ..compat import (
    compat_urllib_parse_urlencode,
)
from ..utils import (
    determine_ext,
    HEADRequest,
)
from ..utilsEX import get_top_host

class SuperManIE(InfoExtractor):
    # http://xpau.se/watch/prison-break/s5/e1
    _VALID_URL = r'superMan://(.*)'

    def importCookie(self, url ,cookie, Jar):
        import http.cookiejar
        def make_cookie(domain, name, value):
            return http.cookiejar.Cookie(
                version=0,
                name=name,
                value=value,
                port=None,
                port_specified=False,
                domain=domain,
                domain_specified=True,
                domain_initial_dot=False,
                path="/",
                path_specified=True,
                secure=False,
                expires=None,
                discard=False,
                comment=None,
                comment_url=None,
                rest=None
            )
        try:
            domain = get_top_host(url)
            mobj = re.findall(r'(.+?)=(.+?);', cookie)
            for key, value in mobj:
                Jar.set_cookie(make_cookie(domain, key, value))
        except:
            pass
    def _real_extract(self, url):
        video_id = 'haha'
        url = self._search_regex(self._VALID_URL, url, url)

        localhost = 'http://127.0.0.1:8499'
        # sendRequestUrl = 'url=%s&browser=firefox' % (localhost, compat_urllib_parse_urlencode(url))
        # 求第一级iframe
        try:
            jsonData = self._download_json(localhost, 'sendRequestUrl', query={'url': url, 'browser': 'chrome'})
        except Exception as ex:
            if ex.message.find('urlopen error')>-1:
                raise Exception('kv_server no exists!')
        if 'error' in jsonData:
            raise Exception(jsonData['error'])

        resultID = jsonData['resultID']
        start = time.time()
        while (time.time() - start < 120):
            getResult = '%s?getResult=%s' % (localhost, resultID)
            try:
                jsonData = self._download_json(getResult, 'getResult')
                if jsonData['result'] == 'waitting':
                    time.sleep(5)
                else:
                    break
            except Exception as e:
                print(e)
                return

        if jsonData['result'] == 'waitting':
            return
        jsonData = jsonData['result']
        try:
            webPage = self._download_webpage(url, url)

            title = self._og_search_title(webPage, default=None)
            if not title:
                title = self._html_search_meta('title', webPage, default=None)
            if not title:
                title = self._search_regex(r'<title[^>]*>([^<]+)</title>', webPage, 'title', default=None)
            if not title:
                title = 'unkown'

            thumbail = self._html_search_meta('thumbnail', webPage, default=None)
            if not thumbail:
                thumbail = self._search_regex(r'<meta[ \t\r\n\v\f]+property=\"og:image\"[ \t\r\n\v\f]+content=\"(http[s]?://[^\"]+)\"', webPage, 'thumbail', default=None)
            if not thumbail:
                thumbail = self._search_regex(r'<meta[ \t\r\n\v\f]+name=\"og:image\"[ \t\r\n\v\f]+content=\"(http[s]?://[^\"]+)\"', webPage, 'thumbail', default=None)
            if not thumbail:
                thumbail = self._search_regex(r'<meta[ \t\r\n\v\f]+itemprop=\"image\"[ \t\r\n\v\f]+content=\"(http[s]?://[^\"]+)\"', webPage, 'thumbail', default=None)
        except:
            title = 'unkown'
            thumbail = None
        formats = []

        if 'dash' in jsonData:
            for key in ['video', 'audio']:
                media = jsonData[key]
                http_headers = media['request.headers']
                #print 'video http header ', http_headers
                # mobj = re.findall(r'\'([^\']+)\':\s*u\'([^\']+)', http_headers)
                # if mobj:
                #     http_headers = {item[0]:item[1] for item in mobj}
                video_url = media['request.url']
                ext = determine_ext(video_url)
                format = {
                    'url': video_url,
                    'ext': ext,
                    'http_headers': http_headers,
                    'format_note': 'DASH %s' % key,
                }

                if key == 'video':
                    format['acodec'] = 'none'
                else:
                    format['ext'] = 'm4a'
                formats.append(format)

        else:
            http_headers = jsonData['request.headers']
            video_url = jsonData['request.url']
            self.importCookie(video_url, http_headers.get('Cookie'), self._downloader.cookiejar)
            # print http_headers
            # mobj = re.findall(r'\'([^\']+)\':\s*u\'([^\']+)', http_headers)
            # if mobj:
            #     http_headers = {item[0]:item[1] for item in mobj}


            ext = jsonData.get('ext',determine_ext(video_url))
            try:
                if ext == 'smil':
                    formats.extend(self._extract_smil_formats(video_url, video_id))
                elif ext == 'm3u8':
                     formats.extend(self._extract_m3u8_formats(
                                        video_url, video_id, 'mp4', m3u8_id='hls', fatal=True))
                elif ext == 'mpd':
                    formats.extend(self._extract_mpd_formats(
                        video_url, video_id, fatal=True))
                else:
                    formats.append({
                        'url': video_url,
                        'http_headers': http_headers,
                        'ext': ext,
                    })
            except:
                formats.append({
                    'url': video_url,
                    'ext': ext,
                })
        self._check_formats(formats, '')
        return {
            'id': 'haha',
            'title': title,
            'thumbail': thumbail,
            'formats': formats,
        }
