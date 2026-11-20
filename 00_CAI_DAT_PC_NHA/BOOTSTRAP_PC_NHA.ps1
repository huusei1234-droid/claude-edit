[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
Write-Host "=====================================================================" -ForegroundColor Cyan
Write-Host "   SIÊU TRÌNH CÀI ĐẶT & TỐI ƯU PC Ở NHÀ (FULL STUDIO × ANTIGRAVITY)  " -ForegroundColor Cyan
Write-Host "=====================================================================" -ForegroundColor Cyan

# 1. Cài đặt toàn bộ phần mềm cốt lõi nếu máy ở nhà chưa có
if (Get-Command winget -ErrorAction SilentlyContinue) {
    $apps = @(
        @{ cmd = "git";    id = "Git.Git";                label = "Git" },
        @{ cmd = "python"; id = "Python.Python.3.11";     label = "Python 3.11" },
        @{ cmd = "node";   id = "OpenJS.NodeJS.LTS";      label = "Node.js LTS" },
        @{ cmd = "ffmpeg"; id = "Gyan.FFmpeg";            label = "FFmpeg Full" },
        @{ cmd = "bun";    id = "Oven-sh.Bun";            label = "Bun" },
        @{ cmd = "uv";     id = "astral-sh.uv";           label = "uv" }
    )
    foreach ($a in $apps) {
        if (-not (Get-Command $a.cmd -ErrorAction SilentlyContinue)) {
            Write-Host "-> Đang cài $($a.label)..." -ForegroundColor Yellow
            winget install --id $a.id -e --accept-package-agreements --accept-source-agreements --silent
        } else {
            Write-Host "[ĐÃ CÓ] $($a.label)" -ForegroundColor Green
        }
    }

    # Kiểm tra Google Drive for Desktop & CapCut & Brave
    if (-not (Test-Path "C:\Program Files\Google\Drive File Stream") -and -not (Test-Path "$env:LOCALAPPDATA\Google\DriveFS")) {
        Write-Host "-> Đang cài Google Drive for Desktop để đồng bộ kho AI_Full_Studio..." -ForegroundColor Yellow
        winget install --id Google.GoogleDrive -e --accept-package-agreements --accept-source-agreements --silent
    }
    if (-not (Test-Path "$env:LOCALAPPDATA\CapCut\Apps\CapCut.exe")) {
        Write-Host "-> Đang cài CapCut PC..." -ForegroundColor Yellow
        winget install --id ByteDance.CapCut -e --accept-package-agreements --accept-source-agreements --silent
    }
    if (-not (Test-Path "C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe") -and -not (Test-Path "$env:LOCALAPPDATA\BraveSoftware\Brave-Browser\Application\brave.exe")) {
        Write-Host "-> Đang cài trình duyệt Brave (chạy Google Flow & ChatGPT HTPM)..." -ForegroundColor Yellow
        winget install --id Brave.Brave -e --accept-package-agreements --accept-source-agreements --silent
    }
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
}

# 2. Tối ưu ngay Windows, Nguồn Ultimate Performance, GPU rời NVIDIA & Adobe CEP
foreach ($ver in @("CSXS.9", "CSXS.10", "CSXS.11", "CSXS.12", "CSXS.13")) {
    $rp = "HKCU:\Software\Adobe\$ver"
    New-Item -Path $rp -Force | Out-Null
    Set-ItemProperty -Path $rp -Name "PlayerDebugMode" -Value "1" -Type String -Force
}

$adminScript = @'
powercfg -duplicatescheme e9a42b02-d5df-448d-aa00-03f14749eb61 | Out-Null
$ult = (powercfg -list | Select-String -Pattern "([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}).*(Ultimate Performance|Hiệu suất tối ưu)" | Select-Object -First 1)
if ($ult) { powercfg -setactive $ult.Matches[0].Groups[1].Value } else { powercfg -setactive 8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c }
powercfg -change -standby-timeout-ac 0
Set-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Control\FileSystem" -Name "LongPathsEnabled" -Value 1 -Type DWord -Force
New-Item -Path "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\AppModelUnlock" -Force | Out-Null
Set-ItemProperty -Path "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\AppModelUnlock" -Name "AllowDevelopmentWithoutDevLicense" -Value 1 -Type DWord -Force
Set-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Control\GraphicsDrivers" -Name "HwSchMode" -Value 2 -Type DWord -Force
'@
try {
    Start-Process powershell.exe -Verb RunAs -ArgumentList "-NoProfile -WindowStyle Hidden -ExecutionPolicy Bypass -Command `"$adminScript`"" -Wait
    Write-Host "[OK] Đã bật Ultimate Performance + GPU Hardware Scheduling + LongPaths!" -ForegroundColor Green
} catch {}

# 3. Tìm kho AI_Full_Studio trên Google Drive và kích hoạt InitHome
function Get-DriveStudio {
    foreach ($l in @("Z","G","H","E","F","I","J","D","C")) {
        $r = "${l}:\"
        if (-not (Test-Path -LiteralPath $r)) { continue }
        foreach ($s in @("Drive của tôi\AI_Full_Studio", "My Drive\AI_Full_Studio", "AI_Full_Studio")) {
            $c = Join-Path $r $s
            if (Test-Path -LiteralPath $c) { return $c }
        }
        $w = Get-ChildItem -Path "${r}*" -Directory -ErrorAction SilentlyContinue | ForEach-Object {
            $p = Join-Path $_.FullName "AI_Full_Studio"
            if (Test-Path -LiteralPath $p) { $p }
        } | Select-Object -First 1
        if ($w) { return $w }
    }
    return $null
}

$studioDrive = Get-DriveStudio
if (-not $studioDrive) {
    Write-Host "`n[CHỜ ĐĂNG NHẬP GOOGLE DRIVE]" -ForegroundColor Yellow
    Write-Host "Vui lòng đăng nhập tài khoản Google chứa kho 'AI_Full_Studio' trong Google Drive vừa mở..." -ForegroundColor White
    $gdExe = Get-ChildItem "C:\Program Files\Google\Drive File Stream" -Recurse -Filter "GoogleDriveFS.exe" -ErrorAction SilentlyContinue | Select-Object -First 1
    if ($gdExe) { Start-Process $gdExe.FullName }
    for ($i = 0; $i -lt 120; $i++) {
        Start-Sleep -Seconds 5
        $studioDrive = Get-DriveStudio
        if ($studioDrive) { break }
    }
}

if ($studioDrive) {
    $engine = Join-Path $studioDrive "00_DONG_BO_2_MAY\sync_engine.ps1"
    if (Test-Path -LiteralPath $engine) {
        Write-Host "`n[PHÁT HIỆN KHO DRIVE: $studioDrive] -> Bắt đầu đồng bộ Full Studio, 27 Skills, Font TVC & MCP!" -ForegroundColor Green
        powershell.exe -NoProfile -ExecutionPolicy Bypass -File $engine -Mode InitHome
    }
} else {
    Write-Host "`n[XONG BƯỚC NỀN] Sau khi bạn đăng nhập Google Drive xong, chỉ cần chạy file 0_CAI_DAT_LAN_DAU_MAY_NHA.bat trong AI_Full_Studio\00_DONG_BO_2_MAY!" -ForegroundColor Cyan
}
