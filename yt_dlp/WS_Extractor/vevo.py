

import re
import json
from ..compat import (
    compat_urlparse,
)

from ..extractor.common import (
    InfoExtractor
)

from ..extractor.vevo import (
    VevoBaseIE,
    VevoPlaylistIE as old,
    VevoIE
)

from ..utilsEX import download_webPage_by_PYCURL, url_result

class VevolyIE(InfoExtractor):
    _VALID_URL = r'https?://(?:www\.)?vevo\.ly'

    def _real_extract(self, url):
        webpage = self._download_webpage(url, url)
        vevo_id = self._search_regex(r' href\s*=\s*"vevo://video/([^"]+)', webpage, 'ID')
        return self.url_result('vevo:%s' % vevo_id, ie='Vevo')

class VevoPlaylistBaseIE(old):

    def _real_extract(self, url):
        try:
            mobj = re.match(self._VALID_URL, url)
            playlist_id = mobj.group('id')

            webpage = self._download_webpage(url, playlist_id)
            cookies = self._get_cookies(url)
            token = cookies.get('ApiToken').value if cookies and 'ApiToken' in cookies else None
            if not token:
                # tokenUrl = 'https://www.vevo.com/%s' % self._search_regex(r'nucleus/(browser\.\w+?\.js)', webpage, '')
                # webpage1 = self._download_webpage(tokenUrl, tokenUrl, '')
                # token = self._search_regex('token:{key:"([^"]+)', webpage1, '')
                token = "SPupX1tvqFEopQ1YS6SS"
                data = {"client_id":token,"grant_type":"urn:vevo:params:oauth:grant-type:anonymous"}
                data = self._download_json('https://accounts.vevo.com/token', '', data=json.dumps(data).encode('utf-8'), headers={
                    'Content-Type': 'application/json',
                    'Origin': 'https://www.vevo.com',
                    'x-vevo-country': 'US'
                })
                token = data['access_token']
            qs = compat_urlparse.parse_qs(compat_urlparse.urlparse(url).query)
            index = qs.get('index', [None])[0]


            # if index:
            #     video_id = self._search_regex(
            #         r'<meta[^>]+content=(["\'])vevo://video/(?P<id>.+?)\1[^>]*>',
            #         webpage, 'video id', default=None, group='id')
            #     if video_id:
            #         return self.url_result('vevo:%s' % video_id, VevoIE.ie_key())
            #     else:  # get real video_url
            #         pn = r'<link\s*itemprop="url"\s*href="(?P<url>[^\"]+)'
            #         # <link itemprop="url" href="http://www.vevo.com/watch/jon-pardi/Dirt-On-My-Boots-(Lyric-Video)/USUV71601455"
            #         video_url = self._search_regex(pn, webpage, 'video url', default=None, group='url')
            #         if video_url:
            #             return self.url_result(video_url, VevoIE.ie_key())

            data = {"query": "query MorePlaylistVideos($ids: [String]!, $offset: Int, $limit: Int) {\n  playlists(ids: $ids) {\n    id\n    videos(limit: $limit, offset: $offset) {\n      items {\n        id\n        index\n        isrc\n        videoData {\n          id\n          likes\n          liked\n          basicMetaV3 {\n            youTubeId\n            monetizable\n            isrc\n            title\n            urlSafeTitle\n            startDate\n            endDate\n            releaseDate\n            copyright\n            copyrightYear\n            genres\n            contentProviders\n            shortUrl\n            thumbnailUrl\n            duration\n            hasLyrics\n            explicit\n            allowEmbed\n            allowMobile\n            categories\n            credits {\n              role\n              name\n              __typename\n            }\n            artists {\n              id\n              basicMeta {\n                urlSafeName\n                role\n                name\n                thumbnailUrl\n                __typename\n              }\n              __typename\n            }\n            errorCode\n            __typename\n          }\n          __typename\n        }\n        __typename\n      }\n      offset\n      limit\n      __typename\n    }\n    __typename\n  }\n}\n",
                    "variables":{
                        "ids":["%s" % playlist_id],
                        "offset":1,
                        "limit":200
                    },
                    "operationName":"MorePlaylistVideos"
            }
            data = json.dumps(data)
            # data = '''{"query":"query MorePlaylistVideos($ids: [String]!, $offset: Int, $limit: Int) {\n  playlists(ids: $ids) {\n    id\n    videos(limit: $limit, offset: $offset) {\n      items {\n        id\n        index\n        isrc\n        videoData {\n          id\n          likes\n          liked\n          basicMetaV3 {\n            youTubeId\n            monetizable\n            isrc\n            title\n            urlSafeTitle\n            startDate\n            endDate\n            releaseDate\n            copyright\n            copyrightYear\n            genres\n            contentProviders\n            shortUrl\n            thumbnailUrl\n            duration\n            hasLyrics\n            explicit\n            allowEmbed\n            allowMobile\n            categories\n            credits {\n              role\n              name\n              __typename\n            }\n            artists {\n              id\n              basicMeta {\n                urlSafeName\n                role\n                name\n                thumbnailUrl\n                __typename\n              }\n              __typename\n            }\n            errorCode\n            __typename\n          }\n          __typename\n        }\n        __typename\n      }\n      offset\n      limit\n      __typename\n    }\n    __typename\n  }\n}\n","variables":{"ids":["%s"],"offset":0,"limit":200},"operationName":"MorePlaylistVideos"}''' % playlist_id
            data = self._download_json('https://veil.vevoprd.com/graphql', '', data=data.encode('utf-8'), headers={
                'Authorization': 'Bearer %s' % token,
                'Content-Type': 'application/json',
                'Origin': 'https://www.vevo.com',
            })

            items = data['data']['playlists'][0]['videos']['items']
            entries = []
            for item in items:
                id = item['isrc']
                basicMetaV3 = item['videoData']['basicMetaV3']
                duration = basicMetaV3['duration'] / 1000
                shortUrl = basicMetaV3['shortUrl']
                title = basicMetaV3['title']
                entries.append(url_result(shortUrl, VevolyIE.ie_key(), id, title, duration))
                if index and item['index'] == int(index):
                     return url_result(shortUrl, VevolyIE.ie_key(), id, title, duration)
            # data = self._extract_json(webpage, playlist_id)
            # data = data[u'apollo']['data']
            # items = data['$%s.videos({"limit":20,"offset":0})' % playlist_id]['items']
            # items = [ data.get('$%s.basicMetaV3' %self._search_regex(r'\((.+)\)', item['id'], '', fatal=False), None) for item in items if self._search_regex(r'\((.+)\)', item.get('id', ''), '', fatal=False, default=None)]


            # entries = [
            #     url_result(item['shortUrl'], VevoIE.ie_key(), item['isrc'], item['title'], item['duration'])
            #     for item in items ]

            return self.playlist_result(
                entries, playlist_id,
                self._search_regex(r'<div class="title-text">([^<]+)?', webpage, ''))
        except:
            import traceback
            print(traceback.format_exc())
            return super(VevoPlaylistBaseIE, self)._real_extract(url)

class VevoPlaylistIE(VevoPlaylistBaseIE):
    def _real_extract(self, url):
        url = url.rsplit('?index')[0]
        return super(VevoPlaylistIE, self)._real_extract(url)

class VevoExIE(VevoIE):
    def _download_webpage(self, url_or_request, video_id, note=None, errnote=None, fatal=True, tries=1, timeout=5, encoding=None, data=None, headers={}, query={}):
        try:
            return super(VevoExIE, self)._download_webpage(url_or_request, video_id, note, errnote, fatal, tries, timeout, encoding, data, headers, query)
        except:
            return download_webPage_by_PYCURL(self, url_or_request, timeout, data, headers, query)