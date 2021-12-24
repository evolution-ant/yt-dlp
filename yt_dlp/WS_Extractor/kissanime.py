# encoding: utf-8


import re
import random
from time import sleep
from ..extractor.common import InfoExtractor

from ..utils import (
    urlencode_postdata,
    sanitized_Request
)
from ..compat import (
    compat_urllib_parse_urlparse,
    compat_http_client
)
from ..utilsEX import JSInterpreter

class KissanimeIE(InfoExtractor):

    _VALID_URL = r'https?://(?:.+\.)?(?:kissanime|kisscartoon)\.(?:io|ru|so|me)'

    def solve_challenge(self, body):
        try:
            js = re.search(r"setTimeout\(function\(\){\s+(var "
                        "s,t,o,p,b,r,e,a,k,i,n,g,f.+?\r?\n[\s\S]+?a\.value =.+?)\r?\n", body).group(1)
        except Exception:
            raise ValueError("Unable to identify Cloudflare IUAM Javascript on website.")

        js = re.sub(r"a\.value = (parseInt\(.+?\)).+", r"\1", js)
        js = re.sub(r"\s{3,}[a-z](?: = |\.).+", "", js)

        js = re.sub(r"[\n\\']", "", js)

        if "parseInt" not in js:
            raise ValueError("Error parsing Cloudflare IUAM Javascript challenge.")

        js = js.replace('parseInt', ';return parseInt')
        js = 'function answer(){%s}' % js
        result = JSInterpreter(js, 'answer')
        try:
            result = int(result)
        except Exception:
            raise ValueError("Cloudflare IUAM challenge returned unexpected value")

        return result

    def _download_webpage_Ex(self, p, DEFAULT_USER_AGENT):

        httpClient = None
        try:
            httpClient = compat_http_client.HTTPConnection(p.netloc, 80, timeout=30)
            httpClient.request('GET', p.path, headers={'user-agent': DEFAULT_USER_AGENT})
            response = httpClient.getresponse()
            return response.status, response.read()

        except Exception as e:
            print(e)
        finally:
            if httpClient:
                httpClient.close()
    def _real_extract(self, url):

        DEFAULT_USER_AGENTS = [
            "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36",
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36",
            "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:46.0) Gecko/20100101 Firefox/46.0",
            "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:41.0) Gecko/20100101 Firefox/41.0"
        ]
        DEFAULT_USER_AGENT = random.choice(DEFAULT_USER_AGENTS)
        #DEFAULT_USER_AGENT = 'Mozilla/5.0 (iPad; CPU OS 9_1 like Mac OS X) AppleWebKit/601.1.46 (KHTML, like Gecko) Version/9.0 Mobile/13B143 Safari/601.1'
        try:
            url = url.replace('.ru/', '.io/').replace('.so', '.io')
            p = compat_urllib_parse_urlparse(url)
            domain = p.netloc
            webpage = self._download_webpage(url, url, headers={'user-agent': DEFAULT_USER_AGENT})
        except Exception as ex:

            status, body = self._download_webpage_Ex(p, DEFAULT_USER_AGENT)

            if status == 503:
                webpage = body
                jschl_vc = self._search_regex(r'name="jschl_vc" value="(\w+)"', webpage, 'jschl_vc', fatal=False)
                if jschl_vc:
                    sleep(5)  # Cloudflare requires a delay before solving the challenge

                    submit_url = "%s://%s/cdn-cgi/l/chk_jschl" % (p.scheme, domain)
                    try:
                        s_pass = self._search_regex(r'name="pass" value="(.+?)"', webpage, 'pass')
                    except Exception as e:
                        raise ValueError("Unable to parse Cloudflare anti-bots page: %s" % (e.message))
                    # Solve the Javascript challenge
                    jschl_answer= str(self.solve_challenge(webpage) + len(domain))
                    webpage = self._download_webpage(submit_url, submit_url, query={'jschl_vc': jschl_vc, 'pass': s_pass, 'jschl_answer': jschl_answer}, headers={'Referer': url, 'user-agent': DEFAULT_USER_AGENT})
            else:
                raise ex

        title = self._og_search_title(webpage, default=None) or self._html_search_regex(
            r'(?s)<title>(.*?)</title>', webpage, 'video title',
            default='video')

        episode_id = self._search_regex(r'var\s*current_episode_id\s*=\s*(\d+)|episode_id:\s*(\d+)', webpage, 'episode_id')
        data = {
            'episode_id': episode_id,
        }

        thumbnail = self._og_search_thumbnail(webpage)
        json_url = "%s://%s/ajax/anime/load_episodes" % (p.scheme, domain)
        json_url = json_url.replace('http://', 'https://')
        request = sanitized_Request(json_url, data=urlencode_postdata(data))
        request.add_header('x-requested-with', 'XMLHttpRequest')
        request.add_header('Referer', url)
        request.add_header('user-agent', DEFAULT_USER_AGENT)
        request.add_header('content-type', 'application/x-www-form-urlencoded; charset=UTF-8')

        playData = self._download_json(
            request, json_url
        )
        if playData['embed']:
            return self.url_result(playData['value'])
        else:
            playerUrl = playData['value']
            playData = self._download_json(playerUrl, playerUrl, headers={'Referer': url, 'user-agent': DEFAULT_USER_AGENT})
            formats = []
            if playData['playlist'][0].get('sources', None):
                for key, value in playData['playlist'][0]['sources']:
                    width = value['label']
                    formats.append({'url': value['file'], 'ext': '', 'width': width})
            else:
                videoUrl = playData['playlist'][0]['file']
                if videoUrl.find('m3u8') > -1:
                    formats.extend(self._extract_m3u8_formats(videoUrl,episode_id, 'mp4', fatal=False))
            self._sort_formats(formats)
            return {
                'id': episode_id,
                'title': title,
                'thumbnail': thumbnail,
                'formats': formats,
            }