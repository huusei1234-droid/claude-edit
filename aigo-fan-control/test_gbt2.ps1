$ErrorActionPreference = 'Continue'
$lines = @("PtrSize: $([IntPtr]::Size)")
$mbDir = 'C:\Program Files\GIGABYTE\Control Center\Lib\MBEasyTune'
$commDir = 'C:\Program Files\GIGABYTE\Control Center\Lib\COMMDLL'
Set-Location $mbDir
foreach ($dll in @(
    "$commDir\Gigabyte.dll",
    "$commDir\Gigabyte.Win32.dll",
    "$mbDir\Gigabyte.Engine.dll",
    "$mbDir\Gigabyte.Engine.Remoting.dll",
    "$mbDir\Gigabyte.ComputerSystemHardware.dll",
    "$mbDir\Gigabyte.ComputerSystemHardware.PCI.dll",
    "$mbDir\Gigabyte.EnvironmentControl.Common.dll",
    "$mbDir\Gigabyte.EnvironmentControl.LowPinCount.dll",
    "$mbDir\Gigabyte.EnvironmentControl.dll",
    "$mbDir\Gigabyte.Engine.EnvironmentControl.dll"
)) {
    if (Test-Path $dll) { [Reflection.Assembly]::LoadFrom($dll) | Out-Null }
}

foreach ($cls in @(
    'Gigabyte.Engine.EnvironmentControl.CoolingDevice.Fan.SmartGuardianFanControlModule',
    'Gigabyte.Engine.EnvironmentControl.CoolingDevice.Fan.SmartGuardianFanControlModuleEx',
    'Gigabyte.Engine.EnvironmentControl.CoolingDevice.Fan.SmartGuardianFanControlCoordinateSystemModule',
    'Gigabyte.EnvironmentControl.CoolingDevice.Fan.SmartGuardianFanControlCoordinateSystem'
)) {
    try {
        $obj = New-Object $cls
        $lines += "$cls => IsSupported=$($obj.IsSupported)"
        $temps = $null; $rpms = $null
        $obj.GetHardwareMonitorDatas([ref]$temps, [ref]$rpms)
        $lines += "  Temps count=$($temps.Count), Rpms count=$($rpms.Count)"
        foreach ($t in $temps) { $lines += "    T: $($t.DisplayName) = $($t.Value)" }
        foreach ($r in $rpms) { $lines += "    F: $($r.DisplayName) = $($r.Value)" }
        $obj.Dispose()
    } catch {
        $lines += "$cls ERROR: $($_.Exception.Message)"
    }
}
$lines | Set-Content -Path 'd:\AI\full studio\aigo-fan-control\test_gbt2_out.txt' -Encoding UTF8
