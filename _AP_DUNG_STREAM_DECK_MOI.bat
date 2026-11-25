@echo off
chcp 65001 >nul
echo ====================================================================
echo   ĐANG CẬP NHẬT BỘ 3 TRANG STREAM DECK PRO (45 NÚT + ICON RETINA)
echo ====================================================================
set "SD_APP=%APPDATA%\Elgato\StreamDeck"
set "BACKUP_DIR=%SD_APP%\BackupV3\Backup_Truoc_Khi_Nang_Cap_%RANDOM%"

echo [1/4] Sao lưu cấu hình Stream Deck cũ vào BackupV3...
mkdir "%BACKUP_DIR%" 2>nul
xcopy /E /I /Y "%SD_APP%\ProfilesV3\BC31E860-727A-4D47-8EBF-276D4A834544.sdProfile" "%BACKUP_DIR%\BC31E860-727A-4D47-8EBF-276D4A834544.sdProfile" >nul

echo [2/4] Tạm đóng ứng dụng Stream Deck để ghi cấu hình mới...
taskkill /IM StreamDeck.exe /F >nul 2>&1
timeout /t 2 /nobreak >nul

echo [3/4] Ghi bộ 3 Trang (45 phím + Icon Studio) vào thiết bị...
rmdir /S /Q "%SD_APP%\ProfilesV3\BC31E860-727A-4D47-8EBF-276D4A834544.sdProfile" 2>nul
xcopy /E /I /Y "d:\AI\full studio\cong-cu-streamdeck\staged_v3\BC31E860-727A-4D47-8EBF-276D4A834544.sdProfile" "%SD_APP%\ProfilesV3\BC31E860-727A-4D47-8EBF-276D4A834544.sdProfile" >nul

echo [4/4] Khởi động lại Stream Deck — bàn phím cứng sẽ sáng đủ 15 nút ngay!
start "" "C:\Program Files\Elgato\StreamDeck\StreamDeck.exe"
echo.
echo [HOÀN TẤT 100%%] Hãy nhìn xuống bàn phím Stream Deck của bạn!
timeout /t 3
