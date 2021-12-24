# coding: utf-8

import re
from ..extractor.nbc import NBCIE as Old

from ..utils import (
    smuggle_url,
    update_url_query,
    int_or_none,
)

class NBCIE(Old):

    def _real_extract(self, url):
        try:
            result = super(NBCIE, self)._real_extract(url)
            if not result or not result.get('formats', None):
                raise
            return result
        except:
            permalink, video_id = re.match(self._VALID_URL, url).groups()
            webpage = self._download_webpage(url, url).replace('https://schema.org', 'http://schema.org')
            video_data = self._search_json_ld(webpage, '', fatal=False)
            query = {
                'mbr': 'true',
                'manifest': 'm3u',
            }
            theplatform_url = smuggle_url(update_url_query(
                'http://link.theplatform.com/s/NnzsPC/media/guid/2410887629/' + video_id,
                query), {'force_smil_url': True})
            return {
                '_type': 'url_transparent',
                'id': video_id,
                'title': video_data.get('title'),
                'url': theplatform_url,
                'description': video_data.get('description'),
                'keywords': video_data.get('keywords'),
                'season_number': int_or_none(video_data.get('seasonNumber')),
                'episode_number': int_or_none(video_data.get('episodeNumber')),
                'series': video_data.get('showName'),
                'ie_key': 'ThePlatform',
            }
