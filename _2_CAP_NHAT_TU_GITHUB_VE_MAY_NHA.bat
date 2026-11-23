@echo off
chcp 65001 >nul
echo ======================================================================
echo   ĐANG KÉO BẢN CẬP NHẬT MỚI NHẤT TỪ GITHUB VỀ MÁY Ở NHÀ...
echo ======================================================================
if exist "%~dp000_CAI_DAT_PC_NHA\github_sync_22h_pull.ps1" (
    powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp000_CAI_DAT_PC_NHA\github_sync_22h_pull.ps1"
) else (
    powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0.sync\github_sync_22h_pull.ps1"
)
echo.
echo [HOÀN TẤT] Máy ở nhà đã cập nhật xong toàn bộ Code, Skills, Rules & 65 Font TVC!
pause
