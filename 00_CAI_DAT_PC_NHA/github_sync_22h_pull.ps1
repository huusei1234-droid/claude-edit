# ==============================================================================
# TU DONG NHAN DONG BO TAI NGUYEN TU GITHUB LUC 22H00 HANG NGAY (DANH CHO MAY O NHA)
# Kéo trọn bộ mã nguồn, 27+ Skills, Rules, Plugins & 44 Font TVC từ GitHub về máy nhà
# ==============================================================================
$ErrorActionPreference = "SilentlyContinue"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

$studioRoot = if (Test-Path "D:\AI\full studio") {
    "D:\AI\full studio"
} elseif (Test-Path "E:\AI\full studio") {
    "E:\AI\full studio"
} elseif (Test-Path "D:\") {
    "D:\AI\full studio"
} else {
    "C:\AI\full studio"
}

$syncBin = Join-Path $studioRoot ".sync"
New-Item -ItemType Directory -Force -Path $syncBin | Out-Null
$logFile = Join-Path $syncBin "github_pull_22h.log"

function Write-PullLog($msg) {
    $line = "[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] $msg"
    Add-Content -LiteralPath $logFile -Value $line -Encoding UTF8
}

Write-PullLog "=== BAT DAU NHAN TAI NGUYEN GITHUB LUC 22H00 TREN MAY '$env:COMPUTERNAME' ==="

$repoUrl = "https://github.com/huusei1234-droid/claude-edit.git"

# 1. Kéo hoặc Clone kho GitHub cá nhân về máy nhà
if (Test-Path -LiteralPath "$studioRoot\.git") {
    Set-Location -LiteralPath $studioRoot
    $remotes = git remote
    if ($remotes -notcontains "mygithub") {
        git remote add mygithub $repoUrl
    } else {
        git remote set-url mygithub $repoUrl
    }

    git fetch mygithub main
    $dirty = git status --porcelain
    $stashed = $false
    if ($dirty) {
        git stash push -u -m "auto-stash-home-before-22h-pull-$(Get-Date -Format 'yyyyMMdd-HHmmss')" | Out-Null
        $stashed = $true
    }

    git checkout main 2>$null
    git reset --hard mygithub/main | Out-Null

    if ($stashed) {
        git stash pop | Out-Null
    }
    $sha = (git rev-parse --short HEAD).Trim()
    Write-PullLog "  [GIT PULL] Da cap nhat thanh cong mygithub/main (HEAD=$sha)."
} else {
    $parentDir = Split-Path $studioRoot -Parent
    New-Item -ItemType Directory -Force -Path $parentDir | Out-Null
    if (-not (Test-Path -LiteralPath "$studioRoot\canvas")) {
        git clone $repoUrl $studioRoot | Out-Null
    } else {
        $tmpClone = Join-Path $env:TEMP "full_studio_22h_clone"
        Remove-Item $tmpClone -Recurse -Force -ErrorAction SilentlyContinue
        git clone --depth 1 $repoUrl $tmpClone | Out-Null
        robocopy $tmpClone $studioRoot /E /XO /NFL /NDL /NJH /NJS /R:1 /W:1 | Out-Null
        Remove-Item $tmpClone -Recurse -Force -ErrorAction SilentlyContinue
    }
    Write-PullLog "  [GIT CLONE] Da khoi tao ma nguon tu GitHub vao $studioRoot."
}

# 2. Đồng bộ sang cấu hình Google Antigravity toàn cục trên máy ở nhà
$agyCfg    = Join-Path $env:USERPROFILE ".gemini\config"
$bundleDir = Join-Path $studioRoot "00_CAI_DAT_PC_NHA"
New-Item -ItemType Directory -Force -Path $agyCfg, "$agyCfg\skills", "$agyCfg\plugins" | Out-Null

if (Test-Path -LiteralPath "$studioRoot\.agents\skills") {
    robocopy "$studioRoot\.agents\skills" "$agyCfg\skills" /E /XO /NFL /NDL /NJH /NJS /R:1 /W:1 | Out-Null
}
if (Test-Path -LiteralPath "$bundleDir\antigravity_bundle\plugins") {
    robocopy "$bundleDir\antigravity_bundle\plugins" "$agyCfg\plugins" /E /XO /XF "auth.json" "*.token" /NFL /NDL /NJH /NJS /R:1 /W:1 | Out-Null
}
if (Test-Path -LiteralPath "$bundleDir\antigravity_bundle\GEMINI_GLOBAL.md") {
    Copy-Item -LiteralPath "$bundleDir\antigravity_bundle\GEMINI_GLOBAL.md" -Destination "$agyCfg\GEMINI.md" -Force
}

