# encoding: utf-8



import re

from ..extractor.common import (
    InfoExtractor,
)
from ..extractor.lynda import (
    LyndaBaseIE,
    LyndaIE as OldLyndaIE
)

from ..utils import (
    int_or_none,
    ExtractorError
)

from ..compat import compat_str

class LyndaIE(OldLyndaIE):
    _VALID_URL = r'https?://www\.lynda\.com/(?:[^/]+/[^/]+/\d+(-\d+)*|player/embed)/(?P<id>\d+)'

    def _real_extract(self, url):
        webPage = self._download_webpage(url, url)
        if OldLyndaIE.suitable(url):
            ie = OldLyndaIE()
            ie.set_downloader(self._downloader)
            # 下载字幕
            self._downloader.params['listsubtitles'] = True
            result = ie._real_extract(url)
            self._downloader.params['listsubtitles'] = False
            result['thumbnail'] = self._og_search_thumbnail(webPage)
            return result

        video_id = self._search_regex(r'data-initial-video-id="(\d+)', webPage, 'video_id')
        query = {
            'videoId': video_id,
            'type': 'video',
        }
        video = self._download_json(
            'https://www.lynda.com/ajax/player', video_id,
            'Downloading video JSON', fatal=False, query=query)

        # Fallback scenario
        if not video:
            raise Exception('not support!')

        if 'Status' in video:
            raise ExtractorError(
                'lynda returned error: %s' % video['Message'], expected=True)

        if video.get('HasAccess') is False:
            self._raise_unavailable(video_id)

        video_id = compat_str(video.get('ID') or video_id)
        duration = int_or_none(video.get('DurationInSeconds'))
        title = video['Title']
        thumbnail = self._og_search_thumbnail(webPage)

        formats = []

        fmts = video.get('Formats')
        if fmts:
            formats.extend([{
                'url': f['Url'],
                'ext': f.get('Extension'),
                'width': int_or_none(f.get('Width')),
                'height': int_or_none(f.get('Height')),
                'filesize': int_or_none(f.get('FileSize')),
                'format_id': compat_str(f.get('Resolution')) if f.get('Resolution') else None,
            } for f in fmts if f.get('Url')])

        prioritized_streams = video.get('PrioritizedStreams')
        if prioritized_streams:
            for prioritized_stream_id, prioritized_stream in list(prioritized_streams.items()):
                formats.extend([{
                    'url': video_url,
                    'height': int_or_none(format_id),
                    'format_id': '%s-%s' % (prioritized_stream_id, format_id),
                } for format_id, video_url in list(prioritized_stream.items())])

        self._check_formats(formats, video_id)
        self._sort_formats(formats)

        self._downloader.params['listsubtitles'] = True
        subtitles = self.extract_subtitles(video_id)
        self._downloader.params['listsubtitles'] = False

        return {
            'id': video_id,
            'title': title,
            'duration': duration,
            'thumbnail': thumbnail,
            'subtitles': subtitles,
            'formats': formats
        }

class LyndaPlaylistIE(InfoExtractor):
    _VALID_URL = r'https?://(?:www|m)\.lynda\.com/.*'

    def _real_extract(self, url):
        self.to_screen('LyndaPlaylistIE 1')
        webpage = self._download_webpage(url, url)
        self.to_screen('LyndaPlaylistIE 2')
        try:
            #self.to_screen(webpage)
            mobj = re.search(r'data-tracking-category="course-page"\s*data-course-id="(.*?)"|'
                             r'<input\s*type="hidden"\s*id="currentCourseId"\s*value="(.*?)"|'
                             r'<link rel="alternate"\s*href=".*\/course\/([^\"]*)',
                             webpage)
            self.to_screen('LyndaPlaylistIE 2.1')
            if mobj:
                self.to_screen('LyndaPlaylistIE 3.1')
                courseId = mobj.group(1) if mobj.group(1) is not None else mobj.group(2)
                if not courseId:
                    courseId = mobj.group(3)
                self.to_screen('LyndaPlaylistIE 3')
                url = 'http://www.lynda.com/ajax/player?courseId=%s&type=course' % courseId
                data = self._download_json(url, url)
                self.to_screen('LyndaPlaylistIE 4')
                entries = []
                self.to_screen('LyndaPlaylistIE 5')
                for chapter in data['Chapters']:
                    for video in chapter['Videos']:
                        entries.append({'id': str(video['ID']), 'title': video['Title'],
                        'url': 'http://www.lynda.com' + video['CourseURLs']['www.lynda.com'].replace('2.html', '2/' + str(video['ID']) + '-4.html'),
                        'duration': video['DurationInSeconds']})
                self.to_screen('LyndaPlaylistIE 6')
                return self.playlist_result(entries, courseId, data['Title'])
            else:
                return None
        except Exception as e:
            self.to_screen(e.message)
            return None