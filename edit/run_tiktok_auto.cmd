@echo off
chcp 65001 >nul
set "PYTHON=C:\Users\Hang thu\AppData\Local\Programs\Python\Python311\python.exe"
echo ================================================== >> "D:\AI\full studio\edit\tiktok_autopost.log"
echo [%DATE% %TIME%] Starting TikTok Auto-Post... >> "D:\AI\full studio\edit\tiktok_autopost.log"

REM Wait up to 60s if Google Drive Z:\ is still mounting right after boot
for /L %%i in (1,1,12) do (
  if exist "Z:\Máy tính khác\My Computer" goto :DRIVE_READY
  timeout /t 5 /nobreak >nul
)
:DRIVE_READY

REM Retry up to 3 times on transient network/DOM timeout (exit code 1), stop immediately on success (0) or AUTH_REQUIRED (2)
for /L %%r in (1,1,3) do (
  "C:\Program Files\nodejs\node.exe" "D:\AI\full studio\edit\tiktok_brave_post.mjs" --post >> "D:\AI\full studio\edit\tiktok_autopost.log" 2>&1
  if errorlevel 2 (
    if not errorlevel 3 (
      echo [%DATE% %TIME%] Stopped: AUTH_REQUIRED ^(exit code 2^) >> "D:\AI\full studio\edit\tiktok_autopost.log"
      exit /b 2
    )
  )
  if not errorlevel 1 (
    echo [%DATE% %TIME%] Finished successfully ^(attempt %%r^) >> "D:\AI\full studio\edit\tiktok_autopost.log"
    exit /b 0
  )
  echo [%DATE% %TIME%] Transient error on attempt %%r, retrying in 25s... >> "D:\AI\full studio\edit\tiktok_autopost.log"
  timeout /t 25 /nobreak >nul
)
echo [%DATE% %TIME%] Failed after 3 attempts >> "D:\AI\full studio\edit\tiktok_autopost.log"
exit /b 1
