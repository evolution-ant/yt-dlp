# coding: utf-8

import re
import threading
from ..extractor.common import InfoExtractor

from ..utils import (
    compat_urllib_parse,
    parse_duration,
)

class YoutubeExternallinkSiteIE(InfoExtractor):
    _VALID_URL = r'https?://(.*\.)napster.com/artist/(.*)track/.*'
    _TEST = {
        'url': 'http://gb.napster.com/artist/madness/album/keep-moving-salvo/track/wings-of-a-dove',
    }
    def __init__(self):
        self._lock = threading.Lock()

    def getVideoInfo(self, vid):
        url = 'https://www.googleapis.com/youtube/v3/videos?part=snippet%2CcontentDetails' \
                  '&key=AIzaSyBW7ikTCKkhOZqSPUPkf5xVw12cjYKI5Ag&id=' + vid
        data = self._download_json(url, url)
        return {
            'id': vid,
            'url': 'https://www.youtube.com/watch?v=%s' % vid,
            'title': data['items'][0]['snippet']['title'],
            'thumbnail': data['items'][0]['snippet']['thumbnails']['default'],
            'description': data['items'][0]['snippet']['description'],
            'duration': parse_duration(data['items'][0]['contentDetails']['duration']),
        }

    def getEntries(self, querylist):
        entries = []
        for track, artist, duration in querylist:
            entries.append({
                'id': None,
                'title': track,
                'artist': artist,
                'duration': duration,
            })
        return entries

    def appendEntry(self, entries, entry):
        self._lock.acquire()
        try:
            entries.append(entry)
        finally:
            self._lock.release()

    def getVideoInfoEx(self, url, artist, track, duration, entries):
        print(url)
        try:
            data = self._download_json(url, url)
            info = self.getVideoInfo(data['id'])
            if info.get('duration','') == '':
                info['duration'] = duration
            if info.get('artist','') == '':
                info['artist'] = artist
            self.appendEntry(entries, info)
        except Exception as e:
            '''
            self.appendEntry(entries, {
                'id': None,
                'title': track,
                'artist': artist,
                'duration': duration,
            })
        '''
            print('getVideoInfo %s exception: %s' % (url, e.message))
            pass

    def getEntriesEx(self, querylist):
        if (len(querylist)>0):
            list = []
            if len(querylist[0]) > 2:
                list = [('http://groovesharks.org/music/getYoutube/?' +
                    compat_urllib_parse.urlencode({'track': track, 'artist': artist}), artist, track, duration) for track, artist, duration in querylist]
            else:
                list = [('http://groovesharks.org/music/getYoutube/?' +
                    compat_urllib_parse.urlencode({'track': track, 'artist': artist}), artist, track, '') for artist, track in querylist]
            threadList = []
            entries = []
            for url, artist, track, duration in list:
                try:
                    t = threading.Thread(target=self.getVideoInfoEx, args=(url, artist, track, duration, entries))
                    threadList.append(t)
                    t.setDaemon(True)
                    t.start()
                except:
                    pass
            for t in threadList:
                t.join()
            return entries
        else:
            return []


    def getVideoInfByID(self, VID, entries):
        try:
            info = self.getVideoInfo(VID)
            if info.get('duration','') == '':
                info['duration'] = '3:40'
            if info.get('artist','') == '':
                info['artist'] = 'unkown'
            self.appendEntry(entries, info)
        except Exception as e:
            '''
            self.appendEntry(entries, {
                'id': None,
                'title': track,
                'artist': artist,
                'duration': duration,
            })
        '''
            print('getVideoInfo %s exception: %s' % (VID, e.message))
            pass

    def getEntriesByID(self, VIDS):
        if (len(VIDS)>0):
            threadList = []
            entries = []
            for ID in VIDS:
                try:
                    t = threading.Thread(target=self.getVideoInfByID, args=(ID, entries))
                    threadList.append(t)
                    t.setDaemon(True)
                    t.start()
                except:
                    pass
            for t in threadList:
                t.join()
            return entries
        else:
            return []
