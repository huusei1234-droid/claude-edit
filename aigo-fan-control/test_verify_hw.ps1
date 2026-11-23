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
# 1. Check FanControl class methods & RPM
$fcType = [Gigabyte.EnvironmentControl.CoolingDevice.Fan.FanControl]
foreach ($m in $fcType.GetMethods([Reflection.BindingFlags]"Public,Instance,Static,DeclaredOnly")) {
    $lines += "FanControl Method: $($m.Name)"
}
try {
    $fc = New-Object Gigabyte.EnvironmentControl.CoolingDevice.Fan.FanControl
    $lines += "FanControl Count: $($fc.Count)"
    for ($i = 0; $i -lt $fc.Count; $i++) {
        $rpm = 0.0
        $fc.GetSpeed($i, [ref]$rpm)
        $lines += "  FanControl[$i] Speed = $rpm RPM"
    }
} catch { $lines += "FanControl err: $($_.Exception.Message)" }

# 2. Write a Turbo/FullSpeed curve (85% -> 100%) to FanCtrl[0..3] and verify readback!
$mod = New-Object Gigabyte.EnvironmentControl.CoolingDevice.Fan.SmartGuardianFanControlCoordinateSystem
$mod.ResetCalibrationPwm()
for ($idx = 0; $idx -lt 4; $idx++) {
    $cfg = New-Object Gigabyte.EnvironmentControl.Common.CoolingDevice.Fan.CoordinateSystem.SmartFanDataPointSet
    $mod.Get($idx, [ref]$cfg)
    # Set strong cooling curve: 0-30C -> 75% (191), 40C -> 85% (217), 50C -> 95% (242), >=55C -> 100% (255)
    $targets = @(191, 191, 204, 217, 242, 255, 255, 255)
    for ($p = 0; $p -lt $cfg.DataPoints.Count -and $p -lt $targets.Count; $p++) {
        $cfg.DataPoints[$p].Y = [byte]$targets[$p]
    }
    $mod.Set($idx, $cfg)
}

# Read back from hardware in a brand new instance!
$mod2 = New-Object Gigabyte.EnvironmentControl.CoolingDevice.Fan.SmartGuardianFanControlCoordinateSystem
for ($idx = 0; $idx -lt 4; $idx++) {
    $vcfg = New-Object Gigabyte.EnvironmentControl.Common.CoolingDevice.Fan.CoordinateSystem.SmartFanDataPointSet
    $mod2.Get($idx, [ref]$vcfg)
    $pts = ($vcfg.DataPoints | ForEach-Object { "($($_.X)C->$([math]::Round($_.Y/2.55))%)" }) -join ', '
    $lines += "VERIFIED HW[$idx]: $pts"
}

$lines | Set-Content -Path 'd:\AI\full studio\aigo-fan-control\test_verify_hw_out.txt' -Encoding UTF8
