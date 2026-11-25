$ErrorActionPreference = 'Continue'
[Reflection.Assembly]::LoadFrom('d:\AI\full studio\aigo-fan-control\lib\lhm\LibreHardwareMonitorLib.dll') | Out-Null
$c = New-Object LibreHardwareMonitor.Hardware.Computer
$c.IsMotherboardEnabled = $true
$c.IsCpuEnabled = $true
$c.IsControllerEnabled = $true
$c.Open()
$lines = @()
foreach ($hw in $c.Hardware) {
    $hw.Update()
    $lines += "HW: $($hw.HardwareType) - $($hw.Name)"
    foreach ($s in $hw.Sensors) {
        $lines += "  SENSOR: [$($s.SensorType)] $($s.Name) = $($s.Value) (HasCtrl=$($null -ne $s.Control))"
    }
    foreach ($sub in $hw.SubHardware) {
        $sub.Update()
        $lines += "  SUBHW: $($sub.HardwareType) - $($sub.Name)"
        foreach ($s in $sub.Sensors) {
            $lines += "    SENSOR: [$($s.SensorType)] $($s.Name) = $($s.Value) (HasCtrl=$($null -ne $s.Control))"
        }
    }
}
$c.Close()
$lines | Set-Content -Path 'd:\AI\full studio\aigo-fan-control\test_lhm_out.txt' -Encoding UTF8
