@echo off
chcp 65001 >nul
echo cancel > "d:\AI\full studio\huu\logs\CANCEL_AUTO_SHUTDOWN.flag"
shutdown.exe /a 2>nul
powershell -NoProfile -Command "Get-CimInstance Win32_Process | Where-Object { $_.Name -match '^python' -and $_.CommandLine -match 'auto_shutdown_watchdog\.py' } | ForEach-Object { Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue }"
echo [DA HUY] Da huy thanh cong che do tu dong tat may!
pause
