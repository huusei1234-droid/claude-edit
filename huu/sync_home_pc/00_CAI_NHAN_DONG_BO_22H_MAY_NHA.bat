@echo off
chcp 65001 >nul
title Cai Dat Tu Dong Nhan Tai Nguyen GitHub 22h00 (May Tinh O Nha)
powershell.exe -NoProfile -ExecutionPolicy Bypass -Command "& { $local = Join-Path $PSScriptRoot 'CAI_NHAN_DONG_BO_22H_MAY_NHA.ps1'; if (Test-Path -LiteralPath $local) { & $local } else { irm 'https://raw.githubusercontent.com/huusei1234-droid/claude-edit/main/00_CAI_DAT_PC_NHA/CAI_NHAN_DONG_BO_22H_MAY_NHA.ps1' | iex } }"
echo.
pause
