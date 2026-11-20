# Cài đặt nhanh toàn bộ Font TVC Tiếng Việt vào Windows (CapCut / Premiere / Photoshop) trên máy mới (Không cần quyền Admin)
$FontDir = $PSScriptRoot
$DestDir = Join-Path $env:LOCALAPPDATA "Microsoft\Windows\Fonts"
New-Item -ItemType Directory -Force -Path $DestDir | Out-Null
$RegPath = "HKCU:\Software\Microsoft\Windows NT\CurrentVersion\Fonts"
Get-ChildItem -Path $FontDir -Filter "*.ttf" | ForEach-Object {
    $dst = Join-Path $DestDir $_.Name
    Copy-Item -LiteralPath $_.FullName -Destination $dst -Force
    New-ItemProperty -Path $RegPath -Name "$($_.BaseName) (TrueType)" -Value $dst -PropertyType String -Force | Out-Null
    Write-Host "Đã cài font: $($_.Name)" -ForegroundColor Green
}
Write-Host "HOÀN TẤT! Mở lại CapCut / Phần mềm thiết kế để nhận diện đủ bộ Font TVC!" -ForegroundColor Cyan
