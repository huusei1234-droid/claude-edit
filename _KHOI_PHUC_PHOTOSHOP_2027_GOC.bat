@echo off
chcp 65001 >nul
powershell -NoProfile -ExecutionPolicy Bypass -Command "Start-Process powershell.exe -Verb RunAs -ArgumentList '-NoProfile -ExecutionPolicy Bypass -NoExit -File \"d:\AI\full studio\launcher\restore_official_photoshop_2027.ps1\"'"
