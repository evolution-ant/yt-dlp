# encoding: utf-8


from ..extractor.common import InfoExtractor
import re

class Movies123IE(InfoExtractor):
    _VALID_URL = r'https?://(?:www\.)?123movies\.\w{2,4}/'

    def _real_extract(self, url):
        # https://123movies.film/film/the-handmaid-s-tale-season-1-2017.74909/watching.html?episode_id=93254
        if '123movies.film' in url:
            return self._extract_film(url)

        # http://123movies.net/watch/GpDJMmgG-shooter-season-2/episode-8.html/watching.html
        # 以net结尾的，它嵌入的url代码经base64编码，存于代码中，解之
        if '123movies.net' in url:
            return self._extract_net(url)

        # http://123movies.sc/watch-clouds-of-sils-maria-2014-123movies.html/watching.html
        # 此网站引用openload网站视频，解析出来，丢给它
        if '123movies.sc' in url or '123movies.ag' in url:
            return self._extract_sc(url)

        # 判断是否跳转
        try:
            wb = self._request_webpage(url, 'video_id')
            if wb and wb.code == 200 and wb.url != url:
                return self.url_result(wb.url)
        except:
            pass

        # https://123movies.co/movie/baby-driver-free112/?watching=HNGgShnEZp/watching.html
        webpage = self._download_webpage(url, 'video_id')
        # 需要再中转
        if '<meta http-equiv="refresh"' in webpage:
            real_url = self._search_regex(r'url=([^"]+)', webpage, 'real_url')
            return self.url_result(real_url)
        if '<div class="ds_seriesplay dsclear">' in webpage:
            real_url = self._search_regex(r'<div class="ds_seriesplay dsclear">\s*<a href="([^"]+)', webpage, 'real_url')
            return self.url_result(real_url)

        # 内嵌url http://123movies.md/movies/the-mummy-2017/
        frame_url = self._search_regex(r'<div class="embed">\s*<iframe[^>]+src="([^"]+)"', webpage, 'frame_url', fatal=False)
        if frame_url:
            return self.url_result(frame_url)

        # 内嵌播放器，putstream
        frame_url = self._search_regex(r'<div class="videoPlayer">\s*<iframe[^>]+src="([^"]+)"', webpage, 'frame_url', fatal=False)
        if frame_url:
            return self.url_result(frame_url)

        # 其它类型frame
        frame_url = self._search_regex(r'<iframe[^>]+src="([^"]+)"', webpage, 'frame_url', fatal=False)
        if frame_url:
            return self.url_result(frame_url)

        return super(Movies123IE, self)._real_extract(url)


    def _extract_film(self, url):
        webpage = self._download_webpage(url, 'video_id')
        # 此类视频，为m3u8格式
        video_id = self._search_regex(r'load_player\(\'([^\']+)?', webpage, 'video_id', fatal=False)
        # 需走m3u8解析
        if video_id:
            title = self._search_regex(r',\s+name:\s+"([^"]*)', webpage, 'title', fatal=False)
            if not title:
                title = self._og_search_title(webpage)
            title = title.replace('Watch The ', '')
            src_url = 'https://123movies.vg/ajax/v2_get_sources?id=%s' % video_id
            media_data = self._download_json(src_url, 'media_data')
            if media_data:
                play_url = media_data.get('value', '')
                if play_url:
                    if play_url.index('//') == 0:
                        play_url = 'https:' + play_url
                    if not media_data.get('embed', False) and not media_data.get('ads', False):
                        headers = {
                            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36',
                            'Referer': url
                        }
                        webpage = self._download_webpage(play_url, 'playlist', headers=headers)
                        if webpage:
                            webpage = webpage.replace('\\/', '/')
                            video_url = self._search_regex(r'(https://[^"]*)', webpage, 'video_url')
                            if video_url and 'm3u8' in video_url:
                                formats = [{
                                    'format_id': '-'.join([_f for _f in [None, 'meta'] if _f]),
                                    'url': video_url,
                                    'ext': 'mp4',
                                    'protocol': 'm3u8',
                                }]

                                return {
                                    'id': video_id,
                                    'title': title,
                                    'formats': formats
                                }
                    elif media_data.get('embed', False):
                        return self.url_result(play_url)

        return super(Movies123IE, self)._real_extract(url)


    def _extract_net(self, url):
        webpage = self._download_webpage(url, 'video_id')
        video_id = ''
        title = self._og_search_title(webpage)
        description = self._og_search_description(webpage)
        thumbnail = self._og_search_thumbnail(webpage)

        import base64
        base64_str = self._search_regex(r'Base64.decode\("([^"]+)"\)', webpage, 'base64_str', fatal=False)
        frame_str = base64.decodestring(base64_str)
        frame_url = self._search_regex(r'<iframe[^>]+src="([^"]+)"', frame_str, 'frame_url', fatal=False)
        if not frame_url:
            return super(Movies123IE, self)._real_extract(url)

        webpage = self._download_webpage(frame_url, 'video_id')
        video_url = self._search_regex(r'<source[^>]+src="([^"]+)"', webpage, 'base64_str', fatal=False)
        if not video_url:
            return super(Movies123IE, self)._real_extract(url)

        return {
            'id': video_id,
            'title': title,
            'thumbnail': thumbnail,
            'description': description,
            'url': video_url,
            'ext': 'mp4',
            'http_headers': {
                # 验证发现，下载需如此设其头，清除User-Agent，加入Referer
                'User-Agent': '',
                'Referer': frame_url,
            },
        }


    def _extract_sc(self, url):
        # 抠取所需参数
        webpage = self._download_webpage(url, 'video_id')
        # 求可用视频组合
        pattern = r"ip_build_player\(([^,]+),'([^\']*)','([^\']*)',([^\)]*)"
        m = re.search(pattern, webpage)
        if not m:
            return super(Movies123IE, self)._real_extract(url)

        # 此请求网址，可得一s值，并以其为请求key，再求得内嵌网址
        post_url = 'http://123movies.sc/ip.file/swf/plugins/ipplugins.php'
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'
        }
        post_data = {
            'ipplugins': 1,
            'ip_film': m.group(1),
            'ip_server': m.group(2),
            'ip_name': m.group(3),
            'fix': m.group(4)
        }

        play_data = self._download_json(post_url, 'video_id', headers=headers, query=post_data)
        if not play_data or not 's' in play_data or 'error' in play_data['p']:
            return super(Movies123IE, self)._real_extract(url)

        # 取出其s值，以求所引用之视频网址，验证其引用openload.co视频内网，但直转至openload解析失败，故此再拿其信息
        key_s = play_data['s']
        post_url = 'http://123movies.sc/ip.file/swf/ipplayer/ipplayer.php?u=%s&s=%s&n=%s' % (key_s, m.group(2), m.group(4))
        media_info = self._download_json(post_url, 'media_info')
        if not media_info or not 'data' in media_info:
            return super(Movies123IE, self)._real_extract(url)

        video_url = media_info['data']
        if not 'https:' in video_url and '//' in video_url:
            video_url = 'https:' + video_url
        if not 'openload' in video_url:
            return super(Movies123IE, self)._real_extract(url)

        return self.url_result(video_url)