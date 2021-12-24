

import re
from ..compat import (
    compat_urllib_request,
)
from ..utils import parse_duration

from ..extractor.common import InfoExtractor
from ..utils import (
    str_to_int,
)
class porntubeIE(InfoExtractor):
    _VALID_URL = r'https?://(?:www\.)?porntube.com'
    #http://www.porntube.com/videos/hot-maid-emy-reyes-sucks-fucks-awesome-dick_7213015
    def _real_extract(self, url):
        webpage = self._download_webpage(url, url)
        duration = self._search_regex(r'<meta\s*itemprop="duration"\s*content="([^\"]+)', webpage, 'duration', default=None)
        if duration:
            duration = parse_duration(duration)
        title = self._search_regex(r'<title>(.*)\|.*</title>', webpage, 'title', default='no title')
        thumbnail = self._search_regex(r'<meta\s*itemprop="thumbnailUrl"\s*content="([^\"]+)', webpage, 'thumbnail', default=None)
        video_id = self._search_regex(r'</i><button id=".*?data-id="([^\"]*)', webpage, 'video_id')
        play_url = "http://tkn.porntube.com/%s/desktop/240+360+480+720+1080" % video_id
        req = compat_urllib_request.Request(play_url, play_url)
        req.add_header('Origin', ' www.porntube.com')
        jsondata = self._download_json(req, url)
        formats = [{
            'url': jsondata[key]['token'],
            'quality': key,
        } for key in jsondata]
        self._check_formats(formats, 'xxx')
        self._sort_formats(formats)

        return {
            'id': video_id,
            'title': title,
            'thumbnail': thumbnail,
            'duration': duration,
            'formats': formats,
        }
