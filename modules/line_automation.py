"""
LINE Automation - ควบคุม LINE app ผ่าน ADB และ LDConsole
"""
import logging
import time
from typing import List, Optional
from .adb_controller import ADBController
from .ldconsole_controller import LDConsoleController

logger = logging.getLogger(__name__)


class LINEAutomation:
    """Automation สำหรับ LINE app"""
    
    def __init__(self, adb: ADBController, config: dict, ldconsole: Optional[LDConsoleController] = None):
        """
        Args:
            adb: ADB Controller instance
            config: configuration dict
            ldconsole: LDConsole Controller instance (optional)
        """
        self.adb = adb
        self.ldconsole = ldconsole
        self.config = config
        self.package = config.get('package_name', 'jp.naver.line.android')
        self.activity = config.get('activity_name', 'jp.naver.line.android.activity.SplashActivity')
        self.timeout = config.get('wait_timeout', 10)
        
        # ดึงขนาดหน้าจอ
        screen_size = self.adb.get_screen_size()
        if screen_size:
            self.screen_width, self.screen_height = screen_size
            logger.info(f"Screen size: {self.screen_width}x{self.screen_height}")
        else:
            # ค่า default สำหรับ LDPlayer
            self.screen_width, self.screen_height = 540, 960
            logger.warning(f"Using default screen size: {self.screen_width}x{self.screen_height}")
    
    def start_line(self) -> bool:
        """เปิด LINE app"""
        try:
            logger.info("Starting LINE app...")
            
            # วิธีที่ 1: ใช้ ldconsole (เร็วกว่า)
            if self.ldconsole:
                emulator_name = self.config.get('emulator_name', '0')
                
                # ปิดก่อน (ถ้าเปิดอยู่)
                if self.adb.is_app_running(self.package):
                    logger.info("LINE is already running, stopping first...")
                    self.ldconsole.kill_app(emulator_name, self.package)
                    self.adb.wait(2)
                
                # เปิดแอป ด้วย ldconsole
                success = self.ldconsole.run_app(emulator_name, self.package)
                if not success:
                    logger.warning("ldconsole run_app failed, trying ADB...")
                    success = self.adb.start_app(self.package, self.activity)
            else:
                # วิธีที่ 2: ใช้ ADB (ถ้าไม่มี ldconsole)
                if self.adb.is_app_running(self.package):
                    logger.info("LINE is already running, stopping first...")
                    self.adb.stop_app(self.package)
                    self.adb.wait(2)
                
                success = self.adb.start_app(self.package, self.activity)
            
            if not success:
                return False
            
            # รอให้แอปโหลด
            logger.info("Waiting for LINE to load...")
            self.adb.wait(5)
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to start LINE: {e}")
            return False
    
    def go_to_friends_tab(self) -> bool:
        """ไปที่แท็บเพื่อน"""
        try:
            logger.info("Going to Friends tab...")
            
            # ตำแหน่งแท็บเพื่อน (อาจต้องปรับตามหน้าจอ)
            # ปกติอยู่ที่ 1/5 ของความกว้าง, ด้านล่าง
            x = self.screen_width // 5
            y = self.screen_height - 50
            
            self.adb.tap(x, y)
            self.adb.wait(2)
            
            logger.info("✅ Navigated to Friends tab")
            return True
            
        except Exception as e:
            logger.error(f"Failed to go to Friends tab: {e}")
            return False
    
    def get_friend_positions(self, count: int = 3) -> List[tuple]:
        """
        คำนวณตำแหน่งเพื่อน N คนแรก
        
        Args:
            count: จำนวนเพื่อนที่ต้องการ
            
        Returns:
            list of (x, y) positions
        """
        positions = []
        
        # เพื่อนปกติเริ่มจากด้านบนลงมา
        # แต่ละคนห่างกัน ~160-180 pixels
        start_y = 300
        spacing = 170
        x = self.screen_width // 2  # กลางหน้าจอ
        
        for i in range(count):
            y = start_y + (i * spacing)
            if y < self.screen_height - 200:  # ไม่ให้ต่ำเกินไป
                positions.append((x, y))
        
        return positions
    
    def send_message_to_friend(self, friend_position: tuple, message: str) -> bool:
        """
        ส่งข้อความหาเพื่อนคนหนึ่ง
        
        Args:
            friend_position: (x, y) ตำแหน่งของเพื่อน
            message: ข้อความที่จะส่ง
            
        Returns:
            True ถ้าสำเร็จ
        """
        try:
            x, y = friend_position
            logger.info(f"Sending message to friend at ({x}, {y})")
            
            # 1. แตะที่เพื่อน
            self.adb.tap(x, y)
            self.adb.wait(2)
            
            # 2. แตะที่ช่องพิมพ์ข้อความ (ด้านล่าง)
            input_x = self.screen_width // 2
            input_y = self.screen_height - 100
            self.adb.tap(input_x, input_y)
            self.adb.wait(1)
            
            # 3. พิมพ์ข้อความ
            # แยกข้อความเป็นบรรทัด (ถ้ามี \n)
            lines = message.split('\n')
            for i, line in enumerate(lines):
                if line.strip():
                    self.adb.input_text(line.strip())
                    if i < len(lines) - 1:  # ถ้าไม่ใช่บรรทัดสุดท้าย
                        self.adb.press_key("KEYCODE_ENTER")
            
            self.adb.wait(1)
            
            # 4. กดปุ่มส่ง (ด้านขวาล่าง)
            send_x = self.screen_width - 80
            send_y = self.screen_height - 100
            self.adb.tap(send_x, send_y)
            
            logger.info(f"✅ Message sent: {message[:20]}...")
            self.adb.wait(1)
            
            # 5. กลับไปหน้ารายชื่อเพื่อน
            self.adb.press_key("KEYCODE_BACK")
            self.adb.wait(2)
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to send message: {e}")
            return False
    
    def send_to_first_n_friends(self, message: str, count: int = 3) -> dict:
        """
        ส่งข้อความหาเพื่อน N คนแรก
        
        Args:
            message: ข้อความที่จะส่ง
            count: จำนวนเพื่อน
            
        Returns:
            dict with results
        """
        logger.info(f"Starting to send message to {count} friends...")
        
        results = {
            'success': 0,
            'failed': 0,
            'total': count,
            'errors': []
        }
        
        try:
            # 1. เปิด LINE
            if not self.start_line():
                results['errors'].append("Failed to start LINE")
                return results
            
            # 2. ไปแท็บเพื่อน
            if not self.go_to_friends_tab():
                results['errors'].append("Failed to go to Friends tab")
                return results
            
            # 3. ดึงตำแหน่งเพื่อน
            friend_positions = self.get_friend_positions(count)
            
            if not friend_positions:
                results['errors'].append("No friend positions calculated")
                return results
            
            # 4. ส่งข้อความทีละคน
            for i, pos in enumerate(friend_positions, 1):
                logger.info(f"Sending to friend {i}/{count}...")
                
                try:
                    if self.send_message_to_friend(pos, message):
                        results['success'] += 1
                        logger.info(f"✅ Friend {i}: Success")
                    else:
                        results['failed'] += 1
                        results['errors'].append(f"Friend {i}: Failed to send")
                        logger.error(f"❌ Friend {i}: Failed")
                    
                    # หน่วงเวลาระหว่างส่ง
                    if i < count:
                        delay = self.config.get('message_delay_seconds', 2)
                        logger.info(f"Waiting {delay}s before next message...")
                        self.adb.wait(delay)
                        
                except Exception as e:
                    results['failed'] += 1
                    results['errors'].append(f"Friend {i}: {str(e)}")
                    logger.error(f"❌ Friend {i} error: {e}")
            
            logger.info(f"✅ Completed! Success: {results['success']}/{count}")
            return results
            
        except Exception as e:
            logger.error(f"Send to friends failed: {e}")
            results['errors'].append(str(e))
            return results
    
    def take_screenshot(self, filename: str) -> bool:
        """ถ่ายภาพหน้าจอ"""
        try:
            return self.adb.screenshot(filename)
        except Exception as e:
            logger.error(f"Screenshot failed: {e}")
            return False
    
    def close_line(self) -> bool:
        """ปิด LINE app"""
        try:
            logger.info("Closing LINE...")
            return self.adb.stop_app(self.package)
        except Exception as e:
            logger.error(f"Failed to close LINE: {e}")
            return False
