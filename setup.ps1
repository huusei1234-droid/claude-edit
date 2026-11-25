# ==============================================================================
# FULL STUDIO x ANTIGRAVITY - 1-COMMAND GITHUB INSTALLER & PC OPTIMIZER
# Usage on any PC (PowerShell):
#   irm https://raw.githubusercontent.com/huusei1234-droid/claude-edit/main/setup.ps1 | iex
# ==============================================================================

$ErrorActionPreference = "SilentlyContinue"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host "  FULL STUDIO AI - TU DONG CAI DAT & TOI UU PC TU GITHUB (1 CHAM)     " -ForegroundColor Cyan
Write-Host "======================================================================" -ForegroundColor Cyan

# 1. CAI DAT PHAN MEM NEN QUA WINGET
Write-Host "`n[1/7] Kiem tra & cai dat Git, Python 3.11, Node LTS, FFmpeg, Bun, uv, Brave, CapCut, Google Drive..." -ForegroundColor Cyan
if (Get-Command winget -ErrorAction SilentlyContinue) {
    $corePkgs = @(
        @{ cmd = "git";    id = "Git.Git";            name = "Git" },
        @{ cmd = "python"; id = "Python.Python.3.11"; name = "Python 3.11" },
        @{ cmd = "node";   id = "OpenJS.NodeJS.LTS";  name = "Node.js LTS" },
        @{ cmd = "ffmpeg"; id = "Gyan.FFmpeg";        name = "FFmpeg Full" },
        @{ cmd = "bun";    id = "Oven-sh.Bun";        name = "Bun" },
        @{ cmd = "uv";     id = "astral-sh.uv";       name = "uv" }
    )
    foreach ($p in $corePkgs) {
        if (-not (Get-Command $p.cmd -ErrorAction SilentlyContinue)) {
            Write-Host "  -> Installing $($p.name) ($($p.id))..." -ForegroundColor Yellow
            winget install --id $p.id -e --accept-package-agreements --accept-source-agreements --silent
        } else {
            Write-Host "  [OK] $($p.name)" -ForegroundColor Green
        }
    }
    if (-not (Test-Path "C:\Program Files\Google\Drive File Stream") -and -not (Test-Path "$env:LOCALAPPDATA\Google\DriveFS")) {
        Write-Host "  -> Installing Google Drive for Desktop..." -ForegroundColor Yellow
        winget install --id Google.GoogleDrive -e --accept-package-agreements --accept-source-agreements --silent
    }
    if (-not (Test-Path "$env:LOCALAPPDATA\CapCut\Apps\CapCut.exe")) {
        Write-Host "  -> Installing CapCut PC..." -ForegroundColor Yellow
        winget install --id ByteDance.CapCut -e --accept-package-agreements --accept-source-agreements --silent
    }
    if (-not (Test-Path "C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe") -and -not (Test-Path "$env:LOCALAPPDATA\BraveSoftware\Brave-Browser\Application\brave.exe")) {
        Write-Host "  -> Installing Brave Browser..." -ForegroundColor Yellow
        winget install --id Brave.Brave -e --accept-package-agreements --accept-source-agreements --silent
    }
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
}

# 2. TOI UU WINDOWS, NGUON ULTIMATE PERFORMANCE, GPU NVIDIA & ADOBE CEP
Write-Host "`n[2/7] Toi uu he thong cho dung phim & AI (Ultimate Performance, GPU Scheduling, Adobe CEP)..." -ForegroundColor Cyan
foreach ($ver in @("CSXS.9","CSXS.10","CSXS.11","CSXS.12","CSXS.13")) {
    New-Item -Path "HKCU:\Software\Adobe\$ver" -Force | Out-Null
    Set-ItemProperty -Path "HKCU:\Software\Adobe\$ver" -Name "PlayerDebugMode" -Value "1" -Type String -Force
}

