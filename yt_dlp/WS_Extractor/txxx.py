#encoding: utf-8


from ..extractor.common import InfoExtractor

class TxxxIE(InfoExtractor):
    #http://www.txxx.com/videos/2631606/stepmom-seduces-teen-babe/
    _VALID_URL = r'https?://(?:(?:www|m)\.)?txxx\.com/videos'

    def _real_extract(self, url):
        webpage = self._download_webpage(url, url)

        title = self._html_search_regex(r'var video_title="([^"]+)', webpage, 'video title', fatal=False) or self._og_search_title(
            webpage, default=None) or self._html_search_regex(
            r'(?s)<title>(.*?)</title>', webpage, 'video title',
            default='video')
        thumbnail = self._search_regex(r'image: \'([^\']+)', webpage, 'thumbnail',  default=None)
        try:
            # 直找其下载地址
            video_url = self._search_regex(r'<a href="([^"]+)" id="download_link"|<a class="btn btn-default js--watch" href="([^"]+)"', webpage, 'video_url')
        except Exception as e:
            return super(TxxxIE, self)._real_extract(url)

        if video_url and 'mp4' in video_url:
            formats = [{
                'url': video_url,
                'ext': 'mp4',
            }]

        self._sort_formats(formats)
        return ({
            'id': '',
            'title': title,
            'thumbnail': thumbnail,
            'formats': formats,
        })


