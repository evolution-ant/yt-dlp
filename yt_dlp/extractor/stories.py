#!/usr/bin/env python
from __future__ import unicode_literals
from .common import InfoExtractor
import urllib.request
import urllib.parse
import json

class STORIESIE(InfoExtractor):
    def _extract_feed_info(self, id):

        licenseRequestUrl = 'https://stories.audible.com/audibleapi/1.0/content/%s/licenserequest'%id
        data = {"disableErrorHandler": "true", "doRetry": "true", "consumption_type": "Streaming", "drm_type": "Hls","useAdaptiveBitRate": "true","rights_validations":"Client"}
        lrHeaders = {"Content-Type":"application/json","x-api-key":"f8ecd313-a40b-46be-80cd-87789c4a7a51"}

        data = json.dumps(data)
        data = bytes(data, 'utf8')
        req = urllib.request.Request(url= licenseRequestUrl, headers=lrHeaders, data=data)  
        lrResponse = urllib.request.urlopen(req).read()
        dict_json = json.loads(lrResponse.decode('utf-8'))

        manifest_url = dict_json["content_license"]["license_response"]
        urlHeaders = {
                "Accept-Encoding": "gzip, deflate, br",
                "Accept-Language": "zh-CN,zh-TW;q=0.9,zh;q=0.8,en;q=0.7",
                "Connection": "keep-alive",
                "Host": "audiblecdns3prod-vh.akamaihd.net",
                "Origin": "https://stories.audible.com",
                "Referer": "https://stories.audible.com/pdp/%s?ref=adbl_ent_anon_ds_pdp_pc_cntr-0-1"%id,
                "Sec-Fetch-Dest": "document",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-Site": "None",
                "Upgrade-Insecure-Requests": "1",
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.106 Safari/537.36"
        }

        req = urllib.request.Request(url = manifest_url, headers=urlHeaders)
        mResponse = urllib.request.urlopen(req).read()
        url = "https://" + mResponse.decode('utf-8').split('https://')[1].replace("\n","")
        
        meteUrl = "https://stories.audible.com/audibleapi/1.0/catalog/products/%s?response_groups=product_desc,product_attrs,product_details,product_extended_attrs,contributors,media,rating"%id
        meteResponse = urllib.request.urlopen(meteUrl).read()
        meteInfo = json.loads(meteResponse.decode('utf-8'))

        thumbnails = [{
                'url':meteInfo["product"]["product_images"]['500']
        }]
        title = meteInfo["product"]["title"]
        description = meteInfo["product"]["merchandising_summary"]

        chapterInfoUrl = 'https://stories.audible.com/audibleapi/1.0/content/%s/metadata?drm_type=Hls&response_groups=chapter_info'%id
        chapterInfoResponse = urllib.request.urlopen(chapterInfoUrl).read()
        chapterInfo = json.loads(chapterInfoResponse.decode('utf-8'))
        durationStr = chapterInfo['content_metadata']['chapter_info']['runtime_length_ms']

        duration = round(int(durationStr)/1000)
        print(duration)
        info_dict = {
            'id': id,
            'title': title,
            'description': description,
            'thumbnails': thumbnails,
            'timestamp': None,
            'duration': duration,
        #     'subtitles': {
        #                 'en': [{
        #             'url': '',
        #             'ext': ''
        #                 }]
        #     },
            'formats': [{
                        'format_id': 'hls-523',
                        'url': url,
                        'manifest_url': manifest_url,
                        'tbr': 523.0,
                        'ext': 'mp4',
                        'fps': None,
                        'protocol': 'm3u8',
                        'preference': None,
                        'width': 512,
                        'height': 288,
                        'vcodec': 'avc1.77.30',
                        'acodec': 'mp4a.40.2'
            }]
                }
        return info_dict
