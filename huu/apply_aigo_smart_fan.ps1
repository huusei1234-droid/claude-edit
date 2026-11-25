# ==============================================================================
# CAI DAT QUAT AIGO THONG MINH THEO NHIET DO CPU (GIGABYTE B760M G P WIFI DDR4)
# Chay voi quyen Administrator -> Chuyen FullSpeed sang SmartFan (Customize)
# ==============================================================================
$ErrorActionPreference = "Stop"

# Tự động yêu cầu quyền Administrator chuẩn của Windows (UAC) nếu chưa có
$isAdmin = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Start-Process powershell.exe -Verb RunAs -ArgumentList "-NoProfile -ExecutionPolicy Bypass -File `"$PSCommandPath`""
    exit
}

$fanDir = "C:\Program Files\GIGABYTE\Control Center\Fan"
$setupXml = Join-Path $fanDir "setupmode.xml"
$profXml  = Join-Path $fanDir "Profile-0.xml"

Write-Host "=== DANG CAU HINH QUAT AIGO THONG MINH THEO NHIET DO CPU ===" -ForegroundColor Cyan

# 1. Sao lưu cấu hình cũ
Copy-Item $setupXml "$setupXml.bak" -Force
Copy-Item $profXml  "$profXml.bak"  -Force

# 2. Chuyển từ FullSpeed (quay 100% ồn) sang Customize (Smart Fan Curve)
@"
<?xml version="1.0" encoding="utf-8"?>
<FanModeConfig xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <Mode>Customize</Mode>
</FanModeConfig>
"@ | Set-Content -Path $setupXml -Encoding UTF8

# 3. Chỉnh toàn bộ CPU + System 1, 2, 3 (quạt Aigo) bám theo nhiệt độ CPU (TemperatureInputSelection = 2)
# Đường cong êm - mát thông minh: 35°C -> 30% | 45°C -> 42% | 55°C -> 58% | 65°C -> 78% | 75°C -> 100%
[xml]$doc = Get-Content $profXml -Encoding UTF8
$curve = @(
    @{X=0;  Y=76},
    @{X=35; Y=76},
    @{X=45; Y=108},
    @{X=55; Y=148},
    @{X=65; Y=199},
    @{X=75; Y=255},
    @{X=80; Y=255},
    @{X=85; Y=255}
)

foreach ($cfg in $doc.ArrayOfSmartFanDataPointConfig.SmartFanDataPointConfig) {
    $cfg.TemperatureInputSelection = "2" # CPU Temperature
    $cfg.Mode = "SmartFanMode"
    foreach ($ms in $cfg.ModeSettings.SmartFanDataPointSet) {
        if ($ms.Mode -eq "SmartFanMode" -or $ms.Mode -eq "StairStepMode") {
            $ms.DeltaTemperature = "3"
            $pts = $ms.DataPoints.SmartFanDataPoint
            for ($i = 0; $i -lt $pts.Count -and $i -lt $curve.Count; $i++) {
                $pts[$i].X = [string]$curve[$i].X
                $pts[$i].Y = [string]$curve[$i].Y
            }
        }
    }
}
$doc.Save($profXml)

# 4. Khởi động lại dịch vụ Gigabyte EasyTune & mở GIGABYTE Control Center (Fan + RGB Fusion)
Restart-Service -Name "EasyTuneEngineService" -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 1
Start-Process "C:\Program Files\GIGABYTE\Control Center\LaunchGCC.exe"

Write-Host ""
Write-Host "[THANH CONG] Da chuyen quat Aigo sang che do thong minh theo nhiet do CPU!" -ForegroundColor Green
Write-Host "  - 0..35°C : ~30% (sieu em)" -ForegroundColor Gray
Write-Host "  - 45°C    : ~42% (em nhe)" -ForegroundColor Gray
Write-Host "  - 55°C    : ~58% (mat khi dung phim)" -ForegroundColor Gray
Write-Host "  - 65°C    : ~78% (tang gio)" -ForegroundColor Gray
Write-Host "  - 75°C+   : 100% (giai nhiet toi da)" -ForegroundColor Gray
Write-Host ""
Write-Host "GIGABYTE Control Center dang mo len -> Vao muc 'RGB Fusion' de chinh mau quat Aigo!" -ForegroundColor Yellow
Start-Sleep -Seconds 4
