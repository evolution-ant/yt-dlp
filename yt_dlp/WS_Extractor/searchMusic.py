# coding: utf-8

import re
import json
from operator import itemgetter
from difflib import SequenceMatcher as SM

from ..extractor.common import InfoExtractor

from ..utils import (
    compat_urllib_parse_urlencode,
    parse_duration,
)

class searchMusicIE(InfoExtractor):
    _VALID_URL = r'searchMusic://metaTitle=(.+)?&metaArtist=(.+)?&(?:duration=(.+)?|duration=)'
    _TEST = {
        'url': 'http://gb.napster.com/artist/madness/album/keep-moving-salvo/track/wings-of-a-dove',
    }

    def _real_extract(self, url):
        mobj = re.search(self._VALID_URL, url)
        metaTitle = mobj.group(1)
        metaArtist = mobj.group(2)
        duration = mobj.group(3) if mobj.group(3) else '0'
        result = self._get(metaTitle, metaArtist, duration)
        url = result['id'] if result['id'] != '' else None
        if url:
            entries = []
            entries.append(self.url_result(url, ie='youtube'))
            return self.playlist_result(entries)

    def getAllEntriesSequenceMatcherRatio(self, title, artist, entries, TopCount = 10, fun1 = False):
            result = []
            i = 0
            for entry in entries['entries']:
                if i > TopCount: break
                try:
                    if fun1:
                        if re.match(title, entry['title'], re.IGNORECASE):
                            entry['ratio'] = 0
                            if re.match(artist, entry['title'], re.IGNORECASE):
                                entry['ratio'] = 1
                            result.append(entry)
                    else:
                        ratio = SM(None, artist + ' '+ title, entry['title']).ratio()
                        if ratio >= 0.4:
                            result.append(entry)
                except:
                    continue
            return result

    def getAllVideosInfo(self, entries):
        key = ''
        for entry in entries:
            try:
                key += ',' + entry['id']
            except:
                pass
        query_infos_url = 'https://www.googleapis.com/youtube/v3/videos?part=snippet%2Cconte' \
                          'ntDetails&key=AIzaSyBW7ikTCKkhOZqSPUPkf5xVw12cjYKI5Ag&id=' + key
        return self._download_json(query_infos_url, query_infos_url)

    def getApiAllEntriesSequenceMatcherRatio(self, title, artist, entries, TopCount = 10, fun1 = False):
            result = []
            i = 0
            for entry in entries:
                if i > TopCount: break
                try:
                    if fun1:
                        if re.match(title, entry['snippet']['title'], re.IGNORECASE):
                            entry['ratio'] = 0
                            if re.match(artist, entry['snippet']['title'], re.IGNORECASE):
                                entry['ratio'] = 1
                            result.append(entry)
                    else:
                        ratio = SM(None, artist + ' '+ title, entry['snippet']['title']).ratio()
                        if ratio >= 0.4:
                            result.append(entry)
                except:
                    continue
            return result

    def getApiAllVideosInfo(self, entries):
        key = ''
        for entry in entries:
            try:
                key += ',' + entry['id']['videoId']
            except:
                pass
        query_infos_url = 'https://www.googleapis.com/youtube/v3/videos?part=snippet%2Cconte' \
                          'ntDetails&key=AIzaSyBW7ikTCKkhOZqSPUPkf5xVw12cjYKI5Ag&id=' + key
        return self._download_json(query_infos_url, query_infos_url)


    def _get(self, metaTitle, metaArtist, duration):

        duration = parse_duration(duration)

        if re.sub(r'\(.*\)', '', metaTitle, 0) == metaTitle:
            queryList = [{'artist': metaArtist, 'title': metaTitle}, {'artist': '', 'title': metaTitle}]
        else:
            queryList = [{'artist': metaArtist,  'title': metaTitle},
                         {'artist': metaArtist,  'title': re.sub(r'\(.*\)', '', metaTitle, 0)},
                         {'artist': '', 'title': metaTitle}]

        for query in queryList:
            params = '%s %s'% (query['artist'],  query['title']) if query['artist'] != '' else ' %s' % query['title']
            query_url = 'https://www.youtube.com/results?' + compat_urllib_parse_urlencode({'search_query': str(params).encode('utf-8')})
            print('query_url:', query_url)
            videosInfo = None
            try:
                result = self._downloader.extract_info(query_url, download=False, process=False)
                entries = self.getAllEntriesSequenceMatcherRatio(query['title'],query['artist'], result)
                if len(entries) > 1:
                    videosInfo = self.getAllVideosInfo(entries)
            except:
                search_url = 'https://www.googleapis.com/youtube/v3/search?' \
                             '&part=id,snippet&key=AIzaSyBW7ikTCKkhOZqSPUPkf5xVw12cjYKI5Ag&maxResults=10&q=' + params
                try:
                    search_result = self._download_json(search_url, search_url)
                    entries = self.getApiAllEntriesSequenceMatcherRatio(query['title'],query['artist'], search_result['items'])
                    if len(entries) > 1:
                        videosInfo = self.getApiAllVideosInfo(entries)
                except Exception as ex:
                    # print ex
                    pass

            if videosInfo:
                bigList = []
                smallList = []
                for item in videosInfo['items']:
                    try:
                        duration2 = parse_duration(item['contentDetails']['duration'])
                        if duration == duration2:
                            return {'id': item['id'], 'title': item['snippet']['title'], 'duration': duration2}
                        elif duration > duration2:
                            smallList.append({'id': item['id'], 'title': item['snippet']['title'], 'duration': duration2})
                        else:
                            bigList.append({'id': item['id'], 'title': item['snippet']['title'], 'duration': duration2})
                    except:
                        pass
                smallList = sorted(smallList, cmp= lambda x,y : cmp(float(x), float(y)), key=itemgetter('duration'), reverse=True)
                bigList = sorted(bigList, cmp= lambda x,y : cmp(float(x), float(y)), key=itemgetter('duration'), reverse=False)
                if ((len(bigList) > 0) and  (bigList[0]['duration'] - duration < 5)):
                    return bigList[0]
                elif ((len(smallList) > 0) and (duration - smallList[0]['duration'] < 5)):
                    return  smallList[0]
        return {'id': '', 'title': '', 'ratio': ''}
