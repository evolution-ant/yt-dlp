# -*- coding: utf-8 -*-

import re
import json
from ..extractor.cbsnews import CBSNewsIE as old
from ..utils import (
    int_or_none
)
from ..extractor.common import InfoExtractor

class CBSNewsIE(old):
    def _real_extract(self, url):
        try:
            webpage = self._download_webpage(url, url)
            formats = []
            mobj = self._search_regex(r'data-cbsvideoui-options=\'([^\']+)', webpage, 'data', default=None)
            if mobj:
                data = json.loads(mobj)
                vid = data['state']['video']['id']
                title = data['state']['video']['title']
                medias = data['state']['video']['medias']
                thumbnail = data['state']['video']['image']['path']
                for key, media in list(medias.items()):
                    if media['url'].find('rtmp') != -1:
                        continue
                    elif media['url'].find('.mp4') != -1:
                        ext = 'mp4'
                    elif media['url'].find('.m3u') != -1:
                        ext = 'mp4'
                    else:
                        continue

                    bitrate = int_or_none(media['bitrate'],default=0)  if 'bitrate' in media else 0
                    height = 360
                    if key == 'tablet':
                        height = 480
                    elif key == 'mobile':
                        height = 360
                    formats.append({
                        'url': media['url'],
                        'tbr': bitrate,
                        'ext': ext,
                        'height': height
                    })
                return {
                    'id': vid,
                    'title': title,
                    'thumbnail': thumbnail,
                    'formats': formats,
                }
            else:
                raise
        except:
            try:
                return super(CBSNewsIE, self)._real_extract(url)
            except:
                ie = CBSNewsNormalVideoIE()
                ie.set_downloader(self._downloader)
                return ie._real_extract(url)


class CBSNewsNormalVideoIE(InfoExtractor):
    IE_NAME = 'cbsnews:NormalVideo'
    _VALID_URL = r'https?://(?:www\.)?cbsnews\.com/video/(?P<id>[^/?#]+)'

    # Live videos get deleted soon. See http://www.cbsnews.com/live/ for the latest examples
    _TEST = {
        'url': 'https://www.cbsnews.com/video/preparation-for-the-fourth-democratic-debate-underway/',
    }

    def _real_extract(self, url):
        webpage = self._download_webpage(url, url)
        json_ld_groups = re.findall(r'(?s)<script[^>]+type=(["\'])application/ld\+json\1[^>]*>(?P<json_ld>.+?)</script>', webpage)
        for group in json_ld_groups:
            data = self._json_ld(group[1], '', fatal=False)
            if data and 'url' in data:
                data['id'] = 'test'
                return data
