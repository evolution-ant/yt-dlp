# coding=utf-8

import os, io
import sys
import json
import traceback

from yt_dlp.utilsEX import (
    debug,
#    injectYoutubeDL_make_HTTPS_handler
)
from .. import YoutubeDL

from .youtube import YoutubeIE
from .savefrom import SaveFromIE
from .CommonHTML5 import CommonHTML5IE

class YoutubeDLPatch(YoutubeDL):
    #智能判断如果是SSL错误就设置忽略SSL验证重新建立链路
    # def urlopen(self, req):
    #     try:
    #         return super(YoutubeDLPatch, self).urlopen(req)
    #     except Exception as ex:
    #         if sys.platform != 'win32':
    #             if not self.params.get('usingUrllib3', False) and str(ex).find('SSL:') > -1:
    #                 debug("usingUrllib3..........")
    #                 injectYoutubeDL_make_HTTPS_handler()
    #                 self.params['usingUrllib3'] = True
    #                 self._setup_opener()
    #                 return super(YoutubeDLPatch, self).urlopen(req)
    #             else:
    #                 raise ex
    #         else:
    #             raise ex

    def print_debug_header(self):
        return super(YoutubeDLPatch, self).print_debug_header()
        #return
        from ..utils import write_string
        from ..version import __version__
        import locale

        from ..compat import compat_str
        if not self.params.get('verbose'):
            return

        stdout_encoding = getattr(
            sys.stdout, 'encoding', 'missing (%s)' % type(sys.stdout).__name__)

        try:
            write_string(stdout_encoding, encoding=None)
        except:
           errmsg = 'Failed to write encoding string %r' % stdout_encoding
           try:
               sys.stdout.write(errmsg)
           except:
               pass

        self._write_string('[debug] yt-dlp version ' + __version__ + '\n')

        proxy_map = {}
        for handler in self._opener.handlers:
            if hasattr(handler, 'proxies'):
                proxy_map.update(handler.proxies)
        self._write_string('[debug] Proxy map: ' + compat_str(proxy_map) + '\n')

        if self.params.get('call_home', False):
            ipaddr = self.urlopen('https://yt-dl.org/ip').read().decode('utf-8')
            self._write_string('[debug] Public IP address: %s\n' % ipaddr)


