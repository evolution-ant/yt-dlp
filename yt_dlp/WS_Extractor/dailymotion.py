


import re
import json
import itertools
import threading

from ..extractor.common import (
    InfoExtractor,
)

from ..utils import (
    smuggle_url,
    determine_ext,
    int_or_none,
    sanitized_Request,
    try_get,
    parse_filesize,
    unsmuggle_url,
    std_headers,
    RegexNotFoundError,
    ExtractorError,
    clean_html,
    urlencode_postdata
)

from ..compat import (
    compat_str,
    compat_urlparse,
    compat_HTTPError,
    compat_urllib_parse_unquote_plus,

)

from ..extractor.dailymotion import (
    DailymotionBaseInfoExtractor,
    DailymotionUserIE as OldDailymotionUserIE,
    DailymotionPlaylistIE
)

def url_result(url, ie=None, video_id=None, video_title=None, video_duration = None):
    video_info = {'_type': 'url',
                  'url': url,
                  'ie_key': ie}
    if video_id is not None:
        video_info['id'] = video_id
    if video_title is not None:
        video_info['title'] = video_title
    if video_duration is not None:
        video_info['duration'] = video_duration
    return video_info

def _extract_entries(self, id):

    video_ids = set()
    processed_urls = set()
    for pagenum in itertools.count(1):
        page_url = self._PAGE_TEMPLATE % (id, pagenum)
        webpage, urlh = self._download_webpage_handle_no_ff(
            page_url, id, 'Downloading page %s' % pagenum)
        if urlh.geturl() in processed_urls:
            self.report_warning('Stopped at duplicated page %s, which is the same as %s' % (
                page_url, urlh.geturl()), id)
            break

        processed_urls.add(urlh.geturl())

        p = r'data-xid="(.+?)"><div class="badge badge--duration">([\s\S]+?)</div><img class="preview"\s+alt="([^"]+)'
        for item in re.findall(p, webpage):
            video_id = item[0]
            try:
                duration = re.findall(r'[^\s]+', item[1])[0]
            except:
                duration = '02:00'
            try:
                title = clean_html(item[2]).strip()
            except:
                title = 'unkown'
            if video_id not in video_ids:
                yield url_result('http://www.dailymotion.com/video/%s' % video_id, 'dailymotion', video_id=video_id, video_title=title, video_duration=duration)
                video_ids.add(video_id)

        if re.search(self._MORE_PAGES_INDICATOR, webpage) is None:
            break

def _real_extract(self, url):
    mobj = re.match(self._VALID_URL, url)
    playlist_id = mobj.group('id')
    webpage = self._download_webpage(url, playlist_id)
    title = self._search_regex(r'<title>([^>]+)</title>', webpage, 'title', default=None, fatal=False) or self._og_search_title(webpage)

    return {
        '_type': 'playlist',
        'id': playlist_id,
        'title': title,
        'entries': self._extract_entries(playlist_id),
    }

DailymotionPlaylistIE._extract_entries = _extract_entries
DailymotionPlaylistIE._real_extract = _real_extract

class DailymotionUserIE(OldDailymotionUserIE):
    _VALID_URL = r'https?://(?:www\.)?dailymotion\.[a-z]{2,3}/(?!(?:embed|swf|#|video|playlist|search)/)(?:(?:old/)?user/)?(?P<user>[^/]+)'

    def _real_extract(self, url):
        if url.find('/topic/') > -1:
            ie = DailymotionTopicIE()
            ie.set_downloader(self._downloader)
            return ie._real_extract(url)
        else:
            return super(DailymotionUserIE, self)._real_extract(url)

