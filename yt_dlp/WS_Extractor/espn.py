

from ..extractor.espn import (
    ESPNIE,
    ESPNArticleIE as ESPNArticleIEBase
)

class ESPNArticleIE(ESPNArticleIEBase):

    def _real_extract(self, url):
        try:
            return super(ESPNArticleIE, self)._real_extract(url)
        except:
            pass

        video_id = self._match_id(url)

        webpage = self._download_webpage(url, video_id)

        video_id = self._search_regex(
            # <a href="http://www.espn.com/video/clip?id=12302153"><b>Watch</b></a>
            r'<a\s+href="http\://www\.espn\.com/video/clip\?id=(?P<id>\d+)".*Watch.*</a>',
            webpage, 'video id', group='id')

        return self.url_result(
            'http://espn.go.com/video/clip?id=%s' % video_id, ESPNIE.ie_key())
