

import re

from ..extractor.common import (
    InfoExtractor,
)


class StupidVideosIE(InfoExtractor):
    IE_NAME = 'stupidvideos.com'
    _VALID_URL = r'https?://(?:www\.)?stupidvideos\.com'

    def _real_extract(self, url):
        html = self._download_webpage(url, url)
        id = self._search_regex(r'#([0-9]+)$', url, url, default=None)
        if not id:
            id = self._search_regex(r'var\s+videoID\s*=\s*\'(\d+)', html, 'id')
        if id:
            if len(id) < 6:
                id = '0' + id
            play_url = 'http://videos.stupidvideos.com/2/00/%s/%s/%s/%s.flv' % (id[0:2], id[2:4], id[4:6], id)
            title = self._html_search_meta('og:title', html)
            thumbail = self._html_search_meta('og:image', html)

            return {
                'id': 'xxx',
                'title': title,
                'formats': [{'url': play_url}],
                'thumbnail': thumbail,
            }
        else:
            raise 'not support'