# 3. Cài đặt tự động các Font TVC mới (nếu có thêm từ máy công ty)
$fontDir = Join-Path $bundleDir "fonts_tvc_vi"
if (Test-Path -LiteralPath $fontDir) {
    $userFontDir = Join-Path $env:LOCALAPPDATA "Microsoft\Windows\Fonts"
    New-Item -ItemType Directory -Force -Path $userFontDir | Out-Null
    $regFonts = "HKCU:\Software\Microsoft\Windows NT\CurrentVersion\Fonts"
    New-Item -Path $regFonts -Force | Out-Null
    Get-ChildItem -Path $fontDir -Recurse -Include "*.ttf","*.otf" -ErrorAction SilentlyContinue | ForEach-Object {
        $dest = Join-Path $userFontDir $_.Name
        if (-not (Test-Path -LiteralPath $dest)) {
            Copy-Item -LiteralPath $_.FullName -Destination $dest -Force
            Set-ItemProperty -Path $regFonts -Name "$($_.BaseName) (TrueType)" -Value $dest -Type String -Force
        }
    }
}

# 4. Đồng bộ bổ sung tài nguyên từ Google Drive (AI_Full_Studio) nếu máy nhà đang mở Google Drive
if (Test-Path -LiteralPath "$syncBin\sync_engine.ps1") {
    powershell.exe -NoProfile -ExecutionPolicy Bypass -File "$syncBin\sync_engine.ps1" -Mode Pull | Out-Null
}

# 4b. Tự động cài đặt & cập nhật bộ Hình nền động 4K Hữu Seiz (Code từ GitHub + Media 4K từ Drive Z:)
$wpInstaller = Join-Path $bundleDir "live_wallpapers_bundle\install_live_wallpapers_home.ps1"
if (Test-Path -LiteralPath $wpInstaller) {
    powershell.exe -NoProfile -ExecutionPolicy Bypass -File $wpInstaller | Out-Null
    Write-PullLog "  [WALLPAPER] Da dong bo & cap nhat hinh nen dong 4K Huu Seiz."
}

# 5. Ghi dấu xác nhận máy nhà đã nhận đồng bộ 22h lên Google Drive (nếu có) để dễ kiểm tra từ xa
foreach ($letter in @("Z", "G", "H", "E", "F", "I", "D")) {
    foreach ($sub in @("Drive của tôi\AI_Full_Studio\00_DONG_BO_2_MAY\machines", "My Drive\AI_Full_Studio\00_DONG_BO_2_MAY\machines")) {
        $mDir = "${letter}:\$sub"
        if (Test-Path -LiteralPath $mDir) {
            $receipt = @{
                computer       = $env:COMPUTERNAME
                user           = $env:USERNAME
                lastPull22hAt  = (Get-Date -Format "yyyy-MM-dd HH:mm:ss")
                gitCommit      = (git -C $studioRoot rev-parse --short HEAD 2>$null)
            } | ConvertTo-Json
            Set-Content -LiteralPath (Join-Path $mDir "${env:COMPUTERNAME}_GitHub_22h.json") -Value $receipt -Encoding UTF8
            break
        }
    }
}

# 6. Đặt biểu tượng Shortcut gọn đẹp ngoài Desktop máy ở nhà (không để rác file .bat)
try {
    $homeDesk = [Environment]::GetFolderPath("Desktop")
    $sh = New-Object -ComObject WScript.Shell
    $tmpPull = Join-Path $homeDesk "CapNhatTuGitHubNgay.lnk"
    $sp = $sh.CreateShortcut($tmpPull)
    $sp.TargetPath = Join-Path $studioRoot "_2_CAP_NHAT_TU_GITHUB_VE_MAY_NHA.bat"
    $sp.WorkingDirectory = $studioRoot
    $sp.IconLocation = "C:\Windows\System32\shell32.dll,238"
    $sp.Save()
    $finalPullLnk = Join-Path $homeDesk "Cập nhật từ GitHub ngay.lnk"
    if (Test-Path -LiteralPath $finalPullLnk) { Remove-Item -LiteralPath $finalPullLnk -Force }
    Move-Item -LiteralPath $tmpPull -Destination $finalPullLnk -Force
} catch {}

Write-PullLog "=== HOAN TAT NHAN DONG BO 22H00 TREN MAY '$env:COMPUTERNAME' ==="
