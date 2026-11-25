$ErrorActionPreference = 'Continue'
$dir = 'C:\Program Files (x86)\GIGABYTE\EasyTuneEngineService'
Set-Location $dir
$env:PATH = "$dir;$env:PATH"
foreach ($dll in @(
    "$dir\Gigabyte.dll",
    "$dir\Gigabyte.Win32.dll",
    "$dir\Gigabyte.ComputerSystemHardware.dll",
    "$dir\Gigabyte.ComputerSystemHardware.PCI.dll",
    "$dir\Gigabyte.EnvironmentControl.Common.dll",
    "$dir\Gigabyte.EnvironmentControl.LowPinCount.dll",
    "$dir\Gigabyte.WmiAcpi.dll",
    "$dir\Gigabyte.WmiAcpi.EnvironmentControl.dll",
    "$dir\Gigabyte.EnvironmentControl.dll"
)) {
    if (Test-Path $dll) { [Reflection.Assembly]::LoadFrom($dll) | Out-Null }
}

$lines = @()
$mod = New-Object Gigabyte.EnvironmentControl.CoolingDevice.Fan.SmartGuardianFanControlCoordinateSystem
$mod.ResetCalibrationPwm()
Start-Sleep -Milliseconds 300

# Read after ResetCalibrationPwm
$cfg0 = New-Object Gigabyte.EnvironmentControl.Common.CoolingDevice.Fan.CoordinateSystem.SmartFanDataPointSet
$mod.Get(0, [ref]$cfg0)
$lines += "After Reset -> Mode=$($cfg0.Mode), Count=$($cfg0.DataPoints.Count)"
if ($cfg0.DataPoints) {
    $pts0 = ($cfg0.DataPoints | ForEach-Object { "($($_.X)C->$([math]::Round($_.Y/2.55))%)" }) -join ', '
    $lines += "  Points0: $pts0"
}

# Build fresh SmartFanDataPointSet for Turbo (85% -> 100%) and Set!
$newSet = New-Object Gigabyte.EnvironmentControl.Common.CoolingDevice.Fan.CoordinateSystem.SmartFanDataPointSet
$newSet.Mode = [Gigabyte.EnvironmentControl.Common.CoolingDevice.Fan.FanConfigMode]::SmartFanMode
$newSet.DeltaTemperature = 2
$newSet.FanSpeed = 0
$newSet.DataPoints = New-Object 'System.Collections.Generic.List[Gigabyte.EnvironmentControl.Common.CoolingDevice.Fan.CoordinateSystem.SmartFanDataPoint]'
$curve = @(
    @(0, 217), @(20, 217), @(30, 224), @(40, 235),
    @(50, 248), @(60, 255), @(70, 255), @(75, 255)
)
foreach ($pair in $curve) {
    $dp = New-Object Gigabyte.EnvironmentControl.Common.CoolingDevice.Fan.CoordinateSystem.SmartFanDataPoint
    $dp.X = [int]$pair[0]
    $dp.Y = [int]$pair[1]
    $newSet.DataPoints.Add($dp)
}

for ($idx = 0; $idx -lt 4; $idx++) {
    $mod.Set($idx, $newSet)
}

# Verify readback in fresh object!
$mod2 = New-Object Gigabyte.EnvironmentControl.CoolingDevice.Fan.SmartGuardianFanControlCoordinateSystem
$vcfg = New-Object Gigabyte.EnvironmentControl.Common.CoolingDevice.Fan.CoordinateSystem.SmartFanDataPointSet
$mod2.Get(0, [ref]$vcfg)
$vpts = ($vcfg.DataPoints | ForEach-Object { "($($_.X)C->$([math]::Round($_.Y/2.55))%)" }) -join ', '
$lines += "VERIFIED CURVE[0]: Mode=$($vcfg.Mode) Points: $vpts"

$temps = New-Object 'System.Collections.Generic.List[Single]'
$rpms = New-Object 'System.Collections.Generic.List[Single]'
$mod2.GetHardwareMonitorDatas([ref]$temps, [ref]$rpms)
$lines += "CPU Temp Now: $($temps[2]) C | RPMs: $($rpms -join ', ')"

$lines | Set-Content -Path 'd:\AI\full studio\aigo-fan-control\test_curve_write_out.txt' -Encoding UTF8
