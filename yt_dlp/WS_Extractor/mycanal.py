# encoding: utf-8



from ..utils import (
    determine_ext,
    qualities,
)
from ..extractor.common import InfoExtractor

class MycanalIE(InfoExtractor):
    # https://www.mycanal.fr/divertissement/la-semaine-des-guignols-semaine-du-21-05/p/1449485
    _VALID_URL = r'https?://(?:www\.)?mycanal\.fr/(?:[^/]+/)*(?P<id>[\d_]+)$'

    def _real_extract(self, url):
        video_id = self._match_id(url)
        api_url = r'https://secure-service.canal-plus.com/video/rest/getVideosLiees/cplus/%s?format=json' % video_id
        video_data = self._download_json(api_url, video_id)
        if isinstance(video_data, dict):
            return self._get_video_info(video_data, url)
        # https://www.mycanal.fr/cinema/debat-sur-vers-la-lumiere-le-cercle-du-12-01/p/1476850
        elif isinstance(video_data, list):
            for vi in video_data:
                if isinstance(vi, dict) and vi.get('ID', '') == video_id:
                    return self._get_video_info(vi, url)

        return super(MycanalIE, self)._real_extract(url)

    def _get_video_info(self, video_dict, url):
        if 'URL' in video_dict:
            return self.url_result(video_dict['URL'])

        # 解析其中内容
        video_id = video_dict['ID']
        title = video_dict['INFOS']['TITRAGE']['TITRE']
        description = video_dict['INFOS']['DESCRIPTION']
        thumbnail = video_dict['MEDIA']['IMAGES']['GRAND']
        formats = []
        # for key, value in video_dict['MEDIA']['VIDEOS'].items():
        #     formats.append({
        #         'format_id': key,
        #         'ext': determine_ext(value),
        #         'url': value
        #     })
        preference = qualities(['MOBILE', 'BAS_DEBIT', 'HAUT_DEBIT', 'HD'])
        for format_id, format_url in list(video_dict['MEDIA']['VIDEOS'].items()):
            if not format_url:
                continue
            if format_id == 'HLS':
                formats.extend(self._extract_m3u8_formats(
                    format_url, video_id, 'mp4', 'm3u8_native', m3u8_id=format_id, fatal=False))
            elif format_id == 'HDS':
                formats.extend(self._extract_f4m_formats(
                    format_url + '?hdcore=2.11.3', video_id, f4m_id=format_id, fatal=False))
            else:
                formats.append({
                    # the secret extracted ya function in http://player.canalplus.fr/common/js/canalPlayer.js
                    'url': format_url + '?secret=pqzerjlsmdkjfoiuerhsdlfknaes',
                    'format_id': format_id,
                    'preference': preference(format_id),
                })
        self._sort_formats(formats)

        return {
            'id': video_id,
            'title': title,
            'description': description,
            'thumbnail': thumbnail,
            'formats': formats,
        }
