"""
ตัวอย่างการใช้งาน LDConsole Controller
ทดสอบการควบคุม LDPlayer ผ่าน ldconsole.exe
"""
from modules.ldconsole_controller import LDConsoleController
import time

# ============================================
# ตั้งค่า
# ============================================

# Path ไปยัง ldconsole.exe
LDCONSOLE_PATH = r"C:\LDPlayer\LDPlayer9\ldconsole.exe"

# ชื่อ emulator (ดูได้จาก LDPlayer)
EMULATOR_NAME = "LDPlayer"  # หรือใช้ index "0"

# Package name ของ LINE
LINE_PACKAGE = "jp.naver.line.android"

# ============================================
# Main
# ============================================

def main():
    print("="*70)
    print("🎮 LDConsole Controller Demo")
    print("="*70)
    
    try:
        # 1. สร้าง controller
        print("\n1️⃣ Initializing LDConsole...")
        ldconsole = LDConsoleController(LDCONSOLE_PATH)
        print("   ✅ Initialized!")
        
        # 2. ดูรายชื่อ emulators
        print("\n2️⃣ Listing emulators...")
        devices = ldconsole.list_devices()
        
        if not devices:
            print("   ❌ No emulators found!")
            print("   💡 Please create an emulator in LDPlayer first")
            return
        
        print(f"   ✅ Found {len(devices)} emulators:")
        for device in devices:
            status = "🟢 Running" if device['running'] else "⚪ Stopped"
            print(f"      {status} - {device['name']} (index: {device['index']})")
        
        # 3. ตรวจสอบ emulator
        print(f"\n3️⃣ Checking emulator '{EMULATOR_NAME}'...")
        is_running = ldconsole.is_running(EMULATOR_NAME)
        
        if is_running:
            print(f"   ✅ Emulator is running!")
        else:
            print(f"   ⚪ Emulator is not running")
            
            # ถามว่าจะเปิดไหม
            choice = input("\n   ❓ Do you want to start it? (y/n): ").strip().lower()
            
            if choice == 'y':
                print(f"\n   🚀 Starting emulator...")
                if ldconsole.launch(EMULATOR_NAME):
                    print(f"   ✅ Emulator started!")
                    print(f"   ⏳ Waiting for boot (15 seconds)...")
                    time.sleep(15)
                else:
                    print(f"   ❌ Failed to start emulator")
                    return
            else:
                print(f"   ℹ️ Skipping... (emulator must be running for app commands)")
                return
        
        # 4. ดูรายชื่อ running emulators
        print(f"\n4️⃣ Getting running emulators...")
        running_devices = ldconsole.get_running_devices()
        print(f"   ✅ Running: {len(running_devices)}")
        for device in running_devices:
            print(f"      • {device['name']} (PID: {device['pid']})")
        
        # 5. ดู ADB address
        print(f"\n5️⃣ Getting ADB address...")
        adb_devices = ldconsole.get_adb_devices()
        if adb_devices:
            print(f"   ✅ ADB Devices:")
            for addr in adb_devices:
                print(f"      • {addr}")
        else:
            print(f"   ⚠️ No ADB devices found")
        
        # 6. ทดสอบเปิด LINE
        print(f"\n6️⃣ Testing LINE app control...")
        choice = input(f"   ❓ Do you want to open LINE? (y/n): ").strip().lower()
        
        if choice == 'y':
            print(f"\n   🚀 Opening LINE...")
            if ldconsole.run_app(EMULATOR_NAME, LINE_PACKAGE):
                print(f"   ✅ LINE opened!")
                time.sleep(3)
                
                # ถามว่าจะปิดไหม
                choice = input(f"\n   ❓ Do you want to close LINE? (y/n): ").strip().lower()
                if choice == 'y':
                    print(f"\n   🛑 Closing LINE...")
                    if ldconsole.kill_app(EMULATOR_NAME, LINE_PACKAGE):
                        print(f"   ✅ LINE closed!")
                    else:
                        print(f"   ⚠️ Failed to close LINE")
            else:
                print(f"   ❌ Failed to open LINE")
                print(f"   💡 Make sure LINE is installed in the emulator")
        
        # 7. ทดสอบ GPS (optional)
        print(f"\n7️⃣ Testing GPS...")
        choice = input(f"   ❓ Do you want to set GPS location? (y/n): ").strip().lower()
        
        if choice == 'y':
            # Bangkok, Thailand
            lat = "13.7563"
            lng = "100.5018"
            print(f"\n   📍 Setting GPS to Bangkok ({lat}, {lng})...")
            if ldconsole.set_gps(EMULATOR_NAME, lat, lng):
                print(f"   ✅ GPS location set!")
            else:
                print(f"   ⚠️ Failed to set GPS")
        
        # เสร็จสิ้น
        print("\n" + "="*70)
        print("✅ Demo completed successfully!")
        print("="*70)
        
        # แสดงสรุป
        print("\n📊 Summary:")
        print(f"   • Total emulators: {len(devices)}")
        print(f"   • Running: {len(running_devices)}")
        print(f"   • LDConsole: Working ✅")
        
    except FileNotFoundError as e:
        print(f"\n❌ Error: {e}")
        print(f"\n💡 Solutions:")
        print(f"   1. Check ldconsole.exe path in the script")
        print(f"   2. Make sure LDPlayer is installed")
        print(f"   3. Current path: {LDCONSOLE_PATH}")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
