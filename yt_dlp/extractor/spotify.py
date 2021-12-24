# coding: utf-8
from __future__ import unicode_literals
import time
import json
import re
from math import ceil
from functools import cmp_to_key

from .common import InfoExtractor

from ..compat import (
    compat_urllib_parse
)
from ..utils import (
    unsmuggle_url,
    sanitized_Request,
    ExtractorError,
    parse_duration,
)

from difflib import SequenceMatcher


# @mtrace
class SpotifyIE(InfoExtractor):
    # region Youtube Music Search
    _youtube_access_token = ""
    _YOUTUBE_MUSIC_URL = "https://music.youtube.com"

    def attr(self, o, f, d=''):
        try:
            return f(o)
        except Exception:
            return d

    def headers(self, referer):
        return {
            'dnt': '1',
            'content-type': 'application/json',
            'origin': self._YOUTUBE_MUSIC_URL,
            'referer': referer,
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/75.0.3770.142 Safari/537.36',
        }

    def post_data(self, q=None, params=None):
        obj = json.loads(
            '{"context":{"client":{"clientName":"WEB_REMIX","clientVersion":"0.1","hl":"en","gl":"US","experimentIds":[],"utcOffsetMinutes":480,"locationInfo":{"locationPermissionAuthorizationStatus":"LOCATION_PERMISSION_AUTHORIZATION_STATUS_UNSUPPORTED"},"musicAppInfo":{"musicActivityMasterSwitch":"MUSIC_ACTIVITY_MASTER_SWITCH_INDETERMINATE","musicLocationMasterSwitch":"MUSIC_LOCATION_MASTER_SWITCH_INDETERMINATE"}},"capabilities":{},"request":{"internalExperimentFlags":[{"key":"music_enable_you_there","value":"true"},{"key":"music_web_enable_library_v2","value":"true"},{"key":"music_web_enable_album_details_more_button","value":"true"},{"key":"kevlar_enable_vimio_logging","value":"true"},{"key":"music_web_enable_madison_account_support","value":"true"},{"key":"music_web_send_initial_endpoint_for_playlist_urls","value":"true"},{"key":"music_web_disable_mobile_miniplayer","value":"true"},{"key":"music_display_empty_playlists","value":"true"},{"key":"music_enable_responsive_list_item_mobile_web_treatment","value":"true"},{"key":"enable_ve_tracker_key","value":"true"},{"key":"debug_forced_promo_id","value":""},{"key":"music_web_like_buttons_on_album_detail_page","value":"true"},{"key":"client_streamz_web_flush_count","value":"2"},{"key":"music_web_playlist_id_in_responsive_list_play_button","value":"true"},{"key":"music_entitlement_subscription_reads","value":"true"},{"key":"music_web_disable_home_background_fetch","value":"true"},{"key":"kevlar_enable_vimio_callback","value":"true"},{"key":"music_enable_mix_free_tier_curated_playlists","value":"true"},{"key":"music_show_buffering_spinner_in_player_bar","value":"true"},{"key":"music_web_enable_prelive_bylines","value":"true"},{"key":"music_web_track_focus_via_tab_key_in_carousels","value":"true"},{"key":"music_web_enable_start_radio_from_album","value":"true"},{"key":"ad_to_video_use_gel","value":"true"},{"key":"music_web_play_buttons_on_album_detail_page","value":"true"},{"key":"music_enable_plds_random_shuffle_in_watch_next","value":"true"},{"key":"music_enable_prelive_bylines_localization","value":"true"},{"key":"music_web_enable_prebuffering","value":"true"},{"key":"log_foreground_heartbeat_music_web","value":"true"},{"key":"music_web_enable_player_attestation","value":"true"},{"key":"polymer2_not_shady_build","value":"true"},{"key":"enable_premium_voluntary_pause","value":"true"},{"key":"music_enable_see_all_expand_buttons","value":"true"},{"key":"music_web_fill_page_type_in_playlist_endpoints","value":"true"},{"key":"kevlar_use_vimio_behavior","value":"true"},{"key":"music_fill_text_endpoints_in_two_row_item_renderer","value":"true"},{"key":"music_enable_prelive_bylines","value":"true"},{"key":"kevlar_attach_vimio_behavior","value":"true"},{"key":"music_web_body_line_height","value":"1.4"},{"key":"web_logging_max_batch","value":"100"},{"key":"music_web_enable_audio_only_playback","value":"true"},{"key":"music_web_autoplay_blocked_prompt","value":"true"},{"key":"music_web_handle_active_session_changes","value":"true"},{"key":"music_enable_playlist_context_menu_share_endpoint","value":"true"},{"key":"ignore_empty_xhr","value":"true"},{"key":"music_web_title_line_height","value":"1.2"},{"key":"music_enable_nitrate_based_tastebuilder_onboarding_flow","value":"true"},{"key":"music_web_enable_nerd_stats","value":"true"},{"key":"music_web_service_worker_caching_strategy","value":""},{"key":"music_enable_improve_your_recommendations_setting","value":"true"},{"key":"attach_child_on_gel_web","value":"true"},{"key":"music_enable_navigation_client_streamz","value":"true"},{"key":"music_web_enable_focus_tracker","value":"true"},{"key":"kevlar_import_vimio_behavior","value":"true"},{"key":"enable_client_streamz_web","value":"true"},{"key":"music_playlist_detail_use_country_restrictions_from_ytms","value":"true"},{"key":"music_library_shelf_item_fetch_count_override","value":"25"},{"key":"web_gel_debounce_ms","value":"10000"},{"key":"music_web_session_check_interval_millis","value":"120000"},{"key":"music_enable_album_entity_getbrowse","value":"true"},{"key":"music_web_confirm_add_existing_song_to_playlist","value":"true"},{"key":"enable_web_music_player_error_message_renderer","value":"true"},{"key":"music_web_app_non_teamfood","value":"true"},{"key":"enable_mixed_direction_formatted_strings","value":"true"},{"key":"music_web_enable_kav_prompt","value":"true"},{"key":"video_to_ad_use_gel","value":"true"},{"key":"music_web_enable_rtl","value":"true"},{"key":"music_web_show_player_bezel","value":"true"},{"key":"client_streamz_web_flush_interval_seconds","value":"60"},{"key":"music_enable_share_for_search_albums","value":"true"},{"key":"enable_playability_filtering_in_entity_manager","value":"true"},{"key":"enable_memberships_and_purchases","value":"true"},{"key":"enable_video_list_browse_for_topical_mixes","value":"true"},{"key":"web_gel_timeout_cap","value":"true"},{"key":"music_enable_album_page_alternate_releases_shelf","value":"true"},{"key":"music_web_teamfood_dogfood_logos","value":"true"},{"key":"music_enable_responsive_list_items_for_search","value":"true"},{"key":"music_web_hide_carousel_buttons_on_non_hover_devices","value":"true"},{"key":"music_web_send_initial_endpoint_for_landing_page_urls","value":"true"},{"key":"flush_onbeforeunload","value":"true"},{"key":"polymer_simple_endpoint","value":"true"},{"key":"user_preference_collection_initial_browse_id","value":"FEmusic_tastebuilder"},{"key":"force_music_enable_outertube_tastebuilder_browse","value":"true"},{"key":"music_web_signup_canonical_base_urls","value":"true"},{"key":"music_web_serve_app_for_scrapers","value":"true"},{"key":"music_web_embed_initial_innertube_data","value":"true"}],"sessionIndex":{}},"user":{"enableSafetyMode":false}},"query":"Soon You’ll Get Better (feat. Dixie Chicks) Taylor Swift","suggestStats":{"validationStatus":"VALID","parameterValidationStatus":"VALID_PARAMETERS","clientName":"youtube-music","searchMethod":"ENTER_KEY","inputMethod":"KEYBOARD","originalQuery":"Soon You’ll Get Better (feat. Dixie Chicks) Taylor Swift","availableSuggestions":[{"index":0,"type":0}],"zeroPrefixEnabled":true}}')
        obj['query'] = q
        if params is not None:
            obj['params'] = params
        return json.dumps(obj, ensure_ascii=False)

    def scrape(self, url, data, headers, validator=None, method='POST', tries=6):
        res = None
        for i in range(0, tries):
            try:
                request = sanitized_Request(url)
                for hkey in headers:
                    request.add_header(hkey, headers[hkey])
                if method == 'POST':
                    data = data.encode("utf-8", 'ignore')
                    content = self._download_webpage(request, None, data=data, timeout=15, headers=headers, fatal=False)
                else:
                    content = self._download_webpage(request, None, timeout=15, headers=headers, fatal=False)

                if callable(validator):
                    if validator(content):
                        res = content
                        break
                else:
                    res = content
                    break
            except Exception as e:
                if i == tries - 1:
                    self.to_screen('scrape, ' + str(e))

            time.sleep(0.1 + 10 * i)

        return res

    def request_key(self, q):
        if self._youtube_access_token:
            return self._youtube_access_token

        resp = self.scrape(self._YOUTUBE_MUSIC_URL + '/search?q=' + q, '',
                           headers=self.headers(referer='%s/search?%s' % (
                           self._YOUTUBE_MUSIC_URL, compat_urllib_parse.urlencode({'q': q}))),
                           validator=lambda r: 'INNERTUBE_API_KEY' in r,
                           method='GET')
        if resp is None:
            self.to_screen('request internal key failed')
            return None
        obj = json.loads(resp.split('<script >ytcfg.set(')[1].split(');</script>')[0])
        if 'INNERTUBE_API_KEY' in obj:
            self._youtube_access_token = obj['INNERTUBE_API_KEY']
            return obj['INNERTUBE_API_KEY']
        else:
            return None

    def parse_title(self, obj):
        if 'simpleText' in obj:
            return obj['simpleText']
        elif 'runs' in obj:
            if len(obj['runs']) > 0:
                if 'text' in obj['runs'][0]:
                    return obj['runs'][0]['text']
                else:
                    return ''
            else:
                return ''
        elif obj == {}:
            return ''
        else:
            return ''

    def parse_entries(self, data):
        if len(data) <= 0:
            raise ExtractorError("No data is matched")
        else:
            return data

    def extract_youtube_songs(self, obj):
        try:
            shelf = obj['contents']['sectionListRenderer']['contents']
            song_items = None
            for songs in shelf:
                if "musicShelfRenderer" in songs:
                    song_items = songs['musicShelfRenderer']['contents']
                    break

            result = []
            for item in song_items:
                if 'musicResponsiveListItemRenderer' not in item:
                    continue
                item = item['musicResponsiveListItemRenderer']
                video_id = self.attr(
                    item,
                    lambda o: o['overlay']['musicItemThumbnailOverlayRenderer']['content']['musicPlayButtonRenderer']
                        ['playNavigationEndpoint']['watchEndpoint']['videoId']
                )
                _data = {
                    '_type': "url",
                    'id': video_id,
                    'uploader': '',
                    'title': self.attr(item, lambda o: self.parse_title(
                        o['flexColumns'][0]['musicResponsiveListItemFlexColumnRenderer']['text'])),
                    'artist': self.attr(item, lambda o: self.parse_title(
                        o['flexColumns'][2]['musicResponsiveListItemFlexColumnRenderer']['text'])),
                    'duration': parse_duration(self.attr(item, lambda o: self.parse_title(
                        o['flexColumns'][4]['musicResponsiveListItemFlexColumnRenderer']['text']))),
                    "webpage_url": "https://www.youtube.com/watch?v=%s" % video_id,
                }
                if _data['id'] != '' and _data['title'] != '' and _data['artist'] != '' and _data['duration'] != '':
                    result.append(_data)
        except Exception:
            result = []
        return result

    # 生成搜索结果列表
    def search_keyword(self, q):
        self._verbose("Info:[search key] " + json.dumps(q))
        key = self.request_key(q)
        url = '%s/youtubei/v1/search?alt=json&key=%s' % (self._YOUTUBE_MUSIC_URL, key)
        resp = self.scrape(
            url,
            self.post_data(q),
            headers=self.headers(
                referer='%s/search?%s' % (self._YOUTUBE_MUSIC_URL, compat_urllib_parse.urlencode({'q': q}))),
            validator=lambda r: 'contents' in json.loads(r))
        if resp is None:
            self.to_screen('search_keyword, request %s failed' % url)
            return

        obj = json.loads(resp)
        songs = []
        top_results = []
        videos = []
        for shelf in obj['contents']['sectionListRenderer']['contents']:
            if 'musicShelfRenderer' in shelf:
                category = self.parse_title(shelf['musicShelfRenderer']['title'])
                temp_obj = {"contents": {"sectionListRenderer": {"contents": [shelf]}}}

                if category == 'Songs':
                    songs = self.extract_youtube_songs(temp_obj)
                elif category == 'Top result':
                    top_results = self.extract_youtube_songs(temp_obj)
                elif category == 'Videos':
                    videos = self.extract_youtube_songs(temp_obj)

        return songs, top_results, videos

    # endregion Youtube Music Search

    _spotify_access_token = ''

    def _filter_by_artist(self, youtube_songs, spotify_song):
        # .lower() 24kGoldn -> 24KGoldn
        # Rory Fresco -> Rory Fresco & Kid Ink
        # YNW Melly , 9lokknine -> YNW Melly & 9lokknine
        #                       -> YNW Melly
        #                       -> 9lokknine
        # Nature Recordings     -> Outside Broadcast Recordings
        # "Tyler, The Creator"  -> Tyler, The Creator
        if spotify_song['artist'] == '' or \
                spotify_song['artist'].lower() == 'Various Artists'.lower():
            return youtube_songs

        def has_common_artists(spotify_artist, youtube_artist):
            return len(
                set([v.strip() for v in spotify_artist.split(',')]).intersection(
                set([v.strip() for v in youtube_artist.split('&')])
            )) > 0

        def real_artist(s):
            for c in "’'…":
                s = s.replace(c, ' ')
            return s

        res = []
        for a_song in youtube_songs:
            if real_artist(spotify_song['artist'].lower()) == real_artist(a_song['artist'].lower()):
                res.append(a_song)
            elif has_common_artists(real_artist(spotify_song['artist'].lower()),
                              real_artist(a_song['artist'].lower())):
                res.append(a_song)
            else:
                pass

        self._verbose("Info:[_filter_by_artist] " + json.dumps(res))
        return res

    def _filter_by_title(self, youtube_songs, spotify_song):
        # Mac 10 -> # Mac 10 (feat. Lil Baby & Lil Duke)
        # Sunflower (Remix) [with Swae Lee, Nicky Jam, and Prince Royce] -> Sunflower (Spider-Man: Into the Spider-Verse)
        if spotify_song['title'] == '':
            return youtube_songs

        def real_title(s):
            s = s.split('(')[0].split('[')[0].split('{')[0]
            for c in "’'\u2026":
                s = s.replace(c, ' ')
            return s

        res = []
        for a_song in youtube_songs:
            a_song_title = a_song['title'].lower()
            spotify_song_title = spotify_song['title'].lower()
            matched = real_title(a_song_title) in real_title(spotify_song_title) or \
                      real_title(spotify_song_title) in real_title(a_song_title)
            if matched:
                res.append(a_song)
            # elif self.similar(real_title(a_song_title), real_title(spotify_song_title)) >= 0.5:
            #    res.append(a_song)
            else:
                pass

        self._verbose("Info:[_filter_by_title] " + json.dumps(res))
        return res

    def _order_by_title_artist(self, youtube_songs, spotify_song):
        # Sunflower (Remix) [with Swae Lee, Nicky Jam, and Prince Royce] Various Artists
        #   Sunflower (Remix) Shaun Reynolds & Esmée Denters
        #   Sunflower (Spider-Man: Into the Spider-Verse) Post Malone, Swae Lee & Swae Lee
        def compare(song1, song2):
            song1_text = song1['title'] + '' + song1['artist']
            song2_text = song2['title'] + '' + song2['artist']
            spotify_text = spotify_song['title'] + '' + spotify_song['artist']
            return SequenceMatcher(None, song1_text.lower(), spotify_text.lower()).quick_ratio() >= \
                   SequenceMatcher(None, song2_text.lower(), spotify_text.lower()).quick_ratio()
        return sorted(youtube_songs, key=cmp_to_key(compare))

    def _choose_best_music(self, youtube_songs, spotify_song):
        res = youtube_songs
        res = self._filter_by_artist(res, spotify_song)  # 艺术家不能全匹配则丢弃
        res = self._filter_by_title(res, spotify_song)  # 标题分词后匹配度低则丢弃
        res = self._order_by_title_artist(res, spotify_song) # 根据相似度排序
        return res[0] if len(res) > 0 else None

    def _search_from_youtube(self, spotify_songs):
        return self.search_keyword(spotify_songs['title'] + " " + spotify_songs['artist'])

    def _get_entries_from_youtube(self, spotify_songs):
        entries = []
        search_results_of_entries = []

        for a_song in spotify_songs:
            self._verbose("Info:[match spotify song] " + json.dumps(a_song))

            songs_search_results, top_search_results, videos_search_results = self._search_from_youtube(a_song)
            self._verbose("Info:[songs_search_results] " + json.dumps(songs_search_results))
            self._verbose("Info:[top_search_results] " + json.dumps(top_search_results))
            self._verbose("Info:[videos_search_results] " + json.dumps(videos_search_results))

            best_song = None
            if len(songs_search_results) > 0:
                best_song = self._choose_best_music(songs_search_results, a_song)
            if best_song is None and len(top_search_results) > 0:
                best_song = self._choose_best_music(top_search_results, a_song)
            if best_song is None and len(videos_search_results) > 0:
                best_song = self._choose_best_music(videos_search_results, a_song)
            if best_song:
                self._verbose("Success:" + json.dumps(a_song))
                entries.append(best_song)
            else:
                self._verbose("Fail:" + json.dumps(a_song))
                entries.append(None)

        return entries, search_results_of_entries

    def _request_spotify_token(self, url, video_id, tries=6):
        if self._spotify_access_token:
            return self._spotify_access_token

        for i in range(tries):
            self._download_webpage(url, video_id, fatal=False)
            try:
                self._spotify_access_token = self._get_cookies(url).get('wp_access_token').value
                return self._spotify_access_token
            except Exception as e:
                time.sleep(0.1 + 10 * i)
                continue

        raise ExtractorError('request access token error')

    def _request_spotify(self, url, video_id=None, data=None, web_page_url=None, tries=6):
        access_token = self._request_spotify_token(web_page_url, video_id)
        for i in range(tries):
            try:
                result = self._download_json(url, video_id,
                                           data=data.encode("utf-8") if data is not None else None,
                                           headers={"Authorization": "Bearer %s" % access_token},
                                           fatal=False)
                if isinstance(result, dict):
                    return result
                continue
            except Exception as e:
                time.sleep(0.1 + 10 * i)
                # solve requests 429
                if 'too many requests' in str(e).lower():
                    access_token = self._request_spotify_token(web_page_url, video_id)
                continue
        raise ExtractorError('request spotify  timeout')

    def similar(self, title1, title2):
        s1 = set([o for o in title1.split(' ') if o != ''])
        s2 = set([o for o in title2.split(' ') if o != ''])
        return len(s1.intersection(s2)) / len(s1)

    def _verbose(self, msg=""):
        if self._downloader.params.get('test_info'):
            print(msg)


