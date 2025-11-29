"""
LINE LDPlayer Automation - GUI Mode
รัน GUI แทน command line
"""
import sys
import os

# เปลี่ยน working directory ให้ถูกต้อง
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)

# เพิ่ม path ให้หา modules
sys.path.insert(0, script_dir)

from modules.gui import ModernGUI

if __name__ == "__main__":
    print("="*70)
    print("🎨 Starting GUI...")
    print("="*70)
    print(f"📁 Working directory: {os.getcwd()}")
    print("="*70)
    
    try:
        gui = ModernGUI()
        gui.run()
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        input("\nPress Enter to exit...")
