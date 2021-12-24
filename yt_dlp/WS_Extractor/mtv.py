# encoding: utf-8



from ..extractor.mtv import MTVServicesInfoExtractor
from ..extractor import gen_extractor_classes
from ..utils import url_basename

class MTVPlaylistIE(MTVServicesInfoExtractor):
    IE_NAME = 'mtv:playlist'
    _VALID_URL = r'https?://(?:www\.)?mtv\.com/(?:video-playlists)/(?P<id>[^/?#.]+)'

    def _real_extract(self, url):
        title = url_basename(url)
        webpage = self._download_webpage(url, title)
        mgid = self._extract_mgid(webpage)
        # 曲线救下国吧
        embed_url = 'http://media.mtvnservices.com/embed/mgid:arc:video:mtv.com:%s' % mgid
        return {
            '_type': 'url',
            'url': embed_url,
            'title': title,
            'ie_key': 'MTVServicesEmbedded',
        }


class MTVNewsIE(MTVServicesInfoExtractor):
    IE_NAME = 'mtv:news'
    # http://www.mtv.com/news/3023803/siesta-key-new-series/
    _VALID_URL = r'https?://(?:www\.)?mtv\.com/(?:news)/\d+/(?P<id>[^/?#.]+)'
    _FEED_URL = 'http://www.mtv.com/feeds/mrss/'

    def _real_extract(self, url):
        video_id = self._match_id(url)
        webpage = self._download_webpage(url, video_id)
        title = self._og_search_title(webpage)
        thumbnail = self._html_search_meta('thumbnail', webpage)

        # 寻找嵌入视频
        if (webpage.find('"inline-oembed') != -1):
            ie_name = self._search_regex(r'"inline-oembed (\w+)"', webpage, 'ie_name')
            ie_url = self._search_regex(r'<div class="inline-oembed %s"><a\s+href="(.+?)"' % (ie_name), webpage, 'ie_url')
            # 找内置IE
            ie_key = ''
            for ie in gen_extractor_classes():
                if (ie.ie_key().lower() == ie_name.lower()):
                    ie_key = ie.ie_key()
                    break

            if (ie_name and ie_url):
                return {
                    '_type': 'url',
                    'url': ie_url,
                    'thumbnail': thumbnail,
                    'title': title,
                    'ie_key': ie_key,
                }
            else:
                 return super(MTVNewsIE, self)._real_extract(url)
        # MTVNPlayer，找mgid，下载m3u8
        elif (webpage.find('MTVNPlayer') != -1 and webpage.find('data-contenturi') != -1):
            # mgid = data-contenturi="mgid:arc:video:mtv.com:88e78665-6c34-4e3c-a1f9-7f07bd3bc0a5">
            mgid = self._search_regex(r'data-contenturi="(.+?)"', webpage, 'mgid')
            if (mgid):
                _srv_url = 'https://media-utils.mtvnservices.com/services/MediaGenerator/%s?format=json&acceptMethods=hls' % mgid
                webpage = self._download_webpage(_srv_url, 'mgid')
                # 不用json了，直接正则解析吧
                if (webpage and webpage.find('m3u8') != -1 and webpage.find('src') != -1):
                    video_url = self._search_regex(r'"src":.*"(.+?)"', webpage, '_m3u8_url')
                    formats = [{
                        'url': video_url,
                        'protocol': 'm3u8'
                    }]
                    return {
                        'id': video_id,
                        'title': title,
                        'thumbnail': thumbnail,
                        'formats': formats,
                    }
                else:
                    return super(MTVNewsIE, self)._real_extract(url)
            else:
                return super(MTVNewsIE, self)._real_extract(url)

        else:
            return super(MTVNewsIE, self)._real_extract(url)