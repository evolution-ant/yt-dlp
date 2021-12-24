

import re
import sys
import socket
import itertools

from ..compat import (
    compat_HTTPError,
    compat_urllib_request,
    compat_urllib_parse_unquote_plus,
    compat_urllib_error,
    compat_http_client,

)

from ..extractor.common import InfoExtractor
from ..utils import (
    str_to_int,
    update_Request,
    update_url_query,
    sanitized_Request,
    error_to_compat_str,
    orderedSet, ExtractorError
)

from ..utilsEX import url_result

from ..extractor.pornhub import PornHubIE, PornHubPlaylistBaseIE

def _extract_entriesEx(self, webpage):
    # Only process container div with main playlist content skipping
    # drop-down menu that uses similar pattern for videos (see
    # https://github.com/rg3/yt-dlp/issues/11594).
    container = self._search_regex(
        r'(?s)(<div[^>]+class=["\']container.+)', webpage,
        'container', default=webpage)

    return [
        url_result(
            'http://www.pornhub.com/%s' % video_url,
            PornHubIE.ie_key(), video_title=title, video_duration=duration if duration else 0)
        for video_url, title, duration in orderedSet(re.findall(
            # r'href="/?(view_video\.php\?.*\bviewkey=[\da-z]+[^"]*)"[^>]*\s+title="([^"]+)"',
            r'href="/?(view_video\.php\?.*\bviewkey=[\da-z]+[^"]*)"[^>]*\s+title="([^"]+)"[\s\S]+?<var class="duration">(.+)</var>',
            container))
    ][2:]



PornHubPlaylistBaseIE._extract_entries = _extract_entriesEx


class PostRequest(compat_urllib_request.Request):
    def get_method(self):
        return 'POST'

class PornHubUserVideosIE(PornHubPlaylistBaseIE):
    _VALID_URL = r'https?://(?:www\.)?pornhub\.com/users/(?P<id>[^/]+)/videos'
    _TESTS = [{
        'url': 'http://www.pornhub.com/users/zoe_ph/videos/public',
        'info_dict': {
            'id': 'zoe_ph',
        },
        'playlist_mincount': 171,
    }, {
        'url': 'http://www.pornhub.com/users/rushandlia/videos',
        'only_matching': True,
    }]

    def _request_webpage(self, url_or_request, video_id, note=None, errnote=None, fatal=True, data=None, headers={}, query={}):
        """ Returns the response handle """
        url_or_request = PostRequest(
            url_or_request, data=data, headers=headers)

        try:

            return self._downloader.urlopen(url_or_request)
        except (compat_urllib_error.URLError, compat_http_client.HTTPException, socket.error) as err:
            if errnote is False:
                return False
            if errnote is None:
                errnote = 'Unable to download webpage'

            errmsg = '%s: %s' % (errnote, error_to_compat_str(err))
            if fatal:
                raise ExtractorError(errmsg, sys.exc_info()[2], cause=err)
            else:
                self._downloader.report_warning(errmsg)
                return False

    def _real_extract(self, url):
        user_id = self._match_id(url)
        entries = []
        for page_num in itertools.count(1):
            try:
                webpage = self._download_webpage(
                   'https://www.pornhub.com/users/%s/videos/public/ajax?o=mr' % user_id
                    , user_id, 'Downloading page %d' % page_num,
                    query={'page': page_num}, headers={'Referer' : 'https://www.pornhub.com/users/zoe_ph/videos/public', 'X-Requested-With': 'XMLHttpRequest',
                                                       'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36'})
            except ExtractorError as e:
                if isinstance(e.cause, compat_HTTPError) and e.cause.code == 404:
                    break
                raise
            page_entries = self._extract_entries(webpage)

            if page_entries[0] in entries:
                break
            entries.extend(page_entries)
            if len(entries) > 1024:
                break

        return self.playlist_result(entries, user_id, playlist_title=user_id)


class PornHubSearchIE(PornHubPlaylistBaseIE):
    _VALID_URL = r'https?://(?:www\.)?pornhub\.com/video/search'

    def _real_extract(self, url):
        key = self._search_regex(r'search=([^&]+)', url, '')
        key = compat_urllib_parse_unquote_plus(key)
        entries = []
        for page_num in itertools.count(1):
            try:
                webpage = self._download_webpage(
                    'https://www.pornhub.com/video/search?search=', '', 'Downloading page %d' % page_num,
                    query={'page': page_num, 'search': key})
            except ExtractorError as e:
                if isinstance(e.cause, compat_HTTPError) and e.cause.code == 404:
                    break
                raise
            page_entries = self._extract_entries(webpage)
            if not page_entries:
                break
            entries.extend(page_entries)
            if len(entries) > 1024:
                break

        return self.playlist_result(entries, '', playlist_title=key)