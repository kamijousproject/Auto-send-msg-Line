@echo off
:: LINE LDPlayer Automation - GUI (Admin Mode)
:: ไฟล์นี้จะขอสิทธิ์ Admin อัตโนมัติ

echo ======================================================================
echo LINE LDPlayer Automation - GUI (Admin Mode)
echo ======================================================================
echo.

:: Check for admin rights
net session >nul 2>&1
if %errorLevel% == 0 (
    echo [OK] Running with Administrator privileges
    echo.
) else (
    echo [!] Not running as Administrator
    echo [!] Please run this file as Administrator
    echo.
    pause
    exit /b 1
)

:: Run GUI
python gui.py

pause
