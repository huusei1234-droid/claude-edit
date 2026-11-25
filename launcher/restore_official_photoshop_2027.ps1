# Khôi phục các tệp gốc có chữ ký số chính hãng Adobe cho Photoshop 2027 & Creative Cloud
$ErrorActionPreference = "Continue"

Write-Host "=== KHOI PHUC TEP GOC CHINH HANG ADOBE PHOTOSHOP 2027 & CREATIVE CLOUD ===" -ForegroundColor Cyan

# 1. Kiểm tra nếu Photoshop đang chạy thì nhắc đóng
if (Get-Process -Name "Photoshop" -ErrorAction SilentlyContinue) {
    Write-Host "[!] Phat hien Photoshop dang chay. Vui long dong Photoshop truoc roi chay lai." -ForegroundColor Yellow
    Pause
    exit 1
}

# 2. Khôi phục 3 tệp gốc có chữ ký số Valid cho Adobe Photoshop 2027
Write-Host "`n[1/3] Dang khoi phuc 3 tep goc chinh hang cho Adobe Photoshop 2027..." -ForegroundColor Cyan
$psBaks = @(
    "C:\Program Files\Adobe\Adobe Photoshop 2027\Photoshop.exe.bak",
    "C:\Program Files\Adobe\Adobe Photoshop 2027\dvaappsupport.dll.bak",
    "C:\Program Files\Adobe\Adobe Photoshop 2027\dynamic-torqnative.dll.bak"
)

foreach ($bak in $psBaks) {
    if (Test-Path $bak) {
        $target = $bak -replace '\.bak$', ''
        $sig = (Get-AuthenticodeSignature $bak).Status
        if ($sig -eq 'Valid') {
            Copy-Item -Path $bak -Destination $target -Force
            $newSig = (Get-AuthenticodeSignature $target).Status
            Write-Host "  [OK] $(Split-Path $target -Leaf) -> Chu ky so: $newSig" -ForegroundColor Green
        } else {
            Write-Host "  [BO QUA] $bak khong co chu ky Valid ($sig)" -ForegroundColor Yellow
        }
    } else {
        Write-Host "  [KHONG THAY] $bak" -ForegroundColor DarkYellow
    }
}

# 3. Khôi phục 4 tệp gốc chính hãng Adobe Creative Cloud (nếu có .bak Valid)
Write-Host "`n[2/3] Dang khoi phuc 4 tep goc chinh hang cho Adobe Creative Cloud..." -ForegroundColor Cyan
Stop-Service -Name "AdobeUpdateService", "AGMService", "AGSService" -Force -ErrorAction SilentlyContinue
$ccProcs = @(
    "Creative Cloud",
    "Creative Cloud Helper",
    "Creative Cloud UI Helper",
    "Adobe Desktop Service",
    "AdobeIPCBroker",
    "AdobeNotificationClient",
    "CCXProcess",
    "CoreSync"
)
foreach ($pn in $ccProcs) {
    Get-Process -Name $pn -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
}
Start-Sleep -Seconds 2

$ccBaks = @(
    "C:\Program Files (x86)\Common Files\Adobe\Adobe Desktop Common\ADS\Adobe Desktop Service.exe.bak",
    "C:\Program Files (x86)\Common Files\Adobe\Adobe Desktop Common\ADS\ContainerBL.dll.bak",
    "C:\Program Files (x86)\Common Files\Adobe\Adobe Desktop Common\AppsPanel\AppsPanelBL.dll.bak",
    "C:\Program Files (x86)\Common Files\Adobe\Adobe Desktop Common\HDBox\HDPIM.dll.bak"
)

foreach ($bak in $ccBaks) {
    if (Test-Path $bak) {
        $target = $bak -replace '\.bak$', ''
        $sig = (Get-AuthenticodeSignature $bak).Status
        if ($sig -eq 'Valid') {
            Copy-Item -Path $bak -Destination $target -Force
            $newSig = (Get-AuthenticodeSignature $target).Status
            Write-Host "  [OK] $(Split-Path $target -Leaf) -> Chu ky so: $newSig" -ForegroundColor Green
        } else {
            Write-Host "  [BO QUA] $bak khong co chu ky Valid ($sig)" -ForegroundColor Yellow
        }
    }
}

# 4. Sao lưu & đặt lại Preferences Photoshop 2027 về mặc định sạch
Write-Host "`n[3/3] Dang sao luu va dat lai cau hinh (Preferences) Photoshop 2027..." -ForegroundColor Cyan
$settingsDir = "$env:APPDATA\Adobe\Adobe Photoshop 2027\Adobe Photoshop 2027 Settings"
if (Test-Path $settingsDir) {
    $backupDir = "$env:APPDATA\Adobe\Adobe Photoshop 2027\Adobe Photoshop 2027 Settings.bak_$(Get-Date -Format 'yyyyMMdd_HHmmss')"
    Rename-Item -Path $settingsDir -NewName (Split-Path $backupDir -Leaf) -Force -ErrorAction SilentlyContinue
    Write-Host "  [OK] Da sao luu Preferences cu sang: $backupDir" -ForegroundColor Green
}

# 5. Khởi động lại dịch vụ Adobe & mở Creative Cloud
Start-Service -Name "AdobeUpdateService" -ErrorAction SilentlyContinue
if (Test-Path "C:\Program Files\Adobe\Adobe Creative Cloud\ACC\Creative Cloud.exe") {
    Start-Process "C:\Program Files\Adobe\Adobe Creative Cloud\ACC\Creative Cloud.exe"
}

Write-Host "`nHOAN TAT! Dang mo Adobe Photoshop 2027 de kiem tra..." -ForegroundColor Green
Start-Sleep -Seconds 3
Start-Process "C:\Program Files\Adobe\Adobe Photoshop 2027\Photoshop.exe"
Start-Sleep -Seconds 4
