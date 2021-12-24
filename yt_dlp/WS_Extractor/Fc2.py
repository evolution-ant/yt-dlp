

import re

from ..extractor.common import (
    InfoExtractor,
)
from ..extractor.fc2 import (
    FC2IE as base,
    FC2EmbedIE as base2,
)

class FC2IE(base):
    _VALID_URL = r'^(?:https?://(?:video\.fc2\.com|jinniumovie\.be)/(?:[^/]+/)*content/|fc2:)(?P<id>[^/]+)'

class FC2EmbedIE(base2):
    _VALID_URL = r'https?://video\.(?:fc2\.com|jinniumovie\.be)/flv2\.swf\?(?P<query>.+)'