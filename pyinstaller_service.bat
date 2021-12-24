rmdir /s /q build
rmdir /s /q dist
"%PYTHON3%\Scripts\pyinstaller.exe" -i ./resource/exe.ico yt_dlp\WebService.py
xcopy /s /e bin\win\win32_dll\*.* dist\WebService\

"%PYTHON3%\Scripts\pyinstaller.exe" -i ./resource/exe.ico yt_dlp\__main__.py
xcopy /s /e bin\win\win32_dll\*.* dist\__main__  

rmdir /s /q .\bin\win\x86
mkdir .\bin\win\x86


xcopy  /s /e dist\__main__ .\bin\win\x86
ren .\bin\win\x86\__main__.exe YoutubeToMP3Process.exe
ren .\bin\win\x86\__main__.exe.manifest YoutubeToMP3Process.exe.manifest

xcopy  /s /e /Y dist\WebService .\bin\win\x86
ren .\bin\win\x86\WebService.exe YoutubeToMP3Service.exe
ren .\bin\win\x86\WebService.exe.manifest YoutubeToMP3Service.exe.manifest


xcopy /s /e .\bin\win\shared_bin\ffmpeg_win32\*.* .\bin\win\x86
xcopy  .bin\win\shared_bin\AtomicParsley.exe .\bin\win\x86

rmdir /s /q .\bin\win\x64
mkdir .\bin\win\x64
xcopy  /s /e dist\WebService .\bin\win\x64
ren .\bin\win\x64\WebService.exe YoutubeToMP3Service.exe
ren .\bin\win\x64\WebService.exe.manifest YoutubeToMP3Service.exe.manifest
xcopy /s /e .\bin\win\shared_bin\ffmpeg_win32\*.* .\bin\win\x64
xcopy  .\bin\win\shared_bin\AtomicParsley.exe .\bin\win\x64
