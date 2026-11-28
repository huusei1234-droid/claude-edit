# Bộ Cài Đặt Tự Động 1 Chạm Cho Máy Mới Từ Kho Git (`setup_new_pc.ps1`)
# Khôi phục 100% Settings Antigravity, 39 Skills, 7 Plugins, 4 Subagents, Hooks, MCP Adobe, Fonts Tiếng Việt & Codex/ChatGPT Plus
$ErrorActionPreference = "Continue"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

$bundleDir   = $PSScriptRoot
$studioRoot  = (Resolve-Path (Join-Path $bundleDir "..")).Path
$agySrc      = Join-Path $bundleDir "antigravity_config"
$codexSrc    = Join-Path $bundleDir "codex_and_chatgpt"
$fontsSrc    = Join-Path $bundleDir "fonts_tvc_vi"
$agyTarget   = Join-Path $env:USERPROFILE ".gemini\config"

Write-Host "`n==========================================================================" -ForegroundColor Cyan
Write-Host "  KHÔI PHỤC 100% CÀI ĐẶT ANTIGRAVITY & FULL STUDIO TRÊN MÁY MỚI" -ForegroundColor Cyan
Write-Host "  Thư mục Studio : $studioRoot" -ForegroundColor White
Write-Host "  Cấu hình AGY   : $agyTarget" -ForegroundColor White
Write-Host "==========================================================================`n" -ForegroundColor Cyan

# 1. Cài đặt phần mềm nền còn thiếu qua winget
if (Get-Command winget -ErrorAction SilentlyContinue) {
    $prereqs = @(
        @{ cmd = "git";    id = "Git.Git";            name = "Git" },
        @{ cmd = "python"; id = "Python.Python.3.11"; name = "Python 3.11" },
        @{ cmd = "node";   id = "OpenJS.NodeJS.LTS";  name = "Node.js LTS" },
        @{ cmd = "ffmpeg"; id = "Gyan.FFmpeg";        name = "FFmpeg" },
        @{ cmd = "bun";    id = "Oven-sh.Bun";        name = "Bun" },
        @{ cmd = "uv";     id = "astral-sh.uv";       name = "uv" }
    )
    foreach ($p in $prereqs) {
        if (-not (Get-Command $p.cmd -ErrorAction SilentlyContinue)) {
            Write-Host "[1/7] Đang cài tự động $($p.name)..." -ForegroundColor Yellow
            winget install --id $p.id -e --accept-package-agreements --accept-source-agreements --silent
        }
    }
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
}

# 2. Tạo môi trường Python .venv (voice-studio\.venv) để chạy MCP Servers, TTS & Video QC Gate
Write-Host "[2/7] Chuẩn bị môi trường Python (.venv) cho MCP Servers & AI Tools..." -ForegroundColor Cyan
$venvDir = Join-Path $studioRoot "voice-studio\.venv"
$venvPy  = Join-Path $venvDir "Scripts\python.exe"
if (-not (Test-Path -LiteralPath $venvPy)) {
    python -m venv "$venvDir"
}
if (Test-Path -LiteralPath $venvPy) {
    & $venvPy -m pip install --upgrade pip -q
    & $venvPy -m pip install mcp fastmcp edge-tts pillow opencv-python numpy requests faster-whisper -q
    if (Get-Command nvidia-smi -ErrorAction SilentlyContinue) {
        Write-Host "  -> Phát hiện card rời NVIDIA, cài đặt PyTorch CUDA..." -ForegroundColor Green
        & $venvPy -m pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124 -q
    }
}

# 3. Cài đặt gói Node.js cho MCP Premiere / Photoshop & Infinite Canvas
Write-Host "[3/7] Cài đặt Premiere MCP, Photoshop MCP & thư viện Infinite Canvas..." -ForegroundColor Cyan
if (Get-Command npm -ErrorAction SilentlyContinue) {
    npm install -g premiere-pro-mcp @immersive-media-technologies/photoshop-mcp-imt
    $cepScript = Join-Path $env:APPDATA "npm\node_modules\premiere-pro-mcp\scripts\install-cep.ps1"
    if (Test-Path -LiteralPath $cepScript) {
        powershell -NoProfile -ExecutionPolicy Bypass -File $cepScript -ConnectorHost Premiere | Out-Null
        powershell -NoProfile -ExecutionPolicy Bypass -File $cepScript -ConnectorHost AfterEffects | Out-Null
    }
    foreach ($sub in @("canvas\desktop", "canvas\app\canvas-proxy")) {
        $pkg = Join-Path $studioRoot "$sub\package.json"
        if (Test-Path -LiteralPath $pkg) {
            npm --prefix (Split-Path $pkg -Parent) install
        }
    }
}

