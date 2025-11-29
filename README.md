# LINE LDPlayer Automation

โปรแกรม Python สำหรับควบคุม LDPlayer เพื่อส่งข้อความ LINE อัตโนมัติ

> 🚀 **Quick Start:** อ่าน [QUICKSTART.md](QUICKSTART.md) เพื่อเริ่มใช้งานใน 5 นาที!  
> 📖 **Setup Guide:** อ่าน [SETUP_GUIDE.md](SETUP_GUIDE.md) สำหรับคู่มือละเอียด  
> 💡 **Technical Details:** อ่าน [IMPROVEMENTS.md](IMPROVEMENTS.md) เพื่อเข้าใจเทคนิคที่ใช้

## ✨ ฟีเจอร์

- 🎨 **GUI แบบ Modern** - ใช้ Tkinter แบ่งเป็น 5 tabs ใช้งานง่าย
- 📱 ควบคุม LDPlayer ผ่าน ldconsole.exe และ ADB
- 💬 ส่งข้อความหาเพื่อน 3 คนแรก
- ⏰ ตั้งเวลาส่งข้อความ (Scheduler)
- 📝 จัดการชุดข้อความผ่าน GUI
- ⚙️ ตั้งค่าทั้งหมดผ่าน GUI
- 📊 Dashboard แสดงสถิติ
- 📝 ดู Logs แบบ real-time

## 📋 ความต้องการ

- Python 3.8+
- LDPlayer 4.x หรือ 9.x (Android Emulator)
- LINE app ติดตั้งและ login ใน LDPlayer
- ADB และ ldconsole.exe (มากับ LDPlayer อยู่แล้ว)

## ⚡ ข้อดี

- **ไม่ต้องใช้ OpenCV** - ใช้ ldconsole.exe และ ADB โดยตรง
- **ติดตั้งง่าย** - dependencies น้อยมาก (~10 MB)
- **เร็วกว่า** - ใช้ ldconsole สำหรับจัดการ app (เร็วกว่า ADB 2-3 เท่า)
- **เสถียร** - ใช้ official tools จาก LDPlayer

## 🔧 ติดตั้ง

```bash
# สร้าง virtual environment
python -m venv venv

# เปิดใช้งาน venv
venv\Scripts\activate  # Windows

# ติดตั้ง dependencies
pip install -r requirements.txt
```

## 🚀 การใช้งาน

### วิธีที่ 1: GUI Mode ⭐ (แนะนำ - ใช้งานง่ายที่สุด!)

```bash
# วิธีที่ 1: ใช้ Quick Start
quick_start.bat
# เลือก: 1 (เปิด GUI)

# วิธีที่ 2: รันตรงๆ
python gui.py
```

**GUI มี 5 tabs:**
- 📊 **Dashboard** - เชื่อมต่อ, ส่งทันที, ดูสถิติ
- 💬 **ข้อความ** - จัดการข้อความทั้งหมด
- ⏰ **ตั้งเวลา** - ตั้งตารางเวลาส่งอัตโนมัติ
- ⚙️ **ตั้งค่า** - ตั้งค่า LDPlayer, ADB, Automation
- 📝 **Logs** - ดู logs แบบ real-time

---

### วิธีที่ 2: Command Line Mode

```bash
# ส่งทันที
python main.py --send-now

# รัน Scheduler
python main.py --scheduler

# Debug mode
python main.py --send-now --debug
```

## 📁 โครงสร้างโปรเจค

```
line-ldplayer-automation/
├── main.py                 # Entry point
├── requirements.txt        # Dependencies
├── config.json            # Configuration
├── messages.json          # Message templates
├── README.md
├── modules/
│   ├── __init__.py
│   ├── adb_controller.py  # ADB wrapper
│   ├── line_automation.py # LINE automation
│   ├── scheduler.py       # Message scheduler
│   └── gui.py            # GUI (Tkinter)
├── data/
│   └── logs/             # Log files
└── screenshots/          # Screenshots (for debugging)
```

## ⚙️ Configuration

แก้ไข `config.json`:

```json
{
  "ldplayer_adb_port": 5555,
  "line_package": "jp.naver.line.android",
  "target_friends_count": 3,
  "message_delay": 2,
  "screenshot_on_error": true
}
```

## 📝 Message Templates

แก้ไข `messages.json`:

```json
{
  "messages": [
    "สวัสดีครับ",
    "สบายดีไหม",
    "วันนี้ทำอะไรอยู่"
  ],
  "schedule": [
    {
      "time": "09:00",
      "message_index": 0
    }
  ]
}
```

## 🐛 Debugging

เปิด debug mode:
```bash
python main.py --debug
```

## ⚠️ ข้อควรระวัง

- ตรวจสอบว่า LDPlayer เปิดอยู่
- ตรวจสอบว่า LINE login แล้ว
- อย่าส่งข้อความบ่อยเกินไป (อาจถูกแบน)
- ใช้เพื่อการทดสอบเท่านั้น

## 📄 License

MIT License