$adminBlock = @'
powercfg -duplicatescheme e9a42b02-d5df-448d-aa00-03f14749eb61 | Out-Null
$ult = (powercfg -list | Select-String -Pattern "([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}).*(Ultimate)" | Select-Object -First 1)
if ($ult) { powercfg -setactive $ult.Matches[0].Groups[1].Value } else { powercfg -setactive 8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c }
powercfg -change -standby-timeout-ac 0
Set-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Control\FileSystem" -Name "LongPathsEnabled" -Value 1 -Type DWord -Force
New-Item -Path "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\AppModelUnlock" -Force | Out-Null
Set-ItemProperty -Path "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\AppModelUnlock" -Name "AllowDevelopmentWithoutDevLicense" -Value 1 -Type DWord -Force
Set-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Control\GraphicsDrivers" -Name "HwSchMode" -Value 2 -Type DWord -Force
'@
try {
    Start-Process powershell.exe -Verb RunAs -ArgumentList "-NoProfile -WindowStyle Hidden -ExecutionPolicy Bypass -Command `"$adminBlock`"" -Wait
    Write-Host "  [OK] Da bat Ultimate Performance + HAGS GPU + LongPaths + Symlink!" -ForegroundColor Green
} catch {
    Write-Host "  [INFO] Bo qua buoc UAC Admin (van tiep tuc cai dat binh thuong)." -ForegroundColor Yellow
}

$gpuReg = "HKCU:\Software\Microsoft\DirectX\UserGpuPreferences"
New-Item -Path $gpuReg -Force | Out-Null
$gpuApps = @(
    "$env:LOCALAPPDATA\CapCut\Apps\CapCut.exe",
    (Get-Command ffmpeg -ErrorAction SilentlyContinue).Source,
    (Get-Command python -ErrorAction SilentlyContinue).Source
) + (Get-ChildItem "C:\Program Files\Adobe" -Recurse -Depth 2 -Include "Adobe Premiere Pro.exe","AfterFX.exe","Photoshop.exe","Adobe Media Encoder.exe" -ErrorAction SilentlyContinue | Select-Object -ExpandProperty FullName)
foreach ($exe in $gpuApps) {
    if ($exe -and (Test-Path -LiteralPath $exe)) {
        Set-ItemProperty -Path $gpuReg -Name $exe -Value "GpuPreference=2;" -Type String -Force
    }
}
Write-Host "  [OK] Da gan GPU roi High-Performance cho FFmpeg, Python, CapCut & Adobe." -ForegroundColor Green

# 3. CLONE / CAP NHAT FULL STUDIO TRUC TIEP TU GITHUB
Write-Host "`n[3/7] Tai / cap nhat ma nguon Full Studio + 27 Skills + 44 Font TVC tu GitHub..." -ForegroundColor Cyan
$studioRoot = if (Test-Path "D:\") { "D:\AI\full studio" } elseif (Test-Path "E:\") { "E:\AI\full studio" } else { "C:\AI\full studio" }
$parentDir  = Split-Path $studioRoot -Parent
New-Item -ItemType Directory -Force -Path $parentDir | Out-Null

if (Test-Path -LiteralPath "$studioRoot\.git") {
    Write-Host "  -> Da co repo tai '$studioRoot', dang git pull ban moi nhat..." -ForegroundColor Yellow
    git -C $studioRoot remote set-url origin https://github.com/huusei1234-droid/claude-edit.git
    git -C $studioRoot pull --ff-only origin main
} elseif (Test-Path -LiteralPath "$studioRoot\canvas") {
    Write-Host "  -> Dong bo git vao thu muc '$studioRoot' hien co..." -ForegroundColor Yellow
    $tmpClone = Join-Path $env:TEMP "full_studio_git_sync"
    Remove-Item $tmpClone -Recurse -Force -ErrorAction SilentlyContinue
    git clone --depth 1 https://github.com/huusei1234-droid/claude-edit.git $tmpClone
    robocopy $tmpClone $studioRoot /E /XO /NFL /NDL /NJH /NJS | Out-Null
    Remove-Item $tmpClone -Recurse -Force -ErrorAction SilentlyContinue
} else {
    Write-Host "  -> Cloning https://github.com/huusei1234-droid/claude-edit.git -> '$studioRoot'..." -ForegroundColor Yellow
    git clone https://github.com/huusei1234-droid/claude-edit.git $studioRoot
}

$driveQual = Split-Path $studioRoot -Qualifier
New-Item -ItemType Directory -Force -Path "$driveQual\antigravyti" | Out-Null
if (-not (Test-Path -LiteralPath "$driveQual\antigravyti\infinite-canvas")) {
    cmd /c mklink /J "$driveQual\antigravyti\infinite-canvas" "$studioRoot\canvas" | Out-Null
}

# 4. DONG BO CAU HINH ANTIGRAVITY GLOBAL (27 SKILLS + PLUGINS + GEMINI.MD + MCP)
Write-Host "`n[4/7] Cai dat 27 Skills, Rules, Plugins & MCP Premiere/Photoshop cho Antigravity..." -ForegroundColor Cyan
$agyCfg = Join-Path $env:USERPROFILE ".gemini\config"
New-Item -ItemType Directory -Force -Path $agyCfg, "$agyCfg\skills", "$agyCfg\plugins" | Out-Null

if (Test-Path -LiteralPath "$studioRoot\.agents\skills") {
    robocopy "$studioRoot\.agents\skills" "$agyCfg\skills" /E /XO /NFL /NDL /NJH /NJS | Out-Null
    Write-Host "  [OK] Da nap 27 Skills vao $agyCfg\skills" -ForegroundColor Green
}
if (Test-Path -LiteralPath "$studioRoot\00_CAI_DAT_PC_NHA\antigravity_bundle\plugins") {
    robocopy "$studioRoot\00_CAI_DAT_PC_NHA\antigravity_bundle\plugins" "$agyCfg\plugins" /E /XO /NFL /NDL /NJH /NJS | Out-Null
}
if (Test-Path -LiteralPath "$studioRoot\00_CAI_DAT_PC_NHA\antigravity_bundle\GEMINI_GLOBAL.md") {
    Copy-Item -LiteralPath "$studioRoot\00_CAI_DAT_PC_NHA\antigravity_bundle\GEMINI_GLOBAL.md" -Destination "$agyCfg\GEMINI.md" -Force
}

if (Get-Command npm -ErrorAction SilentlyContinue) {
    npm install -g premiere-pro-mcp @immersive-media-technologies/photoshop-mcp-imt
    $cepScript = Join-Path $env:APPDATA "npm\node_modules\premiere-pro-mcp\scripts\install-cep.ps1"
    if (Test-Path -LiteralPath $cepScript) {
        powershell -ExecutionPolicy Bypass -File $cepScript -ConnectorHost Premiere
        powershell -ExecutionPolicy Bypass -File $cepScript -ConnectorHost AfterEffects
    }
    $nodeExe = (Get-Command node -ErrorAction SilentlyContinue).Source
    if (-not $nodeExe) { $nodeExe = "C:\Program Files\nodejs\node.exe" }
    $mcpObj = @{
        mcpServers = @{
            "premiere-pro" = @{
                command = $nodeExe
                args    = @("$env:APPDATA\npm\node_modules\premiere-pro-mcp\dist\index.js")
            }
            "photoshop" = @{
                command = $nodeExe
                args    = @("$env:APPDATA\npm\node_modules\@immersive-media-technologies\photoshop-mcp-imt\dist\index.js")
            }
        }
    }
    $mcpJson = $mcpObj | ConvertTo-Json -Depth 5
    [System.IO.File]::WriteAllText("$agyCfg\mcp_config.json", $mcpJson, [System.Text.UTF8Encoding]::new($false))
    Write-Host "  [OK] Da cau hinh MCP Premiere Pro + Photoshop tai $agyCfg\mcp_config.json" -ForegroundColor Green
}

# 5. CAI DAT 44 FONT TVC TIENG VIET VAO WINDOWS
Write-Host "`n[5/7] Cai dat bo 44 Font chu TVC Tieng Viet..." -ForegroundColor Cyan
$fontDirs = @(
    "$studioRoot\00_CAI_DAT_PC_NHA\fonts_tvc_vi",
    "$studioRoot\BO_KIEN_THUC_TVC_AI_PORTABLE\03_TAI_NGUYEN_DUNG_CHUNG\fonts_tvc_vi"
)
$userFontDir = Join-Path $env:LOCALAPPDATA "Microsoft\Windows\Fonts"
New-Item -ItemType Directory -Force -Path $userFontDir | Out-Null
$regFonts = "HKCU:\Software\Microsoft\Windows NT\CurrentVersion\Fonts"
New-Item -Path $regFonts -Force | Out-Null
$fCount = 0
foreach ($fd in $fontDirs) {
    if (Test-Path -LiteralPath $fd) {
        Get-ChildItem -Path $fd -Recurse -Include "*.ttf","*.otf" -ErrorAction SilentlyContinue | ForEach-Object {
            $dest = Join-Path $userFontDir $_.Name
            if (-not (Test-Path -LiteralPath $dest)) {
                Copy-Item -LiteralPath $_.FullName -Destination $dest -Force
                Set-ItemProperty -Path $regFonts -Name "$($_.BaseName) (TrueType)" -Value $dest -Type String -Force
                $fCount++
            }
        }
        break
    }
}
Write-Host "  [OK] Bo font TVC Tieng Viet da san sang (them moi $fCount font)." -ForegroundColor Green

# 6. CAI DAT THU VIEN NODE CANVAS & PYTHON CUDA VENV
Write-Host "`n[6/7] Cai dat thu vien Node (Infinity Studio) & Python GPU (.venv)..." -ForegroundColor Cyan
if (Get-Command npm -ErrorAction SilentlyContinue) {
    if (Test-Path -LiteralPath "$studioRoot\canvas\app\web\package.json") {
        npm --prefix "$studioRoot\canvas\app\web" install --legacy-peer-deps
    }
    foreach ($sub in @("desktop", "app\canvas-agent", "app\canvas-proxy")) {
        if (Test-Path -LiteralPath "$studioRoot\canvas\$sub\package.json") {
            npm --prefix "$studioRoot\canvas\$sub" install
        }
    }
}
if (Get-Command python -ErrorAction SilentlyContinue) {
    python -m pip install --upgrade pip -q
    if (Test-Path -LiteralPath "$studioRoot\edit\requirements.txt") {
        python -m pip install -r "$studioRoot\edit\requirements.txt" pillow -q
    }
    $venvDir = Join-Path $studioRoot ".venv"
    if (-not (Test-Path -LiteralPath "$venvDir\Scripts\python.exe")) {
        python -m venv $venvDir
    }
    $vpy = "$venvDir\Scripts\python.exe"
    if (Test-Path -LiteralPath $vpy) {
        & $vpy -m pip install --upgrade pip -q
        if (Get-Command nvidia-smi -ErrorAction SilentlyContinue) {
            Write-Host "  -> Phat hien card roi NVIDIA -> Cai PyTorch CUDA 12.4..." -ForegroundColor Green
            & $vpy -m pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124 -q
        }
        & $vpy -m pip install numpy opencv-python pillow requests fastapi uvicorn spandrel transformers timm scipy -q
    }
}

# 7. DANG KY DICH VU DONG BO NGAM 3 PHUT/LAN QUA GOOGLE DRIVE
Write-Host "`n[7/7] Kich hoat dich vu Dong Bo Lien Tuc 2 Chieu (3 phut/lan)..." -ForegroundColor Cyan
$syncScript = "$studioRoot\00_CAI_DAT_PC_NHA\sync_engine.ps1"
if (Test-Path -LiteralPath $syncScript) {
    New-Item -ItemType Directory -Force -Path "$studioRoot\.sync" | Out-Null
    Copy-Item -LiteralPath $syncScript -Destination "$studioRoot\.sync\sync_engine.ps1" -Force
    powershell.exe -NoProfile -ExecutionPolicy Bypass -File "$studioRoot\.sync\sync_engine.ps1" -Mode InstallTask
}

# Neu la PC o nha (khac HUUSEIZ) -> Tu dong dang ky lich nhan tai nguyen GitHub luc 22:00 hang ngay
if ($env:COMPUTERNAME -ne "HUUSEIZ" -and (Test-Path -LiteralPath "$studioRoot\00_CAI_DAT_PC_NHA\CAI_NHAN_DONG_BO_22H_MAY_NHA.ps1")) {
    powershell.exe -NoProfile -ExecutionPolicy Bypass -File "$studioRoot\00_CAI_DAT_PC_NHA\CAI_NHAN_DONG_BO_22H_MAY_NHA.ps1"
}

Write-Host "`n======================================================================" -ForegroundColor Green
Write-Host "  HOAN TAT 100%! PC '$env:COMPUTERNAME' DA SAN SANG LAM PHIM AI!      " -ForegroundColor Green
Write-Host "  Mo Google Antigravity -> File -> Open Folder -> $studioRoot         " -ForegroundColor White
Write-Host "======================================================================" -ForegroundColor Green
