#encoding: utf-8


import re
import json

from ..extractor.common import InfoExtractor
from ..compat import compat_urlparse

class BoxIE(InfoExtractor):
    # https://www.bing.com/videos/search?q=youtube+supermarket+flowers&ru=%2fsearch%3fq%3dyoutube%2bsupermarket%2bflowers%26FORM%3dQSRE3&view=detail&mid=616B8E40E9346549CDBB616B8E40E9346549CDBB&&mmscn=vwrc&FORM=VDRVRV
    _VALID_URL = r'https?://m.box.com/shared_item/'

    def _real_extract(self, url):
        if re.search(r'info', url):
            url = re.search(r'(.+)/info', url).group(1)
        webpage = self._download_webpage(url, url)

        self._search_regex(r'(<audio|<video)', webpage, '')

        title = self._search_regex(r'<h1 class="ellipsis">(.+)</h1>', webpage, '', fatal= False) or 'title'

        video_url = self._html_search_regex(r'href="(/file.+)"\s+class="toolbar-btn "', webpage, '')
        video_url = compat_urlparse.urljoin(url, video_url)
        info_url = self._html_search_regex(r'href="(/shared_item.+/info)"', webpage, '')
        info_url = compat_urlparse.urljoin(url, info_url)
        # <a href="/shared_item/https%3A%2F%2Fapp.box.com%2Fs%2Fwux87cq6ffg4l7jqimibc4w45xb7vhut/view/143381736033/info" class="menu-btn">
        # url = '%s/info' % url
        webpage = self._download_webpage(info_url, info_url)

        ext = self._search_regex(r'>Type<\/th>[\s\S]+">(.+?)</td>', webpage, '')
        formats = [{
                       'url': video_url,
                        'ext': ext,
        }]

        return {
            'id': id,
            'title': title,
            'formats': formats,
        }