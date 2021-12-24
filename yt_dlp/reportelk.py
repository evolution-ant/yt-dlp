#!/usr/bin/env python
# coding: utf-8
from __future__ import unicode_literals
from datetime import datetime
import platform
import uuid
import socket
import urllib
import urllib.request
import urllib.parse
import json
import sys
import math
from .version import __elk_version__, __version__
from urllib.parse import urlparse


def get_host_mac():
    node = uuid.getnode()
    return uuid.UUID(int=node).hex[-12:]


class global_var:
    command = []
    isDebug = False
    # user
    mac = get_host_mac()
    platform = platform.platform()
    # client
    elk_version = __elk_version__
    ytdl_version = __version__
    client_id = ''
    client_version = ''
    is_remove_cache = False
    # work
    duration = 0
    url = ''
    start_time = datetime.now()
    all_stop_time = datetime.now()
    analysis_stop_time = datetime.now()
    is_analysis_stop = False

    analysis_error_msg = ''
    analysis_status = 'started'  #'finished','canceled'
    analysis_stage = 'started'
    error_msg = ''
    # download
    # 不汇报
    is_download_start = False
    download_status = 'finished'
    download_error_msg = ''
    download_start_time = datetime.now()
    height = 0
    real_height = 0
    total_bytes = 0

    has_real_height = False

    has_total_bytes = False

    ffmpeg_start_time = datetime.now()
    is_used_ffmpeg = False
    has_total_bytes = False

    progress = "0.0%"

    output = ''

    traceback_info = ''


def set_traceback_info(traceback_info):
    global_var.traceback_info = traceback_info


def get_traceback_info():
    return global_var.traceback_info


def get_is_only_get_ie_key():
    for i in range(len(global_var.command)):
        if global_var.command[i] == "--only-get-ie-key":
            return True


def get_output():
    for i in range(len(global_var.command)):
        if global_var.command[i] == "--output" or global_var.command[i] == "-o":
            return global_var.command[i + 1]


def set_command(command):
    global_var.command = command


def get_command_str():
    return " ".join(global_var.command)


def get_client_id():
    for i in range(len(global_var.command)):
        if global_var.command[i] == "--client-id":
            return global_var.command[i + 1]


def get_client_version():
    for i in range(len(global_var.command)):
        if global_var.command[i] == "--client-version":
            return global_var.command[i + 1]


def get_is_remove_cache():
    for i in range(len(global_var.command)):
        if global_var.command[i] == "--rm-cache-dir":
            return True


def get_is_enable_parallel():
    for i in range(len(global_var.command)):
        if global_var.command[i] == "--enable-parallel":
            return True


def get_is_enable_service():
    for i in range(len(global_var.command)):
        if global_var.command[i] == "--enable-service":
            return True


def get_url():
    url = ""
    for i in range(len(global_var.command)):
        if global_var.command[i].startswith(
                "http://") or global_var.command[i].startswith("https://"):
            url = global_var.command[i]
    return url


def get_domain():
    parse_result = urlparse(get_url())
    return '{uri.netloc}'.format(uri=parse_result)


def set_mac(mac):
    global_var.mac = mac


def get_mac():
    return global_var.mac


def set_platform(platform):
    global_var.platform = platform


def get_platform():
    return global_var.platform


# elk_version
def get_elk_version():
    return global_var.elk_version


# ytdl_version
def get_ytdl_version():
    return global_var.ytdl_version


# work
def set_all_duration(duration):
    global_var.version = duration


def get_all_duration():
    return (global_var.all_stop_time - global_var.start_time).seconds


def dvdfab_print_time(my_time, str):
    if global_var.isDebug:
        # 记录日志
        # logger.info('[dvdfab]|:|[elk]|:| %s:%s\n' % (str,my_time.strftime('%Y-%m-%d %H:%M:%S')))
        # Logger("text.log",'[dvdfab]|:|[elk]|:| %s:%s\n' % (str,my_time.strftime('%Y-%m-%d %H:%M:%S')))
        sys.stdout.write('[dvdfab]|:|[elk]|:| %s:%s\n' %
                         (str, my_time.strftime('%Y-%m-%d %H:%M:%S')))


