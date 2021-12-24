


import re
import json
import itertools
import threading

from ..utils import sanitized_Request
from ..compat import compat_urllib_request
from ..utilsEX import download_webPage_by_PYCURL
from ..extractor.udemy import (
    UdemyIE
)


class UdemyExIE(UdemyIE):

    def _download_webpage(self, url_or_request, video_id, note=None, errnote=None, fatal=True, tries=1, timeout=5, encoding=None, data=None, headers={}, query={}):
        try:
            return super(UdemyExIE, self)._download_webpage(url_or_request=url_or_request, video_id=video_id, note=note, errnote=errnote, fatal=fatal, tries=tries, timeout= timeout, encoding=encoding, data=data, query=query)
        except Exception as ex:
            return download_webPage_by_PYCURL(self, url_or_request, timeout, data, headers, query)


class UdemyCourseIE(UdemyExIE):
    IE_NAME = 'udemy:course'
    _VALID_URL = r'https?://(?:www\.)?udemy\.com/(?P<id>[^/?#&]+)'
    _TESTS = []


    @classmethod
    def suitable(cls, url):
        return False if UdemyIE.suitable(url) else super(UdemyCourseIE, cls).suitable(url)

    def _real_extract(self, url):
        course_path = self._match_id(url)

        webpage = self._download_webpage(url, course_path)

        course_id, title = self._extract_course_info(webpage, course_path)

        self._enroll_course(url, webpage, course_id)

        response = self._download_json(
            'https://www.udemy.com/api-2.0/courses/%s/cached-subscriber-curriculum-items' % course_id,
            course_id, 'Downloading course curriculum', query={
                'fields[asset]': '@title,filename,asset_type,external_url,length',
                'fields[chapter]': 'title,object_index',
                'fields[lecture]': 'title,asset',
                'page_size': '1000',
            })

        entries = []
        chapter, chapter_number = [None] * 2
        for entry in response['results']:
            clazz = entry.get('_class')
            if clazz == 'lecture':
                asset = entry.get('asset')
                if isinstance(asset, dict):
                    asset_type = asset.get('asset_type') or asset.get('assetType')
                    if asset_type != 'Video':
                        continue
                lecture_id = entry.get('id')
                if lecture_id:
                    entry = {
                        '_type': 'url_transparent',
                        'url': 'https://www.udemy.com/%s/learn/v4/t/lecture/%s' % (course_path, entry['id']),
                        'title': entry.get('title'),
                        'ie_key': UdemyIE.ie_key(),
                        'duration': entry.get('asset',{}).get('length', 120),
                    }
                    if chapter_number:
                        entry['chapter_number'] = chapter_number
                    if chapter:
                        entry['chapter'] = chapter
                    entries.append(entry)
            elif clazz == 'chapter':
                chapter_number = entry.get('object_index')
                chapter = entry.get('title')

        return self.playlist_result(entries, course_id, title)