# 4. Khôi phục toàn bộ ~/.gemini/config (GEMINI.md, config.json, mcp_config.json, 7 Plugins, 4 Subagents, Hooks & 39 Skills)
Write-Host "[4/7] Nạp toàn bộ Settings, 7 Plugins, 4 Subagents, Hooks & 39 Skills vào Antigravity..." -ForegroundColor Cyan
New-Item -ItemType Directory -Force -Path $agyTarget, "$agyTarget\plugins", "$agyTarget\skills", "$agyTarget\projects" | Out-Null

# GEMINI.md toàn cục
$gemTpl = Get-Content -LiteralPath (Join-Path $agySrc "GEMINI.template.md") -Raw -Encoding UTF8
Set-Content -LiteralPath (Join-Path $agyTarget "GEMINI.md") -Value ($gemTpl.Replace("__STUDIO__", $studioRoot)) -Encoding UTF8

# config.json (giữ lại remoteControlHostname của máy mới nếu đã có)
$existingHost = $null
$localCfgFile = Join-Path $agyTarget "config.json"
if (Test-Path -LiteralPath $localCfgFile) {
    try {
        $oldCfg = Get-Content -LiteralPath $localCfgFile -Raw -Encoding UTF8 | ConvertFrom-Json
        $existingHost = $oldCfg.userSettings.remoteControlHostname
    } catch {}
}
$newCfg = Get-Content -LiteralPath (Join-Path $agySrc "config.template.json") -Raw -Encoding UTF8 | ConvertFrom-Json
if ($existingHost) {
    $newCfg.userSettings | Add-Member -NotePropertyName "remoteControlHostname" -NotePropertyValue $existingHost -Force
}
$newCfg | ConvertTo-Json -Depth 10 | Set-Content -LiteralPath $localCfgFile -Encoding UTF8

# Tự dò đường dẫn Node, Python .venv & Adobe Photoshop trên máy mới cho mcp_config.json
$nodeExe = (Get-Command node -ErrorAction SilentlyContinue).Source
if (-not $nodeExe) { $nodeExe = "C:\Program Files\nodejs\node.exe" }
$pyExe = if (Test-Path -LiteralPath $venvPy) { $venvPy } else { (Get-Command python -ErrorAction SilentlyContinue).Source }
$psExe = Get-ChildItem "C:\Program Files\Adobe" -Recurse -Depth 2 -Filter "Photoshop.exe" -ErrorAction SilentlyContinue | Sort-Object FullName -Descending | Select-Object -First 1 -ExpandProperty FullName
if (-not $psExe) { $psExe = "C:\Program Files\Adobe\Adobe Photoshop 2027\Photoshop.exe" }

$mcpRaw = Get-Content -LiteralPath (Join-Path $agySrc "mcp_config.template.json") -Raw -Encoding UTF8
$mcpRendered = $mcpRaw.
    Replace("__NODE_EXE__", ($nodeExe -replace "\\", "\\")).
    Replace("__APPDATA__", ($env:APPDATA -replace "\\", "\\")).
    Replace("__PHOTOSHOP_EXE__", ($psExe -replace "\\", "\\")).
    Replace("__VENV_PYTHON__", ($pyExe -replace "\\", "\\")).
    Replace("__USER__", ($env:USERPROFILE -replace "\\", "\\"))
Set-Content -LiteralPath (Join-Path $agyTarget "mcp_config.json") -Value $mcpRendered -Encoding UTF8

# skills.json & Project URI
$studioSlash = ($studioRoot -replace "\\", "/")
$skRaw = Get-Content -LiteralPath (Join-Path $agySrc "skills.template.json") -Raw -Encoding UTF8
Set-Content -LiteralPath (Join-Path $agyTarget "skills.json") -Value ($skRaw.Replace("__STUDIO_SLASH__", $studioSlash)) -Encoding UTF8

