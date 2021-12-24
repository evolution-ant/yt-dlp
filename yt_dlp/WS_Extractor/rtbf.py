# encoding: utf-8


from ..extractor.rtbf import (
    RTBFIE as OldRtbfIE
)

class RtbfIE(OldRtbfIE):
    def _real_extract(self, url):
        result = super(RtbfIE, self)._real_extract(url)
        # 加入高低排序
        if result.get('formats', None):
            for i, format in enumerate(result['formats']):
                format['preference'] = i

        return result