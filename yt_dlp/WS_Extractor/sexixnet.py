

import re
import json

from ..extractor.common import InfoExtractor
from ..utils import (
    js_to_json
)


class sexixnetIE(InfoExtractor):
    #http://www.txxx.com/videos/2631606/stepmom-seduces-teen-babe/
    _VALID_URL = r'https?://(?:www\.)?sexix\.net'

    def _real_extract(self, url):
        webpage = self._download_webpage(url, url)
        title = self._og_search_title(webpage, default=None) or self._html_search_regex(
            r'(?s)<title>(.*?)</title>', webpage, 'video title',
            default='video')
        thumbnail = self._search_regex(r'image: \'([^\']+)', webpage, 'thumbnail',  default=None)
        vid = self._search_regex(r'<iframe src="http://sexix.net/v.php\?u=([^"]+)', webpage, 'emb')
        embUrl = 'http://sexix.net/v.php?u=%s' % vid
        headers = {'Referer': url}
        webpage = self._download_webpage(embUrl, vid, headers=headers)

        jw_config = self._parse_json(
            self._search_regex(
                r'(?s)jwplayer\(([\'"])(?:(?!\1).)+\1\)\.setup\s*\((?P<options>.+?)\);',
                webpage, 'jw config', group='options'),
            '', transform_source=js_to_json)
        playlist_url = jw_config['playlist']
        webpage = self._download_webpage(playlist_url, vid, headers=headers)
        #<jwplayer:source file="http://porn96.xyz/?u=8pFvAZ3bC8jsfGLlJzaPUxZ%2BIL%2FLuJ8hSylcUIoCCQo%2FAyyZHVBvIS27YLs6U8UeKy6oYUwHCtJ6O0YFMAkOSg%3D%3D" type="mp4" label="480p"/>
        list = re.findall(r'file="(.+)"\s*type="(.+)"\s*label="([^"]+)p', webpage)
        formats = []
        for item in list:
            if item[0]!='':
                try:
                    formats.append({
                        'url': item[0],
                        'height': item[2],
                        'ext': item[1],
                    })
                except:
                    pass
        self._sort_formats(formats)

        return  ({
                'id': '',
                'title': title,
                'thumbnail': thumbnail,
                'formats': formats,
            })