class YoutubeDLPatch4Single(YoutubeDLPatch):
    def insert_info_extractor(self, ie):
        self._ies.insert(1, ie)
        if not isinstance(ie, type):
            self._ies_instances[ie.ie_key()] = ie
            ie.set_downloader(self)

    def remove_info_extract(self, ieClass):
        self._ies = [ie for ie in self._ies if ie.ie_key != ieClass.ie_key]
        self._ies_instances[ieClass.ie_key] = None

    def add_default_info_extractors(self):
        from .youtube import YoutubeIE
        from .savefrom import SaveFromIE
        from .cbssports import CBSSportsIE
        from .lynda import LyndaIE
        from .crunchyroll import CrunchyrollIE
        from .Fc2 import FC2IE, FC2EmbedIE
        from .vimeo import VimeoBlogIE
        from .vimeo import VimeoExIE
        from .videobash import VideoBashIE
        from .stupidvideos import StupidVideosIE
        from .history import HistoryIE
        from .ebaumsworld import EbaumsWorldIE
        from .imdb import ImdbIE, ImbdbVideoplayerIE
        from .porntube import porntubeIE
        from .cbsNews import CBSNewsIE, CBSNewsNormalVideoIE
        from .bbc import (BBCCoUkIE, BBCCoUkArticleIE, BBCIE)
        from .godtube import GodTubeIE
        from .aol import AolIE
        from .espn import ESPNArticleIE
        from .ispot import IspotIE
        from .ehow import EHowIE
        from .yahoo import YahooIE
        from .bilibili import BiliBiliIE
        from .howcast import HowcastIE
        from .pbs import Watch_Thirteen_IE
        from .veoh import VeohIE
        from .txxx import TxxxIE
        from .yourpornSex import YourpornSexIE
        from .camwhores import CamwhoresIE
        from .porneq import porneqIE
        from .hqcollect import hqcollectTVIE
        from .vjav import VjavIE
        from .sexixnet import sexixnetIE
        from .ancensored import ancensoredIE
        from .hclips import HclipsIE
        from .thumbzilla import thumbzillaIE
        from .toggle import ToggleIE
        from .gomovies import GoMoviesIE, GoMovies_fm_IE
        from .gyao import GyaoIE
        from .moresisek import MoresisekIE
        from .funimation import FunimationIE
        from .viki import VikiIE, VikiChannelIE
        from .jibjab import jibjabIE
        from .mtv import MTVNewsIE, MTVPlaylistIE
        from .kissanime import KissanimeIE
        from .cloudy import CloudyIE
        from .vevo import VevoPlaylistBaseIE, VevolyIE, VevoExIE
        from .crackle import CrackleIE
        from .xpau import XpauIE
        from .rtbf import RtbfIE
        from .nbc import NBCIE
        from .discovery import DiscoveryIE
        from .bing import BingIE
        from .superMan import SuperManIE
        from .movies123 import Movies123IE
        from .vshare import VShareIE, VShare_euIE
        from .yespornplease import YespornpleaseIE
        from .putstream import PutStreamIE
        from .odnoklassniki import OdnoklassnikiIE
        from .avgle import avgle_IE
        from .udemy import UdemyExIE
        from .fox import FoxIE
        from .box import BoxIE
        from .googledriver import GoogleDriverIE
        from .onedrive import OneDriverIE
        from .dropbox import DropboxExIE
        from . import openload

        from .kaltura import KalturaIE
        from .powtoon import PowtoonIE
        from .thiruttuvcd import ThiruttuvcdIE
        from .hudl import HudlIE
        from .kshow123 import KShow123IE
        from .streamango import StreamangoIE
        from .videojug import VideojugIE
        from .mycanal import MycanalIE
        from .tumblr import TumblrIE
        from .niconico import NiconicoIE

        from . import arte
        from .nuvid import NuvidIE
        from .yesvideo import YesvideoIE
        from .kizzboy import KizzboyIE


        super(YoutubeDLPatch4Single, self).add_default_info_extractors()
        self.insert_info_extractor(YoutubeIE())
        self.insert_info_extractor(LyndaIE())
        self.insert_info_extractor(SaveFromIE())
        self.insert_info_extractor(CBSSportsIE())
        self.insert_info_extractor(CrunchyrollIE())
        self.insert_info_extractor(FC2IE())
        self.insert_info_extractor(FC2EmbedIE())
        self.insert_info_extractor(VimeoBlogIE())
        self.insert_info_extractor(VimeoExIE())
        self.insert_info_extractor(VideoBashIE())
        self.insert_info_extractor(StupidVideosIE())
        self.insert_info_extractor(HistoryIE())
        self.insert_info_extractor(EbaumsWorldIE())
        self.insert_info_extractor(ImbdbVideoplayerIE())
        self.insert_info_extractor(ImdbIE())
        self.insert_info_extractor(CBSNewsIE())
        self.insert_info_extractor(BBCCoUkIE())
        self.insert_info_extractor(BBCCoUkArticleIE())
        self.insert_info_extractor(BBCIE())
        self.insert_info_extractor(GodTubeIE())
        self.insert_info_extractor(AolIE())
        self.insert_info_extractor(YahooIE())
        self.insert_info_extractor(CommonHTML5IE())
        self.insert_info_extractor(ESPNArticleIE())
        self.insert_info_extractor(IspotIE())
        self.insert_info_extractor(EHowIE())
        self.insert_info_extractor(BiliBiliIE())
        self.insert_info_extractor(porntubeIE())
        self.insert_info_extractor(HowcastIE())
        self.insert_info_extractor(Watch_Thirteen_IE())
        self.insert_info_extractor(VeohIE())

        self.insert_info_extractor(TxxxIE())
        self.insert_info_extractor(YourpornSexIE())
        self.insert_info_extractor(CamwhoresIE())
        self.insert_info_extractor(porneqIE())
        self.insert_info_extractor(hqcollectTVIE())
        self.insert_info_extractor(VjavIE())
        self.insert_info_extractor(sexixnetIE())
        self.insert_info_extractor(ancensoredIE())
        self.insert_info_extractor(HclipsIE())
        self.insert_info_extractor(thumbzillaIE())
        self.insert_info_extractor(ToggleIE())
        self.insert_info_extractor(GoMoviesIE())
        self.insert_info_extractor(GoMovies_fm_IE())

        #20170711
        self.insert_info_extractor(GyaoIE())
        self.insert_info_extractor(MoresisekIE())
        #20170718
        self.insert_info_extractor(FunimationIE())
        self.insert_info_extractor(VikiIE())
        self.insert_info_extractor(VikiChannelIE())
        self.insert_info_extractor(jibjabIE())
        #20170721
        self.insert_info_extractor(MTVNewsIE())
        self.insert_info_extractor(MTVPlaylistIE())
        #
        self.insert_info_extractor(KissanimeIE())
        self.insert_info_extractor(CloudyIE())
        self.insert_info_extractor(VevoPlaylistBaseIE())
        self.insert_info_extractor(VevolyIE())
        self.insert_info_extractor(CrackleIE())
        #20170814
        self.insert_info_extractor(VevoExIE())
        #2017-8-23
        self.insert_info_extractor(XpauIE())

        self.insert_info_extractor(RtbfIE())
        self.insert_info_extractor(NBCIE())
        self.insert_info_extractor(DiscoveryIE())
        self.insert_info_extractor(BingIE())
        self.insert_info_extractor(Movies123IE())
        self.insert_info_extractor(VShareIE())
        self.insert_info_extractor(VShare_euIE())

        self.insert_info_extractor(YespornpleaseIE())
        self.insert_info_extractor(PutStreamIE())
        self.insert_info_extractor(OdnoklassnikiIE())
        self.insert_info_extractor(avgle_IE())

        self.insert_info_extractor(UdemyExIE())
        #
        self.insert_info_extractor(FoxIE())
        self.insert_info_extractor(BoxIE())
        self.insert_info_extractor(GoogleDriverIE())
        self.insert_info_extractor(OneDriverIE())
        self.insert_info_extractor(DropboxExIE())
        self.insert_info_extractor(KalturaIE())
        #2017-12-25
        self.insert_info_extractor(PowtoonIE())
        self.insert_info_extractor(ThiruttuvcdIE())
        self.insert_info_extractor(HudlIE())
        #2018-01-05
        self.insert_info_extractor(KShow123IE())

        self.insert_info_extractor(StreamangoIE())
        self.insert_info_extractor(VideojugIE())
        self.insert_info_extractor(MycanalIE())
        self.insert_info_extractor(TumblrIE())
        #2018-02-16
        self.insert_info_extractor(NiconicoIE())

        self.insert_info_extractor(NuvidIE())
        self.insert_info_extractor(CBSNewsNormalVideoIE())
        self.insert_info_extractor(YesvideoIE())
        self.insert_info_extractor(KizzboyIE())


        if sys.platform == 'win32':
            self.insert_info_extractor(SuperManIE())


    def extract_info(self, url, download=True, ie_key=None, extra_info={},
                     process=True, force_generic_extractor=False):
        debug('youtubedl extract_info')
        try:
            result = super(YoutubeDLPatch4Single, self).extract_info(url, download, ie_key, extra_info, process, force_generic_extractor)
            return result
        except:
            error = traceback.format_exc()
            debug('youtubedl extract_info error: %s' % error)
            new_url = CommonHTML5IE.makeUrl(url)
            try:                
                result = super(YoutubeDLPatch4Single, self).extract_info(new_url, download, ie_key, extra_info, process, force_generic_extractor)
                if result:
                    return result
            except Exception as e:
                debug('--------------try CommonHTML5IE fail--------------')
                pass

            if SaveFromIE.support(url):
                debug('youtubedl extract_info try SaveFrom')
                url = SaveFromIE.makeUrl(url)
                try:
                    result = super(YoutubeDLPatch4Single, self).extract_info(url, download, ie_key, extra_info, process, force_generic_extractor)
                    return result
                except:
                    debug('youtubedl extract_info try SaveFrom fail error: %s' % traceback.format_exc())
                    raise Exception(error)
            else:
                raise Exception(error)


