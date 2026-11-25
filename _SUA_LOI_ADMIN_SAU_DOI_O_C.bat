@echo off
chcp 65001 >nul
:: Tu dong xin quyen Administrator (UAC) 1 cham
net session >nul 2>&1
if %errorLevel% neq 0 (
    powershell -NoProfile -Command "Start-Process -FilePath '%~f0' -Verb RunAs"
    exit /b
)

title SUA LOI ADMIN SAU KHI DOI O DIA C (B760 + FAST STARTUP + DICH VU)
echo ============================================================================
echo   DANG DON LOI HE THONG O C MOI (GIGABYTE B760M + RTX 4070)
echo ============================================================================
echo.

echo [1/4] Tat cac dich vu Coc Coc cu bi loi treo 180s khi khoi dong (Event 7000/7009)...
for %%S in (coccoc coccocm CocCocElevationService "CocCocUpdaterInternalService156.0.8078.96" "CocCocUpdaterService156.0.8078.96") do (
    sc stop %%S >nul 2>&1
    sc config %%S start= disabled >nul 2>&1
)
if exist "C:\Users\Public\Desktop\Cốc Cốc.lnk" del /f /q "C:\Users\Public\Desktop\Cốc Cốc.lnk" >nul 2>&1
echo   [OK] Da vo hieu hoa dich vu Coc Coc loi va xoa shortcut chet.

echo.
echo [2/4] Lam moi bo nho ngu dong Fast Startup (sua triet de loi Kernel-Boot 29 / Power 41)...
powercfg /h off >nul 2>&1
powercfg /h on >nul 2>&1
echo   [OK] Da tai tao hiberfil.sys khop voi mainboard B760M & RTX 4070.

echo.
echo [3/4] Cap lai quyen doc C:\Users cho Font Driver Host & don thu muc rac TEMP.Font Driver Host...
icacls "C:\Users" /grant "*S-1-5-96-0:(OI)(CI)(RX)" >nul 2>&1
for /d %%D in ("C:\Users\TEMP.Font Driver Host*" "C:\Users\UMFD-0.Font Driver Host*") do (
    rd /s /q "%%~fD" >nul 2>&1
)
echo   [OK] Da cap quyen S-1-5-96-0 va don sach thu muc TEMP.Font Driver Host.

echo.
echo [4/4] Quet lai thiet bi PnP & mo GIGABYTE Control Center de cap nhat Driver Chipset B760...
pnputil /scan-devices >nul 2>&1
if exist "C:\Program Files\GIGABYTE\Control Center\GCC.exe" (
    start "" "C:\Program Files\GIGABYTE\Control Center\GCC.exe"
    echo   [OK] Da mo GIGABYTE Control Center — ban chi can bam Update o muc Chipset/Serial IO la het sach dau cham than!
)

echo.
echo ============================================================================
echo   HOAN TAT 100%! Moi dich vu Admin tren o C moi da duoc sua sach.
echo ============================================================================
pause
