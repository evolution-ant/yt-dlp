# encoding: utf-8


import json
import threading
from ..extractor.common import InfoExtractor
from ..compat import compat_urllib_request


class jibjabIE(InfoExtractor):
    _USER_AGENT_IPAD = 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.101 Mobile Safari/537.36'
    _VALID_URL = r'https?://(?:.+\.)?jibjab\.com/view'

    # https://www.jibjab.com/view/make/revolves_around_you/f63ed47a-ec7f-4a05-9c56-7cf70f167086?utm_campaign=tx_recipient_noti...
    # http://www.jibjab.com/view/xf7riuoigVakeOefkWbN
    def _real_extract(self, url):
        video_id = self._search_regex(r'/([a-z0-9-]{22,})', url, 'token', fatal=False)
        if not video_id:
            # 求token
            token = self._search_regex(r'view/((?:[^?/]+){20,})', url, 'token', fatal=False) or \
                    self._search_regex(r'token=(.+)', url, 'token', fatal=False) or \
                    self._search_regex(r'view/(.+)\?', url, 'token', fatal=False)

            if not token:
                return super(jibjabIE, self)._real_extract(url)

            if len(token) >= 22:
                video_id = token
            else:
                # 求视频id
                url = r'https://origin-prod-phoenix.jibjab.com/v1/legacy/views/%s?external_key=%s' % (token, token)
                js = self._download_json(url, 'video_id')
                if not js or not js['data'] or not js['data']['id']:
                    return super(jibjabIE, self)._real_extract(url)

                video_id = js['data']['id']

        if not video_id:
            return super(jibjabIE, self)._real_extract(url)

        makes = 'makes'
        url = r'https://origin-prod-phoenix.jibjab.com/v1/%s/%s' % (makes, video_id)
        js = self._download_json(url, 'video_id')
        if not js or not js['data'] or not js['data']['id']:
            return super(jibjabIE, self)._real_extract(url)

        if js['data']['attributes']:
            thumbnail = js['data']['attributes'].get('thumbnail', '')
        if js['included'] and js['included'][0]['attributes']:
            title = js['included'][0]['attributes'].get('template-group-name', '')
            # 实在不行，下载其模板吧
            video_url_bak = js['included'][0]['attributes'].get('webgl-feature-video', '')

        # 等它制作完毕
        render_url = r'origin-prod-phoenix.jibjab.com/v1/mobile/makes/%s/render' % video_id
        data = {"data": {"attributes": {}, "relationships": {"make": {"data": {"type": "makes", "id": video_id}}}, "type": "mobile/renders"}}
        jsonData = None
        headers = {'Referer': 'https://www.jibjab.com/view/make/celebration_edf_group/%s' % video_id,
                   'Origin': 'https://www.jibjab.com',
                   'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.101 Mobile Safari/537.36',
                   'Content-type': 'application/vnd.api+json'}

        try:
            jsonData = self._download_json(
                    'https://' + render_url, video_id, 'Downloading video page',
                    data=json.dumps(data),
                    headers=headers)
        except:
            pass

        if not jsonData:
            headers = {'Accept': 'application/vnd.api+json',
                       'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.101 Mobile Safari/537.36'}
            for i in range(50):
                try:
                    jsonData = self._download_json('https://' + render_url, video_id, '', headers=headers)
                    if jsonData:
                        break
                except:
                    pass
                    threading._sleep(1)

        # 视频地址，如下格式
        video_url = r'https://www.jibjab.com/%s/%s.mp4' % (makes, video_id) if jsonData else video_url_bak
        formats = [{
            'url': video_url,
            'ext': 'mp4'
        }]

        return {
            'id': '',
            'title': title,
            'thumbnail': thumbnail,
            'formats': formats,
        }
