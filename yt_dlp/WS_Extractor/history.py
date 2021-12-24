

from ..extractor.common import InfoExtractor
from ..utils import smuggle_url
from ..extractor.theplatform import ThePlatformIE
from ..compat import (
    compat_urllib_parse,
)
import re

class HistoryIE(InfoExtractor):
    _VALID_URL = r'https?://(?:www\.)?history\.com'

    _TESTS = [{
        'url': 'http://www.history.com/topics/valentines-day/history-of-valentines-day/videos/bet-you-didnt-know-valentines-day?m=528e394da93ae&s=undefined&f=1&free=false',
        'md5': '6fe632d033c92aa10b8d4a9be047a7c5',
        'info_dict': {
            'id': 'bLx5Dv5Aka1G',
            'ext': 'mp4',
            'title': "Bet You Didn't Know: Valentine's Day",
            'description': 'md5:7b57ea4829b391995b405fa60bd7b5f7',
        },
        'add_ie': ['ThePlatform'],
    }]

    def _real_extract(self, url):
        webpage = self._download_webpage(url, url)
        try:
            mobj = re.search(r'history\.com/(?:[^/]+/)+(?P<id>[^/]+?)(?:$|[?#])', url)
            if mobj:
                video_id = mobj.group('id')
                pattern = r'data-href="[^"]*/%s"[^>]+data-release-url="([^"]+)"' % video_id
            else:
                pattern = r'_videoPlayer.play\(\'([^\']+)'
            try:
                video_url = self._search_regex(pattern, webpage, 'video url')
            except:
                pattern = r'_videoPlayer.play\(\'([^\']+)'
                video_url = self._search_regex(pattern, webpage, 'video url')
            redirectUrl = smuggle_url(video_url, {'sig': {'key': 'crazyjava', 'secret': 's3cr3t'}})
        except:
            thePlatformUrl = self._search_regex(r'data-mediaurl="([^"]+)|var media_url\s*=\s*\'([^\']*)|data-media-url="([^"]+)', webpage, 'ThePlatformUrl')
            #https://signature.video.aetndigital.com/?callback=&url=http%3A%2F%2Flink.theplatform.com%2Fs%2Fxc6n8B%2Fmedia%2Fb61lmysmBC6_&_=1456305232473
            data = compat_urllib_parse.urlencode({'url': thePlatformUrl.replace('https', 'http'),
                                                  'callback': 'jQuery220012530179592710228_1456305232472',
                                                  '_': '1456305232473'})

            html = self._download_webpage('https://signature.video.aetndigital.com/?' + data, 'signature')
            sig = self._html_search_regex(r'auth"\s*:\s*"([^"]*)', html, 'auth')

            data = compat_urllib_parse.urlencode({'sig': sig, 'assetTypes': 'medium_video_ak', 'formats': 'm3u,mpeg4',
                                           'format': 'SMIL', 'embedded': 'true', 'tracking': 'true'})
            redirectUrl = thePlatformUrl + '?' + data
            redirectUrl = smuggle_url(redirectUrl, {'sig': {'key': 'crazyjava', 'secret': sig}})
        if redirectUrl.find('theplatform') == -1:
            return self.url_result(redirectUrl)
        else:
            ie = ThePlatformIE(self._downloader)
            try:
                result = ie.extract(redirectUrl)
            except:
                str = r'(?:link|player)\.theplatform\.com/[sp]/(?P<provider_id>[^/]+)/(?P<media>media/)(?P<id>[^/\?&]+)'
                #str = self._search_regex(r'theplatform', redirectUrl, 'x')
                mobj = re.search(str, redirectUrl)
                provider_id = mobj.group('provider_id')
                video_id = mobj.group('id')
                formats = ie._extract_theplatform_smil(redirectUrl, video_id)
                result = ie._download_theplatform_metadata('%s/media/%s' % (provider_id, video_id), video_id)
                result.update({
                    'id': video_id,
                    'formats': formats[0],
                })
           # return result
            return {
                'id': result['id'],
                'title': result['title'],
                'description': result['description'],
                'thumbnail': result['thumbnail'] if 'thumbnail' in result else '',
                'duration': result['duration'],
                'url': result['formats'][0]['url'],
                'ext': result['formats'][0]['ext']
            }