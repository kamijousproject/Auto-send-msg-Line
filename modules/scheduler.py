"""
Message Scheduler - จัดการตารางส่งข้อความ
"""
import logging
import schedule
import time
from datetime import datetime, timedelta
from typing import List, Dict, Callable
import threading

logger = logging.getLogger(__name__)


class MessageScheduler:
    """จัดการตารางเวลาส่งข้อความ"""
    
    def __init__(self, timezone: str = "Asia/Bangkok"):
        """
        Args:
            timezone: timezone string
        """
        self.timezone = timezone
        self.schedules = []
        self.is_running = False
        self.thread = None
        
        logger.info(f"Scheduler initialized (timezone: {timezone})")
    
    def add_schedule(
        self,
        time_str: str,
        callback: Callable,
        days: List[str] = None,
        message: str = "",
        **kwargs
    ) -> str:
        """
        เพิ่มตารางเวลา
        
        Args:
            time_str: เวลา เช่น "09:00", "14:30"
            callback: function ที่จะเรียก
            days: วันที่จะทำงาน (monday, tuesday, ...) ถ้าไม่ระบุ = ทุกวัน
            message: ข้อความที่จะส่ง
            **kwargs: arguments อื่นๆ ส่งให้ callback
            
        Returns:
            schedule_id
        """
        try:
            # สร้าง schedule ID
            schedule_id = f"schedule_{len(self.schedules) + 1}_{int(time.time())}"
            
            # ถ้าไม่ระบุวัน = ทุกวัน
            if not days or len(days) == 0:
                days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
            
            # แปลงเป็นตัวพิมพ์เล็ก
            days = [d.lower() for d in days]
            
            schedule_data = {
                'id': schedule_id,
                'time': time_str,
                'days': days,
                'callback': callback,
                'message': message,
                'kwargs': kwargs,
                'enabled': True,
                'last_run': None,
                'next_run': None
            }
            
            self.schedules.append(schedule_data)
            
            # ลงทะเบียนกับ schedule library
            self._register_schedule(schedule_data)
            
            logger.info(f"✅ Schedule added: {schedule_id} at {time_str} on {', '.join(days)}")
            return schedule_id
            
        except Exception as e:
            logger.error(f"Failed to add schedule: {e}")
            return None
    
    def _register_schedule(self, schedule_data: dict):
        """ลงทะเบียน schedule กับ library"""
        time_str = schedule_data['time']
        days = schedule_data['days']
        callback = schedule_data['callback']
        
        # สร้าง wrapper function
        def job_wrapper():
            # ตรวจสอบว่า enabled
            if not schedule_data['enabled']:
                logger.debug(f"Schedule {schedule_data['id']} is disabled, skipping...")
                return
            
            # ตรวจสอบวันที่
            current_day = datetime.now().strftime('%A').lower()
            if current_day not in days:
                logger.debug(f"Today ({current_day}) is not in schedule days, skipping...")
                return
            
            # เรียก callback
            try:
                logger.info(f"⏰ Running schedule: {schedule_data['id']}")
                schedule_data['last_run'] = datetime.now()
                
                # เรียก function
                callback(
                    message=schedule_data['message'],
                    **schedule_data['kwargs']
                )
                
                logger.info(f"✅ Schedule completed: {schedule_data['id']}")
                
            except Exception as e:
                logger.error(f"❌ Schedule error: {e}")
        
        # ลงทะเบียนตามวัน
        if len(days) == 7:
            # ทุกวัน
            schedule.every().day.at(time_str).do(job_wrapper).tag(schedule_data['id'])
        else:
            # วันที่กำหนด
            day_map = {
                'monday': schedule.every().monday,
                'tuesday': schedule.every().tuesday,
                'wednesday': schedule.every().wednesday,
                'thursday': schedule.every().thursday,
                'friday': schedule.every().friday,
                'saturday': schedule.every().saturday,
                'sunday': schedule.every().sunday
            }
            
            for day in days:
                if day in day_map:
                    day_map[day].at(time_str).do(job_wrapper).tag(schedule_data['id'])
    
    def remove_schedule(self, schedule_id: str) -> bool:
        """ลบตารางเวลา"""
        try:
            # ลบจาก list
            self.schedules = [s for s in self.schedules if s['id'] != schedule_id]
            
            # ลบจาก schedule library
            schedule.clear(schedule_id)
            
            logger.info(f"✅ Schedule removed: {schedule_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to remove schedule: {e}")
            return False
    
    def enable_schedule(self, schedule_id: str) -> bool:
        """เปิดใช้งานตารางเวลา"""
        for s in self.schedules:
            if s['id'] == schedule_id:
                s['enabled'] = True
                logger.info(f"✅ Schedule enabled: {schedule_id}")
                return True
        return False
    
    def disable_schedule(self, schedule_id: str) -> bool:
        """ปิดการใช้งานตารางเวลา"""
        for s in self.schedules:
            if s['id'] == schedule_id:
                s['enabled'] = False
                logger.info(f"⏸️ Schedule disabled: {schedule_id}")
                return True
        return False
    
    def get_schedules(self) -> List[Dict]:
        """ดูตารางเวลาทั้งหมด"""
        return [
            {
                'id': s['id'],
                'time': s['time'],
                'days': s['days'],
                'message': s['message'],
                'enabled': s['enabled'],
                'last_run': s['last_run'].isoformat() if s['last_run'] else None
            }
            for s in self.schedules
        ]
    
    def start(self):
        """เริ่มต้น scheduler (background thread)"""
        if self.is_running:
            logger.warning("Scheduler is already running")
            return
        
        self.is_running = True
        
        def run_scheduler():
            logger.info("🚀 Scheduler started")
            while self.is_running:
                try:
                    schedule.run_pending()
                    time.sleep(1)
                except Exception as e:
                    logger.error(f"Scheduler error: {e}")
            
            logger.info("⏹️ Scheduler stopped")
        
        self.thread = threading.Thread(target=run_scheduler, daemon=True)
        self.thread.start()
        
        logger.info("✅ Scheduler thread started")
    
    def stop(self):
        """หยุด scheduler"""
        if not self.is_running:
            logger.warning("Scheduler is not running")
            return
        
        logger.info("Stopping scheduler...")
        self.is_running = False
        
        if self.thread:
            self.thread.join(timeout=5)
        
        logger.info("✅ Scheduler stopped")
    
    def clear_all(self):
        """ลบตารางเวลาทั้งหมด"""
        schedule.clear()
        self.schedules = []
        logger.info("✅ All schedules cleared")
    
    def get_next_run_time(self, schedule_id: str) -> datetime:
        """ดูเวลาทำงานถัดไป"""
        try:
            jobs = schedule.get_jobs(schedule_id)
            if jobs:
                return jobs[0].next_run
            return None
        except:
            return None
    
    def __repr__(self):
        return f"MessageScheduler(schedules={len(self.schedules)}, running={self.is_running})"
