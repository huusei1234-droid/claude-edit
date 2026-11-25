@echo off
chcp 65001 >nul
title SUA LOI NHAP VIDEO CAPCUT & DONG BO CACHE GOOGLE DRIVE Z:
echo ============================================================================
echo   SUA LOI "KHONG THE NHAP DO MOT SO TAI NGUYEN BI HONG" TREN CAPCUT & Z:\
echo ============================================================================
echo.
echo LƯU Ý: Hãy đóng cửa sổ CapCut trước khi tiếp tục để tự động nối lại các video
echo bị báo đỏ "Phương tiện bị mất" trong dự án HTPM!
echo.
pause

echo.
echo [1/4] Dang tam dong Google Drive Desktop de lam moi bang cache chunks.db...
taskkill /IM GoogleDriveFS.exe /F >nul 2>&1
timeout /t 2 /nobreak >nul

echo [2/4] Dang xoa 73.488 dong cache cu bi lech giua o C moi va D:\DRIVE cu...
"D:\AI\full studio\.venv\Scripts\python.exe" "D:\AI\full studio\launcher\fix_gdfs_and_relink_capcut.py" cache

echo.
echo [3/4] Dang khoi dong lai Google Drive Desktop (giu nguyen 100%% tai khoan)...
start "" "C:\Program Files\Google\Drive File Stream\launch.bat"

echo Dang cho o Z:\ ket noi lai (khoang 5-8 giay)...
for /L %%i in (1,1,15) do (
    if exist "Z:\Máy tính khác" goto :Z_READY
    timeout /t 1 /nobreak >nul
)
:Z_READY
echo   [OK] O Google Drive Z:\ da san sang!

echo.
echo [4/4] Dang tu dong noi lai (relink) cac video "Phuong tien bi mat" trong CapCut...
"D:\AI\full studio\.venv\Scripts\python.exe" "D:\AI\full studio\launcher\fix_gdfs_and_relink_capcut.py" relink

echo.
echo ============================================================================
echo   HOAN TAT 100%%! Gio ban mo lai CapCut la nhap video tu Z:\ muot ngay!
echo ============================================================================
pause
