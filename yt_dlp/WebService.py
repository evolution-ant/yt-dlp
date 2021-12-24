#!/usr/bin/env python
# coding: utf-8
"""
@api {post} stop_download 停止下载任务
@apiGroup       iOS
@apiName        stop_download
@apiPermission  iOS
@apiVersion     1.0.0
@apiDescription 无

@apiParam {String} request_id 下载任务 id
@apiSampleRequest http://0.0.0.0:52080/stop_download
@apiParamExample {json} Request-Example:
{"request_id": "1111222233334444"}

@apiSuccess  200 成功
@apiSuccessExample {json} 成功
{"code": 0}


@api {post} download 下载
@apiGroup       iOS
@apiName        download
@apiPermission  iOS
@apiVersion     1.0.0
@apiDescription 无

@apiParam {String} format 格式
@apiParam {String} url 视频地址
@apiSampleRequest http://0.0.0.0:52080/download
@apiParamExample {json} Request-Example:
{
    "request_id": "1111222233334444",
    "ffmpegargs": "True",
    "outtmpl": "/var/mobile/Containers/Data/Application/9E155626-EB10-4E11-A099-F0AAD110D2A6/Documents/8f2ZyO1q6qw.mp3",
    "format": "bestaudio",
    "url": "https://www.youtube.com/watch?v=8f2ZyO1q6qw"
}

@apiSuccess  200 成功

@apiErrorExample {json} 出现异常
{"code": -1}


@api {post} playlist_info 获取播放列表信息
@apiGroup       iOS
@apiName        playlist_info
@apiPermission  iOS
@apiVersion     1.0.0
@apiDescription 无

@apiParam {String} format 格式
@apiParam {String} url 视频地址
@apiSampleRequest http://0.0.0.0:52080/playlist_info
@apiParamExample {json} Request-Example:
{"url":"https://m.youtube.com/playlist?list=PLDcnymzs18LU4Kexrs91TVdfnplU3I5zs", "extract_flat":"in_playlist", "dump_single_json":"True"}

@apiSuccess  200 成功
@apiSuccessExample {json} 成功
{"_type":"playlist","entries":[{"_type":"url","webpage_url":"https://www.youtube.com/watch?v=HNeje0KLVZ4","ie_key":"Youtube","id":"HNeje0KLVZ4","title":"\u3010\u674e\u5fd7\u3001\u7535\u58f0\u4e0e\u7ba1\u5f26\u4e50 II\u3011 01.\u76f8\u4fe1\u672a\u6765\u5e8f\u66f2 Intro","thumbnail":"https://i.ytimg.com/vi/HNeje0KLVZ4/hqdefault.jpg?sqp=-oaymwEZCNACELwBSFXyq4qpAwsIARUAAIhCGAFwAQ==&rs=AOn4CLDJPqkMJqPHeA3Ddon1Dna-rTysvQ","duration":"5:10","artists":["\u674e\u5fd7Lizhi"]},{"_type":"url","webpage_url":"https://www.youtube.com/watch?v=kf9DPdJpqTc","ie_key":"Youtube","id":"kf9DPdJpqTc","title":"\u3010\u674e\u5fd7\u3001\u7535\u58f0\u4e0e\u7ba1\u5f26\u4e50 II\u3011 02.\u4e00\u5934\u5076\u50cf A Piece of Idol","thumbnail":"https://i.ytimg.com/vi/kf9DPdJpqTc/hqdefault.jpg?sqp=-oaymwEZCNACELwBSFXyq4qpAwsIARUAAIhCGAFwAQ==&rs=AOn4CLCzOva5f3C4raec8X3FB81cu3fu3A","duration":"4:52","artists":["\u674e\u5fd7Lizhi"]}],"id":"PLi-BejM1PTHqGnrb370jyIDaBiZfUlsM0","title":"\u674e\u5fd7\u3001\u7535\u58f0\u4e0e\u7ba1\u5f26\u4e50 II 2017-2018\u8de8\u5e74\u73b0\u573a","extractor":"youtube:playlist","webpage_url":"https://www.youtube.com/watch?v=HNeje0KLVZ4&list=PLi-BejM1PTHqGnrb370jyIDaBiZfUlsM0","webpage_url_basename":"watch","extractor_key":"YoutubePlaylist"}

@apiErrorExample {json} 出现异常
{"code": -1}


@api {post} info 获取视频信息
@apiGroup       iOS
@apiName        info
@apiPermission  iOS
@apiVersion     1.0.0
@apiDescription 无

@apiParam {String} format 格式
@apiParam {String} url 视频地址
@apiParam {String} dump_single_json 返回 JSON
@apiSampleRequest http://0.0.0.0:52080/info
@apiParamExample {json} Request-Example:
{"format":"bestaudio","url":"https://www.youtube.com/watch?v=NunAl4BRVx8","dump_single_json":"True"}

@apiSuccess  200 成功
@apiSuccessExample {json} 成功
{"id":"NunAl4BRVx8","uploader":"OfMonstersAndMenVEVO","uploader_id":"OfMonstersAndMenVEVO","uploader_url":"http://www.youtube.com/user/OfMonstersAndMenVEVO","channel_id":"UCNqs2VoY5KXMeOm4wo5U2Lw","channel_url":"http://www.youtube.com/channel/UCNqs2VoY5KXMeOm4wo5U2Lw","upload_date":"20190502","license":null,"creator":"Of Monsters And Men","title":"Of Monsters and Men - Alligator (Lyric Video)","alt_title":"Alligator","thumbnail":"https://i.ytimg.com/vi/NunAl4BRVx8/maxresdefault.jpg","description":"Alligator (Official Lyric Video)\n\nSong available everywhere now: https://OMAM.lnk.to/AlligatorYD\n\nConnect with Of Monsters And Men:\nhttps://www.facebook.com/ofmonstersandmen\nhttps://twitter.com/monstersandmen\nhttps://www.instagram.com/ofmonstersandmen/\nhttp://www.ofmonstersandmen.com/\n\nVideo director/editor/producer: Kamiel Rongen\nWebsite www.water-ballet.com\nInstagram: @waterballet\n\nMusic video by Of Monsters and Men performing Alligator (Lyric Video). \u00a9 2019 SKRIMSL ehf, under exclusive license to Republic Records, a division of UMG Recordings, Inc.\n\nhttp://vevo.ly/66e3tE","categories":["Music"],"tags":["Of","Monsters","and","Men","Alligator","(Lyric","Video)","Republic","Records","Alternative"],"subtitles":{},"automatic_captions":{},"duration":185,"age_limit":0,"annotations":null,"chapters":null,"webpage_url":"https://www.youtube.com/watch?v=NunAl4BRVx8","view_count":4550114,"like_count":59176,"dislike_count":2070,"average_rating":4.854764,"formats":[{"format_id":"249","url":"https://r6---sn-n8v7znlk.googlevideo.com/videoplayback?expire=1560784162&ei=wVgHXdTfNciigAe54IOYDQ&ip=78.155.199.200&id=o-AG5zI64aDxoArFDDUBRkfd_pJ_afpDpr5TVefBPL3ABU&itag=249&source=youtube&requiressl=yes&mm=31%2C26&mn=sn-n8v7znlk%2Csn-axq7sn7l&ms=au%2Conr&mv=u&pl=25&nh=%2CIgpwcjAyLnN2bzA2KgkxMjcuMC4wLjE&gcr=ae&mime=audio%2Fwebm&gir=yes&clen=1114753&dur=185.261&lmt=1556918605336455&mt=1560761278&fvip=6&keepalive=yes&c=WEB&txp=5531432&sparams=expire%2Cei%2Cip%2Cid%2Citag%2Csource%2Crequiressl%2Cgcr%2Cmime%2Cgir%2Cclen%2Cdur%2Clmt&lsparams=mm%2Cmn%2Cms%2Cmv%2Cpl%2Cnh&lsig=AHylml4wRgIhAN5n7WVriRF9zdCWKQxyBp1AIQATD5d7F1j0dVt4pb2_AiEA42JowDw5em5LAlxETIp22ixFrO9i1HzU1o1UiPg0RpU%3D&sig=ALgxI2wwRgIhAL4rlkPdUEHXekXkipUQGrV5cq_kypWtPe8OWqtKQl1zAiEAk4NzNlNE-Hnb9AJLiW9TVym9xSKiAXeYYU_o0cdxr6I=&ratebypass=yes","player_url":"/yts/jsbin/player_ias-vflzbi_R5/en_US/base.js","ext":"webm","format_note":"DASH audio","acodec":"opus","abr":50,"filesize":1114753,"tbr":54.297,"quality":-1,"vcodec":"none","downloader_options":{"http_chunk_size":10485760},"format":"249 - audio only (DASH audio)","protocol":"https","http_headers":{"User-Agent":"Mozilla/5.0 (X11; Linux x86_64; rv:59.0) Gecko/20100101 Firefox/59.0","Accept-Charset":"ISO-8859-1,utf-8;q=0.7,*;q=0.7","Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8","Accept-Encoding":"gzip, deflate","Accept-Language":"en-us,en;q=0.5"}}],"is_live":null,"start_time":null,"end_time":null,"series":null,"season_number":null,"episode_number":null,"track":"Alligator","artist":"Of Monsters And Men","album":null,"release_date":null,"release_year":null,"extractor":"youtube","webpage_url_basename":"watch","extractor_key":"Youtube","playlist":null,"playlist_index":null,"thumbnails":[{"url":"https://i.ytimg.com/vi/NunAl4BRVx8/maxresdefault.jpg","id":"0"}],"display_id":"NunAl4BRVx8","requested_subtitles":null,"format_id":"251","url":"https://r6---sn-n8v7znlk.googlevideo.com/videoplayback?expire=1560784162&ei=wVgHXdTfNciigAe54IOYDQ&ip=78.155.199.200&id=o-AG5zI64aDxoArFDDUBRkfd_pJ_afpDpr5TVefBPL3ABU&itag=251&source=youtube&requiressl=yes&mm=31%2C26&mn=sn-n8v7znlk%2Csn-axq7sn7l&ms=au%2Conr&mv=u&pl=25&nh=%2CIgpwcjAyLnN2bzA2KgkxMjcuMC4wLjE&gcr=ae&mime=audio%2Fwebm&gir=yes&clen=2968055&dur=185.261&lmt=1556918569086482&mt=1560761278&fvip=6&keepalive=yes&c=WEB&txp=5531432&sparams=expire%2Cei%2Cip%2Cid%2Citag%2Csource%2Crequiressl%2Cgcr%2Cmime%2Cgir%2Cclen%2Cdur%2Clmt&lsparams=mm%2Cmn%2Cms%2Cmv%2Cpl%2Cnh&lsig=AHylml4wRgIhAN5n7WVriRF9zdCWKQxyBp1AIQATD5d7F1j0dVt4pb2_AiEA42JowDw5em5LAlxETIp22ixFrO9i1HzU1o1UiPg0RpU%3D&sig=ALgxI2wwRQIgGO4R8UVDk7u-C9XC1OPnJzrmQetse4DQCVydbOoshj8CIQC50KcYg9EJVCUY1zUkmKbQvqBoiZbclkwc37eYVYPQ7Q==&ratebypass=yes","player_url":"/yts/jsbin/player_ias-vflzbi_R5/en_US/base.js","ext":"webm","format_note":"DASH audio","acodec":"opus","abr":160,"filesize":2968055,"tbr":135.692,"quality":-1,"vcodec":"none","downloader_options":{"http_chunk_size":10485760},"format":"251 - audio only (DASH audio)","protocol":"https","http_headers":{"User-Agent":"Mozilla/5.0 (X11; Linux x86_64; rv:59.0) Gecko/20100101 Firefox/59.0","Accept-Charset":"ISO-8859-1,utf-8;q=0.7,*;q=0.7","Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8","Accept-Encoding":"gzip, deflate","Accept-Language":"en-us,en;q=0.5"}}

@apiErrorExample {json} 出现异常
{"code": -1}

@api {post} command 下载
@apiGroup       client
@apiName        command
@apiPermission  
@apiVersion     1.0.0
@apiDescription 无

@apiParam {String} request_id 任务唯一id
@apiParam [String] args 命令参数
@apiSampleRequest http://0.0.0.0:52080/command
@apiParamExample {json} Request-Example:
{
	"request_id": "1111222233334444",
	"args": ["--skip-download", "--print-dvdfab-out", "--embed-thumbnail", "--dump-json", "--encoding", "utf-8", "--ignore-errors", "--no-playlist", "https://www.youtube.com/watch?v=XZgiNnGB8m4"]
}
@apiSuccess  200 成功

@apiErrorExample {json} 出现异常
{"code": -1}

@api {get} version 版本
@apiGroup       client
@apiName        version
@apiPermission  
@apiVersion     1.0.0
@apiDescription 无

@apiSampleRequest http://0.0.0.0:52080/version

@apiSuccess  200 成功
@apiSuccessExample {json} 成功
{"version": "2020.05.08"}'

@apiErrorExample {json} 出现异常
{"code": -1}
"""

