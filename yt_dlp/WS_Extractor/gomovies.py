# encoding: utf-8


import re
import base64
from ..utils import int_or_none
from ..utilsEX import download_webPage_by_PYCURL

from ..extractor.common import InfoExtractor
from ..extractor.generic import GenericIE
class GoMoviesIE(InfoExtractor):
    _VALID_URL = r'https?://(?:www\.)?(?:gomovies|gostream)\.\w+/film/[\w-]+-(?P<id>[\d]+)'
    _DOMAIN = ''
    _TESTS = [
        {
            'url': 'https://gomovies.is/film/wonder-woman-20963/',
            'md5': '77108c1e4ab58f48031101a1a2119789',
            'info_dict': {
                'id': 'wonder-woman-20963',
                'ext': 'mp4',
                'title': 'Wonder Woman.',
                'duration': 141,
                'timestamp': 1205712000,
                'uploader': 'none',
                'upload_date': '20080317',
                'thumbnail': r're:^https?://.*\.jpg$',
            },
        },
    ]

    _url = ''

    def _download_webpage(self, url_or_request, video_id, note=None, errnote=None, fatal=True, tries=1, timeout=5, encoding=None, data=None, headers={}, query={}):
        try:
            return super(GoMoviesIE, self)._download_webpage(url_or_request, video_id, note, errnote, fatal, tries, timeout, encoding, data, headers, query)
        except:
            return download_webPage_by_PYCURL(self, url_or_request, timeout, data, headers, query)

    def _real_extract(self, url):
        if (not 'watching.html' in url):
            url += 'watching.html'
        self._url = url
        video_id = self._match_id(url)
        #根据video_id求播放源data_id，都取出来
        episodes_url = r'https://gostream.is/ajax/movie_episodes/' + video_id
        webpage = self._download_webpage(episodes_url, video_id)
        data_ids = re.findall(r'id=\\"ep-(?P<id>\d+)?\\"', webpage)
        if (not data_ids):
            return super(GoMoviesIE, self)._real_extract(url)

        formats = []
        for data_id in data_ids:
            formats.extend(self.get_medias(video_id, data_id))

        # openload?
        if len(formats) != 0:
            for format in formats:
                if format['url'] and ('openload' in format['url'] or format['ext'] == 'url'):
                    return self.url_result(format['url'])
        #影片信息
        webpage = self._download_webpage(url, video_id)
        title = self._og_search_title(webpage)
        description = self._og_search_description(webpage)
        thumbnail = self._og_search_thumbnail(webpage)

        return {
            'id': video_id,
            'title': title,
            'formats': formats,
            'description': description,
            'thumbnail': thumbnail,
            'http_headers': {
                'Referer': url
            }
        }

    def get_medias(self, video_id, data_id):
        formats = []
        try:
            #根据video_id、data_id获取所需_x、_y参数
            token_url = r'https://gostream.is/ajax/movie_token?eid=%s&mid=%s' % (data_id, video_id)
            webpage = self._download_webpage(token_url, video_id)
            #取_x、_y参数
            #_x='4f90e3b8e08d4afe5ec3e87cffbed574', _y='2b48fcf478de468252b0d522d5fb30ce';
            _x = self._search_regex(r'_x=\'(\w+)\'', webpage, '_x')
            _y = self._search_regex(r'_y=\'(\w+)\'', webpage, '_y')
            if (not _x or not _y):
                return formats

            #https://gomovies.is/ajax/movie_sources/655099?x=4f90e3b8e08d4afe5ec3e87cffbed574&y=2b48fcf478de468252b0d522d5fb30ce
            sources_url = r'https://gostream.is/ajax/movie_sources/%s?x=%s&y=%s' % (data_id, _x, _y)
            movie_json = self._download_json(sources_url, video_id)
            if (not movie_json or not movie_json['playlist'] or not movie_json['playlist'][0]['sources']):
                return formats

            #解析格式
            movie_list = movie_json['playlist'][0]['sources']
            if isinstance(movie_list, dict):
                tl = movie_list
                movie_list = []
                movie_list.append(tl)
            for movie in movie_list:
                label = movie.get('label', '0p')
                height = int_or_none(label.lower().rstrip('p'), default=0)
                ext = movie['type']
                ext = ext if (ext.find('video/') == -1) else ext.replace('video/', '')
                formats.append({
                    'format_id': label,
                    #为排序用
                    'height': height,
                    'ext': ext,
                    'url':  movie['file'],
                })
        except Exception as e:
            try:
                # openload一支
                sources_url = r'https://gomovies.is/ajax/movie_embed/%s' % data_id
                movie_json = self._download_json(sources_url, video_id)
                if not movie_json or not movie_json['src']:
                    return formats

                formats.append({
                    'ext': 'url',
                    'url': movie_json['src'],
                })
            except:
                pass

        #去除无效资源
        self._check_formats(formats, video_id)
        return formats

    # 加headers判断
    def _is_valid_url(self, url, video_id, item='video', headers={}):
        try:
            headers = { 'Referer': self._url }
            result = super(GoMoviesIE, self)._is_valid_url(url, video_id, item, headers)
            if result:
                webpage = self._download_webpage(url, video_id, headers=headers)
                err_infos = ['''There could be several reasons for this, for example it got removed by the owner.''',
                            '''It maybe got deleted by the owner or was removed due a copyright violation.''']
                for err_info in err_infos:
                    if err_info in webpage:
                        result = False

            return result
        except:
            return False


class GoMovies_fm_IE(InfoExtractor):

    _VALID_URL = r'https?://(?:www\.)?gomovies\.fm'

    def _real_extract(self, url):

        webpage = self._download_webpage(url, url)
        str = self._search_regex(r'document\.write\(Base64.decode\("([^"]+)', webpage, 'xxxx')
        str = base64.b64decode(str.encode('ascii')).decode('utf-8')
        video_url = self._search_regex(r'src="([^"]+)', str, '')
        ie = GenericIE()
        ie.set_downloader(self._downloader)
        result = ie.extract(video_url)
        result['http_headers'] = {'Referer': video_url, 'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36'}
        for entry in result.get('entries', {}):
            for format in  entry['formats']:
                format['http_headers'] = result['http_headers']
        return result