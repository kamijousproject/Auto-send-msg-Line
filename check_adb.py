"""
ตรวจสอบ ADB connection และหา port ที่ถูกต้อง
"""
import json
import subprocess
import os

print("="*70)
print("🔍 ตรวจสอบ ADB Connection")
print("="*70)

# Load config
try:
    with open('config.json', 'r', encoding='utf-8') as f:
        config = json.load(f)
except:
    print("❌ ไม่พบ config.json")
    exit(1)

ldconsole_path = config.get('ldplayer', {}).get('ldconsole_path')
adb_path = config.get('ldplayer', {}).get('adb_path')

if not ldconsole_path or not os.path.exists(ldconsole_path):
    print("❌ ldconsole.exe path ไม่ถูกต้อง")
    exit(1)

if not adb_path or not os.path.exists(adb_path):
    print("❌ adb.exe path ไม่ถูกต้อง")
    exit(1)

print(f"✅ ldconsole: {ldconsole_path}")
print(f"✅ adb: {adb_path}")

# 1. ดูรายการ emulators
print("\n" + "="*70)
print("1️⃣ รายการ Emulators")
print("="*70)

try:
    result = subprocess.run(
        [ldconsole_path, "list2"],
        capture_output=True,
        text=True,
        timeout=10,
        creationflags=subprocess.CREATE_NO_WINDOW
    )
    
    if result.returncode == 0:
        lines = result.stdout.strip().split('\n')
        emulators = [line for line in lines if ',' in line]
        
        if not emulators:
            print("❌ ไม่พบ emulator")
            print("💡 สร้าง emulator ใน LDPlayer ก่อน")
            exit(1)
        
        print(f"พบ {len(emulators)} emulators:\n")
        
        running = []
        for line in emulators:
            parts = line.split(',')
            if len(parts) >= 4:
                index = parts[0]
                name = parts[1]
                pid = parts[2]
                is_running = parts[3] == '1'
                
                status = "🟢 Running" if is_running else "⚪ Stopped"
                print(f"  {status} - {name} (index: {index}, PID: {pid})")
                
                if is_running:
                    running.append((index, name))
        
        if not running:
            print("\n⚠️ ไม่มี emulator ที่กำลังทำงาน")
            print("💡 เปิด LDPlayer ก่อน แล้วรอให้ boot เสร็จ")
            exit(1)
        
        print(f"\n✅ มี {len(running)} emulator ที่กำลังทำงาน")
        
    else:
        print("❌ ldconsole command failed")
        exit(1)
        
except Exception as e:
    print(f"❌ Error: {e}")
    exit(1)

# 2. ดู ADB addresses
print("\n" + "="*70)
print("2️⃣ ADB Addresses")
print("="*70)

try:
    result = subprocess.run(
        [ldconsole_path, "adb"],
        capture_output=True,
        text=True,
        timeout=10,
        creationflags=subprocess.CREATE_NO_WINDOW
    )
    
    if result.returncode == 0:
        lines = result.stdout.strip().split('\n')
        adb_lines = [line for line in lines if ',' in line]
        
        print("ADB Addresses:\n")
        
        adb_addresses = []
        for line in adb_lines:
            parts = line.split(',')
            if len(parts) >= 3:
                index = parts[0]
                name = parts[1]
                adb_addr = parts[2].strip()
                
                if adb_addr:
                    print(f"  • {name} (index: {index}) → {adb_addr}")
                    adb_addresses.append(adb_addr)
        
        if not adb_addresses:
            print("  ❌ ไม่พบ ADB address")
            exit(1)
        
        # แนะนำ address ที่ควรใช้
        print(f"\n💡 ควรใช้ ADB address นี้:")
        for addr in adb_addresses:
            print(f"   → {addr}")
        
        # ตรวจสอบกับ config
        config_host = config.get('ldplayer', {}).get('adb_host', '127.0.0.1')
        config_port = config.get('ldplayer', {}).get('adb_port', 5555)
        config_addr = f"{config_host}:{config_port}"
        
        print(f"\n📋 Config ปัจจุบัน: {config_addr}")
        
        if config_addr in adb_addresses:
            print("   ✅ ตรงกัน!")
        else:
            print("   ❌ ไม่ตรงกัน!")
            print(f"\n🔧 แนะนำแก้ไข config.json:")
            
            first_addr = adb_addresses[0]
            if ':' in first_addr:
                host, port = first_addr.split(':')
                print(f'   "adb_host": "{host}",')
                print(f'   "adb_port": {port}')
    
    else:
        print("❌ ไม่สามารถดู ADB addresses")
        
except Exception as e:
    print(f"❌ Error: {e}")

# 3. ทดสอบ ADB connection
print("\n" + "="*70)
print("3️⃣ ทดสอบ ADB Connection")
print("="*70)

try:
    # ลอง list devices
    result = subprocess.run(
        [adb_path, "devices"],
        capture_output=True,
        text=True,
        timeout=10,
        creationflags=subprocess.CREATE_NO_WINDOW
    )
    
    print("ADB Devices:\n")
    print(result.stdout)
    
    if "device" in result.stdout.lower():
        print("✅ ADB server กำลังทำงาน")
        print("✅ พบ device connected")
        
        # ลอง connect
        for addr in adb_addresses:
            print(f"\nทดสอบ connect to {addr}...")
            result = subprocess.run(
                [adb_path, "connect", addr],
                capture_output=True,
                text=True,
                timeout=10,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            print(result.stdout.strip())
    else:
        print("⚠️ ไม่พบ device")
        print("💡 ลองรันคำสั่งนี้:")
        for addr in adb_addresses:
            print(f"   {adb_path} connect {addr}")
        
except Exception as e:
    print(f"❌ Error: {e}")

# สรุป
print("\n" + "="*70)
print("📊 สรุป")
print("="*70)

print("""
ถ้าเจอปัญหา:

1. ตรวจสอบว่า LDPlayer เปิดอยู่และ boot เสร็จแล้ว
   (รอให้เห็น Android home screen)

2. แก้ไข config.json ให้ adb_host และ adb_port ตรงกับที่แสดงข้างบน

3. ลองรันคำสั่งนี้ก่อน:
   "{adb_path}" connect {adb_addresses[0] if adb_addresses else '127.0.0.1:5555'}

4. แล้วลองเชื่อมต่อใน GUI อีกครั้ง
""".format(adb_path=adb_path, adb_addresses=adb_addresses if 'adb_addresses' in locals() else []))

print("="*70)