from __future__ import unicode_literals


import json
from urllib.parse import urlparse
from http.server import HTTPServer, BaseHTTPRequestHandler
# from . import YoutubeDL  # We will import YoutubeDL async to speed up initialize
from threading import Thread
import sys
import datetime

if __package__ is None and not hasattr(sys, 'frozen'):
    import os.path
    path = os.path.realpath(os.path.abspath(__file__))
    sys.path.insert(0, os.path.dirname(os.path.dirname(path)))

YoutubeDLClass = None  # We will import YoutubeDL async to speed up initialize
YoutubeDLMain = None
Report = None
SetAllStopTime = None
Version = ""


def import_YoutubeDL():
    global YoutubeDLClass, YoutubeDLMain, Report, SetAllStopTime, Version
    if YoutubeDLClass is None:
        print("import_YoutubeDL begin")
        from yt_dlp import YoutubeDL, main, report, set_all_stop_time, __version__
        YoutubeDLClass = YoutubeDL
        YoutubeDLMain = main
        Report = report
        SetAllStopTime = set_all_stop_time
        Version = __version__
        print("import_YoutubeDL end")
    return YoutubeDLClass


download_stop_flags = {}


class ThreadedHTTPServer(HTTPServer):
    '''https://stackoverflow.com/questions/19537132/threaded-basehttpserver-one-thread-per-request'''
    def process_request(self, request, client_address):
        thread = Thread(target=self.__new_request,
                        args=(self.RequestHandlerClass, request,
                              client_address, self))
        thread.start()

    def __new_request(self, handlerClass, request, address, server):
        handlerClass(request, address, server)
        self.shutdown_request(request)