def dvdfab_print_msg(msg, str):
    if global_var.isDebug:
        # logger.info('[dvdfab]|:|[elk]|:| %s:%s\n' % (str,msg))
        sys.stdout.write('[dvdfab]|:|[elk]|:| %s:%s\n' % (str, msg))


def set_start_time(start_time):
    global_var.start_time = start_time
    dvdfab_print_time(global_var.start_time, "set_start_time")


def get_start_time():
    return global_var.start_time


def set_all_stop_time(all_stop_time):
    global_var.all_stop_time = all_stop_time
    dvdfab_print_time(global_var.all_stop_time, "set_all_stop_time")


def get_all_stop_time():
    return global_var.all_stop_time


def set_analysis_stop_time(analysis_stop_time):
    # 当分析完成后 stage 也设置完成
    set_analysis_stage('return_format')
    if not global_var.is_analysis_stop:
        global_var.is_analysis_stop = True
        global_var.analysis_stop_time = analysis_stop_time
        set_analysis_status('finished')
        dvdfab_print_time(global_var.analysis_stop_time,
                          "set_analysis_stop_time")


def get_analysis_stop_time():
    return global_var.analysis_stop_time


def get_analysis_duration():
    if not global_var.is_analysis_stop:
        dvdfab_print_time(global_var.all_stop_time,
                          "get_analysis_duration,all_stop_time:")
        dvdfab_print_time(global_var.start_time,
                          "get_analysis_duration,start_time:")
        return (global_var.all_stop_time - global_var.start_time).seconds
    elif (global_var.analysis_stop_time <= global_var.start_time):
        return 0
    dvdfab_print_time(global_var.analysis_stop_time,
                      "get_analysis_duration,analysis_stop_time:")
    dvdfab_print_time(global_var.start_time,
                      "get_analysis_duration,start_time:")
    return (global_var.analysis_stop_time - global_var.start_time).seconds


def set_analysis_error_msg(analysis_error_msg):
    global_var.analysis_status = 'failed'
    global_var.analysis_error_msg = analysis_error_msg


def get_analysis_error_msg():
    return global_var.analysis_error_msg


def set_download_error_msg(download_error_msg):
    global_var.download_status = 'failed'
    global_var.download_error_msg = download_error_msg


def get_download_error_msg():
    return global_var.download_error_msg


def set_error_msg(error_msg):
    # 接收错误值,根据分析,下载,状态判断是在那个阶段报的错
    global_var.error_msg = error_msg
    if get_analysis_status() != 'finished':
        set_analysis_error_msg(error_msg)
    elif get_download_status() != 'finished':
        set_download_error_msg(error_msg)


def get_error_msg():
    return global_var.error_msg


def set_analysis_stage(analysis_stage):
    dvdfab_print_msg('set_analysis_stage', analysis_stage)
    global_var.analysis_stage = analysis_stage


def get_analysis_stage():
    return global_var.analysis_stage


def set_analysis_status(analysis_status):
    dvdfab_print_msg('set_analysis_status', analysis_status)
    global_var.analysis_status = analysis_status


def get_analysis_status():
    if not global_var.is_analysis_stop:
        global_var.analysis_status = "canceled"
    return global_var.analysis_status


def set_download_status(download_status):
    global_var.download_status = download_status


def get_download_status():
    return global_var.download_status


def set_download_start_time(download_start_time):
    if not global_var.is_download_start:
        global_var.is_download_start = True
        global_var.download_start_time = download_start_time
        dvdfab_print_time(global_var.download_start_time,
                          "set_download_start_time")


def get_download_start_time():
    return global_var.download_start_time


def get_is_download_start():
    return global_var.is_download_start


def get_download_duration():
    return (global_var.all_stop_time - global_var.download_start_time).seconds


def set_height(height):
    global_var.height = height
    dvdfab_print_msg(global_var.height, "set_height")


def get_height():
    return global_var.height


def set_real_height(real_height):
    if not global_var.has_real_height:
        global_var.has_real_height = True
        global_var.real_height = real_height
        dvdfab_print_msg(global_var.real_height, "set_real_height")


def get_real_height():
    return global_var.real_height


def set_total_bytes(total_bytes):
    global_var.total_bytes = total_bytes
    dvdfab_print_msg(global_var.total_bytes, "set_total_bytes")


