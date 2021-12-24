import sys
import os
import re
import string
import unicodedata
import threading
import subprocess
#from urlparse import *
import traceback
import time
from .UniversalAnalytics import Tracker as GATacker
from .utils import update_url_query, sanitized_Request, make_HTTPS_handler, YoutubeDLHTTPSHandler
import base64

try:
    from Crypto.Cipher import AES
except:
    pass
from hashlib import md5

# '{ hei ght: 720, 'abr': 192, no_vcodec: vp9}' to '{"hei ght": 720, "abr": 192, "no_vcodec": "vp9"}'
def fix_json_str(str_json):
    if not isinstance(str_json, str):
        return str_json

    def ret_right_str(_str):
        if _str == '':
            return _str
        elif _str[0] == '"':
            return _str
        else:
            try:
               int(_str)
               return _str
            except:
                try:
                    float(_str)
                    return _str
                except:
                    pass

            return '"' + _str + '"'

    in_word = False
    str_tmp = ''
    str_tmp2 = ''
    str_json_ret = ''
    for c in str_json:
        if not in_word:
            if c == ' ':
                str_json_ret += c
            else:
                if c in ',:{}':
                    str_json_ret += c
                elif c in  """'""":
                    in_word = True
                    str_tmp2 = ''
                    str_tmp = ''
                else:
                    str_tmp2 = c
                    str_tmp = c
                    in_word = True
        else:
            if c == ' ':
                str_tmp += c
            else:
                if c in ',:{}':
                    in_word = False
                    str_json_ret += ret_right_str(str_tmp2)
                    if len(str_tmp2) < len(str_tmp):
                        str_json_ret += str_tmp[len(str_tmp2):]
                    str_json_ret += c
                    str_tmp2 = ''
                    str_tmp = ''
                elif c in  """'""":
                    in_word = False
                    str_tmp2 = str_tmp
                    str_json_ret += ret_right_str(str_tmp2)
                    if len(str_tmp2) < len(str_tmp):
                        str_json_ret += str_tmp[len(str_tmp2):]
                    str_tmp2 = ''
                    str_tmp = ''
                else:
                    str_tmp += c
                    str_tmp2 = str_tmp

    return str_json_ret



def FixDefaultEncoding():
    import sys
    if sys.getdefaultencoding() == 'ascii':
        reload(sys)
        sys.setdefaultencoding('utf-8')


def debug(str):
    try:
        if sys.stdout:
            sys.stdout.write('[dvdfab]|:|[debug]|:| %s:%s\n' % (time.strftime('%Y-%m-%d %H:%M:%S'), str))
            # sys.stdout.write('%s\n' % str)
            sys.stdout.flush()
    except:
        pass


if sys.platform == 'win32':
    def JSInterpreter(code, functionName, params=''):
        from comtypes import client
        js = client.CreateObject("MSScriptControl.ScriptControl")
        js.Language = 'JavaScript'
        js.AllowUI = False
        js.AddCode(code)
        return js.Run(functionName, params)
elif sys.platform == 'darwin':
    import execjs


    def JSInterpreter(code, functionName, params=''):
        ctx = execjs.compile(code)
        return ctx.call(functionName, params)
else:
    def JSInterpreter(code, functionName):
        return ''


def execjs_execute(code, methodname, *args):
    import execjs
    ctx = execjs.compile(code)
    return ctx.call(methodname, *args)


def validFileName(inputName):
    if sys.version_info[0] == 2:
        if isinstance(inputName, unicode) == True or isinstance(inputName, str) == True:
            if isinstance(inputName, str) == True:
                inputName = inputName.decode('UTF-8')
        else:
            raise TypeError
    reservedCharacters = '<>:"/\|?*\n\t'

    validName = ''.join(char for char in inputName if char not in reservedCharacters)
    validName = decode_html(validName)
    if isinstance(validName, str) == True:
        validName = validName.decode('UTF-8')

    while (len(validName) > 100):
        validName = validName[0:100]

    return validName


# AES decrypt
def aes_decrypt(data, password):
    bs = AES.block_size
    if len(data) <= bs:
        return data

    unpad = lambda s: s[0:-ord(s[-1])]

    def bytes_to_key(my_data, salt, output=48):
        # extended from https://gist.github.com/gsakkis/4546068
        assert len(salt) == 8, len(salt)
        my_data += salt
        key = md5(my_data).digest()
        final_key = key
        while len(final_key) < output:
            key = md5(key + my_data).digest()
            final_key += key
        return final_key[:output]

    data = base64.b64decode(data)
    salt = data[8:16]
    key_iv = bytes_to_key(password, salt, 32 + 16)
    key = key_iv[:32]
    iv = key_iv[32:]

    cipher = AES.new(key, AES.MODE_CBC, iv)
    return unpad(cipher.decrypt(data[bs:]))


