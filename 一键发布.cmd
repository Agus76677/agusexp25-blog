@echo off
REM Double-click to publish the blog: build + commit + push main.
REM GitHub Actions then deploys to https://agusexp25.top (~2-3 min).
REM Equivalent to `pnpm deploy`, but calls node directly so it works
REM even if pnpm is not on PATH.

chcp 65001 >nul
cd /d "%~dp0"

if not exist "scripts\deploy.mjs" (
  echo [!] scripts\deploy.mjs not found. Is this the blog project root?
  echo.
  pause
  exit /b 1
)

where node >nul 2>nul
if errorlevel 1 (
  echo [!] Node.js not found. Install it from https://nodejs.org first.
  echo.
  pause
  exit /b 1
)

REM Optional commit message. Just press Enter to use the default.
set "MSG="
set /p "MSG=Commit message (press Enter for default): "

echo.
if defined MSG (
  node scripts\deploy.mjs --message "%MSG%"
) else (
  node scripts\deploy.mjs
)

echo.
pause
