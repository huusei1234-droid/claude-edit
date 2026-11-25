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
    "$dir\Gigabyte.EnvironmentControl.dll"
)) {
    [Reflection.Assembly]::LoadFrom($dll) | Out-Null
}

$lines = @()
$mod = New-Object Gigabyte.EnvironmentControl.CoolingDevice.Fan.SmartGuardianFanControlCoordinateSystem

$temps = New-Object 'System.Collections.Generic.List[Single]'
$rpms = New-Object 'System.Collections.Generic.List[Single]'
$mod.GetHardwareMonitorDatas([ref]$temps, [ref]$rpms)

$lines += "=== 6 TEMPERATURE SENSORS ==="
for ($i = 0; $i -lt $temps.Count; $i++) {
    $tName = ""
    $mod.GetSensorTitle([Gigabyte.EnvironmentControl.Common.HardwareMonitor.SensorTypes]::Temperature, $i, [ref]$tName)
    $lines += "  Temp[$i] '$tName' = $($temps[$i]) C"
}

$lines += "=== 4 FAN TACHOMETERS (RPM) ==="
for ($i = 0; $i -lt $rpms.Count; $i++) {
    $fName = ""
    $mod.GetSensorTitle([Gigabyte.EnvironmentControl.Common.HardwareMonitor.SensorTypes]::Fan, $i, [ref]$fName)
    $lines += "  Fan[$i] '$fName' = $($rpms[$i]) RPM"
}

$lines += "=== CURRENT FAN CURVES ==="
for ($i = 0; $i -lt 4; $i++) {
    $cfg = New-Object Gigabyte.EnvironmentControl.Common.CoolingDevice.Fan.CoordinateSystem.SmartFanDataPointSet
    $mod.Get($i, [ref]$cfg)
    $tSel = 0
    $mod.GetTemperatureInputSelection($i, [ref]$tSel)
    $pts = ($cfg.DataPoints | ForEach-Object { "($($_.X)C -> $([math]::Round($_.Y / 2.55))%)" }) -join ', '
    $lines += "  FanCtrl[$i] TempSrc=$tSel Mode=$($cfg.Mode) DeltaT=$($cfg.DeltaTemperature) Points: $pts"
}

$lines | Set-Content -Path 'd:\AI\full studio\aigo-fan-control\test_live_rpm_out.txt' -Encoding UTF8
