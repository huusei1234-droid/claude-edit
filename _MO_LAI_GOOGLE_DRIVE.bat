@echo off
chcp 65001 >nul
taskkill /F /IM GoogleDriveFS.exe >nul 2>&1
timeout /t 1 /nobreak >nul
if exist "C:\Program Files\Google\Drive File Stream\launch.bat" (
  call "C:\Program Files\Google\Drive File Stream\launch.bat"
) else (
  start "" "C:\Program Files\Google\Drive File Stream\134.0.1.0\GoogleDriveFS.exe"
)
