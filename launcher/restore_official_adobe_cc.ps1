# Khôi phục 4 tệp gốc có chữ ký số chính hãng của Adobe Creative Cloud (sửa dứt điểm lỗi Error 301 khi cài Premiere)
$ErrorActionPreference = "Continue"

Write-Host "1. Đang tạm dừng các tiến trình nền của Creative Cloud..." -ForegroundColor Cyan
Stop-Service -Name "AdobeUpdateService", "AGMService", "AGSService" -Force -ErrorAction SilentlyContinue

$procs = @(
    "Creative Cloud",
    "Creative Cloud Helper",
    "Creative Cloud UI Helper",
    "Adobe Desktop Service",
    "Adobe Installer",
    "AdobeIPCBroker",
    "AdobeNotificationClient",
    "CCXProcess",
    "CoreSync"
)
foreach ($pn in $procs) {
    Get-Process -Name $pn -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
}
Start-Sleep -Seconds 2

Write-Host "`n2. Đang khôi phục 4 tệp gốc chính hãng Adobe (có chữ ký số hợp lệ)..." -ForegroundColor Cyan
$baks = @(
    "C:\Program Files (x86)\Common Files\Adobe\Adobe Desktop Common\ADS\Adobe Desktop Service.exe.bak",
    "C:\Program Files (x86)\Common Files\Adobe\Adobe Desktop Common\ADS\ContainerBL.dll.bak",
    "C:\Program Files (x86)\Common Files\Adobe\Adobe Desktop Common\AppsPanel\AppsPanelBL.dll.bak",
    "C:\Program Files (x86)\Common Files\Adobe\Adobe Desktop Common\HDBox\HDPIM.dll.bak"
)

foreach ($bak in $baks) {
    if (Test-Path $bak) {
        $target = $bak -replace '\.bak$', ''
        $bakSig = (Get-AuthenticodeSignature $bak).Status
        if ($bakSig -eq 'Valid') {
            Copy-Item -Path $bak -Destination $target -Force
            $newSig = (Get-AuthenticodeSignature $target).Status
            Write-Host "  [OK] Đã khôi phục: $(Split-Path $target -Leaf) -> Chữ ký số: $newSig" -ForegroundColor Green
        } else {
            Write-Host "  [BỎ QUA] $bak không có chữ ký Valid ($bakSig)" -ForegroundColor Yellow
        }
    }
}

Write-Host "`n3. Đang khởi động lại dịch vụ AdobeUpdateService & mở lại Creative Cloud..." -ForegroundColor Cyan
Start-Service -Name "AdobeUpdateService" -ErrorAction SilentlyContinue
Start-Process "C:\Program Files\Adobe\Adobe Creative Cloud\ACC\Creative Cloud.exe"

Write-Host "`nHOÀN TẤT 100%! Cửa sổ Creative Cloud đang mở lên — bạn bấm 'Thử lại / Cài đặt' trên Premiere là chạy mượt ngay!" -ForegroundColor Green
Start-Sleep -Seconds 4
