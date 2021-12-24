#!/bin/bash
set -v on

export PATH=/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin

rm -rf  build
rm -rf  dist
/Library/Frameworks/Python.framework/Versions/3.6/bin/pyinstaller --windowed --onefile --clean --noconfirm --hidden-import=execjs yt_dlp/__main__.py
/Library/Frameworks/Python.framework/Versions/3.6/bin/pyinstaller --windowed --onefile --clean --noconfirm --hidden-import=execjs yt_dlp/WebService.py

rm -rf  bin/mac
mkdir bin/mac

cp -f dist/__main__ bin/mac/
mv bin/mac/__main__ bin/mac/YoutubeToMP3Process

cp -f dist/WebService bin/mac/
mv bin/mac/WebService bin/mac/YoutubeToMP3Service

cp bin/win/shared_bin/ffmpeg_mac/* bin/mac
chmod -R 755 bin/mac

#cp -rf bin/mac/* ../dvdfabui/runtime/mac_res/python3


