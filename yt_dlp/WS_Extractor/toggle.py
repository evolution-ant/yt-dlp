#coding: utf-8


from ..extractor.toggle import ToggleIE as OldIE

class ToggleIE(OldIE):
    #扩充其正则表达式，支持多一些的网站
    _VALID_URL = r'https?://video\.toggle\.sg/(?:en|zh)/(?:series|clips|movies|tv-show|video|channels|embed)/(?:[^/]+/)*(?P<id>\d+)'

    def _real_extract(self, url):
        result = super(ToggleIE, self)._real_extract(url)
        try:
            video_id = self._match_id(url)
            getSubtitleFilesForMedia = 'http://sub.toggle.sg/toggle_api/v1.0/apiService/getSubtitleFilesForMedia?mediaId=%s' % video_id
            subtitlesData= self._download_json(getSubtitleFilesForMedia, getSubtitleFilesForMedia)
            subtitles = {}

            keysTranslate = {
                'ger': 'de',
                'deu': 'de',
                'eng': 'en',
                'epo': 'es',
                'fre': 'fr',
                'fra': 'fr',
                'ita': 'it',
                'por': 'pt',
                'jpn': 'ja',
                }

            for item in subtitlesData['subtitleFiles']:
                item['ext'] = 'srt'
                key = item['subtitleFileCode']
                key = keysTranslate.get(key, key)
                subtitles[key] = [{
                    'ext': 'srt',
                    'url': item['subtitleFileUrl']
                }]
            result['subtitles'] = subtitles
        except Exception as e:
            print(e)
            pass
        finally:
            return result