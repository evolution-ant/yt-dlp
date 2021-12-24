

from ..utils import (
    update_url_query,
    int_or_none
)

from ..utilsEX import url_result

from ..extractor.pluralsight import PluralsightCourseIE as Old


class PluralsightCourseIE(Old):
   def _real_extract(self, url):
        course_id = self._match_id(url)

        # TODO: PSM cookie

        course = self._download_course(course_id, url, course_id)

        title = course['title']
        course_name = course['name']
        course_data = course['modules']
        description = course.get('description') or course.get('shortDescription')

        entries = []
        for num, module in enumerate(course_data, 1):
            author = module.get('author')
            module_name = module.get('name')
            if not author or not module_name:
                continue
            for clip in module.get('clips', []):
                clip_index = int_or_none(clip.get('index'))
                if clip_index is None:
                    continue
                clip_url = update_url_query(
                    '%s/player' % self._API_BASE, query={
                        'mode': 'live',
                        'course': course_name,
                        'author': author,
                        'name': module_name,
                        'clip': clip_index,
                    })
                entries.append({
                    '_type': 'url_transparent',
                    'url': clip_url,
                    'duration': clip['duration'],
                    'title': module.get('title'),
                })

        return self.playlist_result(entries, course_id, title, description)