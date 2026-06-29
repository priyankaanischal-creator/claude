@echo off
REM Run this whenever clips OR images suddenly stop working. It refreshes the
REM parts that depend on websites that change often (YouTube / DuckDuckGo).
cd /d "%~dp0"
echo Updating yt-dlp (YouTube) and ddgs (image search) to the latest...
python -m pip install -U yt-dlp ddgs requests Pillow
echo.
echo Done. Try generating footage again.
pause
