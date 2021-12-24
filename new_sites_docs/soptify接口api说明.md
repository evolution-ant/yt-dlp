###页面类型：

* show类型（list）
https://open.spotify.com/show/1VXcH8QHkjRcTCEd88U3ti

* album（list）
该地址只有4受，可用来做测试
https://open.spotify.com/album/09sGMSeeP4bZQOCTpgKGX8

* playlist类型
https://open.spotify.com/playlist/37i9dQZF1DXbVmhQBDSKS7

* artist类型
https://open.spotify.com/artist/0WxATzoERy4WPwWO9OD4o3

* track 单歌类型
https://open.spotify.com/track/4Bb8R3YYLxO0iRJdLU6l3a
该链接可能会跳转到：
https://open.spotify.com/embed/track/4Bb8R3YYLxO0iRJdLU6l3a?utm_campaign=twitter-player&utm_source=open&utm_medium=twitter


获取token：
```
url = "https://accounts.spotify.com/api/token"
headers = {
            'Authorization': self._spotify_base64(),
            'Content-Type': "application/x-www-form-urlencoded",
            'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36",
            'cache-control': "no-cache"
        }
data = "grant_type=client_credentials"
```


获取json数据
```
url = https://api.spotify.com/v1/tracks/access_token?market=ES"
headers.pop('Content-Type', None)
headers['Authorization'] = "Bearer %s" % access_token
```

持续更新...