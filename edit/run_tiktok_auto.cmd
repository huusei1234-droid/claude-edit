@echo off
chcp 65001 >nul
set "PYTHON=C:\Users\Hang thu\AppData\Local\Programs\Python\Python311\python.exe"
echo ================================================== >> "D:\AI\full studio\edit\tiktok_autopost.log"
echo [%DATE% %TIME%] Starting TikTok Auto-Post... >> "D:\AI\full studio\edit\tiktok_autopost.log"
REM Wait up to 45s if Google Drive Z:\ is still mounting right after boot
for /L %%i in (1,1,9) do (
  if exist "Z:\Máy tính khác\My Computer" goto :DRIVE_READY
  timeout /t 5 /nobreak >nul
)
:DRIVE_READY
"C:\Program Files\nodejs\node.exe" "D:\AI\full studio\edit\tiktok_brave_post.mjs" --post >> "D:\AI\full studio\edit\tiktok_autopost.log" 2>&1
echo [%DATE% %TIME%] Finished with exit code %ERRORLEVEL% >> "D:\AI\full studio\edit\tiktok_autopost.log"
