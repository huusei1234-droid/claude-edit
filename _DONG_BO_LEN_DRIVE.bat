@echo off
chcp 65001 >nul
powershell -NoProfile -ExecutionPolicy Bypass -File "Z:\Drive của tôi\AI_Full_Studio\00_DONG_BO_2_MAY\sync_engine.ps1" -Mode Push
echo.
pause
