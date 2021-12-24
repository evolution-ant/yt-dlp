#encoding: utf-8


import re
from ..utilsEX import downloadWebPage_BYHeadlessBrowser
from ..extractor.openload import PhantomJSwrapper

def __init__(self, extractor, required_version=None, timeout=10000):
    self.extractor = extractor


def _save_cookies(self, url):
    pass


def _load_cookies(self):
    pass


def get(self, url, html=None, video_id=None, note=None, note2='Executing JS on webpage', headers={}, jscode='saveAndExit();'):
    html, _ = downloadWebPage_BYHeadlessBrowser(url)
    return re.sub('<span\s+id="stream([^"]+)', '<span id="streamurl', html), None

PhantomJSwrapper.__init__ = __init__
PhantomJSwrapper._load_cookies = _load_cookies
PhantomJSwrapper._save_cookies = _save_cookies
PhantomJSwrapper.get = get