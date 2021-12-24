# coding: utf-8



import os
import re
import sys

from ..extractor.common import InfoExtractor
from ..extractor.generic import GenericIE as OldGenericIE
from ..utils import (
    sanitized_Request,
    ExtractorError,
    determine_ext,
)

from ..compat import compat_urllib_error

class CommonHTML5IE(InfoExtractor):
    _VALID_URL = 'html5://(.*)'


    def _is_valid_url(self, url, video_id, item='video', headers={}):
        url = self._proto_relative_url(url, scheme='http:')
        # For now assume non HTTP(S) URLs always valid
        # if not (url.startswith('http://') or url.startswith('https://')):
        #     return True
        try:
            self._request_webpage(url, video_id, 'Checking %s URL' % item, headers=headers)
            return True
        except ExtractorError as e:
            if isinstance(e.cause, compat_urllib_error.URLError):
                self.to_screen(
                    '%s: %s URL is invalid, skipping' % (video_id, item))
                return False
            raise

    def _real_extract(self, url):
        if url.find('vshare.eu') > -1:
            raise
        url = self._search_regex(self._VALID_URL, url, 'url')
        request = sanitized_Request(url,
            headers={'User-Agent': 'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.1)'})
        webPage = self._download_webpage(request, url)
        title = self._og_search_title(webPage, default=None)
        if not title:
            title = self._html_search_meta('title', webPage, default=None)
        if not title:
            title = self._search_regex(r'<title[^>]*>([^<]+)</title>', webPage, 'title', default=None)
        if not title:
            title = 'unkown'

        thumbnail = self._og_search_thumbnail(webPage)
        if not thumbnail:
            thumbnail = self._html_search_meta('thumbnail', webPage, default=None)
        if not thumbnail:
            thumbnail = self._search_regex(r'<meta[ \t\r\n\v\f]+property=\"og:image\"[ \t\r\n\v\f]+content=\"(http[s]?://[^\"]+)\"', webPage, 'thumbnail', default=None)
        if not thumbnail:
            thumbnail = self._search_regex(r'<meta[ \t\r\n\v\f]+name=\"og:image\"[ \t\r\n\v\f]+content=\"(http[s]?://[^\"]+)\"', webPage, 'thumbnail', default=None)
        if not thumbnail:
            thumbnail = self._search_regex(r'<meta[ \t\r\n\v\f]+itemprop=\"image\"[ \t\r\n\v\f]+content=\"(http[s]?://[^\"]+)\"', webPage, 'thumbnail', default=None)


        User_Agents = ['Mozilla/5.0 (iPad; CPU OS 5_1 like Mac OS X) AppleWebKit/534.46 (KHTML, like Gecko) Version/5.1 Mobile/9B176 Safari/7534.48.3',
                       'Mozilla/5.0 (iPhone; CPU iPhone OS 9_1 like Mac OS X) AppleWebKit/601.1.46 (KHTML, like Gecko) Version/9.0 Mobile/13B143 Safari/601.1',
                       'Mozilla/5.0 (Linux; Android 5.0; SM-G900P Build/LRX21T) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Mobile Safari/537.36']
        src = None
        for user_agent in User_Agents:
            request = sanitized_Request(url,
                headers={'User-Agent': user_agent})
            webPage = self._download_webpage(request, url)
            videoStr = self._search_regex('<video([\s\S]+)</video>', webPage, 'videoStr', default=None)
            if videoStr:
                src = self.fixUrl(self._search_regex(r'src=[\'"](http[^\'"]+)[^>]*>', videoStr, 'src',default=None))
                if src and self._is_valid_url(src, src):
                    formats = []
                    if src.find('.m3u8') > -1:
                        formats.extend(self._extract_m3u8_formats(src, '',  'mp4', m3u8_id='hls', fatal=False))
                    elif src.find('manifest.mpd') > -1:
                        formats.extend(self._extract_mpd_formats(src, '', mpd_id='dash', fatal=False))
                    else:
                        formats.append({
                            'ext': determine_ext(src),
                            'url': src
                        })
                    if formats:
                        return {
                            'id': 'haha',
                            'title': title,
                            'thumbnail': thumbnail,
                            'formats': formats
                        }
            src = self.fixUrl(self._search_regex('[\'"](http[^\'"]+\\.(flv|mp4)[^.\'"]*)[\'"]', webPage, 'videoStr', default=None))
            if src and self._is_valid_url(src, src):
                break
        if src:
            return {
                'id': 'haha',
                'title': title,
                'thumbnail': thumbnail,
                'formats': [{'url': src}]
            }

    def fixUrl(self, src):
        if src:
            src = src.replace('\\', '').replace(' ', '%20')
            return src
        else:
            return None

    @classmethod
    def makeUrl(cls, url):
        return 'html5://' + url