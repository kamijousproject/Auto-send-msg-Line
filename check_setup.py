"""
ตรวจสอบว่าโปรเจคพร้อมใช้งานหรือไม่
Check all requirements before running
"""
import os
import sys
import json
import subprocess

print("="*70)
print("🔍 LINE LDPlayer Automation - Setup Checker")
print("="*70)

issues = []
warnings = []

# ============================================
# 1. Check Python version
# ============================================
print("\n1️⃣ Checking Python version...")
python_version = sys.version_info

if python_version.major >= 3 and python_version.minor >= 8:
    print(f"   ✅ Python {python_version.major}.{python_version.minor}.{python_version.micro}")
else:
    print(f"   ❌ Python {python_version.major}.{python_version.minor}.{python_version.micro}")
    issues.append("Python version must be 3.8 or higher")

# ============================================
# 2. Check config.json
# ============================================
print("\n2️⃣ Checking config.json...")

if not os.path.exists("config.json"):
    print("   ❌ config.json not found!")
    issues.append("config.json file is missing")
else:
    print("   ✅ config.json exists")
    
    try:
        with open("config.json", 'r', encoding='utf-8') as f:
            config = json.load(f)
        print("   ✅ Valid JSON format")
        
        # Check required keys
        required_keys = ['ldplayer', 'line', 'automation']
        for key in required_keys:
            if key in config:
                print(f"   ✅ Has '{key}' section")
            else:
                print(f"   ❌ Missing '{key}' section")
                issues.append(f"config.json missing '{key}' section")
        
    except Exception as e:
        print(f"   ❌ Invalid JSON: {e}")
        issues.append("config.json is invalid")

# ============================================
# 3. Check LDPlayer paths
# ============================================
print("\n3️⃣ Checking LDPlayer paths...")

ldconsole_path = None
adb_path = None

if 'config' in locals():
    ldconsole_path = config.get('ldplayer', {}).get('ldconsole_path')
    adb_path = config.get('ldplayer', {}).get('adb_path')
    
    # Check ldconsole.exe
    if ldconsole_path:
        if os.path.exists(ldconsole_path):
            print(f"   ✅ ldconsole.exe found: {ldconsole_path}")
        else:
            print(f"   ❌ ldconsole.exe not found: {ldconsole_path}")
            issues.append("ldconsole.exe path is incorrect")
    else:
        print(f"   ⚠️ ldconsole_path not configured")
        warnings.append("ldconsole_path not set in config.json")
    
    # Check adb.exe
    if adb_path:
        if os.path.exists(adb_path):
            print(f"   ✅ adb.exe found: {adb_path}")
        else:
            print(f"   ❌ adb.exe not found: {adb_path}")
            issues.append("adb.exe path is incorrect")
    else:
        print(f"   ❌ adb_path not configured")
        issues.append("adb_path not set in config.json")

# ============================================
# 4. Check Python dependencies
# ============================================
print("\n4️⃣ Checking Python dependencies...")

required_packages = [
    'schedule',
    'dateutil',  # python-dateutil
    'yaml',      # pyyaml
    'requests',
    'colorlog'
]

missing_packages = []

for package in required_packages:
    try:
        __import__(package)
        print(f"   ✅ {package}")
    except ImportError:
        print(f"   ❌ {package}")
        missing_packages.append(package)

if missing_packages:
    issues.append(f"Missing packages: {', '.join(missing_packages)}")
    print(f"\n   💡 Install with: pip install -r requirements.txt")

# ============================================
# 5. Check messages.json
# ============================================
print("\n5️⃣ Checking messages.json...")

if not os.path.exists("messages.json"):
    print("   ❌ messages.json not found!")
    issues.append("messages.json file is missing")
else:
    print("   ✅ messages.json exists")
    
    try:
        with open("messages.json", 'r', encoding='utf-8') as f:
            messages = json.load(f)
        print("   ✅ Valid JSON format")
        
        # Check templates
        templates = messages.get('message_templates', [])
        enabled_templates = [t for t in templates if t.get('enabled', True)]
        print(f"   ℹ️ Found {len(templates)} templates ({len(enabled_templates)} enabled)")
        
        # Check schedules
        schedules = messages.get('schedules', [])
        enabled_schedules = [s for s in schedules if s.get('enabled', True)]
        print(f"   ℹ️ Found {len(schedules)} schedules ({len(enabled_schedules)} enabled)")
        
    except Exception as e:
        print(f"   ❌ Invalid JSON: {e}")
        issues.append("messages.json is invalid")

# ============================================
# 6. Check folders
# ============================================
print("\n6️⃣ Checking folders...")

required_folders = [
    'modules',
    'data/logs',
    'screenshots'
]

for folder in required_folders:
    if os.path.exists(folder):
        print(f"   ✅ {folder}/")
    else:
        print(f"   ⚠️ {folder}/ (will be created)")
        warnings.append(f"Folder '{folder}' will be created automatically")

# ============================================
# 7. Test LDPlayer connection (optional)
# ============================================
print("\n7️⃣ Testing LDPlayer connection...")

if ldconsole_path and os.path.exists(ldconsole_path):
    try:
        result = subprocess.run(
            [ldconsole_path, "list2"],
            capture_output=True,
            text=True,
            timeout=5,
            creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
        )
        
        if result.returncode == 0:
            devices = [line for line in result.stdout.strip().split('\n') if ',' in line]
            print(f"   ✅ LDConsole working ({len(devices)} emulators found)")
            
            for device in devices:
                parts = device.split(',')
                if len(parts) >= 4:
                    name = parts[1]
                    running = "🟢 Running" if parts[3] == '1' else "⚪ Stopped"
                    print(f"      {running} - {name}")
        else:
            print(f"   ⚠️ LDConsole command failed")
            warnings.append("Could not list emulators")
            
    except subprocess.TimeoutExpired:
        print(f"   ⚠️ LDConsole command timeout")
        warnings.append("LDConsole command timeout")
    except Exception as e:
        print(f"   ⚠️ Could not test LDConsole: {e}")
        warnings.append(f"LDConsole test failed: {e}")
else:
    print(f"   ⚠️ Skipping (ldconsole.exe not found)")

# ============================================
# Summary
# ============================================
print("\n" + "="*70)
print("📊 SUMMARY")
print("="*70)

if not issues and not warnings:
    print("✅ Everything looks good!")
    print("\n🚀 Ready to use:")
    print("   python main.py --send-now      # Send messages now")
    print("   python main.py --scheduler     # Run scheduler")
    print("   python demo_ldconsole.py       # Test LDConsole")
    print("   python demo_full_automation.py # Full demo")
    
elif not issues:
    print(f"⚠️ {len(warnings)} warnings (can still use)")
    for i, warning in enumerate(warnings, 1):
        print(f"   {i}. {warning}")
    
    print("\n✅ Can proceed with caution")
    print("\n🚀 Try running:")
    print("   python main.py --send-now")
    
else:
    print(f"❌ {len(issues)} issues found")
    for i, issue in enumerate(issues, 1):
        print(f"   {i}. {issue}")
    
    if warnings:
        print(f"\n⚠️ {len(warnings)} warnings")
        for i, warning in enumerate(warnings, 1):
            print(f"   {i}. {warning}")
    
    print("\n🔧 Please fix the issues above before running")

print("="*70)
