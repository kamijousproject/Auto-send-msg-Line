# 📁 Project Structure

โครงสร้างโปรเจคและคำอธิบายแต่ละไฟล์

---

## 📂 Root Directory

```
line-ldplayer-automation/
├── 📄 main.py                      # Entry point หลัก - รันโปรแกรม
├── 📄 config.json                  # การตั้งค่า (paths, emulator, etc.)
├── 📄 messages.json                # ข้อความและตารางเวลา
├── 📄 requirements.txt             # Python dependencies
│
├── 📄 quick_start.bat              # สคริปต์เริ่มต้นง่ายๆ (Windows)
├── 📄 check_setup.py               # ตรวจสอบความพร้อม
│
├── 📄 demo_ldconsole.py            # Demo: ทดสอบ LDConsole
├── 📄 demo_full_automation.py      # Demo: ทดสอบส่งข้อความเต็มรูปแบบ
│
├── 📄 README.md                    # ภาพรวมโปรเจค
├── 📄 QUICKSTART.md                # คู่มือเริ่มต้นเร็ว (5 นาที)
├── 📄 SETUP_GUIDE.md               # คู่มือติดตั้งละเอียด + แก้ปัญหา
├── 📄 IMPROVEMENTS.md              # เทคนิคที่ใช้ (ldconsole vs OpenCV)
├── 📄 PROJECT_STRUCTURE.md         # ไฟล์นี้
│
├── 📄 .gitignore                   # Git ignore rules
│
├── 📁 modules/                     # Python modules
├── 📁 data/                        # Data และ logs
└── 📁 screenshots/                 # Screenshots (debug)
```

---

## 📂 modules/ - Python Modules

```
modules/
├── __init__.py                     # Module initialization
├── ldconsole_controller.py         # ควบคุม LDPlayer ผ่าน ldconsole.exe ⭐
├── adb_controller.py               # ควบคุม Android ผ่าน ADB
├── line_automation.py              # Automation สำหรับ LINE app
├── scheduler.py                    # Message scheduler
└── gui.py                          # GUI (future)
```

### 🔑 ไฟล์สำคัญ:

#### **ldconsole_controller.py** ⭐ (ใหม่!)
- ควบคุม LDPlayer ผ่าน `ldconsole.exe`
- เร็วกว่า ADB 2-3 เท่า
- ใช้สำหรับ:
  - เปิด/ปิด emulator
  - Run/Kill app
  - ตั้งค่า emulator
  
**Key Methods:**
```python
ldconsole.launch(name)              # เปิด emulator
ldconsole.run_app(name, package)    # เปิด app
ldconsole.kill_app(name, package)   # ปิด app
ldconsole.list_devices()            # ดูรายการ emulators
```

#### **adb_controller.py**
- ควบคุม Android ผ่าน ADB
- ใช้สำหรับ:
  - Tap, Swipe
  - Input text
  - Screenshot
  - Check app running

**Key Methods:**
```python
adb.connect()                       # เชื่อมต่อ
adb.tap(x, y)                       # แตะหน้าจอ
adb.swipe(x1, y1, x2, y2)          # ปัดหน้าจอ
adb.input_text(text)                # พิมพ์ข้อความ
adb.screenshot(path)                # ถ่ายภาพหน้าจอ
```

#### **line_automation.py**
- รวม ldconsole + adb เข้าด้วยกัน
- ควบคุม LINE app โดยเฉพาะ
- ใช้สำหรับ:
  - เปิด LINE
  - ไปแท็บเพื่อน
  - ส่งข้อความ

**Key Methods:**
```python
line.start_line()                   # เปิด LINE
line.go_to_friends_tab()            # ไปแท็บเพื่อน
line.send_to_first_n_friends(msg, n) # ส่งข้อความ
```

#### **scheduler.py**
- จัดการตารางเวลา
- ใช้ `schedule` library
- รันในพื้นหลัง (background thread)

**Key Methods:**
```python
scheduler.add_schedule(time, callback, days)
scheduler.start()                   # เริ่ม scheduler
scheduler.stop()                    # หยุด scheduler
```

---

## 📂 data/ - Data Files

```
data/
└── logs/
    ├── automation.log              # Log หลัก
    └── .gitkeep
```

**Logs:**
- เก็บทุกอย่างที่โปรแกรมทำ
- ใช้สำหรับ debug
- Rotate ทุก 10 MB (future)

---

## 📂 screenshots/ - Screenshots

```
screenshots/
├── error_*.png                     # Screenshots เมื่อเกิด error
└── .gitkeep
```

**ใช้เมื่อ:**
- `screenshot_on_error: true` ใน `config.json`
- เกิด error ขึ้น
- ถ่ายภาพหน้าจอเพื่อ debug

---

## 📄 Configuration Files

