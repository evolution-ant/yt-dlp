# coding: utf-8
def localFrist():
    return False
#--------------------------------------------------New---------------------------------------------------------------------
def CreateExtractor(BaseCLS,
    try_get,
    clean_html,
    str_to_int,
    smuggle_url,
    int_or_none,
    unescapeHTML,
    mimetype2ext,
    parse_codecs,
    float_or_none,
    remove_quotes,
    unsmuggle_url,
    ExtractorError,
    compat_parse_qs,
    parse_duration,
    unified_strdate,
    get_element_by_id,
    compat_urllib_parse_unquote,
    compat_urllib_parse_urlparse,
    compat_urllib_parse_urlencode,
    compat_urllib_parse_unquote_plus):

    print('Youtube CoreVersion:[%s]' % '20171213001')

    import re
    import json

    def CreateJSInterpreter(jsCode):
        import operator
        import re
        import json

        _OPERATORS = [
            ('|', operator.or_),
            ('^', operator.xor),
            ('&', operator.and_),
            ('>>', operator.rshift),
            ('<<', operator.lshift),
            ('-', operator.sub),
            ('+', operator.add),
            ('%', operator.mod),
            ('/', operator.truediv),
            ('*', operator.mul),
        ]
        _ASSIGN_OPERATORS = [(op + '=', opfunc) for op, opfunc in _OPERATORS]
        _ASSIGN_OPERATORS.append(('=', lambda cur, right: right))

        _NAME_RE = r'[a-zA-Z_$][a-zA-Z_$0-9]*'


        class JSInterpreter(object):
            def __init__(self, code, objects=None):
                if objects is None:
                    objects = {}
                self.code = code
                self._functions = {}
                self._objects = objects

            def interpret_statement(self, stmt, local_vars, allow_recursion=100):
                if allow_recursion < 0:
                    raise ExtractorError('Recursion limit reached')

                should_abort = False
                stmt = stmt.lstrip()
                stmt_m = re.match(r'var\s', stmt)
                if stmt_m:
                    expr = stmt[len(stmt_m.group(0)):]
                else:
                    return_m = re.match(r'return(?:\s+|$)', stmt)
                    if return_m:
                        expr = stmt[len(return_m.group(0)):]
                        should_abort = True
                    else:
                        # Try interpreting it as an expression
                        expr = stmt

                v = self.interpret_expression(expr, local_vars, allow_recursion)
                return v, should_abort

            def interpret_expression(self, expr, local_vars, allow_recursion):
                expr = expr.strip()

                if expr == '':  # Empty expression
                    return None

                if expr.startswith('('):
                    parens_count = 0
                    for m in re.finditer(r'[()]', expr):
                        if m.group(0) == '(':
                            parens_count += 1
                        else:
                            parens_count -= 1
                            if parens_count == 0:
                                sub_expr = expr[1:m.start()]
                                sub_result = self.interpret_expression(
                                    sub_expr, local_vars, allow_recursion)
                                remaining_expr = expr[m.end():].strip()
                                if not remaining_expr:
                                    return sub_result
                                else:
                                    expr = json.dumps(sub_result) + remaining_expr
                                break
                    else:
                        raise ExtractorError('Premature end of parens in %r' % expr)

                for op, opfunc in _ASSIGN_OPERATORS:
                    m = re.match(r'''(?x)
                        (?P<out>%s)(?:\[(?P<index>[^\]]+?)\])?
                        \s*%s
                        (?P<expr>.*)$''' % (_NAME_RE, re.escape(op)), expr)
                    if not m:
                        continue
                    right_val = self.interpret_expression(
                        m.group('expr'), local_vars, allow_recursion - 1)

                    if m.groupdict().get('index'):
                        lvar = local_vars[m.group('out')]
                        idx = self.interpret_expression(
                            m.group('index'), local_vars, allow_recursion)
                        assert isinstance(idx, int)
                        cur = lvar[idx]
                        val = opfunc(cur, right_val)
                        lvar[idx] = val
                        return val
                    else:
                        cur = local_vars.get(m.group('out'))
                        val = opfunc(cur, right_val)
                        local_vars[m.group('out')] = val
                        return val

                if expr.isdigit():
                    return int(expr)

                var_m = re.match(
                    r'(?!if|return|true|false)(?P<name>%s)$' % _NAME_RE,
                    expr)
                if var_m:
                    return local_vars[var_m.group('name')]

                try:
                    return json.loads(expr)
                except ValueError:
                    pass

                m = re.match(
                    r'(?P<var>%s)\.(?P<member>[^(]+)(?:\(+(?P<args>[^()]*)\))?$' % _NAME_RE,
                    expr)
                if m:
                    variable = m.group('var')
                    member = m.group('member')
                    arg_str = m.group('args')

                    if variable in local_vars:
                        obj = local_vars[variable]
                    else:
                        if variable not in self._objects:
                            self._objects[variable] = self.extract_object(variable)
                        obj = self._objects[variable]

                    if arg_str is None:
                        # Member access
                        if member == 'length':
                            return len(obj)
                        return obj[member]

                    assert expr.endswith(')')
                    # Function call
                    if arg_str == '':
                        argvals = tuple()
                    else:
                        argvals = tuple([
                            self.interpret_expression(v, local_vars, allow_recursion)
                            for v in arg_str.split(',')])

                    if member == 'split':
                        assert argvals == ('',)
                        return list(obj)
                    if member == 'join':
                        assert len(argvals) == 1
                        return argvals[0].join(obj)
                    if member == 'reverse':
                        assert len(argvals) == 0
                        obj.reverse()
                        return obj
                    if member == 'slice':
                        assert len(argvals) == 1
                        return obj[argvals[0]:]
                    if member == 'splice':
                        assert isinstance(obj, list)
                        index, howMany = argvals
                        res = []
                        for i in range(index, min(index + howMany, len(obj))):
                            res.append(obj.pop(index))
                        return res

                    return obj[member](argvals)

                m = re.match(
                    r'(?P<in>%s)\[(?P<idx>.+)\]$' % _NAME_RE, expr)
                if m:
                    val = local_vars[m.group('in')]
                    idx = self.interpret_expression(
                        m.group('idx'), local_vars, allow_recursion - 1)
                    return val[idx]

                for op, opfunc in _OPERATORS:
                    m = re.match(r'(?P<x>.+?)%s(?P<y>.+)' % re.escape(op), expr)
                    if not m:
                        continue
                    x, abort = self.interpret_statement(
                        m.group('x'), local_vars, allow_recursion - 1)
                    if abort:
                        raise ExtractorError(
                            'Premature left-side return of %s in %r' % (op, expr))
                    y, abort = self.interpret_statement(
                        m.group('y'), local_vars, allow_recursion - 1)
                    if abort:
                        raise ExtractorError(
                            'Premature right-side return of %s in %r' % (op, expr))
                    return opfunc(x, y)

                m = re.match(
                    r'^(?P<func>%s)\((?P<args>[a-zA-Z0-9_$,]+)\)$' % _NAME_RE, expr)
                if m:
                    fname = m.group('func')
                    argvals = tuple([
                        int(v) if v.isdigit() else local_vars[v]
                        for v in m.group('args').split(',')])
                    if fname not in self._functions:
                        self._functions[fname] = self.extract_function(fname)
                    return self._functions[fname](argvals)
                raise ExtractorError('Unsupported JS expression %r' % expr)

            def extract_object(self, objname):
                obj = {}
                obj_m = re.search(
                    (r'(?:var\s+)?%s\s*=\s*\{' % re.escape(objname)) +
                    r'\s*(?P<fields>([a-zA-Z$0-9]+\s*:\s*function\(.*?\)\s*\{.*?\}(?:,\s*)?)*)' +
                    r'\}\s*;',
                    self.code)
                fields = obj_m.group('fields')
                # Currently, it only supports function definitions
                fields_m = re.finditer(
                    r'(?P<key>[a-zA-Z$0-9]+)\s*:\s*function'
                    r'\((?P<args>[a-z,]+)\){(?P<code>[^}]+)}',
                    fields)
                for f in fields_m:
                    argnames = f.group('args').split(',')
                    obj[f.group('key')] = self.build_function(argnames, f.group('code'))

                return obj

            def extract_function(self, funcname):
                func_m = re.search(
                    r'''(?x)
                        (?:function\s+%s|[{;,]\s*%s\s*=\s*function|var\s+%s\s*=\s*function)\s*
                        \((?P<args>[^)]*)\)\s*
                        \{(?P<code>[^}]+)\}''' % (
                        re.escape(funcname), re.escape(funcname), re.escape(funcname)),
                    self.code)
                if func_m is None:
                    raise ExtractorError('Could not find JS function %r' % funcname)
                argnames = func_m.group('args').split(',')

                return self.build_function(argnames, func_m.group('code'))

            def call_function(self, funcname, *args):
                f = self.extract_function(funcname)
                return f(args)

            def build_function(self, argnames, code):
                def resf(args):
                    local_vars = dict(list(zip(argnames, args)))
                    for stmt in code.split(';'):
                        res, abort = self.interpret_statement(stmt, local_vars)
                        if abort:
                            break
                    return res
                return resf
        return JSInterpreter(jsCode)

    class YoutubeIE(BaseCLS):

        def _download_webpage(self, url_or_request, video_id, note=None, errnote=None, fatal=True, tries=1, timeout=5, encoding=None, data=None, headers={}, query={}):
            try:
                return super(YoutubeIE, self)._download_webpage(url_or_request, video_id, note=note, errnote=errnote, fatal=fatal, tries=tries, timeout=timeout, encoding=encoding, data=data, headers=headers, query=query)
            except Exception as ex:
                if ex.message.find('400: Bad Request') > -1:
                    self._downloader.cookiejar.clear()
                return super(YoutubeIE, self)._download_webpage(url_or_request, video_id, note=note, errnote=errnote, fatal=fatal, tries=tries, timeout=timeout, encoding=encoding, data=data, headers=headers, query=query)



        def _parse_sig_js(self, jscode):
            funcname = self._search_regex(
                (r'(["\'])signature\1\s*,\s*(?P<sig>[a-zA-Z0-9$]+)\(',
                 r'\.sig\|\|(?P<sig>[a-zA-Z0-9$]+)\('),
                jscode, 'Initial JS player signature function name', group='sig')

            jsi = CreateJSInterpreter(jscode)
            initial_function = jsi.extract_function(funcname)
            return lambda s: initial_function([s])

        def _is_valid_url(self, url, video_id, item='video', headers={}):
            try:
                return super(YoutubeIE, self)._is_valid_url(url, video_id, item, headers)
            except:
                return False

        def testYoutubeRealAddress(self, url):
            import sys
            import subprocess

            def getStartInfo():
                IS_WIN32 = 'win32' in str(sys.platform).lower()
                if IS_WIN32:
                    startupinfo = subprocess.STARTUPINFO()
                    startupinfo.dwFlags = subprocess.CREATE_NEW_CONSOLE | subprocess.STARTF_USESHOWWINDOW
                    startupinfo.wShowWindow = subprocess.SW_HIDE
                    return startupinfo
                else:
                    return None

            def download_webPage_by_CURLCMD(url, timeout=1, data=None, headers={}, http2=False, justHead = False):

                try:
                    cmd = 'curl -L  -m  %s ' % timeout
                    if http2:
                        cmd += ' --http2 '
                    if justHead:
                        cmd += ' -I '

                    cmd += ' "' + url + '"'
                    if data:
                        cmd += ' -d %s'
                    strHeader = ''
                    if headers:
                        for k, v in list(headers.items()):
                            strHeader += (' -H "%s: %s"') % (k, v)
                        if strHeader:
                            cmd += strHeader
                    print(cmd)
                    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, startupinfo=getStartInfo(),shell=True)
                    subStdout, subStderr = proc.communicate()
                    #print proc.wait()
                    content = str(subStdout, "utf-8")
                    return content
                except Exception as ex:
                    print(ex)
                    raise ex

            try:
                import re
                url2 = download_webPage_by_CURLCMD(url, http2=True, timeout=10)
                print('download_webPage_by_CURLCMD 1 ', url2)
                content = download_webPage_by_CURLCMD(url2, justHead=True, timeout=1)
                print('download_webPage_by_CURLCMD 2 ', content)
                if content.find('HTTP/1.1 200 OK')>-1:
                    print('download_webPage_by_CURLCMD 3 success ', url2)
                    return url2
                else:
                    print('download_webPage_by_CURLCMD 4 fail ', url2)
                    raise
            except:
                raise


        def checkAndReplaceToRedirect(self, f):
            import urllib.request, urllib.error, urllib.parse
            class HEADRequest(urllib.request.Request):
                def get_method(self):
                    return 'HEAD'

            print('checkAndReplaceToRedirect begin')
            if 'fragments' in f:
                print('checkAndReplaceToRedirect fragments begin')
                url = f['fragments'][0]['url']
                fcopy = f['fragments'][0].copy()
                if self.checkAndReplaceToRedirect(fcopy):
                    if fcopy['url'] != url:
                        list(map(self.checkAndReplaceToRedirect, f['fragments']))
                        print('checkAndReplaceToRedirect end begin')
                    else:
                        return True
                else:
                    return False
            elif 'url' in f:
                try:
                    self._downloader.urlopen(HEADRequest(f['url']))
                    return True
                except Exception as ex:
                    print('ex', ex)
                    try:
                        print('checkAndReplaceToRedirect url begin' , f['url'])
                        url = re.sub(r'//([^\.]+)', lambda x: '//redirector', f['url'])
                        if url.find('&alr=yes')==-1:
                            url += '&alr=yes'
                        print('url:', url)
                        f['url'] = self.testYoutubeRealAddress(url)
                        print('checkAndReplaceToRedirect url end')
                    except Exception as ex:
                        print('checkAndReplaceToRedirect url error end Ex:' , ex)
                        pass
                        return False
            print('checkAndReplaceToRedirect end')

        def checkAndReplaceToRedirectEx(self, f):
            def check_format(f):
                result = self._is_valid_url(f['url'], '',
                    item='%s video format' % f.get('format_id') if f.get('format_id') else 'video')
                if not result and 'fragments' in f and len(f['fragments'])>0:
                    try:
                        print('---begin check fragments url---')
                        result = self._is_valid_url(f['fragments'][0]['url'], '',
                            item='%s video format' % f.get('format_id') if f.get('format_id') else 'video')
                        print('---end check fragments url---')
                    except:
                        pass
                return result
            import sys
            if sys.platform == 'win32':
                return check_format(f)
            else:
                return self.checkAndReplaceToRedirect(f)


        def _check_formats(self, formats, video_id):
            if formats:
                formats[:] = [f for f in formats if self.checkAndReplaceToRedirectEx(f)]

        def convertToDash(self, f):

            if 'fragments' in f:
                print(f['format_id'], 'has fragments')
                return
            if 'none' not in [f.get('acodec', 'none'), f.get('vcodec', 'none')]:
                print(f['format_id'], 'not dash')
                return
            try:
                url = f['url']
                clen = self._search_regex(r'clen=(\d+)', url, '', fatal=False)

                if clen:
                    fragments = []
                    mediaLen = int(clen)

                    segmentLen = 2 * 1024 * 1024 if f.get('acodec', 'none') else 1 * 1024 * 1024
                    segmentCount = mediaLen / segmentLen
                    print(f['format_id'], 'mediaLen: %d segmentCount: %d' % (mediaLen, segmentCount))
                    if segmentCount > 0:
                        end = 0
                        for i in range(segmentCount):
                            start = 0 if i ==0 else end + 1
                            end = start + segmentLen
                            fragments.append({'url': '%s&range=%s-%s' % (url, start, end)})
                        if end < mediaLen:
                            fragments.append({'url': '%s&range=%s-%s' % (url, end + 1, mediaLen)})
                        f['fragments'] = fragments
                        # f.pop('url')
                        # f['protocol'] = 'https'
            except:
                pass


        def _real_extract(self, url):
            url, smuggled_data = unsmuggle_url(url, {})

            proto = (
                'http' if self._downloader.params.get('prefer_insecure', False)
                else 'https')

            start_time = None
            end_time = None
            parsed_url = compat_urllib_parse_urlparse(url)
            for component in [parsed_url.fragment, parsed_url.query]:
                query = compat_parse_qs(component)
                if start_time is None and 't' in query:
                    start_time = parse_duration(query['t'][0])
                if start_time is None and 'start' in query:
                    start_time = parse_duration(query['start'][0])
                if end_time is None and 'end' in query:
                    end_time = parse_duration(query['end'][0])

            # Extract original video URL from URL with redirection, like age verification, using next_url parameter
            mobj = re.search(self._NEXT_URL_RE, url)
            if mobj:
                url = proto + '://www.youtube.com/' + compat_urllib_parse_unquote(mobj.group(1)).lstrip('/')
            video_id = self.extract_id(url)

            # Get video webpage
            url = proto + '://www.youtube.com/watch?v=%s&gl=US&hl=en&has_verified=1&bpctr=9999999999' % video_id
            video_webpage = self._download_webpage(url, video_id, tries=3)

            # Attempt to extract SWF player URL
            mobj = re.search(r'swfConfig.*?"(https?:\\/\\/.*?watch.*?-.*?\.swf)"', video_webpage)
            if mobj is not None:
                player_url = re.sub(r'\\(.)', r'\1', mobj.group(1))
            else:
                player_url = None

            dash_mpds = []

            def add_dash_mpd(video_info):
                dash_mpd = video_info.get('dashmpd')
                if dash_mpd and dash_mpd[0] not in dash_mpds:
                    dash_mpds.append(dash_mpd[0])

            # Get video info
            embed_webpage = None
            is_live = None
            if re.search(r'player-age-gate-content">', video_webpage) is not None:
                age_gate = True
                # We simulate the access to the video from www.youtube.com/v/{video_id}
                # this can be viewed without login into Youtube
                url = proto + '://www.youtube.com/embed/%s' % video_id
                embed_webpage = self._download_webpage(url, video_id, 'Downloading embed webpage')
                data = compat_urllib_parse_urlencode({
                    'video_id': video_id,
                    'eurl': 'https://youtube.googleapis.com/v/' + video_id,
                    'sts': self._search_regex(
                        r'"sts"\s*:\s*(\d+)', embed_webpage, 'sts', default=''),
                })
                video_info_url = proto + '://www.youtube.com/get_video_info?' + data
                video_info_webpage = self._download_webpage(
                    video_info_url, video_id,
                    note='Refetching age-gated info webpage',
                    errnote='unable to download video info webpage')
                video_info = compat_parse_qs(video_info_webpage)
                add_dash_mpd(video_info)
            else:
                age_gate = False
                video_info = None
                sts = ''
                # Try looking directly into the video webpage
                ytplayer_config = self._get_ytplayer_config(video_id, video_webpage)
                if ytplayer_config:
                    args = ytplayer_config['args']
                    if args.get('url_encoded_fmt_stream_map'):
                        # Convert to the same format returned by compat_parse_qs
                        video_info = dict((k, [v]) for k, v in list(args.items()))
                        add_dash_mpd(video_info)
                    # Rental video is not rented but preview is available (e.g.
                    # https://www.youtube.com/watch?v=yYr8q0y5Jfg,
                    # https://github.com/rg3/yt-dlp/issues/10532)
                    if not video_info and args.get('ypc_vid'):
                        return self.url_result(
                            args['ypc_vid'], YoutubeIE.ie_key(), video_id=args['ypc_vid'])
                    if args.get('livestream') == '1' or args.get('live_playback') == 1:
                        is_live = True
                    sts = ytplayer_config.get('sts', '')
                if not video_info or self._downloader.params.get('youtube_include_dash_manifest', True):
                    # We also try looking in get_video_info since it may contain different dashmpd
                    # URL that points to a DASH manifest with possibly different itag set (some itags
                    # are missing from DASH manifest pointed by webpage's dashmpd, some - from DASH
                    # manifest pointed by get_video_info's dashmpd).
                    # The general idea is to take a union of itags of both DASH manifests (for example
                    # video with such 'manifest behavior' see https://github.com/rg3/yt-dlp/issues/6093)
                    self.report_video_info_webpage_download(video_id)
                    for el_type in ['&el=info', '&el=embedded', '&el=detailpage', '&el=vevo', '']:
                        video_info_url = (
                            '%s://www.youtube.com/get_video_info?&video_id=%s%s&ps=default&eurl=&gl=US&hl=en&sts=%s'
                            % (proto, video_id, el_type, sts))
                        video_info_webpage = self._download_webpage(
                            video_info_url,
                            video_id, note=False,
                            errnote='unable to download video info webpage')
                        get_video_info = compat_parse_qs(video_info_webpage)
                        if get_video_info.get('use_cipher_signature') != ['True']:
                            add_dash_mpd(get_video_info)
                        if not video_info:
                            video_info = get_video_info
                        # https://youtu.be/nH3AF2O-XP4H 此视频在%el=info下，官方组件返回需要登录，但它是不存在的，因此取最后一个reason
                        elif 'reason' in get_video_info:
                            video_info['reason'] = get_video_info['reason']
                        if 'token' in get_video_info:
                            # Different get_video_info requests may report different results, e.g.
                            # some may report video unavailability, but some may serve it without
                            # any complaint (see https://github.com/rg3/yt-dlp/issues/7362,
                            # the original webpage as well as el=info and el=embedded get_video_info
                            # requests report video unavailability due to geo restriction while
                            # el=detailpage succeeds and returns valid data). This is probably
                            # due to YouTube measures against IP ranges of hosting providers.
                            # Working around by preferring the first succeeded video_info containing
                            # the token if no such video_info yet was found.
                            if 'token' not in video_info:
                                video_info = get_video_info
                            break
            if 'token' not in video_info:
                if 'reason' in video_info:
                    if 'The uploader has not made this video available in your country.' in video_info['reason']:
                        regions_allowed = self._html_search_meta(
                            'regionsAllowed', video_webpage, default=None)
                        countries = regions_allowed.split(',') if regions_allowed else None
                        self.raise_geo_restricted(
                            msg=video_info['reason'][0], countries=countries)
                    raise ExtractorError(
                        'YouTube said: %s' % video_info['reason'][0],
                        expected=True, video_id=video_id)
                else:
                    raise ExtractorError(
                        '"token" parameter not in video info for unknown reason',
                        video_id=video_id)

            # title
            if 'title' in video_info:
                video_title = video_info['title'][0]
            else:
                self._downloader.report_warning('Unable to extract video title')
                video_title = '_'

            # description
            video_description = get_element_by_id("eow-description", video_webpage)
            if video_description:
                video_description = re.sub(r'''(?x)
                    <a\s+
                        (?:[a-zA-Z-]+="[^"]*"\s+)*?
                        (?:title|href)="([^"]+)"\s+
                        (?:[a-zA-Z-]+="[^"]*"\s+)*?
                        class="[^"]*"[^>]*>
                    [^<]+\.{3}\s*
                    </a>
                ''', r'\1', video_description)
                video_description = clean_html(video_description)
            else:
                fd_mobj = re.search(r'<meta name="description" content="([^"]+)"', video_webpage)
                if fd_mobj:
                    video_description = unescapeHTML(fd_mobj.group(1))
                else:
                    video_description = ''

            if 'multifeed_metadata_list' in video_info and not smuggled_data.get('force_singlefeed', False):
                if not self._downloader.params.get('noplaylist'):
                    entries = []
                    feed_ids = []
                    multifeed_metadata_list = video_info['multifeed_metadata_list'][0]
                    for feed in multifeed_metadata_list.split(','):
                        # Unquote should take place before split on comma (,) since textual
                        # fields may contain comma as well (see
                        # https://github.com/rg3/yt-dlp/issues/8536)
                        feed_data = compat_parse_qs(compat_urllib_parse_unquote_plus(feed))
                        entries.append({
                            '_type': 'url_transparent',
                            'ie_key': 'Youtube',
                            'url': smuggle_url(
                                '%s://www.youtube.com/watch?v=%s' % (proto, feed_data['id'][0]),
                                {'force_singlefeed': True}),
                            'title': '%s (%s)' % (video_title, feed_data['title'][0]),
                        })
                        feed_ids.append(feed_data['id'][0])
                    self.to_screen(
                        'Downloading multifeed video (%s) - add --no-playlist to just download video %s'
                        % (', '.join(feed_ids), video_id))
                    return self.playlist_result(entries, video_id, video_title, video_description)
                self.to_screen('Downloading just video %s because of --no-playlist' % video_id)

            if 'view_count' in video_info:
                view_count = int(video_info['view_count'][0])
            else:
                view_count = None

            # Check for "rental" videos
            if 'ypc_video_rental_bar_text' in video_info and 'author' not in video_info:
                raise ExtractorError('"rental" videos not supported. See https://github.com/rg3/yt-dlp/issues/359 for more information.', expected=True)

            # Start extracting information
            self.report_information_extraction(video_id)

            # uploader
            if 'author' not in video_info:
                raise ExtractorError('Unable to extract uploader name')
            video_uploader = compat_urllib_parse_unquote_plus(video_info['author'][0])

            # uploader_id
            video_uploader_id = None
            video_uploader_url = None
            mobj = re.search(
                r'<link itemprop="url" href="(?P<uploader_url>https?://www.youtube.com/(?:user|channel)/(?P<uploader_id>[^"]+))">',
                video_webpage)
            if mobj is not None:
                video_uploader_id = mobj.group('uploader_id')
                video_uploader_url = mobj.group('uploader_url')
            else:
                self._downloader.report_warning('unable to extract uploader nickname')

            # thumbnail image
            # We try first to get a high quality image:
            m_thumb = re.search(r'<span itemprop="thumbnail".*?href="(.*?)">',
                                video_webpage, re.DOTALL)
            if m_thumb is not None:
                video_thumbnail = m_thumb.group(1)
            elif 'thumbnail_url' not in video_info:
                self._downloader.report_warning('unable to extract video thumbnail')
                video_thumbnail = None
            else:   # don't panic if we can't find it
                video_thumbnail = compat_urllib_parse_unquote_plus(video_info['thumbnail_url'][0])

            # upload date
            upload_date = self._html_search_meta(
                'datePublished', video_webpage, 'upload date', default=None)
            if not upload_date:
                upload_date = self._search_regex(
                    [r'(?s)id="eow-date.*?>(.*?)</span>',
                     r'id="watch-uploader-info".*?>.*?(?:Published|Uploaded|Streamed live|Started) on (.+?)</strong>'],
                    video_webpage, 'upload date', default=None)
                if upload_date:
                    upload_date = ' '.join(re.sub(r'[/,-]', r' ', mobj.group(1)).split())
            upload_date = unified_strdate(upload_date)

            video_license = self._html_search_regex(
                r'<h4[^>]+class="title"[^>]*>\s*License\s*</h4>\s*<ul[^>]*>\s*<li>(.+?)</li',
                video_webpage, 'license', default=None)

            m_music = re.search(
                r'<h4[^>]+class="title"[^>]*>\s*Music\s*</h4>\s*<ul[^>]*>\s*<li>(?P<title>.+?) by (?P<creator>.+?)(?:\(.+?\))?</li',
                video_webpage)
            if m_music:
                video_alt_title = remove_quotes(unescapeHTML(m_music.group('title')))
                video_creator = clean_html(m_music.group('creator'))
            else:
                video_alt_title = video_creator = None

            m_episode = re.search(
                r'<div[^>]+id="watch7-headline"[^>]*>\s*<span[^>]*>.*?>(?P<series>[^<]+)</a></b>\s*S(?P<season>\d+)\s*•\s*E(?P<episode>\d+)</span>',
                video_webpage)
            if m_episode:
                series = m_episode.group('series')
                season_number = int(m_episode.group('season'))
                episode_number = int(m_episode.group('episode'))
            else:
                series = season_number = episode_number = None

            m_cat_container = self._search_regex(
                r'(?s)<h4[^>]*>\s*Category\s*</h4>\s*<ul[^>]*>(.*?)</ul>',
                video_webpage, 'categories', default=None)
            if m_cat_container:
                category = self._html_search_regex(
                    r'(?s)<a[^<]+>(.*?)</a>', m_cat_container, 'category',
                    default=None)
                video_categories = None if category is None else [category]
            else:
                video_categories = None

            video_tags = [
                unescapeHTML(m.group('content'))
                for m in re.finditer(self._meta_regex('og:video:tag'), video_webpage)]

            def _extract_count(count_name):
                return str_to_int(self._search_regex(
                    r'-%s-button[^>]+><span[^>]+class="yt-uix-button-content"[^>]*>([\d,]+)</span>'
                    % re.escape(count_name),
                    video_webpage, count_name, default=None))

            like_count = _extract_count('like')
            dislike_count = _extract_count('dislike')

            # subtitles
            video_subtitles = self.extract_subtitles(video_id, video_webpage)
            automatic_captions = self.extract_automatic_captions(video_id, video_webpage)

            video_duration = try_get(
                video_info, lambda x: int_or_none(x['length_seconds'][0]))
            if not video_duration:
                video_duration = parse_duration(self._html_search_meta(
                    'duration', video_webpage, 'video duration'))

            # annotations
            video_annotations = None
            if self._downloader.params.get('writeannotations', False):
                video_annotations = self._extract_annotations(video_id)


            if 'conn' in video_info and video_info['conn'][0].startswith('rtmp'):
                self.report_rtmp_download()
                formats = [{
                    'format_id': '_rtmp',
                    'protocol': 'rtmp',
                    'url': video_info['conn'][0],
                    'player_url': player_url,
                }]
            elif len(video_info.get('url_encoded_fmt_stream_map', [''])[0]) >= 1 or len(video_info.get('adaptive_fmts', [''])[0]) >= 1:
                encoded_url_map = video_info.get('url_encoded_fmt_stream_map', [''])[0] + ',' + video_info.get('adaptive_fmts', [''])[0]
                if 'rtmpe%3Dyes' in encoded_url_map:
                    raise ExtractorError('rtmpe downloads are not supported, see https://github.com/rg3/yt-dlp/issues/343 for more information.', expected=True)
                formats_spec = {}
                fmt_list = video_info.get('fmt_list', [''])[0]
                if fmt_list:
                    for fmt in fmt_list.split(','):
                        spec = fmt.split('/')
                        if len(spec) > 1:
                            width_height = spec[1].split('x')
                            if len(width_height) == 2:
                                formats_spec[spec[0]] = {
                                    'resolution': spec[1],
                                    'width': int_or_none(width_height[0]),
                                    'height': int_or_none(width_height[1]),
                                }
                formats = []
                for url_data_str in encoded_url_map.split(','):
                    url_data = compat_parse_qs(url_data_str)
                    if 'itag' not in url_data or 'url' not in url_data:
                        continue
                    format_id = url_data['itag'][0]
                    url = url_data['url'][0]

                    if 'sig' in url_data:
                        url += '&signature=' + url_data['sig'][0]
                    elif 's' in url_data:
                        encrypted_sig = url_data['s'][0]
                        ASSETS_RE = r'"assets":.+?"js":\s*("[^"]+")'

                        jsplayer_url_json = self._search_regex(
                            ASSETS_RE,
                            embed_webpage if age_gate else video_webpage,
                            'JS player URL (1)', default=None)
                        if not jsplayer_url_json and not age_gate:
                            # We need the embed website after all
                            if embed_webpage is None:
                                embed_url = proto + '://www.youtube.com/embed/%s' % video_id
                                embed_webpage = self._download_webpage(
                                    embed_url, video_id, 'Downloading embed webpage')
                            jsplayer_url_json = self._search_regex(
                                ASSETS_RE, embed_webpage, 'JS player URL')

                        player_url = json.loads(jsplayer_url_json)
                        if player_url is None:
                            player_url_json = self._search_regex(
                                r'ytplayer\.config.*?"url"\s*:\s*("[^"]+")',
                                video_webpage, 'age gate player URL')
                            player_url = json.loads(player_url_json)

                        if self._downloader.params.get('verbose'):
                            if player_url is None:
                                player_version = 'unknown'
                                player_desc = 'unknown'
                            else:
                                if player_url.endswith('swf'):
                                    player_version = self._search_regex(
                                        r'-(.+?)(?:/watch_as3)?\.swf$', player_url,
                                        'flash player', fatal=False)
                                    player_desc = 'flash player %s' % player_version
                                else:
                                    player_version = self._search_regex(
                                        [r'html5player-([^/]+?)(?:/html5player(?:-new)?)?\.js',
                                         r'(?:www|player)-([^/]+)(?:/[a-z]{2}_[A-Z]{2})?/base\.js'],
                                        player_url,
                                        'html5 player', fatal=False)
                                    player_desc = 'html5 player %s' % player_version

                            parts_sizes = self._signature_cache_id(encrypted_sig)
                            self.to_screen('{%s} signature length %s, %s' %
                                           (format_id, parts_sizes, player_desc))

                        signature = self._decrypt_signature(
                            encrypted_sig, video_id, player_url, age_gate)
                        url += '&signature=' + signature
                    if 'ratebypass' not in url:
                        url += '&ratebypass=yes'

                    dct = {
                        'format_id': format_id,
                        'url': url,
                        'player_url': player_url,
                    }

                    if format_id in self._formats:
                        dct.update(self._formats[format_id])
                    if format_id in formats_spec:
                        dct.update(formats_spec[format_id])

                    # Some itags are not included in DASH manifest thus corresponding formats will
                    # lack metadata (see https://github.com/rg3/yt-dlp/pull/5993).
                    # Trying to extract metadata from url_encoded_fmt_stream_map entry.
                    mobj = re.search(r'^(?P<width>\d+)[xX](?P<height>\d+)$', url_data.get('size', [''])[0])
                    width, height = (int(mobj.group('width')), int(mobj.group('height'))) if mobj else (None, None)

                    more_fields = {
                        'filesize': int_or_none(url_data.get('clen', [None])[0]),
                        'tbr': float_or_none(url_data.get('bitrate', [None])[0], 1000),
                        'width': width,
                        'height': height,
                        'fps': int_or_none(url_data.get('fps', [None])[0]),
                        'format_note': url_data.get('quality_label', [None])[0] or url_data.get('quality', [None])[0],
                    }
                    for key, value in list(more_fields.items()):
                        if value:
                            dct[key] = value
                    type_ = url_data.get('type', [None])[0]
                    if type_:
                        type_split = type_.split(';')
                        kind_ext = type_split[0].split('/')
                        if len(kind_ext) == 2:
                            kind, _ = kind_ext
                            dct['ext'] = mimetype2ext(type_split[0])
                            if kind in ('audio', 'video'):
                                codecs = None
                                for mobj in re.finditer(
                                        r'(?P<key>[a-zA-Z_-]+)=(?P<quote>["\']?)(?P<val>.+?)(?P=quote)(?:;|$)', type_):
                                    if mobj.group('key') == 'codecs':
                                        codecs = mobj.group('val')
                                        break
                                if codecs:
                                    dct.update(parse_codecs(codecs))

                    self.convertToDash(dct)
                    formats.append(dct)
            elif video_info.get('hlsvp'):
                manifest_url = video_info['hlsvp'][0]
                formats = []
                m3u8_formats = self._extract_m3u8_formats(
                    manifest_url, video_id, 'mp4', fatal=False)
                for a_format in m3u8_formats:
                    itag = self._search_regex(
                        r'/itag/(\d+)/', a_format['url'], 'itag', default=None)
                    if itag:
                        a_format['format_id'] = itag
                        if itag in self._formats:
                            dct = self._formats[itag].copy()
                            dct.update(a_format)
                            a_format = dct
                    a_format['player_url'] = player_url
                    # Accept-Encoding header causes failures in live streams on Youtube and Youtube Gaming
                    a_format.setdefault('http_headers', {})['Youtubedl-no-compression'] = 'True'
                    formats.append(a_format)
            else:
                unavailable_message = self._html_search_regex(
                    r'(?s)<h1[^>]+id="unavailable-message"[^>]*>(.+?)</h1>',
                    video_webpage, 'unavailable message', default=None)
                if unavailable_message:
                    raise ExtractorError(unavailable_message, expected=True)
                raise ExtractorError('no conn, hlsvp or url_encoded_fmt_stream_map information found in video info')

            # Look for the DASH manifest
            if self._downloader.params.get('youtube_include_dash_manifest', True):
                dash_mpd_fatal = True
                for mpd_url in dash_mpds:
                    dash_formats = {}
                    try:
                        def decrypt_sig(mobj):
                            s = mobj.group(1)
                            dec_s = self._decrypt_signature(s, video_id, player_url, age_gate)
                            return '/signature/%s' % dec_s

                        mpd_url = re.sub(r'/s/([a-fA-F0-9\.]+)', decrypt_sig, mpd_url)

                        for df in self._extract_mpd_formats(
                                mpd_url, video_id, fatal=dash_mpd_fatal,
                                formats_dict=self._formats):
                            # Do not overwrite DASH format found in some previous DASH manifest
                            if df['format_id'] not in dash_formats:
                                dash_formats[df['format_id']] = df
                            # Additional DASH manifests may end up in HTTP Error 403 therefore
                            # allow them to fail without bug report message if we already have
                            # some DASH manifest succeeded. This is temporary workaround to reduce
                            # burst of bug reports until we figure out the reason and whether it
                            # can be fixed at all.
                            dash_mpd_fatal = False
                    except (ExtractorError, KeyError) as e:
                        self.report_warning(
                            'Skipping DASH manifest: %r' % e, video_id)
                    if dash_formats:
                        # Remove the formats we found through non-DASH, they
                        # contain less info and it can be wrong, because we use
                        # fixed values (for example the resolution). See
                        # https://github.com/rg3/yt-dlp/issues/5774 for an
                        # example.
                        #formats = [f for f in formats if f['format_id'] not in dash_formats.keys()]
                        existKeys = [f['format_id'] for f in formats if f['format_id'] in list(dash_formats.keys())]
                        dash_formats = {key: dash_formats[key] for key in list(dash_formats.keys()) if key not in existKeys}

                        print('youtube_include_dash_manifest_as_single_url Begin')
                        for f in list(dash_formats.values()):
                            try:
                                if 'fragments' in f:
                                    if self._downloader.params.get('youtube_include_dash_manifest_as_single_url', False):
                                        if 'url' not in f['fragments'][0]:
                                            formats.append(f)
                                            continue

                                        str = f['fragments'][0]['url']
                                        str = self._search_regex(r'(.+)/\w+/0', str, 'fragments convert to url')
                                        id = f['format_id'] if 'format_id' in f else str
                                        print('---------------------------------begin dash check is_valid_url [[[[%s]]]]-------------------------------' % id)
                                        if self._is_valid_url(str, str):
                                            f['url'] = str
                                            f.pop('fragments')
                                            if 'manifest_url' in f:
                                                f.pop('manifest_url')
                                            f['protocol'] = 'http'
                                            formats.append(f)
                                            print('---------------------------------Sucess end dash check is_valid_url [[[[%s]]]] -------------------------------' % id)
                                        else:
                                            print(f['height'])
                                            print('---------------------------------Fail end dash check is_valid_url [[[[%s]]]] -------------------------------' % id)
                                            formats.append(f)
                                    else:
                                        formats.append(f)
                                else:
                                    print('not fragments in f')
                                    formats.append(f)
                            except:
                                pass
                        print('youtube_include_dash_manifest_as_single_url end')

            # Check for malformed aspect ratio
            stretched_m = re.search(
                r'<meta\s+property="og:video:tag".*?content="yt:stretch=(?P<w>[0-9]+):(?P<h>[0-9]+)">',
                video_webpage)
            if stretched_m:
                w = float(stretched_m.group('w'))
                h = float(stretched_m.group('h'))
                # yt:stretch may hold invalid ratio data (e.g. for Q39EVAstoRM ratio is 17:0).
                # We will only process correct ratios.
                if w > 0 and h > 0:
                    ratio = w / h
                    for f in formats:
                        if f.get('vcodec') != 'none':
                            f['stretched_ratio'] = ratio
            #time_out = self._downloader._socket_timeout
            #self._downloader._socket_timeout = 3
            #self._check_formats(formats, video_id)
            #self._downloader._socket_timeout = time_out
            self._sort_formats(formats)

            self.mark_watched(video_id, video_info)

            return {
                'id': video_id,
                'uploader': video_uploader,
                'uploader_id': video_uploader_id,
                'uploader_url': video_uploader_url,
                'upload_date': upload_date,
                'license': video_license,
                'creator': video_creator,
                'title': video_title,
                'alt_title': video_alt_title,
                'thumbnail': video_thumbnail,
                'description': video_description,
                'categories': video_categories,
                'tags': video_tags,
                'subtitles': video_subtitles,
                'automatic_captions': automatic_captions,
                'duration': video_duration,
                'age_limit': 18 if age_gate else 0,
                'annotations': video_annotations,
                'webpage_url': proto + '://www.youtube.com/watch?v=%s' % video_id,
                'view_count': view_count,
                'like_count': like_count,
                'dislike_count': dislike_count,
                'average_rating': float_or_none(video_info.get('avg_rating', [None])[0]),
                'formats': formats,
                'is_live': is_live,
                'start_time': start_time,
                'end_time': end_time,
                'series': series,
                'season_number': season_number,
                'episode_number': episode_number,
            }
    return YoutubeIE()

