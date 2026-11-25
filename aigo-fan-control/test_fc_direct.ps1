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
$fcType = [Gigabyte.EnvironmentControl.CoolingDevice.Fan.FanControl]
foreach ($m in $fcType.GetMethods([Reflection.BindingFlags]"Public,Instance,DeclaredOnly")) {
    $ps = ($m.GetParameters() | ForEach-Object { "$($_.ParameterType.Name) $($_.Name)" }) -join ', '
    $lines += "SIG: $($m.ReturnType.Name) $($m.Name)($ps)"
}

$fc = New-Object Gigabyte.EnvironmentControl.CoolingDevice.Fan.FanControl
$lines += "ProductName: $($fc.ProductName), IsSupported=$($fc.IsSupported), FanCtrlCount=$($fc.FanControlCount), FanCount=$($fc.FanCount), TempCount=$($fc.TemperatureCount), MaxPwm=$($fc.MaxPwmValue)"

$cpuRpm = 0.0
$fc.GetCpuFanSpeed([ref]$cpuRpm)
$lines += "CPU Fan Speed: $cpuRpm RPM"

for ($i = 0; $i -lt $fc.FanCount; $i++) {
    $name = ""
    $fc.GetFanDisplayName($i, [ref]$name)
    $spd = 0.0
    $fc.GetFanSpeed($i, [ref]$spd)
    $lines += "  Fan[$i] '$name' = $spd RPM"
}

for ($i = 0; $i -lt $fc.TemperatureCount; $i++) {
    $tname = ""
    $fc.GetTemperatureDisplayName($i, [ref]$tname)
    $tval = 0.0
    $fc.GetTemperature($i, [ref]$tval)
    $lines += "  Temp[$i] '$tname' = $tval C"
}

# Test EnableCalibrateStatus + SetFanSpeedFixedMode(idx, 230) (~90%) and check RPM after 3s!
$fc.EnableCalibrateStatus($true)
for ($i = 0; $i -lt $fc.FanControlCount; $i++) {
    $fc.SetCalibrationPwm($i, 95)
}
Start-Sleep -Seconds 3
for ($i = 0; $i -lt $fc.FanCount; $i++) {
    $spd2 = 0.0
    $fc.GetFanSpeed($i, [ref]$spd2)
    $lines += "  AFTER 95% -> Fan[$i] = $spd2 RPM"
}

$lines | Set-Content -Path 'd:\AI\full studio\aigo-fan-control\test_fc_direct_out.txt' -Encoding UTF8
