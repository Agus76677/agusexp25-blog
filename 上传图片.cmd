@echo off
REM Double-click to upload images to the pic.agusexp25.top image host.
REM You can also drag image files or folders onto this file's icon.
REM All real work is done by scripts\upload-images.ps1 + scripts\upload-images.mjs.

REM Use UTF-8 so Chinese messages and image URLs are not garbled.
chcp 65001 >nul

powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\upload-images.ps1" %*

echo.
pause
