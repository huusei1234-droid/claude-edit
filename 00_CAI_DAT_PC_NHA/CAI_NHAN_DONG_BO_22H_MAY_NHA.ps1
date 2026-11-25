# ==============================================================================
# CAI DAT 1 CHAM CHO MAY TINH O NHA: TU DONG NHAN TAI NGUYEN GITHUB LUC 22H00
# Chạy 1 lần duy nhất trên máy ở nhà -> Kéo ngay bản mới nhất & đặt lịch 22h00 hàng ngày
# ==============================================================================
$ErrorActionPreference = "SilentlyContinue"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host "  CAI DAT TU DONG NHAN TAI NGUYEN GITHUB LUC 22H00 (MAY TINH O NHA)   " -ForegroundColor Cyan
Write-Host "======================================================================" -ForegroundColor Cyan

if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    if (Get-Command winget -ErrorAction SilentlyContinue) {
        Write-Host "-> Dang cai Git tu dong..." -ForegroundColor Yellow
        winget install --id Git.Git -e --accept-package-agreements --accept-source-agreements --silent
        $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
    }
}

$studioRoot = if (Test-Path "D:\") { "D:\AI\full studio" } elseif (Test-Path "E:\") { "E:\AI\full studio" } else { "C:\AI\full studio" }
$syncBin    = Join-Path $studioRoot ".sync"
New-Item -ItemType Directory -Force -Path $syncBin | Out-Null

$repoRawPull = "https://raw.githubusercontent.com/huusei1234-droid/claude-edit/main/00_CAI_DAT_PC_NHA/github_sync_22h_pull.ps1"
$localPullPs1 = Join-Path $syncBin "github_sync_22h_pull.ps1"
$sameFolderPs1 = Join-Path $PSScriptRoot "github_sync_22h_pull.ps1"

if (Test-Path -LiteralPath $sameFolderPs1) {
    Copy-Item -LiteralPath $sameFolderPs1 -Destination $localPullPs1 -Force
} elseif (Test-Path -LiteralPath "$studioRoot\00_CAI_DAT_PC_NHA\github_sync_22h_pull.ps1") {
    Copy-Item -LiteralPath "$studioRoot\00_CAI_DAT_PC_NHA\github_sync_22h_pull.ps1" -Destination $localPullPs1 -Force
} else {
    Invoke-WebRequest -Uri $repoRawPull -UseBasicParsing -OutFile $localPullPs1
}

# Đăng ký Scheduled Task chạy đúng 22:00 tối hàng ngày (StartWhenAvailable = bật máy sau 22h vẫn tự chạy bù ngay!)
$taskName = "AI_Full_Studio_GitHub_Pull_22h00"
Unregister-ScheduledTask -TaskName $taskName -Confirm:$false -ErrorAction SilentlyContinue
$trigger  = New-ScheduledTaskTrigger -Daily -At "22:00"
$action   = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File `"$localPullPs1`""
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable -MultipleInstances IgnoreNew -ExecutionTimeLimit (New-TimeSpan -Minutes 20)

Register-ScheduledTask -TaskName $taskName -Trigger $trigger -Action $action -Settings $settings -Description "Tu dong nhan dong bo tai nguyen Full Studio & 27 Skills tu GitHub luc 22:00 hang ngay (sau khi may cong ty day len luc 21:00)" -Force | Out-Null
Write-Host "[OK] Da dang ky lich tu dong nhan tai nguyen GitHub luc 22:00 hang ngay ($taskName)!" -ForegroundColor Green

Write-Host "`n-> Dang keo ngay tai nguyen moi nhat tu GitHub ve may ngay bay gio..." -ForegroundColor Yellow
powershell.exe -NoProfile -ExecutionPolicy Bypass -File $localPullPs1

Write-Host "`n======================================================================" -ForegroundColor Green
Write-Host "  HOAN TAT 100%! MAY TINH O NHA SE TU NHAN DONG BO LUC 22H00 MOI TOI! " -ForegroundColor Green
Write-Host "  (Neu ban bat may sau 22h00, Windows se tu dong chay bu ngay khi mo) " -ForegroundColor White
Write-Host "======================================================================" -ForegroundColor Green
