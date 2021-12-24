# coding: utf-8

import re
from ..extractor.nuvid import NuvidIE as oldIE
from ..utils import (
    parse_duration,
)
import json

class NuvidIE(oldIE):
    def _real_extract(self, url):
        try:
            result = super(NuvidIE, self)._real_extract(url)
            if not result or not result.get('formats', None):
                raise
            return result
        except:
            video_id = self._match_id(url)

            page_url = 'http://m.nuvid.com/video/%s' % video_id
            webpage = self._download_webpage(
                page_url, video_id, 'Downloading video page')
            # When dwnld_speed exists and has a value larger than the MP4 file's
            # bitrate, Nuvid returns the MP4 URL
            # It's unit is 100bytes/millisecond, see mobile-nuvid-min.js for the algorithm
            self._set_cookie('nuvid.com', 'dwnld_speed', '10.0')
            mp4_webpage = self._download_webpage(
                page_url, video_id, 'Downloading video page for MP4 format')
            mobj = re.search(r'data-video_hash="([^"]+).+data-hash_time="([^"]+).+data-video_id="([^"]+).+', mp4_webpage)
            #data-video_hash="3a3948b6e9083e9b9a0a18db2322b682" data-hash_time="1519699034" data-video_id="1818419" >
            video_url = 'http://m.nuvid.com/player_config?video_hash=%s&hash_time=%s&video_id=%s' % mobj.groups()
            data = self._download_json(video_url, video_id)
            mp4_video_url = data['source']
            formats = [{
                'url': mp4_video_url,
            }]


            title = self._html_search_regex(
                [r'<span title="([^"]+)">',
                 r'<div class="thumb-holder video">\s*<h5[^>]*>([^<]+)</h5>',
                 r'<span[^>]+class="title_thumb">([^<]+)</span>'], webpage, 'title').strip()
            thumbnails = [
                {
                    'url': thumb_url,
                } for thumb_url in re.findall(r'<img src="([^"]+)" alt="" />', webpage)
            ]
            thumbnail = thumbnails[0]['url'] if thumbnails else None
            if not thumbnail:
                thumbnail = self._search_regex(r'<video.+?poster="([^"]+)', mp4_webpage, '', fatal=False)
            duration = parse_duration(self._html_search_regex(
                [r'<i class="fa fa-clock-o"></i>\s*(\d{2}:\d{2})',
                 r'<span[^>]+class="view_time">([^<]+)</span>'], webpage, 'duration', fatal=False))

            return {
                'id': video_id,
                'title': title,
                'thumbnails': thumbnails,
                'thumbnail': thumbnail,
                'duration': duration,
                'age_limit': 18,
                'formats': formats,
            }