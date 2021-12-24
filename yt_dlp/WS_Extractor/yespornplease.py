# encoding: utf-8


from ..extractor.common import InfoExtractor

class YespornpleaseIE(InfoExtractor):
    _VALID_URL = r'https?://(?:www\.)?yespornplease\.com/view/(?P<id>\d+)'

    def _real_extract(self, url):
        # http://yespornplease.com/view/119147578
        video_id = self._match_id(url)
        webpage = self._download_webpage(url, video_id)
        frame_url = self._search_regex(r'<iframe[^>]+src="([^"]+)"', webpage, 'frame_url')
        # 其所引用vshare内容
        if frame_url and 'vshare.' in frame_url:
            if '//' in frame_url and not frame_url.startswith('http'):
                frame_url = 'https:' + frame_url
            return self.url_result(frame_url)
        # 若是flash视频，求其flv地址
        elif 'flashvars' in webpage and 'video_url' in webpage:
            video_url = self._search_regex(r'video_url=([^&]+)', webpage, 'frame_url')
            if '//' in video_url and not video_url.startswith('http'):
                video_url = 'https:' + video_url
            # 标题&缩略图
            title = self._og_search_title(webpage)
            title = title.replace(' watch online for free', '')
            thumbnail = self._og_search_thumbnail(webpage)
            description = self._og_search_description(webpage)

            return {
                'id': video_id,
                'title': title,
                'description': description,
                'thumbnail': thumbnail,
                'url': video_url,
            }