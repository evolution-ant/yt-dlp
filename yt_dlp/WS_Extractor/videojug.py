# encoding: utf-8



import re
from ..utils import (
    js_to_json,
    determine_ext,
    urlencode_postdata
)
from ..extractor.common import InfoExtractor

class VideojugIE(InfoExtractor):
    # https://www.vjav.com/videos/6471/natural-production-plants-shit-female-flight-principle/?source=2108980576#
    _VALID_URL = r'https?://(?:www\.)?videojug\.com/(?:[^/]+/)*(?P<id>[^/?#&]+)'

    def _real_extract(self, url):
        video_id = self._match_id(url)
        webpage = self._download_webpage(url, video_id)
        # 其自己内嵌视频
        pid = self._search_regex(r'.*#pid=([^/?#&]+)', url, 'data_id', fatal=False)
        if pid:
            pattern = r'src="//(.*jsonp/pid=%s[^"]*)' % pid
        else:
            pattern = r'src="//(.*jsonp[^"]*)'
        js_url = self._search_regex(pattern, webpage, 'js_url', fatal=False)
        if js_url:
            js_url = 'http://' + js_url
            webpage = self._download_webpage(js_url, video_id)
            video_data = self._parse_json(self._search_regex(r'"videos":\[(.*?)\]},"playerTemplate"', webpage, 'json_str'),
                                          video_id, js_to_json)
            title = video_data['name']
            description = video_data['description']
            thumbnail = video_data['fullsizeThumbnail'] or video_data['thumbnail']
            formats = []
            for video_url in video_data['videoUrls']:
                formats.append({
                    'ext': determine_ext(video_url),
                    'url': video_url
                })

            return {
                'id': video_id,
                'title': title,
                'description': description,
                'thumbnail': thumbnail,
                'formats': formats
            }

        # YouTube视频
        video_url = self._search_regex(r'<iframe[^>]+src="(.*youtube[^"]+)', webpage, 'video_url', fatal=False)
        if video_url:
            return self.url_result(video_url)
        # data-video_id="WpBwacQFtXE"
        # http://www.videojug.com/how-to-do-a-great-golf-swing/
        data_video_id = self._search_regex(r'data-video_id="([^"]+)', webpage, 'video_id', fatal=False)
        if data_video_id:
            video_url = r'https://www.youtube.com/embed/%s' % data_video_id
            return self.url_result(video_url)

        # Facebook视频
        video_url = self._search_regex(r'<div class="fb-video" data-href="([^"]+)', webpage, 'video_url', fatal=False)
        if video_url:
            return self.url_result(video_url)

        # 另一类形式嵌入视频...http://www.videojug.com/3d-food-printer-lets-design-pancake-want/
        # src="https://videos-by.vemba.io/v2/placements/15541.js"></script></p>
        zone_id = self._search_regex(r'src="https://videos-by.vemba.io/v2/placements/(\d+).js"', webpage, 'zone_id', fatal=False)
        if zone_id:
            post_url = 'http://horusii.vemba.io/v1/data/zones/%s' % zone_id
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'
            }
            # 其不能为空方能做post解析
            post_data = urlencode_postdata({})
            video_data = self._download_json(post_url, zone_id, data=post_data, headers=headers)
            if video_data and video_data['playlist'] and isinstance(video_data['playlist'], list):
                video_info = video_data['playlist'][0]
                video_url = video_info['file']
                formats = [{
                    'ext': determine_ext(video_url),
                    'url': video_url
                }]
                return {
                    'id': video_info['id'],
                    'title': video_info['title'],
                    'description': video_info['description'],
                    'thumbnail': video_info['image'].replace('///', '//'),
                    'formats': formats
                }


        return super(VideojugIE, self)._real_extract(url)

# 一页有多个嵌入视频，以列表处之
class VideojugPlaylistIE(InfoExtractor):
    _VALID_URL = r'https?://(?:www\.)?videojug\.com/(?:[^/]+/)*(?P<id>[^/?#&]+)'

    @classmethod
    def suitable(cls, url):
        if not super(VideojugPlaylistIE, cls).suitable(url):
            return False

        import urllib.request, urllib.error, urllib.parse
        # 遍历页面内容看是否有多个视频
        webpage = urllib.request.urlopen(url).read()
        m = re.findall(r'src="//(.*jsonp[^"]*)', webpage)
        if len(m) == 0:
            m = re.findall(r'<iframe[^>]+src="(.*youtube[^"]+)', webpage)
        return len(m) > 1


    def _real_extract(self, url):
        video_id = self._match_id(url)
        webpage = self._download_webpage(url, video_id)
        # 其自己内嵌视频
        js_urls = re.findall(r'src="//(.*jsonp[^"]*)', webpage)
        if len(js_urls) != 0:
            playlist_id = video_id
            playlist_title = self._og_search_title(webpage)
            playlist_description = self._og_search_description(webpage)
            entries = []
            for js_url in js_urls:
                js_url = 'http://' + js_url
                webpage = self._download_webpage(js_url, video_id)
                video_data = self._parse_json(
                    self._search_regex(r'"videos":\[(.*?)\]},"playerTemplate"', webpage, 'json_str'),
                    video_id, js_to_json)
                title = video_data['name']
                description = video_data['description']
                thumbnail = video_data['fullsizeThumbnail'] or video_data['thumbnail']
                duration = int(video_data['metadata']['duration']) / 1000
                pid = self._search_regex(r'pid=([^/]+)', js_url, 'pid'),

                # 列表要显示，其title、duration及url为必须值
                entries.extend([{
                    'id': video_id,
                    # 必须
                    'title': title,
                    'description': description,
                    'thumbnail': thumbnail,
                    # 必须
                    'duration' : duration,
                    # 以锚点返回，仍然解析此页面
                    'url': url + '#pid=%s' % pid
                }])

            return self.playlist_result(entries, playlist_id, playlist_title, playlist_description)

        # YouTube视频
        video_urls = re.findall(r'<iframe[^>]+src="(.*youtube[^"]+)', webpage)
        if len(video_urls) != 0:
            playlist_id = video_id
            playlist_title = self._og_search_title(webpage)
            playlist_description = self._og_search_description(webpage)

            from .youtubeExternallinkSite import YoutubeExternallinkSiteIE
            x = YoutubeExternallinkSiteIE()
            x.set_downloader(self._downloader)
            ids = [self._search_regex(r'/([0-9A-Za-z_-]{11})', video_url, 'id') for video_url in video_urls]
            # 全部赛进去，它是乱序的，一个一个来
            entries = [ x.getEntriesByID([id])[0] for id in ids ]
            return self.playlist_result(entries, playlist_id, playlist_title, playlist_description)