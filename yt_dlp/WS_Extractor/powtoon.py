# encoding: utf-8


from ..extractor.common import InfoExtractor

class PowtoonIE(InfoExtractor):
    # https://www.powtoon.com/online-presentation/fz4lxkkm3Xk/?mode=movie
    # https://www.powtoon.com/c/frsu2KT0bMm/1/m
    # https://www.powtoon.com/html5-studio/#/edit/fzfvYtDUaHC
    _VALID_URL = r'https?://(?:www\.)?powtoon\.com/.+/(?P<id>\w{11})'

    def _real_extract(self, url):
        video_id = self._match_id(url)
        api_url = r'https://www.powtoon.com/api/v2/powtoons/%s?include_content=true' % video_id
        headers = {'Accept': 'application/json'}
        video_data = self._download_json(api_url, video_id, headers=headers)
        video_url = video_data['external_url']

        if video_url:
            return self.url_result(video_url)

        # https://www.powtoon.com/online-presentation/fI9nmoEkOrZ/wedding-invitation-main/?mode=movie
        # 这一种，直接在canvas上画的，下不下来
        return super(PowtoonIE, self)._real_extract(url)