# encoding: utf-8


from ..extractor.common import InfoExtractor

class ThiruttuvcdIE(InfoExtractor):
    # http://www.thiruttuvcd.biz/movie/2017/11/julie-2-2017-tamil-movie-watch-online/
    _VALID_URL = r'https?://(?:www\.)?thiruttuvcd\.\w+/'

    def _real_extract(self, url):
        webpage = self._download_webpage(url, 'video_id')
        if 'openload' in webpage:
            openload_url = self._search_regex(r'<iframe[^>]+?src="(https://openload[^"]+)', webpage, 'openload_url', fatal=False)
            if not openload_url:
                openload_url = self._search_regex(r'(https://openload[^\r\n]+)', webpage, 'openload_url', fatal=False)
            if openload_url:
                return self.url_result(openload_url)

        return super(ThiruttuvcdIE, self)._real_extract(url)