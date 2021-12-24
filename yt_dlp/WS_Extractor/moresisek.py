# coding: utf-8
# 与AES解密冲突
# from __future__ import unicode_literals

import json
import os
from ..extractor.common import InfoExtractor
from ..utils import clean_html
from ..utilsEX import aes_decrypt

class MoresisekIE(InfoExtractor):
    _VALID_URL = r'(?:https?://)?(?:www\.)?moresisek\.com/watch/(?P<id>[^/?#&]+)'

    def _real_extract(self, url):
        webpage = self._download_webpage(url, 'video_id')
        title = self._html_search_regex(r'<title>(.+)</title>', webpage, 'title')
        title = title.replace(' - MORESISEK.COM', '')

        # AES解密video_id。其key为583a01a9ba901a3adda7252ebca42c09
        # key = [int(x, 16) for x in '583a01a9ba901a3adda7252ebca42c09']
        key = '583a01a9ba901a3adda7252ebca42c09'
        video_id = self._search_regex(r'video_id = \'(.+?)\'', webpage, 'video_id')
        try:
            video_id = aes_decrypt(video_id, key)
        except Exception as e:
            return super(MoresisekIE, self)._real_extract(url)

        callbackFn = self._search_regex(r'callbackFn = \'(.+?)\'', webpage, 'callbackFn')
        # 请求实际数据  http://moresisek.com/video.get?video=-108921352_456239053&callback=fn_14996814657464
        query_url = r'http://moresisek.com/video.get?video=%s&callback=%s' % (video_id, callbackFn)
        webpage = self._download_webpage(query_url, 'video_id')
        webpage = clean_html(webpage).replace('\/', '/')
        webpage = self._search_regex(r'(?s)fn_\d+\((.+?)\)', webpage, 'video_info')
        video_info = json.loads(webpage)
        if (video_info.get('files', None) != None):
            thumbnail = video_info['poster']
            formats = []
            for video_key in video_info['files']:
                video_url = video_info['files'][video_key]
                ext = os.path.splitext(video_url)[1].replace('.', '')
                formats.append({
                    'url': video_url,
                    'ext': ext
                })
        else:
            return super(MoresisekIE, self)._real_extract(url)

        return {
            'id': '',
            'title': title,
            'formats': formats,
            'thumbnail': thumbnail
        }