@echo off
chcp 65001 >nul
REM Mở Full Studio an toàn (tuyệt đối không taskkill electron.exe để không bao giờ tắt nhầm Studio đang chạy/thu nhỏ!)
start "" "%~dp0full studido.exe"

REM Nếu Brave chính chưa gắn cổng 9333 -> đóng êm lưu phiên rồi bật lại giữ nguyên 100% tab cá nhân + gắn cổng đồng bộ 9333; nếu đã gắn 9333 rồi thì giữ nguyên!
powershell -NoProfile -Command "$alive=$false; try { $null=Invoke-WebRequest 'http://127.0.0.1:9333/json/version' -TimeoutSec 1 -UseBasicParsing; $alive=$true } catch {}; if(-not $alive){ Get-CimInstance Win32_Process -Filter \"Name='brave.exe'\" | Where-Object { $_.CommandLine -notmatch '--type=' -and $_.CommandLine -notmatch '--user-data-dir=' } | ForEach-Object { taskkill /PID $_.ProcessId | Out-Null }; Start-Sleep -Milliseconds 1200; Start-Process 'C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe' -ArgumentList '--remote-debugging-port=9333','--remote-debugging-address=127.0.0.1','--restore-last-session','--disable-background-timer-throttling','--disable-renderer-backgrounding','--disable-backgrounding-occluded-windows','--disable-features=CalculateNativeWinOcclusion','https://chatgpt.com/g/g-p-6afbde0b943481919c6ec31a3b4f8642/project','https://flow.google.com/' }"