def decode_html(input):
    import HTMLParser
    hp = HTMLParser.HTMLParser()
    return hp.unescape(input)


class GoogleAnalytics:
    def getCustomID(self):
        import errno
        from .utils import expand_path

        cachePath = expand_path(os.path.join('~/.cache', 'yt-dlp'))
        try:
            os.makedirs(cachePath)
        except OSError as ose:
            if ose.errno != errno.EEXIST:
                raise
        list = os.listdir(cachePath)
        for f in list:
            mobj = re.search(r'UID_(.+)', f)
            if mobj:
                return mobj.group(1)

        import uuid
        id = uuid.uuid4()
        fn = os.path.join(cachePath, 'UID_%s' % id)
        f = open(fn, 'a')
        f.close()
        return id

    def __init__(self, account='UA-100395100-1'):
        self.KeyMaps = {'AnalyticsFail': 'cm0', 'DownloadFail': 'cm1', 'DownloadSucess': 'cm2'}
        try:
            self.CUSTOMER_UNIQUE_ID = self.getCustomID()
            self._tracker = GATacker.create(account, client_id=self.CUSTOMER_UNIQUE_ID)
            # self._tracker.send('event', 'account', self.CUSTOMER_UNIQUE_ID)
        except:
            debug(traceback.format_exc())

    def sendDownloadResult(self, result, domain, url):
        self.send('event', result, domain, url)

    def send(self, hittype='event', *args, **data):
        try:
            if self._tracker:
                self._tracker.send(hittype, *args, **data)
        except:
            pass

    def set(self, name, value=None):
        if self._tracker:
            self._tracker.set(name, value)


topHostPostfix = (
    '.com', '.la', '.io',
    '.co',
    '.info',
    '.net',
    '.org',
    '.me',
    '.mobi',
    '.us',
    '.biz',
    '.xxx',
    '.ca',
    '.co.jp',
    '.com.cn',
    '.net.cn',
    '.org.cn',
    '.mx',
    '.tv',
    '.ws',
    '.ag',
    '.com.ag',
    '.net.ag',
    '.org.ag',
    '.am',
    '.asia',
    '.at',
    '.be',
    '.com.br',
    '.net.br',
    '.bz',
    '.com.bz',
    '.net.bz',
    '.cc',
    '.com.co',
    '.net.co',
    '.nom.co',
    '.de',
    '.es',
    '.com.es',
    '.nom.es',
    '.org.es',
    '.eu',
    '.fm',
    '.fr',
    '.gs',
    '.in',
    '.co.in',
    '.firm.in',
    '.gen.in',
    '.ind.in',
    '.net.in',
    '.org.in',
    '.it',
    '.jobs',
    '.jp',
    '.ms',
    '.com.mx',
    '.nl',
    '.nu',
    '.co.nz',
    '.net.nz',
    '.org.nz',
    '.se',
    '.tc',
    '.tk',
    '.tw',
    '.com.tw',
    '.idv.tw',
    '.org.tw',
    '.hk',
    '.co.uk',
    '.me.uk',
    '.org.uk',
    '.vg')


def get_top_host(url):
    parts = urlparse(url)
    host = parts.netloc
    extractPattern = r'[^\.]+(' + '|'.join([h.replace('.', r'\.') for h in topHostPostfix]) + ')$'
    pattern = re.compile(extractPattern, re.IGNORECASE)
    m = pattern.search(host)
    return m.group() if m else host


