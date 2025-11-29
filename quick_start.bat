@echo off
chcp 65001 > nul
echo ======================================================================
echo LINE LDPlayer Automation - Quick Start
echo ======================================================================
echo.

:menu
echo เลือก mode:
echo.
echo 1. 🎨 เปิด GUI (ใช้งานง่ายที่สุด!) ⭐ แนะนำ
echo 2. 🎨 เปิด GUI (Admin Mode) - สำหรับจัดการ LD ⭐ แนะนำถ้าต้องสร้าง/ลบ LD
echo 3. ตรวจสอบความพร้อม (Check Setup)
echo 4. ทดสอบ LDConsole (Demo LDConsole)
echo 5. ทดสอบส่งข้อความแบบเต็ม (Full Demo)
echo 6. ส่งข้อความทันที (Send Now)
echo 7. รัน Scheduler (ส่งตามเวลาที่ตั้งไว้)
echo 8. ทดสอบ ADB Connection
echo 9. ออก
echo.
set /p choice="เลือก (1-9): "

if "%choice%"=="1" goto gui
if "%choice%"=="2" goto gui_admin
if "%choice%"=="3" goto check_setup
if "%choice%"=="4" goto demo_ldconsole
if "%choice%"=="5" goto demo_full
if "%choice%"=="6" goto send_now
if "%choice%"=="7" goto scheduler
if "%choice%"=="8" goto test_adb
if "%choice%"=="9" goto end
goto menu

:gui
echo.
echo ======================================================================
echo กำลังเปิด GUI...
echo ======================================================================
python gui.py
pause
goto menu

:gui_admin
echo.
echo ======================================================================
echo กำลังเปิด GUI (Admin Mode)...
echo ======================================================================
echo.
echo ⚠️ จะขอสิทธิ์ Administrator (กด Yes ในหน้าต่าง UAC)
echo.
pause
powershell -Command "Start-Process python -ArgumentList 'gui.py' -Verb RunAs"
goto menu

:check_setup
echo.
echo ======================================================================
echo ตรวจสอบความพร้อม...
echo ======================================================================
python check_setup.py
pause
goto menu

:demo_ldconsole
echo.
echo ======================================================================
echo ทดสอบ LDConsole...
echo ======================================================================
python demo_ldconsole.py
pause
goto menu

:demo_full
echo.
echo ======================================================================
echo ทดสอบส่งข้อความแบบเต็ม...
echo ======================================================================
python demo_full_automation.py
pause
goto menu

:send_now
echo.
echo ======================================================================
echo กำลังส่งข้อความทันที...
echo ======================================================================
python main.py --send-now
pause
goto menu

:scheduler
echo.
echo ======================================================================
echo เริ่ม Scheduler...
echo กด Ctrl+C เพื่อหยุด
echo ======================================================================
python main.py --scheduler
pause
goto menu

:test_adb
echo.
echo ======================================================================
echo ทดสอบ ADB Connection...
echo ======================================================================
"C:\LDPlayer\LDPlayer9\adb.exe" devices
echo.
echo ถ้าเห็น "127.0.0.1:5555   device" แปลว่า OK!
echo.
pause
goto menu

:end
echo.
echo Bye! 👋
timeout /t 2 > nul