#----------------------------------End------------------------------------------------

# if __name__ == "__main__":
#     from yt_dlp.extractor import YoutubeIE
#
#     from yt_dlp.compat import (
#         compat_chr,
#         compat_parse_qs,
#         compat_urllib_parse_unquote,
#         compat_urllib_parse_unquote_plus,
#         compat_urllib_parse_urlencode,
#         compat_urllib_parse_urlparse,
#     )
#     from yt_dlp.utils import (
#         clean_html,
#         ExtractorError,
#         float_or_none,
#         get_element_by_id,
#         int_or_none,
#         mimetype2ext,
#         parse_codecs,
#         parse_duration,
#         remove_quotes,
#         smuggle_url,
#         str_to_int,
#         try_get,
#         unescapeHTML,
#         unified_strdate,
#         unsmuggle_url,
#     )
#
#     from yt_dlp.WS_Extractor import (
#         YoutubeDLPatch4Single,
#     )
#
#     def buildOptions(verbose=False):
#         ydl_opts = {}
#         ydl_opts['playlistend'] = 1
#         ydl_opts['debug_printtraffic'] =1
#         ydl_opts['verbose'] = 1 #'dump_intermediate_pages': 'debug_printtraffic': 1}
#         ydl_opts['socket_timeout'] = 60
#         ydl_opts['youtube_include_dash_manifest'] = True
#         ydl_opts['youtube_include_dash_manifest_as_single_url'] = True
#         # if sys.platform == 'win32':
#         #     ydl_opts['GA'] = GoogleAnalytics( 'UA-100395100-3')
#         # else:
#         #     ydl_opts['GA'] = GoogleAnalytics( 'UA-100395100-4')
#         return ydl_opts
#
#     ydl = YoutubeDLPatch4Single(buildOptions(False))
#
#     ie = CreateExtractor(YoutubeIE,
#         try_get,
#         clean_html,
#         str_to_int,
#         smuggle_url,
#         int_or_none,
#         unescapeHTML,
#         mimetype2ext,
#         parse_codecs,
#         float_or_none,
#         remove_quotes,
#         unsmuggle_url,
#         ExtractorError,
#         compat_parse_qs,
#         parse_duration,
#         unified_strdate,
#         get_element_by_id,
#         compat_urllib_parse_unquote,
#         compat_urllib_parse_urlparse,
#         compat_urllib_parse_urlencode,
#         compat_urllib_parse_unquote_plus
#     )
#
#     ie.set_downloader(ydl)
#     url = 'https://www.youtube.com/watch?v=D4flBFBd4uk'
#     ie._real_extract(url)
