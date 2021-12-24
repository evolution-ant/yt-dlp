#!/bin/bash
set -v on

rm -rf  build
rm -rf  dist
pyinstaller -i ../YoutubeToMP3/Resources/DVDFab.icns --hidden-import=execjs yt_dlp/__main__.py

#xcopy /s /e win32_dll\*.* dist\__main__
unzip dist/__main__/base_library.zip -d dist/__main__
rm -f dist/__main__/base_library.zip

rm -rf  bin/mac
mkdir bin/mac
cp -rf dist/__main__/* bin/mac/
mv bin/mac/__main__ bin/mac//YoutubeToMP3Process
#ren ..\runtime64\YoutubeToMP3Mac\__main__.exe.manifest YoutubeToMP3Process.exe.manifest
cp bin/win/shared_bin/ffmpeg_mac/* bin/mac

#exit 0

if [ ! -d ../dvdfabui/runtime/mac_res/python3 ]
then
  mkdir ../dvdfabui/runtime/mac_res/python3
fi

cp -rf bin/mac/* ../dvdfabui/runtime/mac_res/python3


