"""
LDConsole Controller - ควบคุม LDPlayer ผ่าน ldconsole.exe
ใช้ ldconsole.exe แทน ADB สำหรับคำสั่งพื้นฐาน (เร็วกว่า)
"""
import subprocess
import os
import logging
from typing import Optional, List, Dict

logger = logging.getLogger(__name__)


class LDConsoleController:
    """ควบคุม LDPlayer ผ่าน ldconsole.exe"""
    
    def __init__(self, ldconsole_path: str):
        """
        Args:
            ldconsole_path: path ไปยัง ldconsole.exe
                            เช่น "C:\\LDPlayer\\LDPlayer9\\ldconsole.exe"
        """
        self.ldconsole_path = ldconsole_path
        
        # ตรวจสอบว่า ldconsole.exe มีอยู่
        if not os.path.exists(ldconsole_path):
            raise FileNotFoundError(f"ldconsole.exe not found: {ldconsole_path}")
        
        logger.info(f"LDConsole Controller initialized: {ldconsole_path}")
    
    def list_devices(self) -> List[Dict]:
        """
        ดูรายชื่อ emulators ทั้งหมด
        
        Returns:
            List of dicts with keys: index, name, pid, running
        """
        try:
            result = self._run_command(["list2"])
            
            devices = []
            for line in result.strip().split('\n'):
                if ',' in line:
                    parts = line.split(',')
                    if len(parts) >= 4:
                        index = parts[0]
                        name = parts[1]
                        pid = parts[2]
                        
                        # เช็ค running status แบบ real-time ด้วย isrunning
                        is_running = False
                        try:
                            status_result = self._run_command(["isrunning", "--index", index])
                            is_running = "running" in status_result.lower()
                        except:
                            # Fallback: ใช้ค่าจาก list2
                            is_running = parts[3] == '1'
                        
                        devices.append({
                            'index': index,
                            'name': name,
                            'pid': pid,
                            'running': is_running
                        })
            
            logger.info(f"Found {len(devices)} devices")
            return devices
            
        except Exception as e:
            logger.error(f"List devices error: {e}")
            return []
    
    def get_running_devices(self) -> List[Dict]:
        """ดูรายชื่อ emulators ที่กำลังรันอยู่"""
        all_devices = self.list_devices()
        return [d for d in all_devices if d['running']]
    
    def is_running(self, name_or_index: str) -> bool:
        """ตรวจสอบว่า emulator กำลังรันอยู่หรือไม่"""
        try:
            result = self._run_command(["isrunning", "--name", name_or_index])
            return "running" in result.lower()
        except:
            return False
    
    def launch(self, name_or_index: str, headless: bool = False) -> bool:
        """
        เปิด emulator พร้อม UI (รองรับหลาย instance พร้อมกัน)
        
        Args:
            name_or_index: ชื่อหรือ index ของ emulator
            headless: True = ไม่แสดง UI, False = แสดง UI (default)
        """
        try:
            import os
            import subprocess
            import time
            
            logger.info(f"Launching emulator: {name_or_index} (headless={headless})")
            
            # ใช้ dnconsole launch command (จะเปิด UI ให้อัตโนมัติ)
            cmd = ["launch", "--index", str(name_or_index)]
            self._run_command(cmd)
            
            logger.info("✅ Emulator launched")
            
            # รอเล็กน้อยให้ emulator boot
            time.sleep(2)
            
            return True
                
        except Exception as e:
            logger.error(f"Launch error: {e}")
            return False
    
    def launch_with_app(self, name_or_index: str, package_name: str) -> bool:
        """
        เปิด emulator พร้อม app
        
        Args:
            name_or_index: ชื่อหรือ index
            package_name: package name ของ app (เช่น jp.naver.line.android)
        """
        try:
            logger.info(f"Launching emulator {name_or_index} with app {package_name}")
            self._run_command(["launchex", "--name", name_or_index, "--packagename", package_name])
            logger.info("✅ Emulator and app launched")
            return True
        except Exception as e:
            logger.error(f"Launch with app error: {e}")
            return False
    
    def quit(self, name_or_index: str) -> bool:
        """ปิด emulator"""
        try:
            logger.info(f"Quitting emulator: {name_or_index}")
            self._run_command(["quit", "--name", name_or_index])
            logger.info("✅ Emulator quit")
            return True
        except Exception as e:
            logger.error(f"Quit error: {e}")
            return False
    
    def quit_all(self) -> bool:
        """ปิด emulators ทั้งหมด"""
        try:
            logger.info("Quitting all emulators...")
            self._run_command(["quitall"])
            logger.info("✅ All emulators quit")
            return True
        except Exception as e:
            logger.error(f"Quit all error: {e}")
            return False
    
    def reboot(self, name_or_index: str) -> bool:
        """รีบูต emulator"""
        try:
            logger.info(f"Rebooting emulator: {name_or_index}")
            self._run_command(["reboot", "--name", name_or_index])
            logger.info("✅ Emulator rebooted")
            return True
        except Exception as e:
            logger.error(f"Reboot error: {e}")
            return False
    
    def install_app(self, name_or_index: str, apk_path: str) -> bool:
        """
        ติดตั้ง APK
        
        Args:
            name_or_index: ชื่อหรือ index
            apk_path: path ไปยังไฟล์ .apk
        """
        try:
            logger.info(f"Installing app from {apk_path}")
            self._run_command(["installapp", "--name", name_or_index, "--filename", apk_path])
            logger.info("✅ App installed")
            return True
        except Exception as e:
            logger.error(f"Install app error: {e}")
            return False
    
    def uninstall_app(self, name_or_index: str, package_name: str) -> bool:
        """ถอนการติดตั้ง app"""
        try:
            logger.info(f"Uninstalling app: {package_name}")
            self._run_command(["uninstallapp", "--name", name_or_index, "--packagename", package_name])
            logger.info("✅ App uninstalled")
            return True
        except Exception as e:
            logger.error(f"Uninstall app error: {e}")
            return False
    
    def run_app(self, name_or_index: str, package_name: str) -> bool:
        """เปิด app"""
        try:
            logger.info(f"Running app: {package_name}")
            self._run_command(["runapp", "--name", name_or_index, "--packagename", package_name])
            logger.info("✅ App started")
            return True
        except Exception as e:
            logger.error(f"Run app error: {e}")
            return False
    
    def kill_app(self, name_or_index: str, package_name: str) -> bool:
        """ปิด app"""
        try:
            logger.info(f"Killing app: {package_name}")
            self._run_command(["killapp", "--name", name_or_index, "--packagename", package_name])
            logger.info("✅ App killed")
            return True
        except Exception as e:
            logger.error(f"Kill app error: {e}")
            return False
    
    def set_gps(self, name_or_index: str, latitude: str, longitude: str) -> bool:
        """
        ตั้งตำแหน่ง GPS
        
        Args:
            latitude: ละติจูด (เช่น "13.7563")
            longitude: ลองจิจูด (เช่น "100.5018")
        """
        try:
            logger.info(f"Setting GPS: {latitude}, {longitude}")
            self._run_command(["locate", "--name", name_or_index, "--LLI", latitude, longitude])
            logger.info("✅ GPS location set")
            return True
        except Exception as e:
            logger.error(f"Set GPS error: {e}")
            return False
    
    def change_property(self, name_or_index: str, **kwargs) -> bool:
        """
        เปลี่ยนคุณสมบัติของ emulator
        
        Args:
            **kwargs: cpu, memory, resolution, imei, etc.
            
        Example:
            change_property("ld0", cpu=2, memory=2048, imei="123456789")
        """
        try:
            cmd = ["modify", "--name", name_or_index]
            
            if 'cpu' in kwargs:
                cmd.extend(["--cpu", str(kwargs['cpu'])])
            if 'memory' in kwargs:
                cmd.extend(["--memory", str(kwargs['memory'])])
            if 'resolution' in kwargs:
                cmd.extend(["--resolution", str(kwargs['resolution'])])
            if 'imei' in kwargs:
                cmd.extend(["--imei", str(kwargs['imei'])])
            if 'manufacturer' in kwargs:
                cmd.extend(["--manufacturer", str(kwargs['manufacturer'])])
            if 'model' in kwargs:
                cmd.extend(["--model", str(kwargs['model'])])
            
            logger.info(f"Changing properties: {kwargs}")
            self._run_command(cmd)
            logger.info("✅ Properties changed")
            return True
            
        except Exception as e:
            logger.error(f"Change property error: {e}")
            return False
    
    def get_adb_devices(self) -> List[str]:
        """ดูรายชื่อ ADB devices (สำหรับ connect กับ ADB Controller)"""
        try:
            result = self._run_command(["adb"])
            devices = []
            
            for line in result.strip().split('\n'):
                if ',' in line:
                    # Format: index,name,adb_address
                    parts = line.split(',')
                    if len(parts) >= 3:
                        adb_address = parts[2].strip()
                        if adb_address:
                            devices.append(adb_address)
            
            return devices
            
        except Exception as e:
            logger.error(f"Get ADB devices error: {e}")
            return []
    
    def get_adb_address(self, name_or_index: str) -> Optional[str]:
        """
        ดู ADB address ของ emulator
        
        Returns:
            ADB address (เช่น "127.0.0.1:5555") หรือ None
        """
        try:
            devices = self.list_devices()
            
            # หาตาม name หรือ index
            for device in devices:
                if device['name'] == name_or_index or device['index'] == name_or_index:
                    # ใช้ adb command เพื่อดู address
                    result = self._run_command(["adb", "--name", name_or_index])
                    if result and ':' in result:
                        return result.strip()
            
            return None
            
        except Exception as e:
            logger.error(f"Get ADB address error: {e}")
            return None
    
    def _run_command(self, args: List[str]) -> str:
        """รัน ldconsole command"""
        cmd = [self.ldconsole_path] + args
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            )
            
            if result.returncode != 0 and result.stderr:
                logger.warning(f"ldconsole stderr: {result.stderr}")
            
            return result.stdout
            
        except subprocess.TimeoutExpired:
            logger.error(f"ldconsole command timeout: {' '.join(args)}")
            raise
        except Exception as e:
            logger.error(f"ldconsole command error: {e}")
            raise
    
    def __repr__(self):
        return f"LDConsoleController(path={self.ldconsole_path})"
