@echo off
REM Run this whenever clips suddenly stop working / "Requested format is not
REM available" appears. YouTube changes often; this updates yt-dlp to the latest.
cd /d "%~dp0"
echo Updating yt-dlp to the latest version...
python -m pip install -U yt-dlp
echo.
echo Done. Try generating footage again.
pause
