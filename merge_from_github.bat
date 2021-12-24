git checkout dev
git remote remove origin
git remote add origin https://github.com/ytdl-org/yt-dlp.git
git pull origin master
git remote remove origin
git remote add origin http://10.10.2.124/software/yt-dlp.git
git push origin dev
