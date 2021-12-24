# coding: utf-8
from __future__ import unicode_literals

import re
from .common import InfoExtractor
from ..utils import (
    unsmuggle_url,
    remove_end,
)


class MapleIE(InfoExtractor):
    # http://maple.bilibili.to/293090
    # (?:video/av|anime/(?P<anime_id>\d+)/play#)
    _VALID_URL = r'https?://maple\.bilibili\.to/(?P<video_id>\d+)'

    _TESTS = [{
        'url': 'http://maple.bilibili.to/293090/',
        'md5': None,
        'info_dict': {
            'id': '293090',
            'display_id': '293090',
            'ext': 'mp4',
            'title': '韋馱天：東京奧運的故事 第1集',
            'description': '',
            'thumbnail': r're:http://.*\.jpg',
            'duration': None,
            'timestamp': 1404273600,
            'upload_date': '20140702',
            'view_count': None,
            'tags': "劇集, 日劇集"  # 可能为数组
        },
    }]

    @staticmethod
    def _match_html_tag_content(tag_info, webpage):
        video_categories_re = r'<a.*?'+tag_info+'.*?>(.*?)</a>'
        video_categories_res = re.findall(video_categories_re, webpage, re.S | re.M)
        return [value for value in video_categories_res]

    def _real_extract(self, url):
        url, smuggled_data = unsmuggle_url(url, {})
        video_id = re.match(self._VALID_URL, url).group('video_id')
        web_page = self._download_webpage(url, video_id)

        # 获取iframe地址
        video_key = re.findall(r'.push\(\'(.*?)_m3u8\'\)', web_page, re.S | re.M)[0]
        video_key = video_key+str("_m3u8")
        video_html_url = 'http://video.bilibili.to/m3u8/?w=600&h=445&url=%s' % video_key

        # 获取iframe网页内容
        headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Connection": "keep-alive",
            "Host": "video.bilibili.to",
            "Referer": "http://maple.bilibili.to/293090/",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36"
        }
        video_html_content = self._download_webpage(video_html_url, video_id, headers=headers)
        video_url = re.findall(r'setup\({.*?file:"(.*?)",.*?autostart', video_html_content, re.S | re.M)[0]

        title = remove_end(
            self._html_search_regex(
                r'(?s)<title>(.+?)</title>', web_page, 'title').strip(),
            ' - Mapple')

        video_categories = self._match_html_tag_content('rel="category tag"', web_page)

        video_tags = self._match_html_tag_content('rel="tag"', web_page)

        return {
            'id': video_id,
            'categories': video_categories,
            'tags': video_tags,
            'title': title,
            'description': self._og_search_description(web_page),
            'webpage_url': url,
            'duration': None,
            'view_count': None,
            'http_headers': {
                'Referer': video_html_url,
                'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36",
            },
            'formats': [{
                "url": video_url
            }]
        }
