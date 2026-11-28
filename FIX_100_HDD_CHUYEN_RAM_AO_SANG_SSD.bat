@echo off
chcp 65001 >nul
title Fix Triệt Để Lỗi 100%% Ổ HDD D: (Chuyển RAM Ảo Pagefile Sang Ổ SSD C:)

:: Tự động xin quyền Quản trị viên (Admin UAC) nếu chưa có
net session >nul 2>&1
if %errorLevel% neq 0 (
    powershell -NoProfile -Command "Start-Process -FilePath '%~f0' -Verb RunAs"
    exit /b
)

echo ============================================================================
echo   ĐANG CHUYỂN BỘ NHỚ ẢO (PAGEFILE 27.6 GB) TỪ Ổ CƠ HDD D: SANG Ổ SSD NVMe C:
echo ============================================================================
echo.

powershell -NoProfile -ExecutionPolicy Bypass -Command ^
  "$reg = 'HKLM:\SYSTEM\CurrentControlSet\Control\Session Manager\Memory Management'; " ^
  "Set-ItemProperty -Path $reg -Name 'PagingFiles' -Type MultiString -Value @('C:\pagefile.sys 8192 16384'); " ^
  "Write-Host '[OK] Đã khóa cứng Pagefile sang ổ SSD C:\pagefile.sys (8 GB - 16 GB) và gỡ hoàn toàn khỏi ổ HDD D:!' -ForegroundColor Green; " ^
  "foreach ($dir in @('D:\AI', 'D:\AI_Caches', 'D:\full studio_data', 'D:\antigravity', 'D:\antigraviti')) { " ^
  "  if (Test-Path $dir) { " ^
  "    $item = Get-Item $dir -Force; " ^
  "    $item.Attributes = $item.Attributes -bor [System.IO.FileAttributes]::NotContentIndexed; " ^
  "    Write-Host ('[OK] Đã tắt quét chỉ mục ngầm trên thư mục cũ: ' + $dir) -ForegroundColor Cyan; " ^
  "  } " ^
  "}"

echo.
echo ============================================================================
echo   HOÀN TẤT 100%%!
echo   Hãy KHỞI ĐỘNG LẠI MÁY (Restart) 1 lần để Windows xóa D:\pagefile.sys cũ
echo   và áp dụng ngay RAM ảo tốc độ cao trên ổ SSD C:!
echo   (Lưu ý: Lần sau mở Antigravity, hãy mở thư mục C:\AI\full studio thay vì D:\)
echo ============================================================================
echo.
pause
