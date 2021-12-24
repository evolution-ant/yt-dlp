#encoding: utf-8


import os
import json
from urllib.parse import quote, unquote
from ..extractor.common import InfoExtractor
from ..extractor.googledrive import GoogleDriveIE as Old
from ..compat import compat_urlparse, compat_urllib_parse_urlencode
from ..utilsEX import Kown_Video_EXTS, Kown_Audio_EXTS


class OneDriverIE(InfoExtractor):
    _VALID_URL = r'https?://(?:onedrive\.live\.com/.+authkey=|1drv\.ms)'

    apiUrl = 'https://skyapi.onedrive.live.com/API/2/GetItems?authKey=%s&id=%s&cid=%s'
    def _real_extract(self, url):
        #self._downloader.cookiejar.clear()
        webpage = self._download_webpage(url, url, '')
        if url.find('1drv')> -1:
            url = self._html_search_regex(r'"refresh" content="0;url=([^"]+)', webpage, '')
            webpage = self._download_webpage(url, url, '')
        filesConfig = self._search_regex(r'FilesConfig\=(.+);var', webpage, '')
        filesConfig = self._parse_json(filesConfig, '')
        authKey = quote(filesConfig['authKey'])
        appId = filesConfig['appId']
        optionsUrl = filesConfig['SuiteNavConfig']['Urls']['Options']
        # webpage = self._download_webpage(url, url)
        cid = self._search_regex(r'cid\%3d(.+?)\%26', optionsUrl, '')
        id = unquote(self._search_regex(r'%26id\%3d(.+?)\%26', optionsUrl, ''))

        data = self._download_json(self.apiUrl % (authKey, id, cid), '', headers={'AppId': appId, 'Accept': 'application/json'})
        item = data['items'][0]
        ext = item['extension'].strip('.').lower()
        title = item['name']
        size = item['size']
        video_url = item['urls']['download']

        if not(ext in Kown_Video_EXTS or ext in Kown_Audio_EXTS):
            ext = 'mp4'
        formats = [{
                       'url': video_url,
                        'ext': ext,
                       'size': size,
                       'http_headers': {'Accept-Encoding': ''}
        }]
        return {
            'id': id,
            'title': title,
            'formats': formats,
        }