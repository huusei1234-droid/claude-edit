$ErrorActionPreference = 'Continue'
$dir = 'C:\Program Files (x86)\GIGABYTE\EasyTuneEngineService'
Set-Location $dir
$env:PATH = "$dir;$env:PATH"
$lines = @("PtrSize: $([IntPtr]::Size)")
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
    "$dir\Gigabyte.Engine.EnvironmentControl.dll",
    "$dir\Gigabyte.SIV.Profile.dll",
    "$dir\Gigabyte.SIV.UnifiedManagement.dll"
)) {
    if (Test-Path $dll) { [Reflection.Assembly]::LoadFrom($dll) | Out-Null }
}

foreach ($cls in @(
    'Gigabyte.EnvironmentControl.CoolingDevice.Fan.SmartGuardianFanControl',
    'Gigabyte.EnvironmentControl.CoolingDevice.Fan.SmartGuardianFanControlCoordinateSystem',
    'Gigabyte.Engine.EnvironmentControl.CoolingDevice.Fan.SmartGuardianFanControlModule',
    'Gigabyte.Engine.EnvironmentControl.CoolingDevice.Fan.SmartGuardianFanControlCoordinateSystemModule'
)) {
    try {
        $obj = New-Object $cls
        $lines += "$cls => IsSupported=$($obj.IsSupported)"
        $temps = $null; $rpms = $null
        $obj.GetHardwareMonitorDatas([ref]$temps, [ref]$rpms)
        $lines += "  Temps=$($temps.Count), Rpms=$($rpms.Count)"
        foreach ($t in $temps) { $lines += "    T: $($t.DisplayName) = $($t.Value)" }
        foreach ($r in $rpms) { $lines += "    F: $($r.DisplayName) = $($r.Value)" }
    } catch {
        $lines += "$cls ERROR: $($_.Exception.Message)"
    }
}
$lines | Set-Content -Path 'd:\AI\full studio\aigo-fan-control\test_x86_out.txt' -Encoding UTF8
