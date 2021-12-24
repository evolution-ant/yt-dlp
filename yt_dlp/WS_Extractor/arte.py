# encoding: utf-8


import re
import base64
from ..utils import int_or_none
from ..extractor.arte import ArteTVBaseIE

from ..compat import (
    compat_str,
)
from ..utils import (
    ExtractorError,
    int_or_none,
    qualities,
    try_get,
    unified_strdate,
)

def _extract_from_json_url(self, json_url, video_id, lang, title=None):
    info = self._download_json(json_url, video_id)
    player_info = info['videoJsonPlayer']

    vsr = try_get(player_info, lambda x: x['VSR'], dict)
    if not vsr:
        error = None
        if try_get(player_info, lambda x: x['custom_msg']['type']) == 'error':
            error = try_get(
                player_info, lambda x: x['custom_msg']['msg'], compat_str)
        if not error:
            error = 'Video %s is not available' % player_info.get('VID') or video_id
        raise ExtractorError(error, expected=True)

    upload_date_str = player_info.get('shootingDate')
    if not upload_date_str:
        upload_date_str = (player_info.get('VRA') or player_info.get('VDA') or '').split(' ')[0]

    title = (player_info.get('VTI') or title or player_info['VID']).strip()
    subtitle = player_info.get('VSU', '').strip()
    if subtitle:
        title += ' - %s' % subtitle

    info_dict = {
        'id': player_info['VID'],
        'title': title,
        'description': player_info.get('VDE'),
        'upload_date': unified_strdate(upload_date_str),
        'thumbnail': player_info.get('programImage') or player_info.get('VTU', {}).get('IUR'),
    }
    qfunc = qualities(['HQ', 'MQ', 'EQ', 'SQ'])

    LANGS = {
        'fr': 'F',
        'de': 'A',
        'en': 'E[ANG]',
        'es': 'E[ESP]',
    }

    langcode = LANGS.get(lang, lang)

    formats = []

    temp = {format_id : format_dict for format_id, format_dict in list(vsr.items()) if dict(format_dict).get('versionShortLibelle').lower() == lang}
    if temp:
        vsr = temp

    for format_id, format_dict in list(vsr.items()):

        f = dict(format_dict)
        versionCode = f.get('versionCode')
        l = re.escape(langcode)

        # Language preference from most to least priority
        # Reference: section 5.6.3 of
        # http://www.arte.tv/sites/en/corporate/files/complete-technical-guidelines-arte-geie-v1-05.pdf
        PREFERENCES = (
            # original version in requested language, without subtitles
            r'VO{0}$'.format(l),
            # original version in requested language, with partial subtitles in requested language
            r'VO{0}-ST{0}$'.format(l),
            # original version in requested language, with subtitles for the deaf and hard-of-hearing in requested language
            r'VO{0}-STM{0}$'.format(l),
            # non-original (dubbed) version in requested language, without subtitles
            r'V{0}$'.format(l),
            # non-original (dubbed) version in requested language, with subtitles partial subtitles in requested language
            r'V{0}-ST{0}$'.format(l),
            # non-original (dubbed) version in requested language, with subtitles for the deaf and hard-of-hearing in requested language
            r'V{0}-STM{0}$'.format(l),
            # original version in requested language, with partial subtitles in different language
            r'VO{0}-ST(?!{0}).+?$'.format(l),
            # original version in requested language, with subtitles for the deaf and hard-of-hearing in different language
            r'VO{0}-STM(?!{0}).+?$'.format(l),
            # original version in different language, with partial subtitles in requested language
            r'VO(?:(?!{0}).+?)?-ST{0}$'.format(l),
            # original version in different language, with subtitles for the deaf and hard-of-hearing in requested language
            r'VO(?:(?!{0}).+?)?-STM{0}$'.format(l),
            # original version in different language, without subtitles
            r'VO(?:(?!{0}))?$'.format(l),
            # original version in different language, with partial subtitles in different language
            r'VO(?:(?!{0}).+?)?-ST(?!{0}).+?$'.format(l),
            # original version in different language, with subtitles for the deaf and hard-of-hearing in different language
            r'VO(?:(?!{0}).+?)?-STM(?!{0}).+?$'.format(l),
        )

        for pref, p in enumerate(PREFERENCES):
            if re.match(p, versionCode):
                lang_pref = len(PREFERENCES) - pref
                break
        else:
            lang_pref = -1

        format = {
            'format_id': format_id,
            'preference': -10 if f.get('videoFormat') == 'M3U8' else None,
            'language_preference': lang_pref,
            'format_note': '%s, %s' % (f.get('versionCode'), f.get('versionLibelle')),
            'width': int_or_none(f.get('width')),
            'height': int_or_none(f.get('height')),
            'tbr': int_or_none(f.get('bitrate')),
            'quality': qfunc(f.get('quality')),
        }

        if f.get('mediaType') == 'rtmp':
            format['url'] = f['streamer']
            format['play_path'] = 'mp4:' + f['url']
            format['ext'] = 'flv'
        else:
            format['url'] = f['url']

        formats.append(format)

    self._check_formats(formats, video_id)
    self._sort_formats(formats)

    info_dict['formats'] = formats
    return info_dict

ArteTVBaseIE._extract_from_json_url = _extract_from_json_url