param(
    [ValidateSet("Push", "Pull", "AutoSync", "InitHome", "InstallTask", "OptimizeOnly")]
    [string]$Mode = "AutoSync"
)

$ErrorActionPreference = "SilentlyContinue"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

# Khóa chống chạy chồng (Mutex) khi chạy định kỳ mỗi 3 phút
$createdNew = $false
$mutex = New-Object System.Threading.Mutex($true, "Local\AIFullStudioContinuousSync", [ref]$createdNew)
if (-not $createdNew -and $Mode -eq "AutoSync") {
    exit 0
}

function Find-AIDriveRoot {
    # Tự động dò mọi ký tự ổ đĩa & mọi ngôn ngữ Google Drive ("Drive của tôi", "My Drive"...)
    foreach ($letter in @("Z", "G", "H", "E", "F", "I", "J", "D", "C")) {
        $rootPath = "${letter}:\"
        if (-not (Test-Path -LiteralPath $rootPath)) { continue }
        foreach ($sub in @("Drive của tôi\AI_Full_Studio", "My Drive\AI_Full_Studio", "AI_Full_Studio")) {
            $cand = Join-Path $rootPath $sub
            if (Test-Path -LiteralPath $cand) { return $cand }
        }
        $wild = Get-ChildItem -Path "${rootPath}*" -Directory -ErrorAction SilentlyContinue | ForEach-Object {
            $p = Join-Path $_.FullName "AI_Full_Studio"
            if (Test-Path -LiteralPath $p) { $p }
        } | Select-Object -First 1
        if ($wild) { return $wild }
    }
    return $null
}

