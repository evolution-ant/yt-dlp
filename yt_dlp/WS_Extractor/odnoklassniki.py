# coding: utf-8


from ..extractor.odnoklassniki import OdnoklassnikiIE as Old

from ..compat import (
    compat_etree_fromstring,
    compat_parse_qs,
    compat_urllib_parse_unquote,
    compat_urllib_parse_urlparse,
)
from ..utils import (
    ExtractorError,
    unified_strdate,
    int_or_none,
    qualities,
    unescapeHTML,
)

class OdnoklassnikiIE(Old):
    _VALID_URL = r'https?://(?:(?:www|m|mobile)\.)?(?:odnoklassniki|ok)\.ru/(?:video(?:embed)?|web-api/video/moviePlayer|live)/(?P<id>[\d-]+)'

    def _real_extract(self, url):
        try:
            result = self._real_extract2(url)
            if not result or not result.get('formats', None):
                raise
            return result
        except:
            return super(OdnoklassnikiIE, self)._real_extract(url)


    def _real_extract2(self, url):
        start_time = int_or_none(compat_parse_qs(
            compat_urllib_parse_urlparse(url).query).get('fromTime', [None])[0])

        video_id = self._match_id(url)

        webpage = self._download_webpage(
            'http://ok.ru/video/%s' % video_id, video_id)

        error = self._search_regex(
            r'[^>]+class="vp_video_stub_txt"[^>]*>([^<]+)<',
            webpage, 'error', default=None)
        if error:
            raise ExtractorError(error, expected=True)

        player = self._parse_json(
            unescapeHTML(self._search_regex(
                r'data-options=(?P<quote>["\'])(?P<player>{.+?%s.+?})(?P=quote)' % video_id,
                webpage, 'player', group='player')),
            video_id)

        flashvars = player['flashvars']

        metadata = flashvars.get('metadata')
        if metadata:
            metadata = self._parse_json(metadata, video_id)
        else:
            metadata = self._download_json(
                compat_urllib_parse_unquote(flashvars['metadataUrl']),
                video_id, 'Downloading metadata JSON')

        movie = metadata['movie']

        # Some embedded videos may not contain title in movie dict (e.g.
        # http://ok.ru/video/62036049272859-0) thus we allow missing title
        # here and it's going to be extracted later by an extractor that
        # will process the actual embed.
        provider = metadata.get('provider')
        title = movie['title'] if provider == 'UPLOADED_ODKL' else movie.get('title')

        thumbnail = movie.get('poster')
        duration = int_or_none(movie.get('duration'))

        author = metadata.get('author', {})
        uploader_id = author.get('id')
        uploader = author.get('name')

        upload_date = unified_strdate(self._html_search_meta(
            'ya:ovs:upload_date', webpage, 'upload date', default=None))

        age_limit = None
        adult = self._html_search_meta(
            'ya:ovs:adult', webpage, 'age limit', default=None)
        if adult:
            age_limit = 18 if adult == 'true' else 0

        like_count = int_or_none(metadata.get('likeCount'))

        info = {
            'id': video_id,
            'title': title,
            'thumbnail': thumbnail,
            'duration': duration,
            'upload_date': upload_date,
            'uploader': uploader,
            'uploader_id': uploader_id,
            'like_count': like_count,
            'age_limit': age_limit,
            'start_time': start_time,
        }

        if provider == 'USER_YOUTUBE':
            info.update({
                '_type': 'url_transparent',
                'url': movie['contentId'],
            })
            return info

        formats = [{
            'url': f['url'],
            'ext': 'mp4',
            'format_id': f['name'],
        } for f in metadata['videos']]
        if not formats:
            quality = qualities(('4', '0', '1', '2', '3', '5'))
            m3u8_url = metadata.get('hlsManifestUrl')
            if m3u8_url:
                formats.extend(self._extract_m3u8_formats(
                    m3u8_url, video_id, 'mp4', 'm3u8_native',
                    m3u8_id='hls', fatal=False))

            dash_manifest = metadata.get('metadataEmbedded')
            if dash_manifest:
                formats.extend(self._parse_mpd_formats(
                    compat_etree_fromstring(dash_manifest), 'mpd'))

            for fmt in formats:
                fmt_type = self._search_regex(
                    r'\btype[/=](\d)', fmt['url'],
                    'format type', default=None)
                if fmt_type:
                    fmt['quality'] = quality(fmt_type)

        self._sort_formats(formats)

        info['formats'] = formats
        return info

