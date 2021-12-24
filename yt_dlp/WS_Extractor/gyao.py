

from ..extractor.common import InfoExtractor

class GyaoIE(InfoExtractor):
    IE_NAME = 'gyao.yahoo.co.jp'
    _VALID_URL = r'https?://gyao.yahoo.co.jp'
    _TEST = {
        'url': 'http://gyao.yahoo.co.jp/player/00597/v12448/v1000000000000003690/?list_id=1654725',
    }

    def extractFromBCPlayer(self, title, video_id, webpage):
        player_url = 'https://s.yimg.jp/images/gyao/bc-player/hls/player.gyao.js?0004'
        space_id = self._html_search_regex(r'data-spaceid=([^\']+)', webpage, 'space_id')
        service_id = self._html_search_regex(r'data-serviceid="([^"]+)', webpage, 'data-serviceid')
        video_uni_id = self._html_search_regex(r'data-vid=([^\']+)', webpage, 'data-vid')
        webpage = self._download_webpage(player_url, player_url)
        account = self._html_search_regex(r'videoElement\.setAttribute\("data-account","([^"]+)', webpage, 'account')
        index_min_js_url = self._html_search_regex(r'BC_PLAYER_URL="([^"]+)', webpage, 'index_min_js_url')
        webpage = self._download_webpage(index_min_js_url, index_min_js_url)
        app_id = self._html_search_regex(r',m\s*=\s*"(.+)";b.checkVisible=', webpage,
                                         'index_min_js_url')  # m="dj0zaiZpPXFuMjk4YTJZcU4wUCZzPWNvbnN1bWVyc2VjcmV0Jng9YjQ-";
        url2 = 'https://gyao.yahooapis.jp/rio/getVideo'
        query = {
            'appid': app_id,
            'output': 'json',
            'space_id': space_id,
            'domain': 'gyao.yahoo.co.jp',
            'start': '1',
            'results': '1',
            'service_id': service_id,  # 'gy
            'video_uni_id': video_uni_id,
            'device_type': '1100',
            'delivery_type': '2,6',
            'premiumgyao_limited_contents_flag': '1',
            'callback': 'jsonp_1499686946866_5949'
        }
        webpage = self._download_webpage(url2, url2, query=query)
        deliveryId = self._search_regex(r'"deliveryId":([^\"]+),"deliveryType":6', webpage, 'deliveryId')
        url3 = 'https://edge.api.brightcove.com/playback/v1/accounts/%s/videos/%s' % (account, deliveryId)
        program_info = self._download_json(
            url3, video_id,
            headers={
            'Accept': 'application/json;pk=BCpkADawqM3UI7LN8vy-xZ-f0EG6Xuch56dMQLuXX-VST0YZFntoAghnCk04EswbZ56BAX20HkAWwYw5M4YbCcSRWgDNcGlbKIUOlw2DNT15MyrRvG2n2y3WAoy1IWfTAlhMgZLc2pa3rZPbjCB23KBFaGZ1ezN5bgDFpOCQ4Rmb8MAx3BSPVrsprtQ'})
        formats = [{
                       'ext': 'm3u8',
                       'url': program_info['sources'][0]['src'],
                   }]
        return {
            'id': video_id,
            'title': title,
            'formats': formats,
            'duration': program_info['duration'],
            'thumbnail': program_info['thumbnail']
        }

    def _real_extract(self, url):
        webpage = self._download_webpage(url, url)
        title = self._html_search_regex(r'<title>(.+)</title>', webpage, 'title')
        video_id = self._search_regex(r'video_uni_id=(.+?)"', webpage, 'video_id')
        try:
            return self.extractFromGYAOPlayer(title, video_id, webpage)
        except:
            return self.extractFromBCPlayer(title, video_id, webpage)


    def extractFromGYAOPlayer(self, title, video_id, webpage):
        try:
            player_url = self._html_search_regex(r'src="(.+)\/player.js.*?">', webpage,
                                                 'player_url') + '/player.js'
        except:
            player_url = 'http://i.yimg.jp/images/gyao/player/js/player.js'
        webpage = self._download_webpage(player_url, player_url)
        appID = self._html_search_regex(r'APPID\s*:\s*"(.+?)"', webpage, 'appID')
        appKey = self._html_search_regex(r'GATE_WAY_APP_KEY\s*:\s*"(.+?)"', webpage, 'GATE_WAY_APP_KEY')
        video_url = 'https://gw.gyao.yahoo.co.jp/v1/hls/%s/variant.m3u8?device_type=1100&' \
                    'delivery_type=2&min_bandwidth=246&appkey=%s&appid=%s' % (video_id, appKey, appID)
        return {
            'id': video_id,
            '_type': 'video',
            'title': title,
            'url': video_url,
            'ext': 'mp4',
        }


'''
http://gyao.yahoo.co.jp/player/00597/v12416/v1000000000000003678/?list_id=1654725
http://i.yimg.jp/images/gyao/bc-player/player.gyao.js?0002
http://players.brightcove.net/4235717419001/H17bGYqS_default/index.min.js
https://vod01-gyao.c.yimg.jp/4235717419001/4235717419001_4971788934001_4971736491001.mpd

GET https://edge.api.brightcove.com/playback/v1/accounts/4235717419001/videos/4971736491001 HTTP/1.1
Accept: application/json;pk=BCpkADawqM2QSOsdGmTVDZ4_Y10f_FHAfpcCmG99ZZC4tNNQclHy44k7klaWnFhZLQvByouh2G0bkPY7xOC5sYPx-Ich7wVBIHCSLxsH-r0eps_GbXxXpMa96eHTJEb_G404XOUt-hpkg21S
Referer: http://gyao.yahoo.co.jp/player/00597/v12416/v1000000000000003678/?list_id=1654725
Accept-Language: zh-Hans-CN,zh-Hans;q=0.8,en-US;q=0.5,en;q=0.3
Origin: http://gyao.yahoo.co.jp
Accept-Encoding: gzip, deflate
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36 Edge/12.10240
Host: edge.api.brightcove.com
Connection: Keep-Alive
Cache-Control: no-cache


HTTP/1.1 200 OK
Content-Type: application/json; charset=UTF-8
Content-Length: 1736
Connection: keep-alive
access-control-allow-origin: *
access-control-expose-headers: x-cache,via,bcov-debug-cache-stats,bcov-instance,x-amz-cf-id
BCOV-instance: i-58dfacc4, ca69ff2, 2016-07-07 07:59:18.679Z
Cache-Control: max-age=0, no-cache, no-store
Date: Thu, 07 Jul 2016 07:59:18 GMT
Server: Jetty(9.2.z-SNAPSHOT)
Strict-Transport-Security: max-age=600
X-Originating-URL: https://edge-elb.api.brightcove.com/playback/v1/accounts/4235717419001/videos/4971736491001
X-Cache: Miss from cloudfront
Via: 1.1 2bb00e225b1b6c3d82913e7c9db706c5.cloudfront.net (CloudFront)
X-Amz-Cf-Id: DYQa8nLJhIDMmKfN6ZyJkp9iz11XD2B1ygSkELoh1g6EYbKLxWQf8Q==
'''