function Resolve-LocalStudioPath {
    if (Test-Path -LiteralPath "D:\") { return "D:\AI\full studio" }
    if (Test-Path -LiteralPath "E:\") { return "E:\AI\full studio" }
    return "C:\AI\full studio"
}

function Optimize-WorkstationForAIFilm {
    Write-Host "`n=== [TỐI ƯU HÓA PC LÀM PHIM AI, CAPCUT, PREMIERE & ULTRAVIEW] ===" -ForegroundColor Cyan

    # 1. Mở khóa Adobe CEP Extension (Premiere Pro & After Effects MCP Bridge) trong HKCU (không cần Admin)
    foreach ($ver in @("CSXS.9", "CSXS.10", "CSXS.11", "CSXS.12", "CSXS.13")) {
        $regPath = "HKCU:\Software\Adobe\$ver"
        New-Item -Path $regPath -Force | Out-Null
        Set-ItemProperty -Path $regPath -Name "PlayerDebugMode" -Value "1" -Type String -Force
    }
    Write-Host "  [OK] Đã bật PlayerDebugMode cho Adobe Premiere Pro & After Effects (CSXS 9-13)." -ForegroundColor Green

    # 2. Ép Windows ưu tiên card rời NVIDIA hiệu năng cao (GpuPreference=2) cho toàn bộ phần mềm dựng & AI
    $gpuReg = "HKCU:\Software\Microsoft\DirectX\UserGpuPreferences"
    New-Item -Path $gpuReg -Force | Out-Null
    $candidateApps = @(
        "$env:LOCALAPPDATA\CapCut\Apps\CapCut.exe",
        (Get-Command ffmpeg -ErrorAction SilentlyContinue).Source,
        (Get-Command python -ErrorAction SilentlyContinue).Source
    )
    $adobeExes = Get-ChildItem "C:\Program Files\Adobe" -Recurse -Depth 2 -Include "Adobe Premiere Pro.exe","AfterFX.exe","Photoshop.exe","Adobe Media Encoder.exe" -ErrorAction SilentlyContinue | Select-Object -ExpandProperty FullName
    foreach ($exe in ($candidateApps + $adobeExes)) {
        if ($exe -and (Test-Path -LiteralPath $exe)) {
            Set-ItemProperty -Path $gpuReg -Name $exe -Value "GpuPreference=2;" -Type String -Force
        }
    }
    Write-Host "  [OK] Đã gán GPU rời Hiệu Năng Cao (High Performance) cho FFmpeg, Python, CapCut & bộ Adobe." -ForegroundColor Green

    # 3. Tối ưu Lively Wallpaper tự tạm dừng 100% khi đang mở Fullscreen / Dựng phim / UltraView
    $livelyCfg = Join-Path $env:LOCALAPPDATA "Lively Wallpaper\Settings.json"
    if (Test-Path -LiteralPath $livelyCfg) {
        try {
            $j = Get-Content -LiteralPath $livelyCfg -Raw -Encoding UTF8 | ConvertFrom-Json
            $j.AppFocusPause = 1
            $j.AppFullscreenPause = 1
            $j | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath $livelyCfg -Encoding UTF8
            Write-Host "  [OK] Đã cấu hình nền động tự nhường 100% GPU khi mở phần mềm dựng phim / UltraView." -ForegroundColor Green
        } catch {}
    }

    # 4. Nâng cấp Hệ thống cần quyền Admin (Ultimate Performance Power Plan + HAGS GPU + LongPaths + Dev Symlinks)
    $adminCmd = @'
powercfg -duplicatescheme e9a42b02-d5df-448d-aa00-03f14749eb61 | Out-Null
$ult = (powercfg -list | Select-String -Pattern "([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}).*(Ultimate Performance|Hiệu suất tối ưu)" | Select-Object -First 1)
if ($ult) {
    $guid = $ult.Matches[0].Groups[1].Value
    powercfg -setactive $guid
} else {
    powercfg -setactive 8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c
}
powercfg -change -monitor-timeout-ac 30
powercfg -change -standby-timeout-ac 0
Set-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Control\FileSystem" -Name "LongPathsEnabled" -Value 1 -Type DWord -Force
New-Item -Path "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\AppModelUnlock" -Force | Out-Null
Set-ItemProperty -Path "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\AppModelUnlock" -Name "AllowDevelopmentWithoutDevLicense" -Value 1 -Type DWord -Force
Set-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Control\GraphicsDrivers" -Name "HwSchMode" -Value 2 -Type DWord -Force
'@
    try {
        Start-Process powershell.exe -Verb RunAs -ArgumentList "-NoProfile -WindowStyle Hidden -ExecutionPolicy Bypass -Command `"$adminCmd`"" -Wait
        Write-Host "  [OK] Đã kích hoạt gói nguồn Ultimate Performance (0 ngủ đông khi render), Hardware GPU Scheduling, LongPaths & HuggingFace Symlink!" -ForegroundColor Green
    } catch {
        Write-Host "  [BỎ QUA ADMIN] Bạn có thể bấm Yes ở hộp thoại UAC lần sau để bật thêm Ultimate Performance." -ForegroundColor Yellow
    }
}

function Install-MissingPrerequisites {
    Write-Host "`n=== [KIỂM TRA & CÀI ĐẶT PHẦN MỀM NỀN TỰ ĐỘNG QUA WINGET] ===" -ForegroundColor Cyan
    if (-not (Get-Command winget -ErrorAction SilentlyContinue)) {
        Write-Host "  [LƯU Ý] Máy chưa có winget, vui lòng cập nhật App Installer từ Microsoft Store." -ForegroundColor Yellow
        return
    }
    $packages = @(
        @{ cmd = "git";     id = "Git.Git";                name = "Git" },
        @{ cmd = "python";  id = "Python.Python.3.11";     name = "Python 3.11" },
        @{ cmd = "node";    id = "OpenJS.NodeJS.LTS";      name = "Node.js LTS" },
        @{ cmd = "ffmpeg";  id = "Gyan.FFmpeg";            name = "FFmpeg Full" },
        @{ cmd = "bun";     id = "Oven-sh.Bun";            name = "Bun Runtime" },
        @{ cmd = "uv";      id = "astral-sh.uv";           name = "uv Python Manager" }
    )
    foreach ($p in $packages) {
        if (-not (Get-Command $p.cmd -ErrorAction SilentlyContinue)) {
            Write-Host "  -> Đang cài tự động $($p.name) ($($p.id))..." -ForegroundColor Yellow
            winget install --id $p.id -e --accept-package-agreements --accept-source-agreements --silent
        } else {
            Write-Host "  [ĐÃ CÓ] $($p.name)" -ForegroundColor Green
        }
    }
    # Làm mới biến PATH ngay trong phiên hiện tại
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
}

function Install-StudioFonts($fontsDir) {
    if (-not (Test-Path -LiteralPath $fontsDir)) { return }
    $userFontDir = Join-Path $env:LOCALAPPDATA "Microsoft\Windows\Fonts"
    New-Item -ItemType Directory -Force -Path $userFontDir | Out-Null
    $regFonts = "HKCU:\Software\Microsoft\Windows NT\CurrentVersion\Fonts"
    New-Item -Path $regFonts -Force | Out-Null
    $count = 0
    Get-ChildItem -Path $fontsDir -Recurse -Include "*.ttf","*.otf" -ErrorAction SilentlyContinue | ForEach-Object {
        $dest = Join-Path $userFontDir $_.Name
        if (-not (Test-Path -LiteralPath $dest)) {
            Copy-Item -LiteralPath $_.FullName -Destination $dest -Force
            Set-ItemProperty -Path $regFonts -Name "$($_.BaseName) (TrueType)" -Value $dest -Type String -Force
            $count++
        }
    }
    if ($count -gt 0) {
        Write-Host "  [OK] Đã cài đặt tự động $count font chữ TVC Tiếng Việt vào Windows (CapCut/Premiere nhận diện ngay)!" -ForegroundColor Green
    } else {
        Write-Host "  [OK] Bộ 44 font chữ TVC Tiếng Việt đã đầy đủ trên máy." -ForegroundColor Green
    }
}

try {
    if ($Mode -eq "OptimizeOnly") {
        Install-MissingPrerequisites
        Optimize-WorkstationForAIFilm
        exit 0
    }

    $driveRoot = Find-AIDriveRoot
    if (-not $driveRoot) {
        if ($Mode -notin @("AutoSync")) {
            Write-Host "[CHỜ] Chưa tìm thấy thư mục AI_Full_Studio trên Google Drive. Đang cài phần mềm nền & tối ưu máy trước..." -ForegroundColor Yellow
            Install-MissingPrerequisites
            Optimize-WorkstationForAIFilm
        }
        exit 0
    }

    $syncDir       = Join-Path $driveRoot "00_DONG_BO_2_MAY"
    $cloudSkills   = Join-Path $driveRoot "01_Skills"
    $cloudKienThuc = Join-Path $driveRoot "02_Kien_Thuc_Va_Quy_Chuan"
    $cloudCore     = Join-Path $syncDir "full_studio_core"
    $cloudAgy      = Join-Path $syncDir "antigravity_global_config"

    $localStudio   = Resolve-LocalStudioPath
    $localAgy      = Join-Path $env:USERPROFILE ".gemini\config"
    $localSyncBin  = Join-Path $localStudio ".sync"

    New-Item -ItemType Directory -Force -Path $syncDir, $cloudCore, $cloudAgy, $localStudio, $localAgy, "$localAgy\plugins", "$localAgy\skills", $localSyncBin | Out-Null

    $excludeDirs = @(
        ".git", ".venv", "venv", "node_modules", "__pycache__", ".sync",
        "output", "exports", ".tiktok-brave-profile", ".cover_frames", ".cover_frames_new",
        "live-wallpapers", "BO_KIEN_THUC_TVC_AI_PORTABLE", "win-unpacked", "data"
    )
    $excludeFiles = @("*.pyc", "*.bak", "*.tmp", "api_key", "auth.json", "canvas-agent.json", ".env")

    function Install-ContinuousSyncTask {
        $localEngine = Join-Path $localSyncBin "sync_engine.ps1"
        $scriptSelf  = $PSCommandPath
        if ($scriptSelf -and ($scriptSelf -ne $localEngine) -and (Test-Path -LiteralPath $scriptSelf)) {
            Copy-Item -LiteralPath $scriptSelf -Destination $localEngine -Force
        }

        $vbsPath = Join-Path $localSyncBin "silent_autosync.vbs"
        $vbsContent = @"
Set sh = CreateObject("WScript.Shell")
sh.Run "powershell.exe -NoProfile -NonInteractive -WindowStyle Hidden -ExecutionPolicy Bypass -File ""$localEngine"" -Mode AutoSync", 0, False
"@
        Set-Content -LiteralPath $vbsPath -Value $vbsContent -Encoding ASCII

        $taskName = "AI_Full_Studio_Continuous_Sync"
        $trLogon  = New-ScheduledTaskTrigger -AtLogOn -User $env:USERNAME
        $trRepeat = New-ScheduledTaskTrigger -Once -At (Get-Date).Date -RepetitionInterval (New-TimeSpan -Minutes 3) -RepetitionDuration (New-TimeSpan -Days 3650)
        $action   = New-ScheduledTaskAction -Execute "wscript.exe" -Argument "//B //NoLogo `"$vbsPath`""
        $settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable -MultipleInstances IgnoreNew -ExecutionTimeLimit (New-TimeSpan -Minutes 10)

        Register-ScheduledTask -TaskName $taskName -Trigger @($trLogon, $trRepeat) -Action $action -Settings $settings -Description "Đồng bộ liên tục 2 chiều tự động Antigravity + Full Studio qua Google Drive (3 phút/lần, ẩn 100%)" -Force | Out-Null
        Write-Host "  [OK] Đã bật dịch vụ Đồng Bộ Liên Tục Ngầm ($taskName - tự chạy mỗi 3 phút & khi mở máy, ẩn 100%)!" -ForegroundColor Green
    }

    function Sync-McpConfigTwoWay {
        $mcpLocal = Join-Path $localAgy "mcp_config.json"
        $mcpTpl   = Join-Path $cloudAgy "mcp_config.template.json"
        $escapedAppData = ($env:APPDATA -replace "\\", "\\\\")

        $hasLocal = Test-Path -LiteralPath $mcpLocal
        $hasCloud = Test-Path -LiteralPath $mcpTpl

        if ($hasLocal -and -not $hasCloud) {
            $raw = Get-Content -LiteralPath $mcpLocal -Raw -Encoding UTF8
            $tpl = $raw.Replace($escapedAppData, "__APPDATA_ESCAPED__").Replace($env:APPDATA, "__APPDATA__")
            Set-Content -LiteralPath $mcpTpl -Value $tpl -Encoding UTF8
        } elseif ($hasCloud -and -not $hasLocal) {
            $tpl = Get-Content -LiteralPath $mcpTpl -Raw -Encoding UTF8
            $rendered = $tpl.Replace("__APPDATA_ESCAPED__", $escapedAppData).Replace("__APPDATA__", $env:APPDATA)
            Set-Content -LiteralPath $mcpLocal -Value $rendered -Encoding UTF8
        } elseif ($hasLocal -and $hasCloud) {
            $lItem = Get-Item -LiteralPath $mcpLocal
            $cItem = Get-Item -LiteralPath $mcpTpl
            if ($cItem.LastWriteTimeUtc -gt $lItem.LastWriteTimeUtc.AddSeconds(2)) {
                $tpl = Get-Content -LiteralPath $mcpTpl -Raw -Encoding UTF8
                $rendered = $tpl.Replace("__APPDATA_ESCAPED__", $escapedAppData).Replace("__APPDATA__", $env:APPDATA)
                $cur = Get-Content -LiteralPath $mcpLocal -Raw -Encoding UTF8
                if ($rendered -ne $cur) {
                    Set-Content -LiteralPath $mcpLocal -Value $rendered -Encoding UTF8
                }
            } elseif ($lItem.LastWriteTimeUtc -gt $cItem.LastWriteTimeUtc.AddSeconds(2)) {
                $raw = Get-Content -LiteralPath $mcpLocal -Raw -Encoding UTF8
                $newTpl = $raw.Replace($escapedAppData, "__APPDATA_ESCAPED__").Replace($env:APPDATA, "__APPDATA__")
                $oldTpl = Get-Content -LiteralPath $mcpTpl -Raw -Encoding UTF8
                if ($newTpl -ne $oldTpl) {
                    Set-Content -LiteralPath $mcpTpl -Value $newTpl -Encoding UTF8
                }
            }
        }
    }

    function Invoke-PullNewer {
        robocopy "$cloudCore" "$localStudio" /E /XO /XD $excludeDirs /XF $excludeFiles /NFL /NDL /NJH /NJS /R:1 /W:1 | Out-Null
        robocopy "$cloudSkills" "$localStudio\.agents\skills" /E /XO /NFL /NDL /NJH /NJS /R:1 /W:1 | Out-Null
        robocopy "$cloudSkills" "$localAgy\skills" /E /XO /NFL /NDL /NJH /NJS /R:1 /W:1 | Out-Null
        if (Test-Path -LiteralPath "$cloudAgy\plugins") {
            robocopy "$cloudAgy\plugins" "$localAgy\plugins" /E /XO /XF "auth.json" "*.token" /NFL /NDL /NJH /NJS /R:1 /W:1 | Out-Null
        }
        foreach ($fn in @("GEMINI.md", "skills.json")) {
            $cFile = Join-Path $cloudAgy $fn
            $lFile = Join-Path $localAgy $fn
            if (Test-Path -LiteralPath $cFile) {
                if (-not (Test-Path -LiteralPath $lFile) -or ((Get-Item -LiteralPath $cFile).LastWriteTimeUtc -gt (Get-Item -LiteralPath $lFile).LastWriteTimeUtc.AddSeconds(2))) {
                    Copy-Item -LiteralPath $cFile -Destination $lFile -Force
                }
            }
        }
    }

    function Invoke-PushNewer {
        if (Test-Path -LiteralPath "$localStudio\.agents\skills") {
            robocopy "$localStudio\.agents\skills" "$cloudSkills" /E /XO /NFL /NDL /NJH /NJS /R:1 /W:1 | Out-Null
        }
        if (Test-Path -LiteralPath "$localAgy\skills") {
            robocopy "$localAgy\skills" "$cloudSkills" /E /XO /NFL /NDL /NJH /NJS /R:1 /W:1 | Out-Null
        }
        if (Test-Path -LiteralPath "$localAgy\plugins") {
            robocopy "$localAgy\plugins" "$cloudAgy\plugins" /E /XO /XF "auth.json" "*.token" /NFL /NDL /NJH /NJS /R:1 /W:1 | Out-Null
        }
        foreach ($fn in @("GEMINI.md", "skills.json")) {
            $lFile = Join-Path $localAgy $fn
            $cFile = Join-Path $cloudAgy $fn
            if (Test-Path -LiteralPath $lFile) {
                if (-not (Test-Path -LiteralPath $cFile) -or ((Get-Item -LiteralPath $lFile).LastWriteTimeUtc -gt (Get-Item -LiteralPath $cFile).LastWriteTimeUtc.AddSeconds(2))) {
                    Copy-Item -LiteralPath $lFile -Destination $cFile -Force
                }
            }
        }
        robocopy "$localStudio" "$cloudCore" /E /XO /XD $excludeDirs /XF $excludeFiles /XD "$localStudio\projects" /NFL /NDL /NJH /NJS /R:1 /W:1 | Out-Null
    }

    if ($Mode -eq "InstallTask") {
        Install-ContinuousSyncTask
        exit 0
    }

    if ($Mode -eq "AutoSync") {
        Invoke-PullNewer
        Invoke-PushNewer
        Sync-McpConfigTwoWay

        $cloudEngine = Join-Path $syncDir "sync_engine.ps1"
        $localEngine = Join-Path $localSyncBin "sync_engine.ps1"
        if ((Test-Path -LiteralPath $cloudEngine) -and ($PSCommandPath -ne $cloudEngine)) {
            if (-not (Test-Path -LiteralPath $localEngine) -or ((Get-Item -LiteralPath $cloudEngine).LastWriteTimeUtc -gt (Get-Item -LiteralPath $localEngine).LastWriteTimeUtc.AddSeconds(2))) {
                Copy-Item -LiteralPath $cloudEngine -Destination $localEngine -Force
            }
        }

        $stampDir = Join-Path $syncDir "machines"
        New-Item -ItemType Directory -Force -Path $stampDir | Out-Null

        # Nếu đây là PC ở nhà (khác HUUSEIZ) và chưa chạy gói tối ưu v2 -> tự động nạp Font TVC, CEP, GPU High-Performance & MCP 1 lần!
        $optFlag = Join-Path $localSyncBin "home_optimized_v2.flag"
        if (($env:COMPUTERNAME -ne "HUUSEIZ") -and (-not (Test-Path -LiteralPath $optFlag))) {
            foreach ($ver in @("CSXS.9", "CSXS.10", "CSXS.11", "CSXS.12", "CSXS.13")) {
                New-Item -Path "HKCU:\Software\Adobe\$ver" -Force | Out-Null
                Set-ItemProperty -Path "HKCU:\Software\Adobe\$ver" -Name "PlayerDebugMode" -Value "1" -Type String -Force
            }
            $gpuReg = "HKCU:\Software\Microsoft\DirectX\UserGpuPreferences"
            New-Item -Path $gpuReg -Force | Out-Null
            $apps = @("$env:LOCALAPPDATA\CapCut\Apps\CapCut.exe", (Get-Command ffmpeg -ErrorAction SilentlyContinue).Source, (Get-Command python -ErrorAction SilentlyContinue).Source) +
                    (Get-ChildItem "C:\Program Files\Adobe" -Recurse -Depth 2 -Include "Adobe Premiere Pro.exe","AfterFX.exe","Photoshop.exe" -ErrorAction SilentlyContinue | Select-Object -ExpandProperty FullName)
            foreach ($exe in $apps) {
                if ($exe -and (Test-Path -LiteralPath $exe)) {
                    Set-ItemProperty -Path $gpuReg -Name $exe -Value "GpuPreference=2;" -Type String -Force
                }
            }
            Install-StudioFonts (Join-Path $cloudKienThuc "BO_KIEN_THUC_TVC_AI_PORTABLE\03_TAI_NGUYEN_DUNG_CHUNG\fonts_tvc_vi")
            if (Get-Command npm -ErrorAction SilentlyContinue) {
                npm install -g premiere-pro-mcp @immersive-media-technologies/photoshop-mcp-imt | Out-Null
                $cepScript = Join-Path $env:APPDATA "npm\node_modules\premiere-pro-mcp\scripts\install-cep.ps1"
                if (Test-Path -LiteralPath $cepScript) {
                    powershell -ExecutionPolicy Bypass -File $cepScript -ConnectorHost Premiere | Out-Null
                    powershell -ExecutionPolicy Bypass -File $cepScript -ConnectorHost AfterEffects | Out-Null
                }
            }
            Set-Content -LiteralPath $optFlag -Value (Get-Date).ToString("o") -Encoding UTF8
        }

        $stamp = @{
            lastAutoSyncAt = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss")
            computer       = $env:COMPUTERNAME
            user           = $env:USERNAME
            optimizedV2    = (Test-Path -LiteralPath $optFlag)
        } | ConvertTo-Json
        Set-Content -LiteralPath (Join-Path $localSyncBin "last_autosync.json") -Value $stamp -Encoding UTF8
        Set-Content -LiteralPath (Join-Path $stampDir "$env:COMPUTERNAME.json") -Value $stamp -Encoding UTF8
        exit 0
    }

    if ($Mode -eq "Push") {
        Write-Host "Đang đẩy cập nhật mới nhất từ '$env:COMPUTERNAME' lên Google Drive ($driveRoot)..." -ForegroundColor Cyan
        Invoke-PushNewer
        Sync-McpConfigTwoWay
        Install-ContinuousSyncTask
        Write-Host "HOÀN TẤT ĐẨY DỮ LIỆU LÊN DRIVE!" -ForegroundColor Green
    }

    if ($Mode -eq "Pull" -or $Mode -eq "InitHome") {
        if ($Mode -eq "InitHome") {
            Install-MissingPrerequisites
            Optimize-WorkstationForAIFilm
        }

        Write-Host "`n=== [ĐỒNG BỘ MÃ NGUỒN FULL STUDIO + 27 SKILLS + CẤU HÌNH ANTIGRAVITY] ===" -ForegroundColor Cyan
        Write-Host "  -> Thư mục đích trên máy này: $localStudio" -ForegroundColor Gray
        Invoke-PullNewer
        Sync-McpConfigTwoWay

        $portableCloud = Join-Path $cloudKienThuc "BO_KIEN_THUC_TVC_AI_PORTABLE"
        $portableLocal = Join-Path $localStudio "BO_KIEN_THUC_TVC_AI_PORTABLE"
        if ((Test-Path -LiteralPath $portableCloud) -and -not (Test-Path -LiteralPath $portableLocal)) {
            Write-Host "  -> Đang chép BO_KIEN_THUC_TVC_AI_PORTABLE về ổ cứng cục bộ lần đầu..." -ForegroundColor Yellow
            robocopy "$portableCloud" "$portableLocal" /E /XO /NFL /NDL /NJH /NJS /R:1 /W:1 | Out-Null
        }

        if ($Mode -eq "InitHome") {
            # Cài bộ 44 Font TVC Tiếng Việt
            Install-StudioFonts (Join-Path $portableLocal "03_TAI_NGUYEN_DUNG_CHUNG\fonts_tvc_vi")

            # Tạo Junction tương thích đường dẫn Infinite Canvas
            $parentDrive = Split-Path $localStudio -Qualifier
            $compatDir = "$parentDrive\antigravyti"
            New-Item -ItemType Directory -Force -Path $compatDir | Out-Null
            if (-not (Test-Path -LiteralPath "$compatDir\infinite-canvas")) {
                cmd /c mklink /J "$compatDir\infinite-canvas" "$localStudio\canvas" | Out-Null
            }

            Write-Host "`n=== [CÀI ĐẶT MCP PREMIERE / PHOTOSHOP & THƯ VIỆN NODE / PYTHON] ===" -ForegroundColor Magenta
            if (Get-Command npm -ErrorAction SilentlyContinue) {
                npm install -g premiere-pro-mcp @immersive-media-technologies/photoshop-mcp-imt
                $cepScript = Join-Path $env:APPDATA "npm\node_modules\premiere-pro-mcp\scripts\install-cep.ps1"
                if (Test-Path -LiteralPath $cepScript) {
                    powershell -ExecutionPolicy Bypass -File $cepScript -ConnectorHost Premiere
                    powershell -ExecutionPolicy Bypass -File $cepScript -ConnectorHost AfterEffects
                }
                if (Test-Path -LiteralPath "$localStudio\canvas\app\web\package.json") {
                    npm --prefix "$localStudio\canvas\app\web" install --legacy-peer-deps
                }
                foreach ($sub in @("desktop", "app\canvas-agent", "app\canvas-proxy")) {
                    if (Test-Path -LiteralPath "$localStudio\canvas\$sub\package.json") {
                        npm --prefix "$localStudio\canvas\$sub" install
                    }
                }
            }

            if (Get-Command python -ErrorAction SilentlyContinue) {
                Write-Host "  -> Đang cài thư viện Python cho hệ thống dựng phim (vf + AI tools)..." -ForegroundColor Yellow
                python -m pip install --upgrade pip -q
                if (Test-Path -LiteralPath "$localStudio\edit\requirements.txt") {
                    python -m pip install -r "$localStudio\edit\requirements.txt" pillow -q
                }
                # Tạo môi trường GPU CUDA riêng (.venv) nếu phát hiện card rời NVIDIA
                $hasNvidia = $null -ne (Get-Command nvidia-smi -ErrorAction SilentlyContinue)
                $venvDir = Join-Path $localStudio ".venv"
                if (-not (Test-Path -LiteralPath "$venvDir\Scripts\python.exe")) {
                    python -m venv $venvDir
                }
                $vpy = "$venvDir\Scripts\python.exe"
                if (Test-Path -LiteralPath $vpy) {
                    & $vpy -m pip install --upgrade pip -q
                    if ($hasNvidia) {
                        Write-Host "  -> Phát hiện GPU NVIDIA! Đang cài PyTorch CUDA 12.4 + Spandrel + OpenCV + Whisper..." -ForegroundColor Green
                        & $vpy -m pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124 -q
                    }
                    & $vpy -m pip install numpy opencv-python pillow requests fastapi uvicorn spandrel transformers timm scipy -q
                }
            }
        }

        Install-ContinuousSyncTask
        Write-Host "`n==================================================================" -ForegroundColor Green
        Write-Host " HOÀN TẤT 100%! PC '$env:COMPUTERNAME' ĐÃ ĐƯỢC TỐI ƯU & ĐỒNG BỘ FULL STUDIO!" -ForegroundColor Green
        Write-Host " - Thư mục làm việc tốc độ cao: $localStudio" -ForegroundColor White
        Write-Host " - Đồng bộ 2 chiều ngầm tự động mỗi 3 phút qua Google Drive" -ForegroundColor White
        Write-Host "==================================================================" -ForegroundColor Green
    }
} finally {
    try { $mutex.ReleaseMutex() } catch {}
    $mutex.Dispose()
}
