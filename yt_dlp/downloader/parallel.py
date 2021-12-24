import os
import threading
import time
import socket
import json
import re
from .common import FileDownloader
from .http import HttpFD
from ..compat import (
    compat_str,
    compat_urllib_error,
)
from ..utils import (
    encodeFilename,
    int_or_none,
    sanitize_open,
    sanitized_Request,
)

class ParallelFD(FileDownloader):
    def real_download(self, filename, info_dict):
        class DownloadContext(dict):
            __getattr__ = dict.get
            __setattr__ = dict.__setitem__
            __delattr__ = dict.__delitem__

        def start_parallel_download(thread_id, range_start, range_end, retries = 5):
            if range_start >= range_end:
                self.report_warning("range end longer than range start.")
                return
            request = sanitized_Request(url, None, headers)
            set_range(request, range_start, range_end)
            try:
                response = self.ydl.urlopen(request)
                content_range = response.headers.get('Content-Range')
                if content_range:
                    content_range_m = re.search(r'bytes (\d+)-(\d+)?(?:/(\d+))?', content_range)
                    content_range_start = int(content_range_m.group(1))
                    self.to_screen("thread: {}, current: {}, tototal: {}, start: {}, end {}, content start:{} content end:{}".format(thread_id, ctx.resume_cfg[thread_id].get('current', 0), (range_end - range_start), range_start, range_end, content_range_start, content_range_m.group(2)))
                    if range_start == content_range_start:
                        content_range_end = int_or_none(content_range_m.group(2))
                        offset = range_start
                        start_time = time.time()
                        while True:
                            while True:
                                try:
                                    content = response.read(ctx.block_size)
                                    break
                                except socket.timeout as e:
                                    self.report_warning(e.strerror + ' try times: ' + retries)
                                    start_parallel_download(thread_id, offset, range_end, retries-1)
                                    break
                                except socket.error as e:
                                    self.report_warning(e.strerror + (' try times: ' + retries))
                                    start_parallel_download(thread_id, offset, range_end, retries-1)
                                    break

                            if not content:
                                if abs(content_range_end - offset) > 1:
                                    start_parallel_download(thread_id, offset, content_range_end)
                                    self.report_warning("expect end  in %d,but offset: %d not end" % (content_range_end, offset))
                                    break
                                else:
                                    break

                            self.slow_down(start_time, time.time(), offset - content_range_start)
                            self._hook_progress(None)
                            with ctx.lock:
                                ctx.stream.seek(offset)
                                ctx.stream.write(content)
                                offset = offset + len(content)
                                ctx.resume_cfg[thread_id]['start'] = offset
                                ctx.resume_cfg[thread_id]['end'] = range_end
                                if ctx.resume_cfg[thread_id].get("current", 0) == 0:
                                    ctx.resume_cfg[thread_id]['current'] = len(content)
                                else:
                                    ctx.resume_cfg[thread_id]['current'] += len(content)

                                ctx.downloaded_bytes += len(content)
                    else:
                        start_parallel_download(thread_id, content_range_start, range_end, retries)
                        self.report_warning("not suppport start:%s should be %%s" % (range_start, content_range_start))
                else:
                    self.report_warning('Not found content-range')
                    raise ValueError

            except (compat_urllib_error.HTTPError, ) as err:
                self.report_warning("connect error.")
                if retries == 0:
                    return
                start_parallel_download(thread_id, range_start, range_end, retries - 1)

        def speed_calc():
            start = time.time()
            now = time.time()
            ctx.before_byte_counter = ctx.downloaded_bytes
            while True:
                now = time.time()
                ctx.resume_cfg_stream.seek(0)
                ctx.resume_cfg_stream.truncate(0)
                ctx.resume_cfg_stream.flush()
                ctx.resume_cfg_stream.write(json.dumps(ctx.resume_cfg))
                ctx.resume_cfg_stream.flush()

                speed = self.calc_speed(start, now, ctx.downloaded_bytes - ctx.before_byte_counter)
                eta = self.calc_eta(start, time.time(), ctx.data_len - ctx.before_byte_counter, ctx.downloaded_bytes - ctx.before_byte_counter)
                self._hook_progress({
                    'status': 'downloading',
                    'downloaded_bytes': ctx.downloaded_bytes,
                    'total_bytes': ctx.data_len,
                    'filename': ctx.filename,
                    'eta': eta,
                    'speed': speed,
                    'elapsed': now - ctx.start_time,
                })

                start = time.time()
                ctx.before_byte_counter = ctx.downloaded_bytes
                time.sleep(1)
                if ctx.downloaded_bytes >= ctx.data_len:
                    self._hook_progress({
                        'downloaded_bytes': ctx.data_len,
                        'total_bytes': ctx.data_len,
                        'filename': ctx.filename,
                        'status': 'finished',
                        'elapsed': time.time() - ctx.start_time,
                    })

                    break

        def set_range(req, start, end):
            range_header = 'bytes=%d-' % start
            if end:
                range_header += compat_str(end)
            req.add_header('Range', range_header)

        url = info_dict['url']
        ctx = DownloadContext()
        ctx.filename = filename
        ctx.tmpfilename = self.temp_name(filename)
        ctx.resume_file = ctx.tmpfilename + '.json'
        ctx.stream = None
        ctx.start_time = time.time()
        ctx.block_size = self.params.get('buffersize', 1024)

        headers = {'Youtubedl-no-compression': 'True'}
        add_headers = info_dict.get('http_headers')
        if add_headers:
            headers.update(add_headers)

        max_try_num = int_or_none(self.params.get('retries', 10))

        request = sanitized_Request(url, headers = headers)
        ctx.data = self.ydl.urlopen(request)
        data_len =  int_or_none(ctx.data.info().get('Content-length', None))
        if data_len is not None and data_len > 0:
            # Not support multiple thread download.
            if ctx.data.info().get('Accept-Ranges', None) is None:
                return HttpFD.real_download(self , filename, info_dict)

            ctx.resume_cfg = []

