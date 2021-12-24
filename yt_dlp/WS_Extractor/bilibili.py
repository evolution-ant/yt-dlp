# coding: utf-8

from ..extractor.bilibili import BiliBiliIE as BiliBiliBase
import hashlib
import re

from ..compat import (
    compat_parse_qs,
    compat_urlparse,
)
from ..utils import (
    ExtractorError,
    int_or_none,
    float_or_none,
    parse_iso8601,
    smuggle_url,
    strip_jsonp,
    unified_timestamp,
    unsmuggle_url,
    urlencode_postdata,
)


class BiliBiliIE(BiliBiliBase):
    def getRate(self, f):
        url = f['url']
        rate = self._search_regex(r'rate=(\d+)', url, '', fatal=False, default='0')
        return rate

    def _real_extract(self, url):
        try:
            result = self._real_extract_HightQuality(url)
        except:
            result = False

        if not result:
            result = super(BiliBiliIE, self)._real_extract(url)

        if 'formats' in result:
            result['formats'].sort(key = self.getRate, reverse=True)
            for f in result['formats']:
                f['preference'] = - result['formats'].index(f) - 1
        # header加入此引用方能下载
        result.update({
            'http_headers': {
                'Referer': url,
            }
        })
        return result

    def _real_extract_HightQuality(self, url):
        url, smuggled_data = unsmuggle_url(url, {})
        mobj = re.match(self._VALID_URL, url)
        video_id = mobj.group('id')
        anime_id = mobj.group('anime_id')
        webpage = self._download_webpage(url, video_id)

        if 'anime/' not in url:
            cid = compat_parse_qs(self._search_regex(
                [r'EmbedPlayer\([^)]+,\s*"([^"]+)"\)',
                 r'<iframe[^>]+src="https://secure\.bilibili\.com/secure,([^"]+)"'],
                webpage, 'player parameters'))['cid'][0]
        else:
            if 'no_bangumi_tip' not in smuggled_data:
                self.to_screen('Downloading episode %s. To download all videos in anime %s, re-run yt-dlp with %s' % (
                    video_id, anime_id, compat_urlparse.urljoin(url, '//bangumi.bilibili.com/anime/%s' % anime_id)))
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            }
            headers.update(self.geo_verification_headers())

            js = self._download_json(
                'http://bangumi.bilibili.com/web_api/get_source', video_id,
                data=urlencode_postdata({'episode_id': video_id}),
                headers=headers)
            if 'result' not in js:
                self._report_error(js)
            cid = js['result']['cid']

        payload = 'appkey=%s&cid=%s&otype=json&quality=80' % (self._APP_KEY, cid)
        sign = hashlib.md5((payload + self._BILIBILI_KEY).encode('utf-8')).hexdigest()

        headers = self.geo_verification_headers()
        headers.update({
            "Referer": url
        })
        video_info = self._download_json(
            'http://interface.bilibili.com/playurl?%s&sign=%s' % (payload, sign),
            video_id, note='Downloading video info page',
            headers=headers)

        if 'durl' not in video_info:
            self._report_error(video_info)

        entries = []
        for idx, durl in enumerate(video_info['durl']):
            formats = [{
                'url': durl['url'],
                'filesize': int_or_none(durl['size']),
            }]
            for backup_url in durl.get('backup_url', []):
                formats.append({
                    'url': backup_url,
                    # backup URLs have lower priorities
                    'preference': -2 if 'hd.mp4' in backup_url else -3,
                })

            self._sort_formats(formats)
            entries.append({
                'id': '%s_part%s' % (video_id, idx),
                'duration': float_or_none(durl.get('length'), 1000),
                'formats': formats,
            })

        title = self._html_search_regex('<h1[^>]+title="([^"]+)">', webpage, 'title')
        description = self._html_search_meta('description', webpage)
        timestamp = unified_timestamp(self._html_search_regex(
            r'<time[^>]+datetime="([^"]+)"', webpage, 'upload time', default=None))
        thumbnail = self._html_search_meta(['og:image', 'thumbnailUrl'], webpage)

        info = {
            'id': video_id,
            'title': title,
            'description': description,
            'timestamp': timestamp,
            'thumbnail': thumbnail,
            'duration': float_or_none(video_info.get('timelength'), scale=1000),
        }

        uploader_mobj = re.search(
            r'<a[^>]+href="(?:https?:)?//space\.bilibili\.com/(?P<id>\d+)"[^>]+title="(?P<name>[^"]+)"',
            webpage)
        if uploader_mobj:
            info.update({
                'uploader': uploader_mobj.group('name'),
                'uploader_id': uploader_mobj.group('id'),
            })

        for entry in entries:
            entry.update(info)
            entry.update({
                'http_headers': {
                    'Referer': url,
                }
            })

        if len(entries) == 1:
            return entries[0]
        else:
            for idx, entry in enumerate(entries):
                entry['id'] = '%s_part%d' % (video_id, (idx + 1))
            self._downloader.params['playlistend'] = -1
            return {
                '_type': 'multi_video',
                'id': video_id,
                'title': title,
                'description': description,
                'entries': entries,
            }