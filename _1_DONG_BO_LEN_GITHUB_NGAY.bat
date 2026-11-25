@echo off
chcp 65001 >nul
echo ======================================================================
echo   ĐANG ĐẨY TOÀN BỘ BẢN CẬP NHẬT MỚI NHẤT LÊN GITHUB + GOOGLE DRIVE...
echo ======================================================================
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0huu\github_sync_19h30_push.ps1"
echo.
echo [HOÀN TẤT] Đã đồng bộ xong lên GitHub (mygithub/main)!
pause
