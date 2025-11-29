"""
ADB Controller สำหรับควบคุม LDPlayer
"""
import subprocess
import time
import os
from typing import Optional, List, Tuple
import logging

logger = logging.getLogger(__name__)


class ADBController:
    """ควบคุม Android device ผ่าน ADB"""
    
    def __init__(self, adb_path: str, host: str = "127.0.0.1", port: int = 5555):
        """
        Args:
            adb_path: path ไปยัง adb.exe
            host: ADB host
            port: ADB port
        """
        self.adb_path = adb_path
        self.host = host
        self.port = port
        self.device = f"{host}:{port}"
        
        # ตรวจสอบว่า adb.exe มีอยู่
        if not os.path.exists(adb_path):
            raise FileNotFoundError(f"ADB not found: {adb_path}")
        
        logger.info(f"ADB Controller initialized: {self.device}")
    
    def connect(self) -> bool:
        """เชื่อมต่อกับ device"""
        try:
            logger.info(f"Connecting to {self.device}...")
            result = self._run_command(["connect", self.device])
            
            if "connected" in result.lower():
                logger.info("✅ Connected successfully!")
                return True
            else:
                logger.error(f"❌ Connection failed: {result}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Connection error: {e}")
            return False
    
    def disconnect(self) -> bool:
        """ตัดการเชื่อมต่อ"""
        try:
            result = self._run_command(["disconnect", self.device])
            logger.info(f"Disconnected: {result}")
            return True
        except Exception as e:
            logger.error(f"Disconnect error: {e}")
            return False
    
    def is_connected(self) -> bool:
        """ตรวจสอบว่าเชื่อมต่ออยู่หรือไม่"""
        try:
            devices = self.get_devices()
            return self.device in devices
        except:
            return False
    
    def get_devices(self) -> List[str]:
        """ดูรายชื่อ devices ที่เชื่อมต่อ"""
        try:
            result = self._run_command(["devices"])
            lines = result.strip().split('\n')[1:]  # ข้าม header
            
            devices = []
            for line in lines:
                if '\t' in line:
                    device = line.split('\t')[0]
                    devices.append(device)
            
            return devices
        except Exception as e:
            logger.error(f"Get devices error: {e}")
            return []
    
    def tap(self, x: int, y: int) -> bool:
        """แตะที่ตำแหน่ง (x, y)"""
        try:
            self._run_command(["-s", self.device, "shell", "input", "tap", str(x), str(y)])
            logger.debug(f"Tapped at ({x}, {y})")
            return True
        except Exception as e:
            logger.error(f"Tap error: {e}")
            return False
    
    def swipe(self, x1: int, y1: int, x2: int, y2: int, duration: int = 300) -> bool:
        """ปัดจาก (x1, y1) ไป (x2, y2)"""
        try:
            self._run_command([
                "-s", self.device, "shell", "input", "swipe",
                str(x1), str(y1), str(x2), str(y2), str(duration)
            ])
            logger.debug(f"Swiped from ({x1}, {y1}) to ({x2}, {y2})")
            return True
        except Exception as e:
            logger.error(f"Swipe error: {e}")
            return False
    
    def input_text(self, text: str) -> bool:
        """พิมพ์ข้อความ"""
        try:
            # แทนที่ช่องว่างด้วย %s (ADB requirement)
            text = text.replace(' ', '%s')
            self._run_command(["-s", self.device, "shell", "input", "text", text])
            logger.debug(f"Input text: {text}")
            return True
        except Exception as e:
            logger.error(f"Input text error: {e}")
            return False
    
    def press_key(self, keycode: str) -> bool:
        """กดปุ่ม (เช่น KEYCODE_ENTER, KEYCODE_BACK)"""
        try:
            self._run_command(["-s", self.device, "shell", "input", "keyevent", keycode])
            logger.debug(f"Pressed key: {keycode}")
            return True
        except Exception as e:
            logger.error(f"Press key error: {e}")
            return False
    
    def start_app(self, package: str, activity: str = None) -> bool:
        """เปิดแอป"""
        try:
            if activity:
                cmd = f"{package}/{activity}"
            else:
                cmd = package
            
            self._run_command(["-s", self.device, "shell", "am", "start", "-n", cmd])
            logger.info(f"Started app: {package}")
            return True
        except Exception as e:
            logger.error(f"Start app error: {e}")
            return False
    
    def stop_app(self, package: str) -> bool:
        """ปิดแอป"""
        try:
            self._run_command(["-s", self.device, "shell", "am", "force-stop", package])
            logger.info(f"Stopped app: {package}")
            return True
        except Exception as e:
            logger.error(f"Stop app error: {e}")
            return False
    
    def screenshot(self, save_path: str) -> bool:
        """ถ่ายภาพหน้าจอ"""
        try:
            # ถ่ายภาพลง device
            device_path = "/sdcard/screenshot.png"
            self._run_command(["-s", self.device, "shell", "screencap", "-p", device_path])
            
            # ดึงมา PC
            self._run_command(["-s", self.device, "pull", device_path, save_path])
            
            # ลบออกจาก device
            self._run_command(["-s", self.device, "shell", "rm", device_path])
            
            logger.info(f"Screenshot saved: {save_path}")
            return True
        except Exception as e:
            logger.error(f"Screenshot error: {e}")
            return False
    
    def get_screen_size(self) -> Optional[Tuple[int, int]]:
        """ดูขนาดหน้าจอ"""
        try:
            result = self._run_command(["-s", self.device, "shell", "wm", "size"])
            # Physical size: 1080x1920
            size_str = result.split(':')[1].strip()
            width, height = map(int, size_str.split('x'))
            return (width, height)
        except Exception as e:
            logger.error(f"Get screen size error: {e}")
            return None
    
    def is_app_running(self, package: str) -> bool:
        """ตรวจสอบว่าแอปกำลังรันอยู่หรือไม่"""
        try:
            result = self._run_command(["-s", self.device, "shell", "pidof", package])
            return bool(result.strip())
        except:
            return False
    
    def _run_command(self, args: List[str]) -> str:
        """รัน ADB command"""
        cmd = [self.adb_path] + args
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=10,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            )
            
            if result.returncode != 0 and result.stderr:
                logger.warning(f"ADB stderr: {result.stderr}")
            
            return result.stdout
            
        except subprocess.TimeoutExpired:
            logger.error(f"ADB command timeout: {' '.join(args)}")
            raise
        except Exception as e:
            logger.error(f"ADB command error: {e}")
            raise
    
    def wait(self, seconds: float):
        """รอ"""
        time.sleep(seconds)
        
    def __repr__(self):
        return f"ADBController(device={self.device})"
