

import re

from ..extractor.common import (
    InfoExtractor
)

from ..extractor.crackle import (
    CrackleIE as Old
)

class CrackleIE(InfoExtractor):
    _VALID_URL = r'https?://(?:www\.)?crackle\.com'

    def _try_extractAs_Channel(self, url):
        if not url.endswith('/'):
           url = url + '/'
        channel_Name = self._search_regex(r'crackle\.com/([^/]+)', url, 'channelID')
        query_url = 'https://web-api-us.crackle.com/Service.svc/playback/channel/%s/US?format=json' % channel_Name
        data = self._download_json(query_url, query_url)
        PlaylistID = data['Result']['PlaylistId']
        MediaId = data['Result']['MediaId']
        url = 'http://www.crackle.com/playlist/%s/%s' % (PlaylistID, MediaId)
        ie = Old()
        ie.set_downloader(self._downloader)
        return ie._real_extract(url)

    def _real_extract(self, url):
        if Old.suitable(url):
            try:
                ie = Old()
                ie.set_downloader(self._downloader)
                return ie._real_extract(url)
            except:
                return self._try_extractAs_Channel(url)
        else:
            return self._try_extractAs_Channel(url)

