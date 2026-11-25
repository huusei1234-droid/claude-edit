$ErrorActionPreference = 'Continue'
$dir = 'C:\Program Files (x86)\GIGABYTE\EasyTuneEngineService'
Set-Location $dir
$env:PATH = "$dir;$env:PATH"
foreach ($dll in @(
    "$dir\Gigabyte.dll",
    "$dir\Gigabyte.Win32.dll",
    "$dir\Gigabyte.Engine.dll",
    "$dir\Gigabyte.Engine.Remoting.dll",
    "$dir\Gigabyte.ComputerSystemHardware.dll",
    "$dir\Gigabyte.ComputerSystemHardware.PCI.dll",
    "$dir\Gigabyte.EnvironmentControl.Common.dll",
    "$dir\Gigabyte.EnvironmentControl.LowPinCount.dll",
    "$dir\Gigabyte.EnvironmentControl.dll",
    "$dir\Gigabyte.Engine.EnvironmentControl.dll"
)) {
    [Reflection.Assembly]::LoadFrom($dll) | Out-Null
}

$lines = @()
$mod = New-Object Gigabyte.EnvironmentControl.CoolingDevice.Fan.SmartGuardianFanControlCoordinateSystem
$t = $mod.GetType()
foreach ($m in $t.GetMethods([Reflection.BindingFlags]"Public,Instance,DeclaredOnly")) {
    $ps = ($m.GetParameters() | ForEach-Object { "$($_.ParameterType.FullName) $($_.Name)" }) -join ', '
    $lines += "METHOD: $($m.ReturnType.Name) $($m.Name)($ps)"
}

$hw = $mod.HardwareInfo
$lines += "HW Info: FanCtrlCount=$($hw.FanControlCount), TachCount=$($hw.FanTachometerCount), TempCount=$($hw.TemperatureCount)"
foreach ($p in $hw.GetType().GetProperties()) {
    $lines += "  HWProp $($p.Name) = $($p.GetValue($hw, $null))"
}

$temps = New-Object 'System.Collections.Generic.List[Gigabyte.EnvironmentControl.Common.HardwareMonitor.HardwareMonitoredData]'
$rpms = New-Object 'System.Collections.Generic.List[Gigabyte.EnvironmentControl.Common.HardwareMonitor.HardwareMonitoredData]'
$mod.GetHardwareMonitorDatas([ref]$temps, [ref]$rpms)
$lines += "=== LIVE TEMPS ($($temps.Count)) ==="
foreach ($item in $temps) {
    $props = ($item.GetType().GetProperties() | ForEach-Object { "$($_.Name)=$($_.GetValue($item, $null))" }) -join '; '
    $lines += "  TEMP: $props"
}
$lines += "=== LIVE RPMS ($($rpms.Count)) ==="
foreach ($item in $rpms) {
    $props = ($item.GetType().GetProperties() | ForEach-Object { "$($_.Name)=$($_.GetValue($item, $null))" }) -join '; '
    $lines += "  RPM: $props"
}

for ($i = 0; $i -lt 4; $i++) {
    $title = ""
    $mod.GetSensorTitle([Gigabyte.EnvironmentControl.Common.HardwareMonitor.SensorTypes]::Fan, $i, [ref]$title)
    $cfg = $null
    $mod.Get($i, [ref]$cfg)
    $pts = ($cfg.DataPoints | ForEach-Object { "($($_.X)C -> $($_.Y)/255)" }) -join ', '
    $lines += "FAN[$i] Title='$title' Mode=$($cfg.Mode) Speed=$($cfg.FanSpeed) Points: $pts"
}

$lines | Set-Content -Path 'd:\AI\full studio\aigo-fan-control\test_coord_out.txt' -Encoding UTF8
