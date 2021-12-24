# coding: utf-8
# 需要心跳的一支，特别处理它


from ..extractor.niconico import NiconicoIE as InconicoBase
from ..utils import (
    float_or_none,
    remove_start
)
import json

class NiconicoIE(InconicoBase):
    def _extract_format_for_quality(self, api_data, video_id, audio_quality, video_quality):
        def yesno(boolean):
            return 'yes' if boolean else 'no'

        session_api_data = api_data['video']['dmcInfo']['session_api']
        session_api_endpoint = session_api_data['urls'][0]

        format_id = '-'.join([remove_start(s['id'], 'archive_') for s in [video_quality, audio_quality]])

        session_response = self._download_json(
            session_api_endpoint['url'], video_id,
            query={'_format': 'json'},
            headers={'Content-Type': 'application/json'},
            note='Downloading JSON metadata for %s' % format_id,
            data=json.dumps({
                'session': {
                    'client_info': {
                        'player_id': session_api_data['player_id'],
                    },
                    'content_auth': {
                        'auth_type': session_api_data['auth_types'][session_api_data['protocols'][0]],
                        'content_key_timeout': session_api_data['content_key_timeout'],
                        'service_id': 'nicovideo',
                        'service_user_id': session_api_data['service_user_id']
                    },
                    'content_id': session_api_data['content_id'],
                    'content_src_id_sets': [{
                        'content_src_ids': [{
                            'src_id_to_mux': {
                                'audio_src_ids': [audio_quality['id']],
                                'video_src_ids': [video_quality['id']],
                            }
                        }]
                    }],
                    'content_type': 'movie',
                    'content_uri': '',
                    'keep_method': {
                        'heartbeat': {
                            'lifetime': session_api_data['heartbeat_lifetime']
                        }
                    },
                    'priority': session_api_data['priority'],
                    'protocol': {
                        'name': 'http',
                        'parameters': {
                            'http_parameters': {
                                'parameters': {
                                    'http_output_download_parameters': {
                                        'use_ssl': yesno(session_api_endpoint['is_ssl']),
                                        'use_well_known_port': yesno(session_api_endpoint['is_well_known_port']),
                                    }
                                }
                            }
                        }
                    },
                    'recipe_id': session_api_data['recipe_id'],
                    'session_operation_auth': {
                        'session_operation_auth_by_signature': {
                            'signature': session_api_data['signature'],
                            'token': session_api_data['token'],
                        }
                    },
                    'timing_constraint': 'unlimited'
                }
            }))

        # 记录心跳数据
        api_url = session_api_endpoint['url'] + '/' + session_response['data']['session']['id'] + '?_format=json&_method=PUT'
        data = json.dumps(session_response['data'])
        resolution = video_quality.get('resolution', {})

        return {
            'url': session_response['data']['session']['content_uri'],
            'format_id': format_id,
            'ext': 'mp4',  # Session API are used in HTML5, which always serves mp4
            'abr': float_or_none(audio_quality.get('bitrate'), 1000),
            'vbr': float_or_none(video_quality.get('bitrate'), 1000),
            'height': resolution.get('height'),
            'width': resolution.get('width'),
            'heartbeat_url': api_url,
            'heartbeat_data': data,
        }