class SpotifyPlaylistIE(SpotifyIE):
    # https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M
    _VALID_URL = r'https?://open\.spotify\.com/playlist/(?P<video_id>[0-9A-Za-z_-]+)'

    def _real_extract(self, url):
        web_page_url, smuggled_data = unsmuggle_url(url, {})
        video_id = re.match(self._VALID_URL, web_page_url).group('video_id')

        # 获取json数据
        playlist = self._request_spotify(
            "https://api.spotify.com/v1/playlists/%s" % video_id, video_id, web_page_url= web_page_url)
        songs = []
        for item in playlist['tracks']['items']:
            if 'track' in item and item['track']:
                artists = ''
                for artist in item['track']['album']['artists']:
                    artists += ' , ' + self.attr(artist, lambda o: artist['name'])
                artists = artists.lstrip(' , ')

                songs.append({
                    'title': self.attr(item, lambda o: o['track']['name']),
                    'duration': ceil(self.attr(item, lambda o: o['track']['duration_ms'], d=0) / 1000),
                    'artist': artists,
                    'album': self.attr(playlist, lambda o: o['name']),
                })
        if len(songs) <= 0:
            raise ExtractorError("get song exception")
        matched_entries, search_results = self.parse_entries(self._get_entries_from_youtube(songs))
        return {
            "_type": "playlist",
            'id': video_id,
            'title': self.attr(playlist, lambda o: o['name']),
            'webpage_url': web_page_url,
            "entries": [o for o in matched_entries if o is not None],
            "matched_entries": matched_entries,
            "origin_entries": songs,
            'search_results': search_results,
            "description": self.attr(playlist, lambda o: o['description']),
            "thumbnail": self.attr(playlist, lambda o: o['images'][0]['url'])
        }