def download_webPage_by_PYCURL(IE, url_or_request, timeout=30, data=None, headers={}, query={}):
    print( 'download_webPage_by_PYCURL Begin')
    from compat import compat_urllib_request
    if isinstance(url_or_request, compat_urllib_request.Request):
        req = url_or_request
        url = req._Request__original
    else:
        req = sanitized_Request(url_or_request)
        url = url_or_request

    IE._downloader.cookiejar.add_cookie_header(req)
    if not headers:
        headers = req.headers

    if 'Cookie' in req.unredirected_hdrs:
        headers['Cookie'] = req.unredirected_hdrs['Cookie']

    try:
        import pycurl
        import StringIO

        def debugtest(debug_type, debug_msg):
            if debug_type == pycurl.INFOTYPE_TEXT:
                print( "debug(TEXT): %s" % (debug_msg) )
            elif debug_type == pycurl.INFOTYPE_HEADER_IN:
                print( "debug(HEADER_IN): %s" % (debug_msg) )
            elif debug_type == pycurl.INFOTYPE_HEADER_OUT:
                print( "debug(HEADER_OUT): %s" % (debug_msg) )

        curl_obj = pycurl.Curl()
        curl_obj.setopt(pycurl.FOLLOWLOCATION, 1)
        curl_obj.setopt(pycurl.MAXREDIRS, 5)
        curl_obj.setopt(pycurl.SSL_VERIFYPEER, 0)
        curl_obj.setopt(pycurl.SSL_VERIFYHOST, 2)
        html = StringIO.StringIO()
        curl_obj.setopt(pycurl.WRITEFUNCTION, html.write)
        curl_obj.setopt(pycurl.CONNECTTIMEOUT, timeout)
        curl_obj.setopt(pycurl.VERBOSE, 1)
        curl_obj.setopt(pycurl.DEBUGFUNCTION, debugtest)

        if data:
            curl_obj.setopt(pycurl.POSTFIELDS, data)
        if headers:
            hdrs = [('%s: %s') % (k, v) for k, v in headers.items()]
            curl_obj.setopt(pycurl.HTTPHEADER, hdrs)

        if query:
            url = update_url_query(url, query)
        curl_obj.setopt(pycurl.URL, url)
        curl_obj.perform()
        status = curl_obj.getinfo(pycurl.HTTP_CODE)
        if status > 399:
            raise Exception('download_webPage_by_PYCURL Error %s' % status)
        content = unicode(html.getvalue(), "utf-8")
        print( 'download_webPage_by_PYCURL end')
        return content
    except Exception as ex:
        if sys.platform != 'win32':
            print( '------------------------------------------------Begin download_webPage_by_CURLCMD')
            return download_webPage_by_CURLCMD(url, timeout, data, headers)
            print( '------------------------------------------------End download_webPage_by_CURLCMD')
        else:
            raise ex


def getStartInfo():
    IS_WIN32 = 'win32' in str(sys.platform).lower()
    if IS_WIN32:
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags = subprocess.CREATE_NEW_CONSOLE | subprocess.STARTF_USESHOWWINDOW
        startupinfo.wShowWindow = subprocess.SW_HIDE
        return startupinfo
    else:
        return None


def download_webPage_by_CURLCMD(url, timeout=30, data=None, headers={}):
    print( 'download_webPage_by_CURLCMD begin')
    try:
        cmd = 'curl -L -m %s ' % timeout

        cmd += url
        if data:
            cmd += ' -d %s'
        strHeader = ''
        if headers:
            for k, v in headers.items():
                strHeader += (' -H "%s: %s"') % (k, v)
            if strHeader:
                cmd += strHeader

        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, startupinfo=getStartInfo(),
                                shell=True)
        subStdout, subStderr = proc.communicate()
        print (proc.wait())
        content = unicode(subStdout, "utf-8")
        print ('download_webPage_by_CURLCMD end')
        return content
    except Exception as ex:
        print ('download_webPage_by_CURLCMD end')
        print(ex)
        raise ex


class convertTimeFormat:
    def __init__(self):
        self.line = 0

    def run2(self, m):
        self.line = self.line + 1
        str = m.group(0).replace('.', ',')
        return str

    def run(self, m):
        self.line = self.line + 1
        str = m.group(0).replace('.', ',')
        str = '\n%s\n%s' % (self.line, str)
        return str

def removeSRTInvalidCharacter(content):
    result = re.sub(r'<.+?>', '', content)
    result = re.sub(r'<\.+?>', '', result)
    return result

def convertWebSRT2SRT(webpage, hasLineTag=False):
    timeStr = r'([0-9]{2}:[0-9]{2}:[0-9]{2}.[0-9]{3}[ ]*-->[ ]*[0-9]{2}:[0-9]{2}:[0-9]{2}.[0-9]{3})'
    mobj = re.search(r'(%s[\s\S]+)' % (timeStr), webpage)
    p = re.compile(timeStr)
    content = mobj.group(0)
    content = re.sub(r'%s[ ]+([^\n]+)' % timeStr, lambda x: x.group(1), content)
    content = re.sub(r'<.+?>', '', content)
    content = re.sub(r'<\.+?>', '', content)

    lines = re.findall(r'(.*)\n', content)
    content = ''

    for line in lines:
        if (re.search(r'\S', line)):
            if content == '':
                content = line
            else:
                content = '%s\n%s' % (content, line)

    replace = convertTimeFormat().run
    if hasLineTag:
        replace = convertTimeFormat().run2
        content = p.sub(replace, content)
        content = re.sub(r'\n(\d+\n)', r'\n\n\1', content)
        content = '\n1\n%s' % content
        return content
    else:
        content = p.sub(replace, content)
        return content


