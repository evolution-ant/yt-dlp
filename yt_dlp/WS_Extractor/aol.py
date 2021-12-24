# coding: utf-8


import re
import json
from ..extractor.common import InfoExtractor
from ..utils import (
    ExtractorError,
    int_or_none,
)
from ..extractor.aol import AolIE as OldAolIE


class AolIE(InfoExtractor):
    IE_NAME = 'on.aol.com'
    _VALID_URL = r'(?:aol-video:|https?://(?:(?:www|on)\.)?aol\.com/(?:[^/]+/)*(?:[^/?#&]+-)?)(?P<id>[^/?#&]+)'

    _TESTS = [{
        # video with 5min ID
        'url': 'http://on.aol.com/video/u-s--official-warns-of-largest-ever-irs-phone-scam-518167793?icid=OnHomepageC2Wide_MustSee_Img',
        'md5': '18ef68f48740e86ae94b98da815eec42',
        'info_dict': {
            'id': '518167793',
            'ext': 'mp4',
            'title': 'U.S. Official Warns Of \'Largest Ever\' IRS Phone Scam',
            'description': 'A major phone scam has cost thousands of taxpayers more than $1 million, with less than a month until income tax returns are due to the IRS.',
            'timestamp': 1395405060,
            'upload_date': '20140321',
            'uploader': 'Newsy Studio',
        },
        'params': {
            # m3u8 download
            'skip_download': True,
        }
    }, {
        # video with vidible ID
        'url': 'http://www.aol.com/video/view/netflix-is-raising-rates/5707d6b8e4b090497b04f706/',
        'info_dict': {
            'id': '5707d6b8e4b090497b04f706',
            'ext': 'mp4',
            'title': 'Netflix is Raising Rates',
            'description': 'Netflix is rewarding millions of it’s long-standing members with an increase in cost. Veuer’s Carly Figueroa has more.',
            'upload_date': '20160408',
            'timestamp': 1460123280,
            'uploader': 'Veuer',
        },
        'params': {
            # m3u8 download
            'skip_download': True,
        }
    }, {
        'url': 'http://on.aol.com/partners/abc-551438d309eab105804dbfe8/sneak-peek-was-haley-really-framed-570eaebee4b0448640a5c944',
        'only_matching': True,
    }, {
        'url': 'http://on.aol.com/shows/park-bench-shw518173474-559a1b9be4b0c3bfad3357a7?context=SH:SHW518173474:PL4327:1460619712763',
        'only_matching': True,
    }, {
        'url': 'http://on.aol.com/video/519442220',
        'only_matching': True,
    }, {
        'url': 'aol-video:5707d6b8e4b090497b04f706',
        'only_matching': True,
    }]

    def _real_extract(self, url):
        if OldAolIE.suitable(url):
            old = OldAolIE()
            old.set_downloader(self._downloader)
            try:
                result= old._real_extract(url)
                return result
            except:
                pass

        webPage = self._download_webpage(url, url)
        link = self._search_regex(r'<script src="//delivery.vidible.tv/jsonp/([^\"]+)?', webPage, 'play info')
        link = 'http://delivery.vidible.tv/jsonp/%s' % link
        webPage = self._download_webpage(link, link)
        str = self._search_regex(r'{"status"(.+)', webPage, 'play info')
        data = json.loads('{"status"' + str)
        if data['status']['code'] !='OK':
            raise
        id = data['bid']
        video = data['bid']['videos'][0]
        title = video['name']
        thumbnail = video['fullsizeThumbnail']
        videoUrls = video['videoUrls']
        formats = [{'url': video_url} for video_url in videoUrls]


        return {
            'id': id,
            'title': title,
            'thumbnail': thumbnail,
            'formats': formats,
        }