class SpotifyAlbumIE(SpotifyIE):
    # https://open.spotify.com/album/4FFBjcmX06VmazABtpRMyv
    _VALID_URL = r'https?://open\.spotify\.com/album/(?P<video_id>[0-9A-Za-z_-]+)'

    def _real_extract(self, url):
        web_page_url, smuggled_data = unsmuggle_url(url, {})
        video_id = re.match(self._VALID_URL, web_page_url).group('video_id')
        try:
            album = self._request_spotify(
                "https://api.spotify.com/v1/albums/%s" % video_id, video_id, web_page_url=web_page_url)
            if len(album) <= 0:
                raise ExtractorError("get spotify song exception")
        except Exception:
            raise ExtractorError('The data obtained was illegal')
        songs = []
        for item in album['tracks']['items']:
            artists = ''
            for artist in album['artists']:
                artists += ' , ' + self.attr(artist, lambda o: artist['name'])
            artists = artists.lstrip(' , ')

            songs.append({
                'title': self.attr(item, lambda o: o['name']),
                'duration': ceil(self.attr(item, lambda o: o['duration_ms'], d=0) / 1000),
                'artist': artists,
                'album': self.attr(album, lambda o: o['name']),
            })

        if len(songs) <= 0:
            raise ExtractorError("get song exception")

        matched_entries, search_results = self.parse_entries(self._get_entries_from_youtube(songs))
        return {
            "_type": "playlist",
            'id': video_id,
            'title': self.attr(album, lambda o: o['name']),
            'webpage_url': web_page_url,
            "entries": [o for o in matched_entries if o is not None],
            "matched_entries": matched_entries,
            "origin_entries": songs,
            'search_results': search_results,
            "description": self.attr(album, lambda o: o['name']),
            "thumbnail": self.attr(album, lambda o: o['images'][0]['url'])
        }