def get_total_bytes():
    return global_var.total_bytes


def get_speed():
    if global_var.total_bytes <= 0:
        return 0
    return int(
        global_var.total_bytes /
        (global_var.all_stop_time - global_var.download_start_time).seconds /
        1024)


def set_progress(progress):
    global_var.progress = progress
    dvdfab_print_msg(global_var.progress, "set_progress")


def get_progress():
    if global_var.download_status == 'finished':
        return "100.0%"
    return global_var.progress


def set_ffmpeg_start_time(ffmpeg_start_time):
    global_var.is_used_ffmpeg = True
    global_var.ffmpeg_start_time = ffmpeg_start_time
    dvdfab_print_time(global_var.ffmpeg_start_time, "set_ffmpeg_start_time")


def get_ffmpeg_start_time():
    return global_var.ffmpeg_start_time


def get_ffmpeg_duration():
    return (global_var.all_stop_time - global_var.ffmpeg_start_time).seconds


def get_is_used_ffmpeg():
    return global_var.is_used_ffmpeg


def format_speed(speed):
    if speed is None:
        return '%10s' % '---b/s'
    return '%10s' % ('%s/s' % format_bytes(speed))


def format_bytes(bytes):
    if bytes is None:
        return 'N/A'
    if type(bytes) is str:
        bytes = float(bytes)
    if bytes == 0.0:
        exponent = 0
    else:
        exponent = int(math.log(bytes, 1024.0))
    suffix = ['B', 'KiB', 'MiB', 'GiB', 'TiB', 'PiB', 'EiB', 'ZiB',
              'YiB'][exponent]
    converted = float(bytes) / float(1024**exponent)
    return '%.2f%s' % (converted, suffix)


def report():
    # fix C0_N_HwcGVc elk error
    if get_is_only_get_ie_key():
        return

    report = {}
    report['mac'] = get_mac()
    report['platform'] = get_platform()
    report['version'] = get_elk_version()
    report['ytdl_version'] = get_ytdl_version()
    if (get_command_str() != None):
        report['command'] = get_command_str()
    if (get_client_id() != None):
        report['client_id'] = get_client_id()
    if (get_client_version() != None):
        report['client_version'] = get_client_version()
    if (get_is_remove_cache()):
        report['is_remove_cache'] = "True"
    if (get_is_enable_parallel()):
        report['is_enable_parallel'] = "True"
    if (get_is_enable_service()):
        report['is_enable_service'] = "True"

    if not get_url():
        return
    report['url'] = get_url()

    report['host'] = get_domain()
    report['analysis_duration'] = get_analysis_duration()
    report['analysis_status'] = get_analysis_status()
    report['analysis_stage'] = get_analysis_stage()

    if (get_analysis_error_msg() != ''):
        report['analysis_error_msg'] = get_analysis_error_msg()
        report['analysis_status'] = 'failed'
    if get_is_download_start():
        report['download_status'] = get_download_status()
        report['download_duration'] = get_download_duration()
        report['download_speeds'] = get_speed()
        report['download_progress'] = get_progress()
    if get_download_status() == 'failed':
        report['download_error_msg'] = get_download_error_msg()

    if get_real_height() != 0 and get_real_height() != None:
        report['download_resolution'] = get_real_height()
    if get_height() != 0:
        report['request_resolution'] = get_height()
    if get_is_used_ffmpeg():
        report['transcoding_duration'] = get_ffmpeg_duration()
    if get_output() != None:
        report['output'] = get_output()
    if get_traceback_info() != '':
        report['traceback_info'] = get_traceback_info()
    url = 'http://app-api.vidusoft.com/api/youtube/'

    dvdfab_print_msg(report, "report msg:")
    report = json.dumps(report)
    data = {}
    data["JSON_DATA"] = report

    if global_var.isDebug:
        print(data)
        # logger.info('[dvdfab]|:|[elk]|:| %s:%s\n' % ("data",data))

    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    data = bytes(urllib.parse.urlencode(data), encoding='utf-8')

    try:
        req = urllib.request.Request(url=url, headers=headers, data=data)
        response = urllib.request.urlopen(req).read()
        if global_var.isDebug:
            print(response)
    except IOError:
        if global_var.isDebug:
            print('elk 接口报错', IOError)
