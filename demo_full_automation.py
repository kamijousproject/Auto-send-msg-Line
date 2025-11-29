"""
ตัวอย่างการใช้งานแบบเต็ม
ส่งข้อความ LINE อัตโนมัติ ผ่าน LDPlayer
"""
import json
import logging
from modules.ldconsole_controller import LDConsoleController
from modules.adb_controller import ADBController
from modules.line_automation import LINEAutomation

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# ============================================
# Configuration
# ============================================

CONFIG = {
    "ldplayer": {
        "ldconsole_path": r"C:\LDPlayer\LDPlayer9\ldconsole.exe",
        "adb_path": r"C:\LDPlayer\LDPlayer9\adb.exe",
        "emulator_name": "LDPlayer",
        "adb_host": "127.0.0.1",
        "adb_port": 5555
    },
    "line": {
        "package_name": "jp.naver.line.android",
        "activity_name": "jp.naver.line.android.activity.SplashActivity",
        "wait_timeout": 10,
        "emulator_name": "LDPlayer"
    },
    "automation": {
        "target_friends_count": 3,
        "message_delay_seconds": 2,
        "retry_attempts": 3,
        "screenshot_on_error": True
    }
}

MESSAGE = """สวัสดีครับ ☀️
วันนี้สบายดีไหม
ขอให้มีความสุขนะครับ"""

# ============================================
# Main
# ============================================

def main():
    print("="*70)
    print("🤖 LINE LDPlayer Automation - Full Demo")
    print("="*70)
    
    try:
        # 1. Initialize LDConsole
        logger.info("1️⃣ Initializing LDConsole...")
        ldconsole = LDConsoleController(CONFIG['ldplayer']['ldconsole_path'])
        logger.info("✅ LDConsole initialized")
        
        # 2. Check if emulator is running
        emulator_name = CONFIG['ldplayer']['emulator_name']
        logger.info(f"2️⃣ Checking emulator '{emulator_name}'...")
        
        if not ldconsole.is_running(emulator_name):
            logger.warning("⚠️ Emulator is not running")
            logger.info("🚀 Starting emulator...")
            
            if not ldconsole.launch(emulator_name):
                logger.error("❌ Failed to start emulator")
                return
            
            logger.info("⏳ Waiting for emulator to boot (15 seconds)...")
            import time
            time.sleep(15)
        
        logger.info("✅ Emulator is running")
        
        # 3. Initialize ADB
        logger.info("3️⃣ Initializing ADB...")
        adb = ADBController(
            adb_path=CONFIG['ldplayer']['adb_path'],
            host=CONFIG['ldplayer']['adb_host'],
            port=CONFIG['ldplayer']['adb_port']
        )
        
        if not adb.connect():
            logger.error("❌ Failed to connect to ADB")
            return
        
        logger.info("✅ ADB connected")
        
        # 4. Initialize LINE Automation
        logger.info("4️⃣ Initializing LINE Automation...")
        line_automation = LINEAutomation(adb, CONFIG['line'], ldconsole)
        line_automation.config.update(CONFIG['automation'])
        logger.info("✅ LINE Automation initialized")
        
        # 5. Show message preview
        print("\n" + "="*70)
        print("📝 Message Preview:")
        print("="*70)
        print(MESSAGE)
        print("="*70)
        
        # 6. Confirm
        choice = input("\n❓ Ready to send? (y/n): ").strip().lower()
        
        if choice != 'y':
            logger.info("ℹ️ Cancelled by user")
            return
        
        # 7. Send messages
        logger.info("5️⃣ Starting automation...")
        target_count = CONFIG['automation']['target_friends_count']
        
        results = line_automation.send_to_first_n_friends(MESSAGE, target_count)
        
        # 8. Show results
        print("\n" + "="*70)
        print("📊 RESULTS")
        print("="*70)
        print(f"✅ Success: {results['success']}/{results['total']}")
        print(f"❌ Failed: {results['failed']}/{results['total']}")
        
        if results['errors']:
            print(f"\n❌ Errors:")
            for error in results['errors']:
                print(f"  • {error}")
        
        print("="*70)
        
        # 9. Cleanup
        logger.info("6️⃣ Cleaning up...")
        adb.disconnect()
        logger.info("✅ Disconnected")
        
        print("\n✅ Demo completed!")
        
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
