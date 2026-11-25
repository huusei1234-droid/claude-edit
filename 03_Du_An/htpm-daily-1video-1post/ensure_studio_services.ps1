# Tự động kiểm tra và bật bền vững các dịch vụ Full Studio cho HTPM Daily (0% taskkill!)
# Dùng Win32_Process.Create qua WMI để tiến trình sống độc lập bền vững sau khi shell kết thúc!
$ErrorActionPreference = "SilentlyContinue"

function Test-LocalPort([int]$Port) {
    try {
        $c = New-Object System.Net.Sockets.TcpClient
        $ar = $c.BeginConnect("127.0.0.1", $Port, $null, $null)
        $ok = $ar.AsyncWaitHandle.WaitOne(800, $false)
        if ($ok) { $c.EndConnect($ar); $c.Close(); return $true }
        $c.Close(); return $false
    } catch { return $false }
}

Write-Output "=== [1/3] KIỂM TRA INFINITE CANVAS (:17371 & :3100) ==="
if (-not (Test-LocalPort 17371)) {
    Write-Output "Canvas Agent :17371 chưa bật -> khởi động bền vững full studido.exe qua Win32_Process..."
    $studioCmd = '"d:\AI\full studio\full studido.exe"'
    Invoke-CimMethod -ClassName Win32_Process -MethodName Create -Arguments @{
        CommandLine = $studioCmd
        CurrentDirectory = "d:\AI\full studio"
    } | Out-Null
    for ($i = 0; $i -lt 35; $i++) {
        Start-Sleep -Seconds 2
        if ((Test-LocalPort 17371) -and (Test-LocalPort 3100)) { break }
    }
}
Write-Output ("Canvas Agent :17371 = " + (Test-LocalPort 17371) + " | Web :3100 = " + (Test-LocalPort 3100))

Write-Output "=== [2/3] KIỂM TRA BRAVE CDP (:9333 — ChatGPT HTPM + Google Flow Ultra) ==="
if (-not (Test-LocalPort 9333)) {
    $braveExe = "C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"
    if (Test-Path $braveExe) {
        Write-Output "Brave :9333 chưa bật -> khởi động bền vững Brave debug :9333 qua Win32_Process..."
        $braveCmd = '"' + $braveExe + '" --remote-debugging-port=9333 --remote-debugging-address=127.0.0.1 --restore-last-session --disable-background-timer-throttling --disable-renderer-backgrounding --disable-backgrounding-occluded-windows --disable-features=CalculateNativeWinOcclusion "https://chatgpt.com/g/g-p-6afbde0b943481919c6ec31a3b4f8642/project" "https://flow.google.com/"'
        Invoke-CimMethod -ClassName Win32_Process -MethodName Create -Arguments @{
            CommandLine = $braveCmd
            CurrentDirectory = "d:\AI\full studio"
        } | Out-Null
        for ($i = 0; $i -lt 20; $i++) {
            Start-Sleep -Seconds 2
            if (Test-LocalPort 9333) { break }
        }
    }
}
Write-Output ("Brave CDP :9333 = " + (Test-LocalPort 9333))

Write-Output "=== [3/3] KIỂM TRA GPU NVIDIA & PYTHON VOICESTUDIO ==="
nvidia-smi --query-gpu=name,memory.total,temperature.gpu --format=csv,noheader
$py = "D:\AI\full studio\voice-studio\.venv\Scripts\python.exe"
if (Test-Path $py) {
    Write-Output "VoiceStudio Python Venv OK"
} else {
    Write-Error "Thiếu Python VoiceStudio tại $py"
    exit 1
}
Write-Output "=== HTPM STUDIO SERVICES READY ==="