### config.json
```json
{
  "ldplayer": {
    "ldconsole_path": "...",        // Path to ldconsole.exe
    "adb_path": "...",              // Path to adb.exe
    "emulator_name": "...",         // Emulator name
    "adb_host": "127.0.0.1",
    "adb_port": 5555
  },
  "line": {
    "package_name": "...",          // LINE package name
    "activity_name": "...",         // LINE activity
    "wait_timeout": 10
  },
  "automation": {
    "target_friends_count": 3,      // จำนวนเพื่อนที่จะส่ง
    "message_delay_seconds": 2,     // หน่วงเวลาระหว่างส่ง
    "retry_attempts": 3,
    "screenshot_on_error": true
  },
  "scheduler": {
    "check_interval_seconds": 30,
    "timezone": "Asia/Bangkok"
  },
  "logging": {
    "level": "INFO",
    "log_to_file": true,
    "log_file": "data/logs/automation.log"
  }
}
```

### messages.json
```json
{
  "message_templates": [            // ชุดข้อความ
    {
      "id": 1,
      "name": "...",
      "content": "...",
      "enabled": true
    }
  ],
  "schedules": [                    // ตารางเวลา
    {
      "id": 1,
      "enabled": true,
      "time": "09:00",
      "days": ["monday", ...],
      "message_template_id": 1
    }
  ],
  "target_friends": {
    "mode": "first_n",              // วิธีเลือกเพื่อน
    "count": 3
  }
}
```

---

## 🎯 Entry Points

### main.py
**หลัก - ใช้งานจริง**

```bash
python main.py --send-now           # ส่งทันที
python main.py --scheduler          # รัน scheduler
python main.py --debug              # Debug mode
```

**Flow:**
1. Load config & messages
2. Initialize ldconsole (ถ้ามี)
3. Initialize adb
4. Initialize line_automation
5. เรียก function ตาม mode

---

### demo_ldconsole.py
**ทดสอบ LDConsole**

```bash
python demo_ldconsole.py
```

**ทำอะไร:**
- ตรวจสอบ emulators
- เปิด/ปิด emulator
- เปิด/ปิด LINE
- ตั้ง GPS

**ใช้เมื่อ:**
- ทดสอบว่า ldconsole.exe ใช้งานได้
- ดูรายชื่อ emulators
- ทดสอบการควบคุม

---

### demo_full_automation.py
**ทดสอบส่งข้อความ**

```bash
python demo_full_automation.py
```

**ทำอะไร:**
- เปิด emulator (ถ้ายังไม่เปิด)
- เชื่อมต่อ ADB
- เปิด LINE
- ส่งข้อความจริง

**ใช้เมื่อ:**
- ทดสอบก่อนใช้งานจริง
- ตรวจสอบว่าทุกอย่างทำงาน

---

### check_setup.py
**ตรวจสอบความพร้อม**

```bash
python check_setup.py
```

**เช็คอะไร:**
- ✅ Python version
- ✅ config.json
- ✅ LDPlayer paths
- ✅ Dependencies
- ✅ messages.json
- ✅ Folders
- ✅ LDPlayer connection

**ใช้เมื่อ:**
- ติดตั้งครั้งแรก
- เกิดปัญหา
- ก่อนใช้งานจริง

---

## 🔄 Workflow

### Send Now Mode:
```
main.py --send-now
    ↓
Initialize (ldconsole + adb + line_automation)
    ↓
Load messages from messages.json
    ↓
line_automation.send_to_first_n_friends()
    ├─ start_line()          (ldconsole.run_app หรือ adb.start_app)
    ├─ go_to_friends_tab()   (adb.tap)
    ├─ for each friend:
    │   ├─ tap friend        (adb.tap)
    │   ├─ tap input         (adb.tap)
    │   ├─ input message     (adb.input_text)
    │   ├─ tap send          (adb.tap)
    │   └─ back              (adb.press_key)
    └─ return results
    ↓
Show results
```

### Scheduler Mode:
```
main.py --scheduler
    ↓
Initialize (ldconsole + adb + line_automation)
    ↓
Load schedules from messages.json
    ↓
scheduler.add_schedule() for each schedule
    ↓
scheduler.start()
    ↓
[Running in background thread]
    ↓
When time matches:
    → Call send callback
    → line_automation.send_to_first_n_friends()
```

---

## 🛠️ Development

### เพิ่ม feature ใหม่:

1. **เพิ่ม module ใหม่:**
   - สร้างไฟล์ใน `modules/`
   - Import ใน `main.py`

2. **เพิ่ม config:**
   - แก้ `config.json`
   - อ่านใน code ด้วย `config.get()`

3. **เพิ่ม command:**
   - เพิ่ม argument ใน `main.py`
   - เพิ่ม function handler

4. **ทดสอบ:**
   - สร้าง `demo_*.py`
   - รัน `check_setup.py`

---

## 📚 Further Reading

- **README.md** - Overview
- **QUICKSTART.md** - Quick start (5 min)
- **SETUP_GUIDE.md** - Detailed setup + troubleshooting
- **IMPROVEMENTS.md** - Technical details

---

**สร้างโดย:** ตัวอย่างจาก AutoLDPlayer (C#) แปลงเป็น Python  
**License:** MIT
