# encoding: utf-8



import tempfile
import os
import io
from ..extractor.common import InfoExtractor

class avgle_IE(InfoExtractor):
    _VALID_URL = r'https?://(?:www\.)?avgle\.com'

    def _real_extract(self, url):
        webpage = self._download_webpage(url, url)
        try:
            video_url = self._search_regex(r'<source\s+src="([^"]+)', webpage, '')
            title = self._og_search_title(webpage)
            thumbnail = self._search_regex(r'poster="([^"]+)', webpage, '', fatal=False) or self._og_search_thumbnail(webpage)
            # formats = [{'url': video_url}]
            formats = []
            formats.extend(self._extract_m3u8_formats(video_url, 'xx', 'mp4', m3u8_id='hls', fatal=True))

            return {
                'id': id,
                'title': title,
                'thumbnail': thumbnail,
                'formats': formats,
            }
        except:
            pass

        video_id = self._search_regex(r'(\d+)', url, 'video_id', fatal=False)
        title = self._og_search_title(webpage, default=None) or self._html_search_regex(r'<title[^>]*>([^<]+)</title>', webpage, 'title')
        thumbnail = self._search_regex(r'poster="([^"]+)', webpage, '', fatal=False) or self._og_search_thumbnail(webpage)

        from ..utilsEX import downloadWebPage_BYHeadlessBrowser
        # 生成临时js文件
        (fd, filename) = tempfile.mkstemp(prefix='kv', suffix='.js')
        os.close(fd)
        js = '''if (currentSrc) { window.external.output('<video id="kv_player" src="' + currentSrc + '" />'); }'''
        with io.open(filename, 'w+', encoding='utf-8') as fp:
            fp.write(js)
        fp.close()
        webpage, _ = downloadWebPage_BYHeadlessBrowser(url, filename)
        # <source id="video-info" data-vid="130177" data-ts="1516619998" data-hash="NzJjZTY3NThlYzRjOWMzYTdlNDQ5OTU4ZWVhYWUwNTI=">
        video_url = self._search_regex(r'<video\s+id="kv_player"\s+src="([^"]+)"', webpage, 'video_url')

        formats = self._extract_m3u8_formats(
            video_url, '', ext='mp4', entry_protocol='m3u8_native',
            m3u8_id='hls', fatal=False)

        return {
            'id': video_id,
            'title': title,
            'thumbnail': thumbnail,
            'formats': formats
        }