class YoutubeDLPatch4Playlist(YoutubeDLPatch):
    def gen_extractors(self):
        """ Return a list of an instance of every supported extractor.
        The order does matter; the first extractor matched is the one handling the URL.
        """

        from .youtube import (
            YoutubePlaylistIE,
            YoutubeChannelIE,
            YoutubeUserIE,
            YoutubeShowIE,
            YoutubeSearchURLIE,
        )

        from .lynda import (
            LyndaPlaylistIE,
        )

        from .searchMusic import (
            searchMusicIE
        )


        from .dailymotion import DailymotionSearchIE, DailymotionUserIE

        from ..extractor.dailymotion import (
            DailymotionPlaylistIE,
        )


        from .vimeo import VimeoSearchIE

        from ..extractor.vimeo import (
            VimeoChannelIE,
            VimeoUserIE,
            VimeoAlbumIE,
            VimeoGroupsIE,
        )

        from .udemy import (
            UdemyCourseIE
        )

        #from qq import QQKEIIE
        from .pornhub import PornHubSearchIE, PornHubUserVideosIE
        from ..extractor.pornhub import PornHubPlaylistIE

        from .pluralsight import PluralsightCourseIE

        from .videojug import VideojugPlaylistIE

        from .vevo import VevoPlaylistIE

        _ALL_CLASSES = [
            klass
            for name, klass in list(locals().items())
            if name.endswith('IE') and name != 'GenericIE'
        ]
        return [klass() for klass in _ALL_CLASSES]


    def add_default_info_extractors(self):
        """
        Add the InfoExtractors returned by gen_extractors to the end of the list
        """

        if not self.params.get('get_playlist_info'):
            return super(YoutubeDLPatch4Playlist, self).add_default_info_extractors()

        for ie in self.gen_extractors():
            try:
                self.add_info_extractor(ie)
            except Exception as e:
                debug(e)
                pass


    def process_ie_result(self, ie_result, download=True, extra_info={}):
        if not self.params.get('get_playlist_info'):
            return super(YoutubeDLPatch4Playlist, self).process_ie_result(ie_result, download, extra_info)

        temp = {
            '_type': 'playlist',
            'id': ie_result.get('id', '1'),
            'title': ie_result.get('title', 'title'),
            'entries': [],
        }
        if ie_result is not None:
            if ie_result.get('_type', '') == 'playlist':
                for item in ie_result['entries']:
                    try:
                        if item.get('ie_key', '') in ['YoutubePlaylist', 'spotifyAlbum']:
                            result = self.extract_info(item['url'], ie_key=item['ie_key'])
                            if (result != None) and (result.get('entries', None) != None):
                                temp['entries'] += result['entries']
                        else:
                            temp['entries'].append(item)
                    except:
                        pass
            else:
                if ie_result.get('ie_key', '') == 'YoutubePlaylist':
                    result = self.extract_info(ie_result['url'], ie_key=ie_result['ie_key'])
                    if (result != None) and (result.get('entries', None) != None):
                        temp['title'] = result.get('title', 'YoutubePlaylist')
                        temp['entries'] += result['entries']
            return temp if temp['entries'] is not None else None
        else:
            return None

    def extract_info(self, url, download=True, ie_key=None, extra_info={},
                     process=True, force_generic_extractor=False):
        if not self.params.get('get_playlist_info'):
            return super(YoutubeDLPatch4Playlist, self).extract_info( url, download, ie_key, extra_info,
            process, force_generic_extractor)

        ies = [self.get_info_extractor(ie_key)] if ie_key else self._ies
        for ie in ies:
            if ie.suitable(url):
                return self.process_ie_result(ie.extract(url))




