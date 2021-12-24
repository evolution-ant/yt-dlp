# coding: utf-8

from ..extractor.common import InfoExtractor
import time
import datetime
import urllib.request, urllib.parse, urllib.error
from ..utilsEX import JSInterpreter

import json
import re
from ..utils import (
    urlencode_postdata,
    sanitized_Request,
    int_or_none
)

class SaveFromIE(InfoExtractor):
    IE_NAME = 'savefrom.net'
    _VALID_URL = r'https?://[^.]+\.savefrom\.net/\#url=(?P<url>.*)$'

    _TEST = {
        'url': 'http://en.savefrom.net/#url=http://youtube.com/watch?v=UlVRAPW2WJY&utm_source=youtube.com&utm_medium=short_domains&utm_campaign=ssyoutube.com',
        'info_dict': {
            'id': 'UlVRAPW2WJY',
            'ext': 'mp4',
            'title': 'About Team Radical MMA | MMA Fighting',
            'upload_date': '20120816',
            'uploader': 'Howcast',
            'uploader_id': 'Howcast',
            'description': r're:(?s).* Hi, my name is Rene Dreifuss\. And I\'m here to show you some MMA.*',
        },
        'params': {
            'skip_download': True
        }
    }

    def _real_extract(self, url):
        url = url[url.index('url=')+4:]
        url = urllib.parse.unquote(url)
        download_link_json = self._get_savefrom_downloadlink_json(url)
        def getQuality(f):
            if 'quality' in f:
                quality = f.get('quality', '')
                try:
                    if quality != '':
                        mobj = re.search(r'(\d+)', quality)
                        return int_or_none(mobj.group(1), default=0)
                except:
                    return 0
            else:
                return 0
        formasts = [
            {
                'format_id':f.get('type'),
                'height': getQuality(f),
                'url':f.get('url'),
                'ext': f.get('ext', 'mp4'),
            }for f in download_link_json['url']
        ]
        if 'id' in list(download_link_json.keys()):
            vid = download_link_json['id']
        else:
            vid = 'sf' + str(int(time.mktime(datetime.datetime.now().timetuple())))
        result = {
            'id':vid,
            'title':download_link_json['meta']['title'],
            'duration':download_link_json['meta']['duration'] if 'duration' in list(download_link_json['meta'].keys()) else '',
            'formats':formasts,
            'thumbnail':download_link_json['thumb'] if 'thumb' in list(download_link_json.keys()) else '',
        }
        return result

    def _get_savefrom_downloadlink_json(self, url):
        savefrom_response = self._get_savefrom_response(url)

        savefrom_js_function = self._make_savefrom_js_function(savefrom_response)

        download_link_str = JSInterpreter(savefrom_js_function, 'getSfDownloadLinks')

        if url.find("soundcloud.com") != -1 and download_link_str.find('audioResult.show') != -1:
            download_link_str = self._get_soundcloud_json_str(download_link_str)

        download_link_json = json.loads(download_link_str)

        if url.find("1tv.ru") != -1:
            download_link_json = self._deal_1tv_link_json(download_link_json)

        return download_link_json

    def _get_savefrom_response(self, url):
        self._request_webpage('http://en.savefrom.net/', 'get the homepage to set cookie')

        requrl = 'http://en.savefrom.net/savefrom.php'

        query = {'sf_url':url,'new':'1','lang':'en','sf_submit':''}
        data = urlencode_postdata(query)

        req = sanitized_Request(requrl, data=data)
        req.add_header('Content-Type', 'application/x-www-form-urlencoded')
        req.add_header('Origin', 'http://en.savefrom.net')
        req.add_header('Referer', 'http://en.savefrom.net/')
        response = self._request_webpage(req, 'get the response')
        body = response.read()

        return body

    def _make_savefrom_js_function(self, body):
        str1 = body[body.index('(function(){')+12:]
        str1 = 'function getSfDownloadLinks(){ var result = "";' + str1
        str2 = str1[0:str1.index('})();')]
        str2 += 'return result;};'
        index = str2.index('eval(')+5
        name = str2[index]
        result = str2.replace('eval(','if('+name+'.indexOf("del()") > 0){var begin='+name+
                                    '.indexOf("videoResult.show(")+17;var end = '+name+
                                    '.indexOf("window.parent.sf.enableElement")-4;result='+name+
                                    '.substring(begin,end)}else eval(')
        return result

    def _get_soundcloud_json_str(self, download_link_str):
        download_link_str = download_link_str[download_link_str.index('audioResult.show')+17:]
        if download_link_str.find(')') != -1:
            index = download_link_str.index(')')
            download_link_str = download_link_str[0:index]
        return download_link_str

    #www.1tv.ru列表链接会返回多个视频的列表，目前对此结果没有处理
    def _deal_1tv_link_json(self, download_link_json):
        download_link_json['url'] = [
            {
                'type':f.get('name'),
                'quality':f.get('subname', 0),
                'url':f['attr']['data-copy'],
                'ext': f.get('name', 'mp4').lower(),
            }for f in download_link_json['action']
        ]
        return download_link_json

    @classmethod
    def support(cls, url):
        url = urllib.parse.unquote(url)
        pattern = re.compile( r'''youtube\.com|facebook\.com|break\.com|dailymotion\.com|vimeo\.com|sevenload\.com|mail\.ru
                        |smotri\.com|yandex\.video|tvigle\.ru|livejournal\.com|vk\.com|odnoklassniki\.ru
                        |soundcloud\.com|liveinternet\.ru|veojam\.com|1tv\.ru|rutv\.ru|ntv\.ru|vesti\.ru
                        |mreporter\.ru|autoplustv\.ru|russiaru\.net|a1tv\.ru''')
        result = pattern.search(url)
        if result:
            return True
        else:
            return False

    @classmethod
    def makeUrl(cls, url):
        return 'http://en.savefrom.net/#url=' + url
