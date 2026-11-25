@echo off
chcp 65001 >nul
echo Đang xin quyền Quản trị viên (Admin) để khôi phục tệp gốc chính hãng của Adobe Creative Cloud...
powershell -NoProfile -Command "Start-Process powershell.exe -Verb RunAs -ArgumentList '-NoProfile -ExecutionPolicy Bypass -File \"%~dp0launcher\restore_official_adobe_cc.ps1\"'"