class YoutubeDLPatch4AccountTest(YoutubeDLPatch4Playlist):

    from .youtube import YoutubeIE
    from .lynda import LyndaIE
    from ..extractor.niconico import NiconicoIE
    from ..extractor.facebook import FacebookIE

    from ..extractor.vimeo import VimeoIE
    ies = {
        'youtube.com': YoutubeIE(),
        'lynda.com': LyndaIE(),
        'nicovideo.jp': NiconicoIE(),
        'facebook.com': FacebookIE(),
        'vimeo.com': VimeoIE(),
    }
    def report_warningEx(self,  msg, video_id=None):
        raise Exception(msg)


    @staticmethod
    def getAccount(url):
        domains = [domain for domain in list(YoutubeDLPatch4AccountTest.ies.keys()) if url.find(domain)>-1]
        if domains:
            try:
                kvconfigPath = os.getenv('KVConfigPath')
                print(('========================================================================%s' % kvconfigPath))
                if not os.path.exists(kvconfigPath):
                    return
                with io.open(os.path.join(kvconfigPath, 'accounts.json'), 'r', encoding='utf-8') as config:
                    accounts = json.load(config)
                    account = accounts.get(domains[0], None)
                    account['site'] = domains[0]
                    return account
            except Exception as Ex:
                print (Ex)
                pass


    def login(self, site):
        ie = YoutubeDLPatch4AccountTest.ies[site.lower()]
        ie.set_downloader(self)
        if site.lower() in ['facebook.com', 'lynda.com']:
            self.report_warning = self.report_warningEx
        return ie._login()