def url_result(url, ie=None, video_id=None, video_title=None, video_duration=None):
    video_info = {'_type': 'url',
                  'url': url,
                  'ie_key': ie}
    if video_id is not None:
        video_info['id'] = video_id
    if video_title is not None:
        video_info['title'] = video_title
    if video_duration is not None:
        video_info['duration'] = video_duration
    return video_info


def downloadWebPage_BYHeadlessBrowser(url, param=None):
    try:
        def waitResult(lines, proc):
            try:
                encoding = sys.getdefaultencoding()
                fs_encoding = sys.getfilesystemencoding()
                while 1:
                    line = proc.stdout.readline()
                    try:
                        line = line.decode(encoding)
                    except UnicodeDecodeError:
                        line = line.decode(fs_encoding)

                    if not line and not param:
                        break

                    line = line.rstrip()
                    lines.append(line)
                    print (line)

                    if 'kv_player' in line:
                        break

                # delete temp file
                if param:
                    os.remove(param)
            except Exception as ex:
                print( ex)

        def run(args):
            html = ''
            try:
                proc = subprocess.Popen(args, stdout=subprocess.PIPE, startupinfo=getStartInfo())
                lines = []
                t = threading.Thread(target=lambda: waitResult(lines, proc))
                t.start()
                t.join(100)
                for line in lines:
                    html += line
            except Exception as ex:
                print (ex)
            finally:
                print ('PhantomJS download finished ...........')
                try:
                    if sys.platform != 'win32':
                        proc.communicate(b'q')
                    else:
                        proc.kill()
                except:
                    print ('PhantomJS download cancle except...........')
                return html

        basePath = os.getenv('KVFfmpegPath')

        if sys.platform == 'win32':
            if basePath is None:
                PhantomJS = r'DownloadRes\WSPhantomJS.exe' if os.path.exists(
                    r'DownloadRes\WSPhantomJS.exe') else 'WSPhantomJS.exe'
            else:
                PhantomJS = os.path.join(basePath, 'WSPhantomJS')
            args = [PhantomJS, url, param] if param else [PhantomJS, url]
        else:
            DynamicAnalysiser = os.getenv('KVDynamicAnalysiser')
            if not DynamicAnalysiser:
                DynamicAnalysiser = 'DynamicAnalysiser'
            args = [(DynamicAnalysiser)]
            args += ['-wu', url]

        html = run(args)
    except Exception as ex:
        print (ex)

    return html, None


Kown_Video_EXTS = ['mp4', 'flv', '3gp', 'mov', 'avi', 'mkv', 'wmv', 'f4v', 'm4v', '3g2', 'asf', ' m2t',
                   'm2ts', 'mod', 'mpeg', 'mpg', 'mts', 'rm', 'rmvb', 'tp', 'trp', 'ts', 'vob', 'webm',
                   'wmv', 'dat', 'dv']  # 'webm']

Kown_Audio_EXTS = ['mp3', 'm4a', 'aac', 'wav', 'ogg', 'opus', 'wma', 'flac', 'mka', 'ape', 'ac3',
                   'aif', 'aiff', 'amr', 'ape', 'au', 'mp2', 'm4b', 'm4p']  # 'webm', ]


def make_HTTPS_handlerEx(params, **kwargs):
    try:
        if sys.platform != 'win32':
            from cffi import cffi_opcode
        from urllib3.contrib.pyopenssl import inject_into_urllib3

        inject_into_urllib3()
        from urllib3.connection import HTTPSConnection

        handler = YoutubeDLHTTPSHandler(params, https_conn_class=HTTPSConnection, **kwargs)
        if hasattr(handler, '_context'):
            delattr(handler, '_context')
        return handler
    except Exception as ex:
        print( "make_HTTPS_handlerEx Exception")
        print (ex)
        return make_HTTPS_handler(params, **kwargs)


def injectYoutubeDL_make_HTTPS_handler():
    try:
        import YoutubeDL
        setattr(YoutubeDL, 'make_HTTPS_handler', make_HTTPS_handlerEx)
    except Exception as ex:
        print (ex)


from .extractor.common import InfoExtractor

def _get_cookies(self, url):
    from compat import compat_cookies
    req = sanitized_Request(url)
    self._downloader.cookiejar.add_cookie_header(req)
    cookie = req.get_header('Cookie')
    return compat_cookies.SimpleCookie(cookie.encode('utf-8')) if cookie else None

#InfoExtractor._get_cookies = _get_cookies