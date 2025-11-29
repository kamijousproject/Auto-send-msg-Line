"""
LINE LDPlayer Automation - Main Entry Point
"""
import json
import logging
import sys
import os
import argparse
from datetime import datetime
from modules.adb_controller import ADBController
from modules.ldconsole_controller import LDConsoleController
from modules.line_automation import LINEAutomation
from modules.scheduler import MessageScheduler

# Setup logging
def setup_logging(log_level="INFO", log_to_file=True, log_file="data/logs/automation.log"):
    """ตั้งค่า logging"""
    
    # สร้างโฟลเดอร์ logs
    if log_to_file:
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
    
    # Format
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    date_format = '%Y-%m-%d %H:%M:%S'
    
    # Handlers
    handlers = [logging.StreamHandler(sys.stdout)]
    
    if log_to_file:
        handlers.append(logging.FileHandler(log_file, encoding='utf-8'))
    
    # Config
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format=log_format,
        datefmt=date_format,
        handlers=handlers
    )
    
    logger = logging.getLogger(__name__)
    logger.info("="*70)
    logger.info("LINE LDPlayer Automation Started")
    logger.info("="*70)
    
    return logger


def load_config(config_path="config.json"):
    """โหลด configuration"""
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        logger.info(f"✅ Config loaded: {config_path}")
        return config
    except Exception as e:
        logger.error(f"❌ Failed to load config: {e}")
        sys.exit(1)


