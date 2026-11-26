# ==============================================================================
# CAI DAT TU DONG HINH NEN DONG 4K HUU SEIZ (40 CANH + iOS LOCK SCREEN + WIDGETS)
# Tu dong ghep: Code tu GitHub + 160 tep 4K .mp4/.jpg tu Google Drive AI_Full_Studio
# ==============================================================================
$ErrorActionPreference = "SilentlyContinue"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

$bundleDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$studioRoot = Split-Path -Parent (Split-Path -Parent $bundleDir)
$livelyWpDir = Join-Path $env:LOCALAPPDATA "Lively Wallpaper\Library\wallpapers\fresh_muses_4k.agy"
$localToolsDir = Join-Path $studioRoot "live-wallpapers\tools"
$localSrcDir = Join-Path $studioRoot "live-wallpapers\Fresh_Muses_4K_Live"

New-Item -ItemType Directory -Force -Path $livelyWpDir, $localToolsDir, $localSrcDir | Out-Null

# 1. Copy latest code (index.html, LivelyInfo.json, sys_telemetry_server.py) from GitHub bundle
Copy-Item -LiteralPath (Join-Path $bundleDir "index.html") -Destination (Join-Path $livelyWpDir "index.html") -Force
Copy-Item -LiteralPath (Join-Path $bundleDir "index.html") -Destination (Join-Path $localSrcDir "index.html") -Force
Copy-Item -LiteralPath (Join-Path $bundleDir "LivelyInfo.json") -Destination (Join-Path $livelyWpDir "LivelyInfo.json") -Force
Copy-Item -LiteralPath (Join-Path $bundleDir "sys_telemetry_server.py") -Destination (Join-Path $localToolsDir "sys_telemetry_server.py") -Force

# 2. Find 4K media pack (160 .mp4 + .jpg files) on Google Drive (Z:, G:, H:, E:, F:, D:)
$cloudWpDir = $null
foreach ($letter in @("Z", "G", "H", "E", "F", "I", "D")) {
    foreach ($sub in @(
        "Drive của tôi\AI_Full_Studio\05_Live_Wallpapers\Fresh_Muses_4K_Live",
        "My Drive\AI_Full_Studio\05_Live_Wallpapers\Fresh_Muses_4K_Live"
    )) {
        $cand = "${letter}:\$sub"
        if (Test-Path -LiteralPath $cand) {
            $cloudWpDir = $cand
            break
        }
    }
    if ($cloudWpDir) { break }
}

if ($cloudWpDir) {
    Write-Output "[SYNC] Dang dong bo an toan 40 canh 4K tu Google Drive ($cloudWpDir) (chong loi file 0x00)..."
    # TUYET DOI KHONG dung robocopy tren Google DriveFS vi robocopy copy sparse placeholder gay 88% byte 0x00!
    Get-ChildItem -LiteralPath $cloudWpDir -Filter "*.jpg" -File | ForEach-Object {
        $dst = Join-Path $livelyWpDir $_.Name
        $need = $true
        if (Test-Path -LiteralPath $dst) {
            try {
                $lb = [System.IO.File]::ReadAllBytes($dst)
                if ($lb.Length -eq $_.Length -and $lb.Length -gt 4 -and $lb[-2] -eq 0xFF -and $lb[-1] -eq 0xD9) {
                    $need = $false
                }
            } catch {}
        }
        if ($need) {
            try {
                $bytes = [System.IO.File]::ReadAllBytes($_.FullName)
                if ($bytes.Length -gt 4 -and $bytes[-2] -eq 0xFF -and $bytes[-1] -eq 0xD9) {
                    [System.IO.File]::WriteAllBytes($dst, $bytes)
                }
            } catch {}
        }
    }
    Write-Output "[SYNC] Da dong bo & kiem tra toan ven 100% anh 4K vao Lively Wallpaper!"
} else {
    Write-Output "[WARN] Chua tim thay Google Drive (AI_Full_Studio\05_Live_Wallpapers). Hay mo Google Drive Desktop roi chay lai!"
}

# 3. Setup silent Windows Startup telemetry daemon (CPU/RAM/GPU/VRAM/Weather/Quick Launch)
$pyw = @(
    (Join-Path $studioRoot "voice-studio\.venv\Scripts\pythonw.exe"),
    (Join-Path $studioRoot ".venv\Scripts\pythonw.exe"),
    (Get-Command pythonw.exe -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Source),
    (Get-Command python.exe -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Source)
) | Where-Object { $_ -and (Test-Path -LiteralPath $_) } | Select-Object -First 1

$telemScript = Join-Path $localToolsDir "sys_telemetry_server.py"
if ($pyw -and (Test-Path -LiteralPath $telemScript)) {
    $startup = [Environment]::GetFolderPath('Startup')
    $vbsPath = Join-Path $startup "AGY_Wallpaper_Telemetry.vbs"
    $vbsContent = "CreateObject(`"WScript.Shell`").Run `"`"`"$pyw`"`" `"`"$telemScript`"`"`", 0, False"
    Set-Content -Path $vbsPath -Value $vbsContent -Encoding ASCII

    # Start if not already listening on 18625
    $alive = $false
    try { Invoke-RestMethod "http://127.0.0.1:18625/stats.json" -TimeoutSec 1 | Out-Null; $alive = $true } catch {}
    if (-not $alive) {
        Start-Process -FilePath "wscript.exe" -ArgumentList "`"$vbsPath`"" -WindowStyle Hidden
    }
}

# 4. Hot-reload Lively Wallpaper on all monitors (without killing Lively.exe)
$livelyExe = @(
    "C:\Program Files\Lively Wallpaper\Lively.exe",
    (Join-Path $env:LOCALAPPDATA "Programs\Lively Wallpaper\Lively.exe")
) | Where-Object { Test-Path -LiteralPath $_ } | Select-Object -First 1

if ($livelyExe) {
    & $livelyExe closewp --monitor -1 | Out-Null
    Start-Sleep -Milliseconds 600
    for ($m = 1; $m -le 3; $m++) {
        & $livelyExe setwp --file "$livelyWpDir" --monitor $m | Out-Null
    }
    Write-Output "[LIVELY] Da ap dung hinh nen dong 4K Huu Seiz len tat ca man hinh!"
} else {
    Write-Output "[INFO] Chua thay Lively Wallpaper. Hay cai Lively Wallpaper tu Microsoft Store roi chay lai script nay."
}
