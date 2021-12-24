# cd $1
# git checkout dev
# git pull
cd './yt_dlp/'
pwd
python3 -O -m compileall .
cd ../pyc
pwd
go run pack.go

zip -r youtube_dl_v1.2.7.2.zip yt_dlp __main__.py 
rm __main__.py ./yt_dlp/__main__.py
