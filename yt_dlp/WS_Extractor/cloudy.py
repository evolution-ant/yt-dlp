# coding: utf-8


from ..extractor.common import InfoExtractor
from ..extractor.cloudy import CloudyIE as Old
from ..utils import (
    str_to_int,
    unified_strdate,
)


class CloudyIE(Old):

    def _real_extract(self, url):
        try:
            result = super(CloudyIE, self)._real_extract(url)
            if not result or not result.get('formats', None):
                raise
            return result
        except:
            video_id = self._match_id(url)

            webpage = self._download_webpage(
                'http://www.cloudy.ec/embed.php?id=%s&playerPage=1&autoplay=1' % video_id, video_id)

            info = self._parse_html5_media_entries(url, webpage, video_id)[0]

            webpage = self._download_webpage(
                'https://www.cloudy.ec/v/%s' % video_id, video_id, fatal=False)

            if webpage:
                info.update({
                    'title': self._search_regex(
                        r'<h\d[^>]*>([^<]+)<', webpage, 'title'),
                    'upload_date': unified_strdate(self._search_regex(
                        r'>Published at (\d{4}-\d{1,2}-\d{1,2})', webpage,
                        'upload date', fatal=False)),
                    'view_count': str_to_int(self._search_regex(
                        r'([\d,.]+) views<', webpage, 'view count', fatal=False)),
                })

            if not info.get('title'):
                info['title'] = video_id
            formats = info['formats']
            self._check_formats(formats, video_id)
            info['formats'] = formats
            info['id'] = video_id

            return info