class MyLogger(object):
    """接受youtube-dl输出"""

    r = None

    def __init__(self, request):
        """init request:Request"""
        self.r = request

    def debug(self, msg):
        data = {"debug": msg}
        self.r.wfile.write(bytes(json.dumps(data) + "@end@", encoding='utf-8'))

    def warning(self, msg):
        data = {"warning": msg}
        self.r.wfile.write(bytes(json.dumps(data) + "@end@", encoding='utf-8'))

    def error(self, msg):
        data = {"error": msg}
        stop_time = datetime.datetime.now()
        SetAllStopTime(stop_time)
        Report()

        self.r.wfile.write(bytes(json.dumps(data) + "@end@", encoding='utf-8'))

    def process(self, msg):
        data = {"process": msg}
        self.r.wfile.write(bytes(json.dumps(data) + "@end@", encoding='utf-8'))


class Request(BaseHTTPRequestHandler):
    params = None

    def _set_response(self, data):
        print("_set_response begin")
        self.wfile.write(bytes(json.dumps(data), encoding='utf-8'))
        print("_set_response end")

    def do_POST(self):
        global download_stop_flags
        logger = MyLogger(self)
        self.params['logger'] = logger

        content_length = int(self.headers['Content-Length'])
        str_data = self.rfile.read(content_length).decode('utf-8')
        print("post data: " + str_data)
        post_data = json.loads(str_data)
        self.params.update(post_data)

        path = urlparse(self.path).path
        print("post %s begin" % path)
        if path == "/info":
            try:
                import_YoutubeDL()
                ydl = YoutubeDLClass(self.params)
                data = ydl.extract_info(self.params['url'], download=False)
                self._set_response(data)
            except Exception as error:
                print('exception: ', error)
                self._set_response({'code': -1})

        elif path == "/playlist_info":
            try:
                import_YoutubeDL()
                self.params['extract_flat'] = 'in_playlist'
                ydl = YoutubeDLClass(self.params)
                data = ydl.extract_info(self.params['url'], download=False)
                self._set_response(data)
            except Exception as error:
                print('exception: ', error)
                self._set_response({'code': -1})

        elif path == '/download':
            download_stop_flags[post_data['request_id']] = False

            def progress_hooks(msg):
                if msg is not None:
                    logger.process(msg)
                if download_stop_flags[post_data['request_id']]:
                    raise Exception('user stop')

            self.params['progress_hooks'] = [progress_hooks]
            if post_data['format'] == 'bestaudio':
                argv = [
                    "--enable-parallel", "-f", "bestaudio",
                    "--no-check-certificate", "--embed-thumbnail", "-x",
                    "--audio-format", "mp3", "--audio-quality",
                    post_data['audioquality'], "--add-metadata",
                    "--metadata-from-title", "(?P<artist>.+?) - (?P<title>.+)",
                    "--xattrs", "--no-part", "--retries", "3", "--no-playlist",
                    "--no-cache-dir", "--ffmpeg-args", "--output",
                    post_data['outtmpl'] + ".%(ext)s", post_data['url']
                ]
            else:
                argv = [
                    "--enable-parallel", "-f", post_data['format'],
                    "--no-check-certificate", "--merge-output-format", "mp4",
                    "--no-part", "--retries", "3", "--no-playlist",
                    "--no-cache-dir", "--ffmpeg-args", "--output",
                    post_data['outtmpl'] + ".%(ext)s", post_data['url']
                ]

            import_YoutubeDL()
            print('download True')
            YoutubeDLMain(argv, [progress_hooks], logger)

        elif path == '/version':
            self._set_response({'version': Version})

        elif path == '/command':
            download_stop_flags[post_data['request_id']] = False

            def progress_hooks(msg):
                if msg is not None:
                    logger.process(msg)
                if download_stop_flags[post_data['request_id']]:
                    raise Exception('user stop')

            self.params['progress_hooks'] = [progress_hooks]
            argv = post_data['args']
            import_YoutubeDL()
            argv.append("--enable-service")
            print('command True')
            YoutubeDLMain(argv, [progress_hooks], logger)

        elif path == '/stop_download':
            download_stop_flags[post_data['request_id']] = True
            self._set_response({'code': 0})

        elif path == '/init':
            import_YoutubeDL()
            self._set_response({'code': 0})

        elif path == '/check':
            self._set_response({'code': 0})

        elif path == '/suport_url':
            try:
                import_YoutubeDL()
                ydl = YoutubeDLClass(self.params)
                data = ydl.extract_info(self.params['url'], download=False)
                self._set_response(data)
            except Exception as error:
                print('exception: ', error)
                self._set_response({'code': -1})

        else:
            print('unknown path %s' % path)

        print("post %s end" % path)


class WebService(object):
    """WebService for yt-dlp."""
    params = None

    def __init__(self, ydl_opt):
        self.params = ydl_opt

    def __enter__(self):
        return self

    def __exit__(self, *args):
        pass

    def start(self,port):
        print("************ WebService begin Port :{}************".format(port))
        host = ("0.0.0.0", port)
        server = ThreadedHTTPServer(host, Request)
        request = server.RequestHandlerClass
        request.params = self.params
        server.serve_forever()
        print("************ WebService end ************")


def main(port):
    service = WebService({"nocheckcertificate": True})
    thread = Thread(target=import_YoutubeDL)
    thread.start()
    service.start(port)


def restart():
    service = WebService({"nocheckcertificate": True})
    service.start()


if __name__ == '__main__':
    port = 52080
    if len(sys.argv)==2:
        port = int(sys.argv[1])
    main(port)
