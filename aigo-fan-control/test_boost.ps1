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

# Also check HardwareMonitorControl directly for all Fan sensors!
$hwm = New-Object Gigabyte.EnvironmentControl.HardwareMonitor.HardwareMonitorControl
$hwm.Initialize([Gigabyte.EnvironmentControl.Common.HardwareMonitor.HardwareMonitorSourceTypes]::All)
Start-Sleep -Milliseconds 800
$coll = $null
$hwm.GetCurrentMonitoredData([Gigabyte.EnvironmentControl.Common.HardwareMonitor.SensorTypes]::Fan, [ref]$coll)
$lines += "=== HWM FAN SENSORS BEFORE BOOST ==="
foreach ($s in $coll) { $lines += "  HWM Fan: $($s.DisplayName) = $($s.Value)" }

# Boost CPU Fan (index 0) and System Fans (1..3) to Turbo (90% base -> 100%) and re-read after 2.5s!
for ($idx = 0; $idx -lt 4; $idx++) {
    $mod.SetCalibrationPwm($idx, 95)
}
Start-Sleep -Milliseconds 2500

$temps2 = New-Object 'System.Collections.Generic.List[Single]'
$rpms2 = New-Object 'System.Collections.Generic.List[Single]'
$mod.GetHardwareMonitorDatas([ref]$temps2, [ref]$rpms2)
$lines += "=== AFTER 95% PWM BOOST ==="
for ($i = 0; $i -lt $rpms2.Count; $i++) {
    $lines += "  Fan[$i] = $($rpms2[$i]) RPM"
}
$coll2 = $null
$hwm.GetCurrentMonitoredData([Gigabyte.EnvironmentControl.Common.HardwareMonitor.SensorTypes]::Fan, [ref]$coll2)
foreach ($s in $coll2) { $lines += "  HWM Fan After: $($s.DisplayName) = $($s.Value)" }

$hwm.Dispose()
$lines | Set-Content -Path 'd:\AI\full studio\aigo-fan-control\test_boost_out.txt' -Encoding UTF8