def load_messages(messages_path="messages.json"):
    """โหลด messages และ schedules"""
    try:
        with open(messages_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        logger.info(f"✅ Messages loaded: {messages_path}")
        return data
    except Exception as e:
        logger.error(f"❌ Failed to load messages: {e}")
        sys.exit(1)


def send_now(adb, line_automation, messages_data):
    """ส่งข้อความทันที"""
    logger.info("\n" + "="*70)
    logger.info("🚀 SEND NOW MODE")
    logger.info("="*70)
    
    # ดึงข้อความที่ enabled
    enabled_messages = [m for m in messages_data['message_templates'] if m.get('enabled', True)]
    
    if not enabled_messages:
        logger.error("❌ No enabled messages found!")
        return
    
    # ใช้ข้อความแรก
    message = enabled_messages[0]['content']
    logger.info(f"📝 Message: {message}")
    
    # ดึงจำนวนเพื่อน
    target_count = messages_data['target_friends'].get('count', 3)
    logger.info(f"👥 Target: {target_count} friends")
    
    # ส่ง!
    results = line_automation.send_to_first_n_friends(message, target_count)
    
    # แสดงผล
    logger.info("\n" + "="*70)
    logger.info("📊 RESULTS")
    logger.info("="*70)
    logger.info(f"✅ Success: {results['success']}/{results['total']}")
    logger.info(f"❌ Failed: {results['failed']}/{results['total']}")
    
    if results['errors']:
        logger.info(f"\n❌ Errors:")
        for error in results['errors']:
            logger.error(f"  - {error}")
    
    logger.info("="*70)


def setup_scheduler(scheduler, line_automation, messages_data):
    """ตั้งค่า scheduler"""
    logger.info("\n" + "="*70)
    logger.info("⏰ SETTING UP SCHEDULER")
    logger.info("="*70)
    
    # ดึง schedules ที่ enabled
    enabled_schedules = [s for s in messages_data['schedules'] if s.get('enabled', True)]
    
    if not enabled_schedules:
        logger.warning("⚠️ No enabled schedules found!")
        return
    
    # สร้าง message template map
    message_map = {m['id']: m['content'] for m in messages_data['message_templates']}
    
    # เพิ่ม schedules
    for sched in enabled_schedules:
        message_id = sched.get('message_template_id')
        message = message_map.get(message_id, "")
        
        if not message:
            logger.warning(f"⚠️ Message template {message_id} not found, skipping schedule {sched['id']}")
            continue
        
        target_count = messages_data['target_friends'].get('count', 3)
        
        # Callback function
        def send_callback(message, count):
            logger.info(f"\n⏰ Scheduled task triggered!")
            logger.info(f"📝 Message: {message}")
            logger.info(f"👥 Sending to {count} friends...")
            
            results = line_automation.send_to_first_n_friends(message, count)
            
            logger.info(f"✅ Sent to {results['success']}/{count} friends")
        
        # เพิ่ม schedule
        schedule_id = scheduler.add_schedule(
            time_str=sched['time'],
            callback=send_callback,
            days=sched.get('days', []),
            message=message,
            count=target_count
        )
        
        logger.info(f"✅ Schedule {schedule_id}: {sched['time']} - {sched.get('description', '')}")
    
    logger.info(f"\n📊 Total schedules: {len(enabled_schedules)}")
    logger.info("="*70)


def run_scheduler_mode(adb, line_automation, messages_data, config):
    """รัน scheduler mode"""
    logger.info("\n" + "="*70)
    logger.info("⏰ SCHEDULER MODE")
    logger.info("="*70)
    
    # สร้าง scheduler
    scheduler = MessageScheduler(timezone=config['scheduler']['timezone'])
    
    # ตั้งค่า schedules
    setup_scheduler(scheduler, line_automation, messages_data)
    
    # เริ่ม scheduler
    scheduler.start()
    
    logger.info("\n✅ Scheduler is running...")
    logger.info("📝 Press Ctrl+C to stop\n")
    
    try:
        # รอจนกว่าจะกด Ctrl+C
        while True:
            import time
            time.sleep(1)
            
    except KeyboardInterrupt:
        logger.info("\n\n⏹️ Stopping scheduler...")
        scheduler.stop()
        logger.info("✅ Scheduler stopped")


def main():
    """Main function"""
    
    # Parse arguments
    parser = argparse.ArgumentParser(description='LINE LDPlayer Automation')
    parser.add_argument('--send-now', action='store_true', help='Send messages now')
    parser.add_argument('--scheduler', action='store_true', help='Run scheduler mode')
    parser.add_argument('--config', default='config.json', help='Config file path')
    parser.add_argument('--messages', default='messages.json', help='Messages file path')
    parser.add_argument('--debug', action='store_true', help='Enable debug logging')
    
    args = parser.parse_args()
    
    # Load config
    config = load_config(args.config)
    
    # Setup logging
    log_level = "DEBUG" if args.debug else config['logging']['level']
    global logger
    logger = setup_logging(
        log_level=log_level,
        log_to_file=config['logging']['log_to_file'],
        log_file=config['logging']['log_file']
    )
    
    # Load messages
    messages_data = load_messages(args.messages)
    
    try:
        # Initialize LDConsole (ถ้ามี)
        ldconsole = None
        if 'ldconsole_path' in config['ldplayer']:
            try:
                logger.info("Initializing LDConsole Controller...")
                ldconsole = LDConsoleController(config['ldplayer']['ldconsole_path'])
                
                # ตรวจสอบ emulator (ไม่เปิดอัตโนมัติแล้ว - ให้ user เปิดเอง)
                emulator_name = config['ldplayer'].get('emulator_name', '0')
                if not ldconsole.is_running(emulator_name):
                    logger.warning(f"⚠️ Emulator '{emulator_name}' is not running")
                    logger.warning("⚠️ Please start the emulator manually or use GUI to launch it")
                    # Commented out auto-launch - user should control this manually
                    # logger.info("Starting emulator...")
                    # ldconsole.launch(emulator_name)
                    # import time
                    # time.sleep(10)  # รอให้ emulator boot
                
            except Exception as e:
                logger.warning(f"⚠️ LDConsole initialization failed: {e}")
                logger.info("Will use ADB only")
                ldconsole = None
        
        # Initialize ADB
        logger.info("Initializing ADB Controller...")
        adb = ADBController(
            adb_path=config['ldplayer']['adb_path'],
            host=config['ldplayer']['adb_host'],
            port=config['ldplayer']['adb_port']
        )
        
        # Connect
        logger.info("Connecting to LDPlayer...")
        if not adb.connect():
            logger.error("❌ Failed to connect to LDPlayer!")
            logger.error("Please make sure:")
            logger.error("  1. LDPlayer is running")
            logger.error("  2. ADB path is correct in config.json")
            logger.error("  3. ADB port is correct")
            sys.exit(1)
        
        # Initialize LINE automation
        logger.info("Initializing LINE Automation...")
        line_automation = LINEAutomation(adb, config['line'], ldconsole)
        line_automation.config.update(config['automation'])
        
        # เลือก mode
        if args.send_now:
            send_now(adb, line_automation, messages_data)
        elif args.scheduler:
            run_scheduler_mode(adb, line_automation, messages_data, config)
        else:
            # Default: แสดง help
            logger.info("\n" + "="*70)
            logger.info("📋 Please choose a mode:")
            logger.info("="*70)
            logger.info("  --send-now    : Send messages immediately")
            logger.info("  --scheduler   : Run scheduler mode")
            logger.info("\nExample:")
            logger.info("  python main.py --send-now")
            logger.info("  python main.py --scheduler")
            logger.info("="*70)
        
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    finally:
        # Disconnect
        if 'adb' in locals():
            logger.info("\nDisconnecting from LDPlayer...")
            adb.disconnect()
        
        logger.info("\n" + "="*70)
        logger.info("👋 LINE LDPlayer Automation Finished")
        logger.info("="*70)


if __name__ == "__main__":
    main()
