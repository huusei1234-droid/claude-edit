$ErrorActionPreference = "Continue"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$env:PYTHON = "C:\Users\Hang thu\AppData\Local\Programs\Python\Python311\python.exe"
$logFile = "D:\AI\full studio\edit\tiktok_autopost.log"

Add-Content -LiteralPath $logFile -Value ("=" * 50) -Encoding UTF8
Add-Content -LiteralPath $logFile -Value "[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] Starting TikTok Auto-Post..." -Encoding UTF8

for ($i = 0; $i -lt 12; $i++) {
  if (Test-Path -LiteralPath "Z:\Máy tính khác\My Computer") { break }
  Start-Sleep -Seconds 5
}

for ($attempt = 1; $attempt -le 3; $attempt++) {
  $out = & "C:\Program Files\nodejs\node.exe" "D:\AI\full studio\edit\tiktok_brave_post.mjs" --post 2>&1
  $code = $LASTEXITCODE
  if ($out) {
    $out | ForEach-Object { Add-Content -LiteralPath $logFile -Value "$_" -Encoding UTF8 }
  }
  if ($code -eq 0) {
    Add-Content -LiteralPath $logFile -Value "[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] Finished successfully (attempt $attempt)" -Encoding UTF8
    exit 0
  }
  if ($code -eq 2) {
    Add-Content -LiteralPath $logFile -Value "[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] Stopped: AUTH_REQUIRED (exit code 2)" -Encoding UTF8
    exit 2
  }
  Add-Content -LiteralPath $logFile -Value "[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] Transient error (code $code) on attempt $attempt, retrying in 25s..." -Encoding UTF8
  Start-Sleep -Seconds 25
}
Add-Content -LiteralPath $logFile -Value "[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] Failed after 3 attempts" -Encoding UTF8
exit 1
