@echo off
setlocal
cd /d "%~dp0"
where node >nul 2>nul
if errorlevel 1 (
  echo Node.js was not found. Install Node.js 20 or newer, then run this file again.
  pause
  exit /b 1
)
if not exist node_modules\express (
  echo Installing website packages for the first run...
  call npm install
  if errorlevel 1 (
    echo Package installation failed. Check your internet connection and try npm install manually.
    pause
    exit /b 1
  )
)
start "Fruit Atlas" cmd /k "cd /d ""%~dp0"" && npm start"
timeout /t 2 >nul
start "" http://localhost:3000
endlocal
