$ErrorActionPreference = 'Stop'
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
try {
    $mod = New-Object Gigabyte.EnvironmentControl.CoolingDevice.Fan.SmartGuardianFanControlCoordinateSystem
    $cfg = New-Object Gigabyte.EnvironmentControl.Common.CoolingDevice.Fan.CoordinateSystem.SmartFanDataPointSet
    $mod.Get(0, [ref]$cfg)

    $lines += "SmartFanDataPointSet props:"
    foreach ($p in $cfg.GetType().GetProperties()) {
        $lines += "  $($p.PropertyType.FullName) $($p.Name) = $($p.GetValue($cfg, $null))"
    }
    $pt0 = $cfg.DataPoints[0]
    $lines += "DataPoint props:"
    foreach ($p in $pt0.GetType().GetProperties()) {
        $lines += "  $($p.PropertyType.FullName) $($p.Name) = $($p.GetValue($pt0, $null))"
    }

    # Modify curve to Turbo/High Speed (80% base -> 100% from 50C) on all 4 headers!
    for ($idx = 0; $idx -lt 4; $idx++) {
        $c = New-Object Gigabyte.EnvironmentControl.Common.CoolingDevice.Fan.CoordinateSystem.SmartFanDataPointSet
        $mod.Get($idx, [ref]$c)
        $ys = @(204, 204, 217, 230, 245, 255, 255, 255)
        for ($k = 0; $k -lt $c.DataPoints.Count; $k++) {
            $dp = $c.DataPoints[$k]
            $dp.Y = $ys[$k]
            $c.DataPoints[$k] = $dp
        }
        $mod.Set($idx, $c)
    }

    # Fresh readback!
    $modCheck = New-Object Gigabyte.EnvironmentControl.CoolingDevice.Fan.SmartGuardianFanControlCoordinateSystem
    for ($idx = 0; $idx -lt 4; $idx++) {
        $vc = New-Object Gigabyte.EnvironmentControl.Common.CoolingDevice.Fan.CoordinateSystem.SmartFanDataPointSet
        $modCheck.Get($idx, [ref]$vc)
        $pts = ($vc.DataPoints | ForEach-Object { "($($_.X)C->$([math]::Round($_.Y/2.55))%)" }) -join ', '
        $lines += "READBACK[$idx]: Mode=$($vc.Mode) Speed=$($vc.FanSpeed) Points: $pts"
    }

    $temps = New-Object 'System.Collections.Generic.List[Single]'
    $rpms = New-Object 'System.Collections.Generic.List[Single]'
    $modCheck.GetHardwareMonitorDatas([ref]$temps, [ref]$rpms)
    $lines += "RPMS AFTER SET: " + ($rpms -join ', ')
    $lines += "TEMPS AFTER SET: " + ($temps -join ', ')
} catch {
    $lines += "ERROR: $($_.Exception.ToString())"
}
$lines | Set-Content -Path 'd:\AI\full studio\aigo-fan-control\test_wmi_set_out.txt' -Encoding UTF8
