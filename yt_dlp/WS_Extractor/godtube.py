
from ..extractor.godtube import GodTubeIE as OldGodTubeIE

class GodTubeIE(OldGodTubeIE):

    def _download_xml(self, url_or_request, video_id,
                      note='Downloading XML', errnote='Unable to download XML',
                      transform_source=None, fatal=True, encoding=None,
                      data=None, headers={}, query={}):

        headers = {
            'Cookie': 'cf_clearance=da3be0f3bf2ec90e828c58fb21d5e41d78e80535-1515650775-57600',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36'
        }
        return super(GodTubeIE, self)._download_xml(url_or_request, video_id, headers=headers)

    def _real_extract(self, url):
        try:
            return super(GodTubeIE, self)._real_extract(url)
        except:
            pass

        video_id = self._match_id(url)
        headers = {
            'Cookie': 'cf_clearance=da3be0f3bf2ec90e828c58fb21d5e41d78e80535-1515650775-57600',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36'
        }
        webpage = self._download_webpage(url, video_id, headers=headers)
        link = self._search_regex(r'file:\s*\'([^\']+)\'', webpage, 'link', default=None)
        if not link:
            link = self._search_regex(r'div class="fb-video" data-href="([^"]+)', webpage, 'link', default=None)

        return self.url_result(link)