$studioUri = "file:///" + ($studioSlash -replace ":", "%3A" -replace " ", "%20")
Get-ChildItem -Path (Join-Path $agySrc "projects") -Filter "*.json" -ErrorAction SilentlyContinue | ForEach-Object {
    $outName = $_.Name -replace "\.template\.json$", ".json"
    $pRaw = Get-Content -LiteralPath $_.FullName -Raw -Encoding UTF8
    $pRendered = $pRaw.Replace("__STUDIO_FILE_URI__", $studioUri).Replace("file:///c%3A/AI/full%20studio", $studioUri).Replace("file:///c:/AI/full%20studio", $studioUri)
    Set-Content -LiteralPath (Join-Path "$agyTarget\projects" $outName) -Value $pRendered -Encoding UTF8
}

# Chép toàn bộ 7 Plugins & tự động sửa đường dẫn bên trong hooks.json / mcp_config.json / server.py theo máy mới!
robocopy "$agySrc\plugins" "$agyTarget\plugins" /E /NFL /NDL /NJH /NJS /R:1 /W:1 | Out-Null
$escPy     = ($pyExe -replace "\\", "\\")
$escUser   = ($env:USERPROFILE -replace "\\", "\\")
$escStudio = ($studioRoot -replace "\\", "\\")

Get-ChildItem -Path "$agyTarget\plugins" -Recurse -Include "hooks.json","mcp_config.json","server.py","AGENTS.md" -ErrorAction SilentlyContinue | ForEach-Object {
    $orig = Get-Content -LiteralPath $_.FullName -Raw -Encoding UTF8
    $upd = $orig
    $upd = $upd -replace 'C:\\\\AI\\\\full studio\\\\voice-studio\\\\\.venv\\\\Scripts\\\\python\.exe', $escPy
    $upd = $upd -replace 'C:\\\\Users\\\\[^"\\]+\\\\AppData\\\\Local\\\\Programs\\\\Python\\\\Python311\\\\python\.exe', $escPy
    $upd = $upd -replace 'C:\\\\Users\\\\[^"\\]+\\\\\.gemini', "$escUser\\.gemini"
    $upd = $upd -replace 'C:\\Users\\[^"\\]+\\\.gemini', "$env:USERPROFILE\.gemini"
    $upd = $upd -replace 'C:\\\\AI\\\\full studio', $escStudio
    $upd = $upd -replace 'C:\\AI\\full studio', $studioRoot
    if ($upd -ne $orig) {
        Set-Content -LiteralPath $_.FullName -Value $upd -Encoding UTF8
    }
}

# Liên kết đủ 39 Skills sang ~/.gemini/config/skills
$wsSkills = Join-Path $studioRoot ".agents\skills"
if (Test-Path -LiteralPath $wsSkills) {
    Get-ChildItem -Path $wsSkills -Directory | ForEach-Object {
        $dstSk = Join-Path "$agyTarget\skills" $_.Name
        if (-not (Test-Path -LiteralPath $dstSk)) {
            cmd /c mklink /J "$dstSk" "$($_.FullName)" | Out-Null
        }
    }
}

# 5. Khôi phục OpenAI Codex & ChatGPT Plus Project IDs
Write-Host "[5/7] Cấu hình OpenAI Codex & Dự án ChatGPT Plus (HTPM + K4)..." -ForegroundColor Cyan
$codexHome = Join-Path $env:USERPROFILE ".codex"
New-Item -ItemType Directory -Force -Path "$codexHome\skills" | Out-Null
if (Test-Path -LiteralPath (Join-Path $codexSrc "AGENTS.template.md")) {
    $ca = (Get-Content -LiteralPath (Join-Path $codexSrc "AGENTS.template.md") -Raw -Encoding UTF8).Replace("C:\AI\full studio", $studioRoot)
    Set-Content -LiteralPath (Join-Path $codexHome "AGENTS.md") -Value $ca -Encoding UTF8
}
Get-ChildItem -Path $wsSkills -Directory -ErrorAction SilentlyContinue | ForEach-Object {
    $cSk = Join-Path "$codexHome\skills" $_.Name
    if (-not (Test-Path -LiteralPath $cSk)) {
        cmd /c mklink /J "$cSk" "$($_.FullName)" | Out-Null
    }
}
$npmBin = Join-Path $env:APPDATA "npm"
if (Test-Path -LiteralPath $npmBin) {
    Copy-Item -LiteralPath (Join-Path $codexSrc "codex.cmd") -Destination (Join-Path $npmBin "codex.cmd") -Force -ErrorAction SilentlyContinue
    Copy-Item -LiteralPath (Join-Path $codexSrc "codex") -Destination (Join-Path $npmBin "codex") -Force -ErrorAction SilentlyContinue
}
$icfData = Join-Path $env:APPDATA "infinite-canvas-flow"
New-Item -ItemType Directory -Force -Path $icfData | Out-Null
Copy-Item -LiteralPath (Join-Path $codexSrc "chatgpt-driver.json") -Destination (Join-Path $icfData "chatgpt-driver.json") -Force -ErrorAction SilentlyContinue