class SpotifyTrackIE(SpotifyIE):
    # https://open.spotify.com/track/7AjfklMN4WpQYz5FkT4E66
    # https://open.spotify.com/embed/track/51RSeoiKEgJFJUqaEGx9hW?utm_campaign=twitter-player&utm_source=open&utm_medium=twitter
    _VALID_URL = r'https?://open\.spotify\.com/(?:track|embed/track)/(?P<video_id>[0-9A-Za-z_-]+)'

    def _real_extract(self, url):
        web_page_url, smuggled_data = unsmuggle_url(url, {})
        video_id = re.match(self._VALID_URL, web_page_url).group('video_id')
        try:
            data = self._request_spotify(
                "https://api.spotify.com/v1/tracks/%s?market=%s" % (video_id, "ES"),
                video_id,
                web_page_url=web_page_url)
        except Exception:
            raise ExtractorError('The data obtained was illegal')

        artists = ''
        for artist in data['album']['artists']:
            artists += ' , ' + self.attr(artist, lambda o: artist['name'])
        artists = artists.lstrip(' , ')

        songs = [{
            'title': self.attr(data, lambda o: o['album']['name']),
            'duration': ceil(self.attr(data, lambda o: o['duration_ms'], d=0) / 1000),
            'artist': artists,
            'album': self.attr(data, lambda o: o['name']),
        }]

        if len(songs) <= 0:
            raise ExtractorError("get song exception")

        matched_entries, search_results = self.parse_entries(self._get_entries_from_youtube(songs))
        return {
            "_type": "playlist",
            'id': video_id,
            'title': self.attr(data, lambda o: o['album']['name']),
            'webpage_url': web_page_url,
            "entries": [o for o in matched_entries if o is not None],
            "matched_entries": matched_entries,
            "origin_entries": songs,
            'search_results': search_results,
            "thumbnail": self.attr(data, lambda o: o['album']['images'][0]['url'])
        }


class SpotifyArtistIE:
    # https://open.spotify.com/artist/7wLyGTO9vUS7ndlq4BvBGe
    _VALID_URL = r'https?://open\.spotify\.com/artist/(?P<video_id>[0-9A-Za-z_-]+)'


class SpotifySearchIE:
    # https://open.spotify.com/search/lady
    _VALID_URL = r'https?://open\.spotify\.com/search/(?P<video_id>[0-9A-Za-z_-]+)'
