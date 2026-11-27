@echo off
chcp 65001 >nul
REM Mở Full Studio an toàn (tuyệt đối không taskkill electron.exe để không bao giờ tắt nhầm Studio đang chạy/thu nhỏ!)
start "" "%~dp0full studido.exe"

REM Tự động tìm đúng đường dẫn brave.exe (cả LocalAppData lẫn Program Files) và gắn cổng đồng bộ 9333 giữ nguyên 100% các tab đang mở!
powershell -NoProfile -Command "$alive=$false; try { $null=Invoke-WebRequest 'http://127.0.0.1:9333/json/version' -TimeoutSec 1 -UseBasicParsing; $alive=$true } catch {}; if(-not $alive){ $b=@(\"$env:LOCALAPPDATA\BraveSoftware\Brave-Browser\Application\brave.exe\",'C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe') | Where-Object { Test-Path $_ } | Select-Object -First 1; Get-CimInstance Win32_Process -Filter \"Name='brave.exe'\" | Where-Object { $_.CommandLine -notmatch '--type=' -and $_.CommandLine -notmatch '--user-data-dir=' } | ForEach-Object { taskkill /PID $_.ProcessId | Out-Null }; Start-Sleep -Milliseconds 1400; Start-Process $b -ArgumentList '--remote-debugging-port=9333','--remote-debugging-address=127.0.0.1','--restore-last-session','--disable-background-timer-throttling','--disable-renderer-backgrounding','--disable-backgrounding-occluded-windows','--disable-features=CalculateNativeWinOcclusion','https://chatgpt.com/g/g-p-6b093335deb88191accc76e34088233f/project','https://flow.google.com/' }"
