# coding: utf-8


import re

from ..extractor.tumblr import TumblrIE as TumblrBase
from ..utils import int_or_none


class TumblrIE(TumblrBase):
    _VALID_URL = r'https?://(?P<blog_name>[^/?#&]+)\.tumblr\.com/(?:post|video)/(?:[^/]+/)*(?P<id>[0-9]+)(?:$|[/?#])'

    def _real_extract(self, url):
        try:
            return super(TumblrIE, self)._real_extract(url)
        except:
            pass

        video_id = self._match_id(url)
        webpage = self._download_webpage(url, video_id)
        video_url = self._search_regex(
            r'"hdUrl":"([^"]+)"', webpage,
            'video_url', fatal=False)
        if not video_url:
            video_url = self._search_regex(
                r'<source[^>]+src=(["\'])(?P<url>.+?)\1', webpage,
                'video_url', default=None, group='url')
        video_url = video_url.replace('\/', '/')

        formats = [{
            'url': video_url,
            'ext': 'mp4',
        }]

        # The only place where you can get a title, it's not complete,
        # but searching in other places doesn't work for all videos
        video_title = self._html_search_regex(
            r'(?s)<title>(?P<title>.*?)(?: \| Tumblr)?</title>',
            webpage, 'title')

        thumbnail = self._og_search_thumbnail(webpage, default=None)
        if not thumbnail:
            thumbnail = self._html_search_regex(
                r"poster='([^']+)", webpage, 'thumbnail', fatal=False)
        return {
            'id': video_id,
            'title': video_title,
            'description': self._og_search_description(webpage, default=None),
            'thumbnail': thumbnail,
            'formats': formats,
        }
