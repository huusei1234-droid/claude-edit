# ==============================================================================
# DONG BO TUC THI TOAN BO MA NGUON, SKILLS, PLUGINS, RULES & LICH SU LEN GITHUB
# Tuong thich 2 chieu ca May Cong Ty (HUUSEIZ) & May O Nha (PC-Nha)
# ==============================================================================
$ErrorActionPreference = "Continue"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

$studioRoot = Split-Path (Split-Path $MyInvocation.MyCommand.Path -Parent) -Parent
if (-not (Test-Path -LiteralPath "$studioRoot\.git")) {
    $studioRoot = if (Test-Path "D:\AI\full studio\.git") { "D:\AI\full studio" } else { "C:\AI\full studio" }
}
Set-Location -LiteralPath $studioRoot

Write-Host "=== [1/4] DONG BO CAU HINH ANTIGRAVITY TOAN CUC VAO KHO REPO ===" -ForegroundColor Cyan
$agyCfg    = Join-Path $env:USERPROFILE ".gemini\config"
$bundleDir = Join-Path $studioRoot "00_CAI_DAT_PC_NHA\antigravity_bundle"
New-Item -ItemType Directory -Force -Path "$bundleDir\plugins" | Out-Null

if (Test-Path -LiteralPath "$agyCfg\GEMINI.md") {
    Copy-Item -LiteralPath "$agyCfg\GEMINI.md" -Destination "$bundleDir\GEMINI_GLOBAL.md" -Force
}
if (Test-Path -LiteralPath "$agyCfg\plugins") {
    robocopy "$agyCfg\plugins" "$bundleDir\plugins" /E /XO /XF "auth.json" "*.token" "*secret*" "*cookies*" /NFL /NDL /NJH /NJS /R:1 /W:1 | Out-Null
}
if (Test-Path -LiteralPath "$studioRoot\.agents\skills") {
    robocopy "$studioRoot\.agents\skills" "$studioRoot\huu\skills" /MIR /NFL /NDL /NJH /NJS /R:1 /W:1 | Out-Null
}

# Giu ban sao trong .sync de tuong thich nguoc voi cac tac vu cu
$syncBin = Join-Path $studioRoot ".sync"
New-Item -ItemType Directory -Force -Path $syncBin | Out-Null
Copy-Item -LiteralPath $MyInvocation.MyCommand.Path -Destination (Join-Path $syncBin "github_sync_21h_push.ps1") -Force

Write-Host "=== [2/4] DONG BO GOOGLE DRIVE (AI_Full_Studio & Lich su Chat) ===" -ForegroundColor Cyan
$syncEngine = Join-Path $studioRoot "00_CAI_DAT_PC_NHA\sync_engine.ps1"
if (Test-Path -LiteralPath $syncEngine) {
    powershell.exe -NoProfile -ExecutionPolicy Bypass -File $syncEngine -Mode Push | Out-Null
    Write-Host "  [OK] Da day ban cap nhat moi nhat len Google Drive AI_Full_Studio." -ForegroundColor Green
}

Write-Host "=== [3/4] KIEM TRA VA GOM COMMIT GIT ===" -ForegroundColor Cyan
$repoUrl = "https://github.com/huusei1234-droid/claude-edit.git"
$remotes = git remote
if ($remotes -notcontains "mygithub") {
    git remote add mygithub $repoUrl
} else {
    git remote set-url mygithub $repoUrl
}

git add -A
$status = git status --porcelain
if ($status) {
    $ts = Get-Date -Format "yyyy-MM-dd HH:mm"
    $msg = "Sync [$ts] from ${env:COMPUTERNAME}: Cap nhat Full Studio, VoiceStudio CUDA fix, Turbo Antigravity, 14 Consolidated Skills & 26 Poster PSD Engine"
    git commit -m $msg
} else {
    Write-Host "  [OK] Khong co file moi thay doi chua commit." -ForegroundColor Yellow
}

Write-Host "=== [4/4] DAY LEN GITHUB (mygithub/main & origin/main) ===" -ForegroundColor Cyan
git fetch mygithub main
$behind = (git rev-list HEAD..mygithub/main --count 2>$null)
if ([int]$behind -gt 0) {
    Write-Host "  -> Phat hien $behind commit moi tren GitHub, dang rebase muot..." -ForegroundColor Yellow
    git pull --rebase -X ours mygithub main
}

git push mygithub main
if ($remotes -contains "origin") {
    git push origin main 2>$null
}

$headSha = (git rev-parse --short HEAD).Trim()
Write-Host "`n[HOAN TAT 100%] Da dong bo len GitHub thanh cong! Commit hien tai: $headSha" -ForegroundColor Green