#region Init file streams
            # Create files if not exist
            if os.path.isfile(encodeFilename(ctx.tmpfilename)) is False:
                f, ctx.tmpfilename = sanitize_open(ctx.tmpfilename, 'wb')
                f.close()
            if os.path.isfile(ctx.resume_file) is False:
                f, ctx.resume_file = sanitize_open(ctx.resume_file, 'w')
                f.close()

            ctx.stream, ctx.tmpfilename = sanitize_open(ctx.tmpfilename, 'rb+')
            ctx.resume_cfg_stream, ctx.resume_file = sanitize_open(ctx.resume_file, 'r+')
            assert ctx.stream is not None
            assert ctx.resume_cfg_stream is not None

            ctx.filename = self.undo_temp_name(ctx.tmpfilename)
            self.report_destination(ctx.filename)
#endregion

            ctx.lock = threading.Lock()
            ctx.data_len = data_len

            ranges = []
            ctx.thread_count = int(self.params.get('thread_count', 5))
            ctx.range_size = int(data_len / ctx.thread_count)
            ctx.diff_size = 0
            real_size = (ctx.range_size * ctx.thread_count)
            if ctx.data_len > real_size:
                ctx.diff_size = ctx.data_len - real_size
            elif ctx.data_len < real_size:
                ctx.diff_size = ctx.data_len - real_size

            try:
                cfg = json.load(ctx.resume_cfg_stream)
            except ValueError as e:
                cfg = None

            need_download_size = 0

            rate_limit = self.params.get('ratelimit')
            if rate_limit:
                self.params['ratelimit'] = float(rate_limit) / float(ctx.thread_count)
            for i in range(ctx.thread_count):
                if cfg is not None:
                    start = cfg[i]['start']
                    end = cfg[i]['end']
                    need_download_size = need_download_size + (end - start)
                    ranges.append((start, end))
                else:
                    need_download_size = data_len
                    if i == ctx.thread_count - 1:
                        ranges.append((i * ctx.range_size + 1, data_len))
                    elif i == 0:
                        ranges.append((i * ctx.range_size, (i + 1) * ctx.range_size + ctx.diff_size))
                    else:
                        ranges.append((i * ctx.range_size + 1, (i + 1) * ctx.range_size))

            ctx.downloaded_bytes = data_len - need_download_size

            calc_thread = threading.Thread(target=speed_calc)
            thread_list = [calc_thread]
            thread_id = 0
            for ran in ranges:
                start, end = ran
                ctx.resume_cfg.append({"start": start, "end": end})
                thread = threading.Thread(target=start_parallel_download, args=(thread_id, start, end, max_try_num), daemon=True)
                thread.start()
                thread_list.append(thread)
                thread_id = thread_id + 1

            calc_thread.start()

            for thread in thread_list:
                thread.join()

            ctx.stream.close()
            ctx.resume_cfg_stream.close()
            try:
                os.remove(ctx.resume_file)
                self.try_rename(ctx.tmpfilename, ctx.filename)
            except OSError as e:
                self.report_warning(e.strerror)

            return True
        else:
            self.report_error('download fail, get content length error.')
            return False
