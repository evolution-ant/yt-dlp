# -*- coding: utf-8 -*-


from ..extractor.cbs import CBSBaseIE
# import sys
# reload(sys)
# sys.setdefaultencoding('utf-8')


class CBSSportsIE(CBSBaseIE):
    #_VALID_URL = r'https?://(?:www\.)?cbssports\.com/video/player/[^/]+/(?P<id>\d+)'
    _VALID_URL = r'https?://(?:www\.)?cbssports\.com/[^/]+'

    _TESTS = [{
        'url': 'http://www.cbssports.com/video/player/videos/708337219968/0/ben-simmons-the-next-lebron?-not-so-fast',
        'info_dict': {
            'id': '708337219968',
            'ext': 'mp4',
            'title': 'Ben Simmons the next LeBron? Not so fast',
            'description': 'md5:854294f627921baba1f4b9a990d87197',
            'timestamp': 1466293740,
            'upload_date': '20160618',
            'uploader': 'CBSI-NEW',
        },
        'params': {
            # m3u8 download
            'skip_download': True,
        }
    },
    {
        'url': 'http://www.cbssports.com/college-football/news/alabama-makes-oc-hire-official-while-dipping-into-nfl-for-another-assistant/',
        'info_dict': {
            'id': '880068675547',
            'ext': 'mp4',
            'title': 'Alabama to hire Brian Daboll as offensive coordinator',
            'description': 'md5:854294f627921baba1f4b9a990d87197',
            'timestamp': 1466293740,
            'upload_date': '20160618',
            'uploader': 'CBSI-NEW',
        },
        'params': {
            # m3u8 download
            'skip_download': True,
        }
    }]

    def _extract_video_info(self, filter_query, video_id):
        return self._extract_feed_info('dJ5BDC', 'VxxJg8Ymh8sE', filter_query, video_id)

    def _real_extract(self, url):
        video_id = self._get_video_id(url)
        if not video_id:
            video_id = self._match_id(url)
        return self._extract_video_info('byId=%s' % video_id, video_id)

    def _get_video_id(self,url):
        response = self._request_webpage(url, 'get cbssports video id')
        body = response.read()
        videoId = self._search_regex(
                                r'pcid\%3D([\d]+)\%26',
                                body, 'get videoId', default='')
        return videoId