# 6. Cài đặt trọn bộ Font TVC Tiếng Việt vào Windows
Write-Host "[6/7] Cài đặt tự động bộ Font chữ TVC Tiếng Việt vào Windows..." -ForegroundColor Cyan
if (Test-Path -LiteralPath $fontsSrc) {
    $uFonts = Join-Path $env:LOCALAPPDATA "Microsoft\Windows\Fonts"
    New-Item -ItemType Directory -Force -Path $uFonts | Out-Null
    $regF = "HKCU:\Software\Microsoft\Windows NT\CurrentVersion\Fonts"
    New-Item -Path $regF -Force | Out-Null
    Get-ChildItem -Path $fontsSrc -Include "*.ttf","*.otf" -Recurse | ForEach-Object {
        $df = Join-Path $uFonts $_.Name
        if (-not (Test-Path -LiteralPath $df)) {
            Copy-Item -LiteralPath $_.FullName -Destination $df -Force
            Set-ItemProperty -Path $regF -Name "$($_.BaseName) (TrueType)" -Value $df -Type String -Force
        }
    }
}

# 7. Bật Adobe CEP Debug, phím tắt chụp màn hình PrintScreen & sửa lỗi khung kéo CapCut đa màn hình
Write-Host "[7/7] Kích hoạt tối ưu Adobe CEP, nút chụp màn hình PS & CapCut mượt đa màn hình..." -ForegroundColor Cyan
foreach ($ver in @("CSXS.9", "CSXS.10", "CSXS.11", "CSXS.12", "CSXS.13")) {
    New-Item -Path "HKCU:\Software\Adobe\$ver" -Force | Out-Null
    Set-ItemProperty -Path "HKCU:\Software\Adobe\$ver" -Name "PlayerDebugMode" -Value "1" -Type String -Force
}
Set-ItemProperty -Path "HKCU:\Control Panel\Keyboard" -Name "PrintScreenKeyForSnippingEnabled" -Value 1 -Type DWord -Force -ErrorAction SilentlyContinue
[Environment]::SetEnvironmentVariable("QT_D3D_NOFLIP", "1", "User")

# 8. Tự động khôi phục 100% Lịch sử Đoạn Chat & Dự án từ Google Drive (nếu máy mới đã đăng nhập Google Drive)
$mergePy = Join-Path $bundleDir "smart_merge_chats.py"
if ((Test-Path -LiteralPath $mergePy) -and (Test-Path -LiteralPath $pyExe)) {
    Write-Host "[8/8] Đang kiểm tra Google Drive để khôi phục 100% Lịch sử Đoạn Chat Antigravity..." -ForegroundColor Cyan
    & $pyExe -X utf8 "$mergePy" --mode pull
}

Write-Host "`n==========================================================================" -ForegroundColor Green
Write-Host "  HOÀN TẤT 100%! MÁY MỚI ĐÃ SẴN SÀNG VỚI TOÀN BỘ SETTINGS ANTIGRAVITY!" -ForegroundColor Green
Write-Host "  Bước cuối trên máy mới:" -ForegroundColor Yellow
Write-Host "   1. Mở Google Antigravity -> mở dự án '$studioRoot'" -ForegroundColor White
Write-Host "   2. Đăng nhập Brave (ChatGPT Plus 'Richard Rodriguez' + các nick Gemini/Flow)" -ForegroundColor White
Write-Host "   3. Trong Plugins của Antigravity, bấm Sign in cho Google Drive/Docs/Canva nếu cần." -ForegroundColor White
Write-Host "==========================================================================`n" -ForegroundColor Green