class DailymotionGraphqlAPIIE(DailymotionBaseInfoExtractor):
    PAGE_MAX_COUNT = 12

    def getToken(self, url):
        webpage = self._download_webpage(url, url, headers= {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36',})
        str = self._search_regex(r'__PLAYER_CONFIG__\s*=\s*(.+);\s', webpage, '')

        data = self._parse_json(str, '')
        if data['context']['access_token']:
            return 'Bearer %s' % data['context']['access_token']
        else:
            apiData = data['context']['api']
            data = { 'client_id' : apiData['client_id'],
                     'client_secret': apiData['client_secret'],
                    'grant_type':'client_credentials',
                     'visitor_id':'',
                     'traffic_segment': ''
                    }
            tokenUrl = apiData['auth_url']
            headers = {
                'Origin': 'http://www.dailymotion.com',
                'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36',
                'Content-Type': 'application/x-www-form-urlencoded',
                #Accept: */*
                'Referer': url
            }
            jsonData = self._download_json(tokenUrl, tokenUrl, headers= headers, data= urlencode_postdata(data))
            return 'Bearer %s' % jsonData['access_token']

    def getHeader(self, url):

        result = {
                'Content-Type': 'application/json',
                'Referer': url,
                'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36',
                'Cookie': '',
                'Origin': 'https://www.dailymotion.com'
        }
        Authorization = self.getToken(url)
        if Authorization:
            result['Authorization'] = Authorization
        return result

    def getEntries(self, id, headers, entries):
        pass

    def getAllEntries(self, headers):
        threadList = []
        results = []
        for i in range(1, self.PAGE_MAX_COUNT):
            try:
                entries = []
                results.append(entries)
                t = threading.Thread(target=self.getEntries, args=(i*5, headers, entries))
                threadList.append(t)
                t.setDaemon(True)
                t.start()
            except:
                pass
            for t in threadList:
                t.join()

        return [item for result in results for item in result if item]



class DailymotionTopicIE(DailymotionGraphqlAPIIE):
    IE_NAME = 'dailymotion:Topic'
    _VALID_URL = r'https?://(?:www\.)?dailymotion\.com/(.+)/topic/'

    payload = {
        "query": "fragment VIDEO_BASE_FRAGMENT on Video {\n  xid\n  title\n  viewCount\n  duration\n  createdAt\n  __typename\n}\n\nfragment VIDEO_SMALL_FRAGMENT on Video {\n  ...VIDEO_BASE_FRAGMENT\n  thumbURLx120: thumbnailURL(size: \"x120\")\n  thumbURLx240: thumbnailURL(size: \"x240\")\n  thumbURLx360: thumbnailURL(size: \"x360\")\n  thumbURLx480: thumbnailURL(size: \"x480\")\n  __typename\n}\n\nfragment METADATA_FRAGMENT on Neon {\n  web(uri: $uri) {\n    author\n    description\n    title\n    metadatas {\n      attributes {\n        name\n        content\n        __typename\n      }\n      __typename\n    }\n    language {\n      codeAlpha2\n      __typename\n    }\n    country {\n      codeAlpha2\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n\nfragment LOCALIZATION_FRAGMENT on Localization {\n  me {\n    country {\n      codeAlpha2\n      name\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n\nquery TOPIC_QUERY($topic_xid: String!, $sort: String, $page: Int!, $uri: String!) {\n  localization {\n    ...LOCALIZATION_FRAGMENT\n    __typename\n  }\n  views {\n    neon {\n      ...METADATA_FRAGMENT\n      __typename\n    }\n    __typename\n  }\n  topic(xid: $topic_xid) {\n    xid\n    name\n    isFollowed\n    coverURL(size: \"x532\")\n    stats {\n      followers {\n        total\n        __typename\n      }\n      videos {\n        total\n        __typename\n      }\n      __typename\n    }\n    topic_most_videos: videos(sort: $sort, page: $page, first: 30) {\n      pageInfo {\n        hasNextPage\n        nextPage\n        __typename\n      }\n      edges {\n        node {\n          ...VIDEO_SMALL_FRAGMENT\n          channel {\n            xid\n            name\n            displayName\n            logoURL(size: \"x60\")\n            __typename\n          }\n          __typename\n        }\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n}\n",
        "variables": {
            "topic_xid": "x2zhdx",
            "sort": "recent",
            "page": 1,
            "uri": "/us/topic/x2zhdx"
        },
        "operationName": "TOPIC_QUERY"
    }

    def getEntries(self, id, headers, entries):
        payload_copy = self.payload.copy()
        for i in range(5):
            payload_copy['variables']['page'] = id + i
            result = self._download_json('https://graphql.api.dailymotion.com/', payload_copy['variables']['topic_xid'],
                    data = json.dumps(payload_copy).encode('utf-8'),
                    headers = headers)
            videos = result['data']['topic']['topic_most_videos']

            for edge in videos['edges']:
                try:
                    edge = edge['node']
                    entry = url_result('http://www.dailymotion.com/video/%s' % edge['xid'], 'dailymotion',
                                          video_id= edge['xid'], video_title=edge['title'], video_duration=edge['duration'])
                    entries.append(entry)
                except:
                    pass


    def _real_extract(self, url):
        webpage = self._download_webpage(url, url, '')
        title = self._og_search_title(webpage) or 'title'

        mobj =  re.search(r'\.com(/.+/topic/(.+))/*', url)
        self.payload['variables']['topic_xid'] = mobj.group(2)
        self.payload['variables']['uri'] = mobj.group(1)
        headers = self.getHeader(url)
        entries = self.getAllEntries(headers)

        return {
            '_type': 'playlist',
            'id': 'title',
            'title': title,
            'entries': entries
        }



class DailymotionSearchIE(DailymotionGraphqlAPIIE):
    IE_NAME = 'dailymotion:search'
    _VALID_URL = r'https?://(?:www\.)?dailymotion\.com/search'
    PAGE_MAX_COUNT = 50

    payload = {
        "query": "fragment METADATA_FRAGMENT on Neon {\n  web(uri: $uri) {\n    author\n    description\n    title\n    metadatas {\n      attributes {\n        name\n        content\n        __typename\n      }\n      __typename\n    }\n    language {\n      codeAlpha2\n      __typename\n    }\n    country {\n      codeAlpha2\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n\nfragment LOCALIZATION_FRAGMENT on Localization {\n  me {\n    country {\n      codeAlpha2\n      name\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n\nquery SEARCH_QUERY($query: String!, $pageVideo: Int, $pageLive: Int, $pageChannel: Int, $pageCollection: Int, $limitVideo: Int, $limitLive: Int, $limitChannel: Int, $limitCollection: Int, $uri: String!) {\n  views {\n    neon {\n      ...METADATA_FRAGMENT\n      __typename\n    }\n    __typename\n  }\n  localization {\n    ...LOCALIZATION_FRAGMENT\n    __typename\n  }\n  search {\n    lives(query: $query, first: $limitLive, page: $pageLive) {\n      pageInfo {\n        hasNextPage\n        nextPage\n        __typename\n      }\n      edges {\n        node {\n          xid\n          title\n          thumbURLx240: thumbnailURL(size: \"x240\")\n          thumbURLx360: thumbnailURL(size: \"x360\")\n          __typename\n        }\n        __typename\n      }\n      __typename\n    }\n    videos(query: $query, first: $limitVideo, page: $pageVideo) {\n      pageInfo {\n        hasNextPage\n        nextPage\n        __typename\n      }\n      edges {\n        node {\n          xid\n          title\n          channel {\n            displayName\n            __typename\n          }\n          duration\n          thumbURLx240: thumbnailURL(size: \"x240\")\n          thumbURLx360: thumbnailURL(size: \"x360\")\n          __typename\n        }\n        __typename\n      }\n      __typename\n    }\n    channels(query: $query, first: $limitChannel, page: $pageChannel) {\n      pageInfo {\n        hasNextPage\n        nextPage\n        __typename\n      }\n      edges {\n        node {\n          xid\n          name\n          description\n          displayName\n          accountType\n          logoURL(size: \"x60\")\n          __typename\n        }\n        __typename\n      }\n      __typename\n    }\n    playlists: collections(query: $query, first: $limitCollection, page: $pageCollection) {\n      pageInfo {\n        hasNextPage\n        nextPage\n        __typename\n      }\n      edges {\n        node {\n          xid\n          name\n          channel {\n            displayName\n            __typename\n          }\n          description\n          thumbURLx240: thumbnailURL(size: \"x240\")\n          thumbURLx480: thumbnailURL(size: \"x480\")\n          stats {\n            videos {\n              total\n              __typename\n            }\n            __typename\n          }\n          __typename\n        }\n        __typename\n      }\n      __typename\n    }\n    topics(query: $query, first: 5, page: 1) {\n      pageInfo {\n        hasNextPage\n        nextPage\n        __typename\n      }\n      edges {\n        node {\n          id\n          xid\n          name\n          isFollowed\n          __typename\n        }\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n}\n",
        "variables": {
            "query": "The Love Boat Season",
            "pageVideo": 1,
            "pageLive": 1,
            "pageChannel": 1,
            "pageCollection": 1,
            "limitVideo": 20,
            "limitLive": 20,
            "limitChannel": 20,
            "limitCollection": 20,
            "uri": "/search/The%20Love%20Boat%20Season/videos"
        },
        "operationName": "SEARCH_QUERY"
    }

    def getEntries(self, id, headers, entries):
        payload_copy = self.payload.copy()

        for i in range(5):
            payload_copy['variables']['pageVideo'] = id + i
            result = self._download_json('https://graphql.api.dailymotion.com/', '',
                    data = json.dumps(payload_copy).encode('utf-8'),
                    headers = headers)
            videos = result['data']['search']['videos']

            for edge in videos['edges']:
                try:
                    edge = edge['node']
                    entry = url_result('http://www.dailymotion.com/video/%s' % edge['xid'], 'dailymotion',
                                          video_id= edge['xid'], video_title=edge['title'], video_duration=edge['duration'])
                    entries.append(entry)
                except:
                    pass


    def _real_extract(self, url):
        if not url.endswith('/videos'):
            if not url.endswith('/'):
                url = url + '/'
            url = url + 'videos'
        mobj =  re.search(r'/search/(.+)/', url)
        key = mobj.group(1)

        self.payload['variables']['query'] = compat_urllib_parse_unquote_plus(key)
        self.payload['variables']['uri'] = '/search/%s/videos' % key
        headers = self.getHeader(url)
        entries = self.getAllEntries(headers)
        return {
            '_type': 'playlist',
            'id': 'title',
            'title': 'All video results for %s' % compat_urllib_parse_unquote_plus(key),
            'entries': entries
        }