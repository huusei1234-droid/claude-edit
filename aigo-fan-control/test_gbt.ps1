$ErrorActionPreference = 'Continue'
$mbDir = 'C:\Program Files\GIGABYTE\Control Center\Lib\MBEasyTune'
$commDir = 'C:\Program Files\GIGABYTE\Control Center\Lib\COMMDLL'
foreach ($dll in @(
    "$commDir\Gigabyte.dll",
    "$commDir\Gigabyte.Win32.dll",
    "$mbDir\Gigabyte.Engine.dll",
    "$mbDir\Gigabyte.Engine.Remoting.dll",
    "$mbDir\Gigabyte.ComputerSystemHardware.dll",
    "$mbDir\Gigabyte.ComputerSystemHardware.PCI.dll",
    "$mbDir\Gigabyte.EnvironmentControl.Common.dll",
    "$mbDir\Gigabyte.EnvironmentControl.dll",
    "$mbDir\Gigabyte.Engine.EnvironmentControl.dll"
)) {
    [Reflection.Assembly]::LoadFrom($dll) | Out-Null
}

$lines = @()
$fanMod = New-Object Gigabyte.EnvironmentControl.CoolingDevice.Fan.SmartGuardianFanControl
$lines += "Direct SmartGuardianFanControl: IsSupported=$($fanMod.IsSupported), FanCtrlCount=$($fanMod.FanControlCount), TachCount=$($fanMod.FanTachometerInputCount), TempCount=$($fanMod.TemperatureInputCount)"

for ($i = 0; $i -lt $fanMod.FanControlCount; $i++) {
    $title = ""
    $fanMod.GetFanControlTitle($i, [ref]$title)
    $mode = $null
    $fanMod.GetFanSpeedControlMode($i, [ref]$mode)
    $cfg = $null
    $fanMod.Get($i, [ref]$cfg)
    $lines += "  Ctrl[$i]: Title='$title' Mode=$mode CfgMode=$($cfg.Mode) StartPwm=$($cfg.StartPwmValue) Slope=$($cfg.DeltaPwm)"
}

$temps = $null
$rpms = $null
$fanMod.GetHardwareMonitorDatas([ref]$temps, [ref]$rpms)
$lines += "=== TEMPERATURES ==="
foreach ($t in $temps) { $lines += "  Temp: $($t.DisplayName) = $($t.Value)" }
$lines += "=== FAN SPEEDS (RPM) ==="
foreach ($r in $rpms) { $lines += "  Fan: $($r.DisplayName) = $($r.Value) RPM" }

$fanMod.Dispose()
$lines | Set-Content -Path 'd:\AI\full studio\aigo-fan-control\test_gbt_out.txt' -Encoding UTF8
