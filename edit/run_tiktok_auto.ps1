param(
  [switch]$Force
)
$ErrorActionPreference = "Continue"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$env:PYTHON = "C:\Users\001\AppData\Local\Programs\Python\Python311\python.exe"
$env:PATH = "$env:PATH;C:\Users\001\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-9.0.2-full_build\bin"
$editDir = "C:\AI\full studio\edit"
$logFile = Join-Path $editDir "tiktok_autopost.log"

Add-Content -LiteralPath $logFile -Value ("=" * 50) -Encoding UTF8
Add-Content -LiteralPath $logFile -Value "[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] Starting TikTok Auto-Post (Force=$Force)..." -Encoding UTF8

for ($i = 0; $i -lt 12; $i++) {
  if ((Test-Path -LiteralPath "G:\Other computers\My Computer") -or (Test-Path -LiteralPath "G:\Máy tính khác\My Computer") -or (Test-Path -LiteralPath "G:\.shortcut-targets-by-id")) { break }
  Start-Sleep -Seconds 5
}

$nodeArgs = @( (Join-Path $editDir "tiktok_brave_post.mjs"), "--post" )
if ($Force) { $nodeArgs += "--force" }

for ($attempt = 1; $attempt -le 3; $attempt++) {
  $out = & "C:\Program Files\nodejs\node.exe" @nodeArgs 2>&1
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
