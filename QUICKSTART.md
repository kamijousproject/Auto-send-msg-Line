# ⚡ Quick Start Guide

เริ่มใช้งานใน 5 นาที!

---

## 📋 ก่อนเริ่ม

ต้องมี:
- ✅ Python 3.8+ ติดตั้งแล้ว
- ✅ LDPlayer ติดตั้งและเปิดอยู่
- ✅ LINE app ติดตั้งและ login แล้วใน LDPlayer

---

## 🚀 ขั้นตอน (5 ขั้นตอน)

### 1️⃣ ติดตั้ง Dependencies

```bash
# เปิด Command Prompt/PowerShell
cd "c:\xampp\htdocs\line chat bot\line-ldplayer-automation"

# ติดตั้ง (ไม่ต้อง venv ก็ได้)
pip install -r requirements.txt
```

**ใช้เวลา:** ~30 วินาที

---

### 2️⃣ แก้ไข config.json

เปิดไฟล์ `config.json` แล้วแก้:

```json
{
  "ldplayer": {
    "ldconsole_path": "C:\\LDPlayer\\LDPlayer9\\ldconsole.exe",  // ← ตรวจสอบ path
    "adb_path": "C:\\LDPlayer\\LDPlayer9\\adb.exe",             // ← ตรวจสอบ path
    "emulator_name": "LDPlayer"  // ← ชื่อ emulator (ดูได้จาก LDPlayer)
  }
}
```

**Tips:** 
- ถ้าใช้ LDPlayer 4.x → path จะเป็น `LDPlayer4.0`
- ชื่อ emulator ดูได้จากหน้าต่าง LDPlayer

---

### 3️⃣ แก้ไข messages.json

```json
{
  "message_templates": [
    {
      "content": "สวัสดีครับ\nวันนี้สบายดีไหม",  // ← แก้ข้อความตรงนี้
      "enabled": true
    }
  ]
}
```

---

### 4️⃣ ตรวจสอบความพร้อม

```bash
python check_setup.py
```

**ควรเห็น:**
```
✅ Everything looks good!
🚀 Ready to use
```

---

### 5️⃣ ทดสอบ!

**วิธีที่ 1: ใช้ GUI ⭐ (ง่ายที่สุด!)**
```bash
# วิธีที่ 1: ใช้ Quick Start
quick_start.bat
# เลือก: 1 (เปิด GUI)

# วิธีที่ 2: รันตรงๆ
python gui.py
```

**GUI มี 5 tabs:**
- 📊 Dashboard - เชื่อมต่อ, ส่งทันที
- 💬 ข้อความ - จัดการข้อความ
- ⏰ ตั้งเวลา - ตั้งตารางส่งอัตโนมัติ
- ⚙️ ตั้งค่า - ตั้งค่าทั้งหมด
- 📝 Logs - ดู logs

> 📖 อ่านคู่มือ GUI ละเอียดที่ [GUI_GUIDE.md](GUI_GUIDE.md)

---

**วิธีที่ 2: Command Line**
```bash
# ทดสอบ LDConsole
python demo_ldconsole.py

# ทดสอบส่งข้อความ (ทั้งหมด)
python demo_full_automation.py

# ส่งข้อความจริง
python main.py --send-now
```

---

## 📊 เมนูใน quick_start.bat

```
1. ตรวจสอบความพร้อม      ⭐ รันก่อนทุกครั้ง
2. ทดสอบ LDConsole        🔧 ทดสอบการควบคุม emulator
3. ทดสอบส่งข้อความ        📱 ทดสอบส่งข้อความจริง (ระวัง!)
4. ส่งข้อความทันที         💬 ใช้งานจริง
5. รัน Scheduler          ⏰ ส่งตามเวลา
6. ทดสอบ ADB             🔌 ทดสอบ connection
7. ออก
```

---

## ⚠️ ถ้าเจอปัญหา

### ❌ "ldconsole.exe not found"

**แก้:**
1. เช็ค path ใน `config.json`
2. เปิด File Explorer ไปที่ `C:\LDPlayer\LDPlayer9\`
3. ตรวจสอบว่ามี `ldconsole.exe` จริง
4. ถ้าไม่มี → อาจเป็น `LDPlayer4.0` แทน

### ❌ "Failed to connect to ADB"

**แก้:**
1. ตรวจสอบว่า LDPlayer เปิดอยู่
2. รอ 5-10 วินาทีหลังเปิด LDPlayer
3. ลองรัน: `"C:\LDPlayer\LDPlayer9\adb.exe" devices`
4. ควรเห็น `127.0.0.1:5555   device`

### ❌ "LINE is not installed"

**แก้:**
1. เปิด LDPlayer
2. เปิด Play Store
3. ติดตั้ง LINE
4. Login เข้า LINE

### ❌ ส่งข้อความไม่ถูกที่

**แก้:**
1. หน้าจอ emulator อาจต่างจาก default
2. แก้ไข `line_automation.py` ปรับตำแหน่ง
3. หรือเปลี่ยนขนาดหน้าจอ emulator ให้เป็น 540x960

---

## 💡 Tips

### ทดสอบปลอดภัย:
1. ตั้งจำนวนเพื่อนเป็น `1` ใน `config.json`
2. ทดสอบส่งให้ตัวเองก่อน (Saved Messages)
3. ตรวจสอบว่าข้อความส่งถูกต้อง
4. ค่อยเพิ่มจำนวนเพื่อน

### ปรับความเร็ว:
```json
{
  "automation": {
    "message_delay_seconds": 3  // ← เพิ่มเวลารอระหว่างส่ง
  }
}
```

### ใช้ Scheduler:
1. แก้ไข `messages.json` ตั้งเวลา
2. รัน `python main.py --scheduler`
3. ทิ้งไว้รันเบื้องหลัง
4. กด Ctrl+C เพื่อหยุด

---

## 🎯 ลำดับการใช้งานแนะนำ

```
1. python check_setup.py           # ✅ ตรวจสอบ
2. python demo_ldconsole.py        # 🔧 ทดสอบ LDConsole
3. python demo_full_automation.py  # 📱 ทดสอบส่งข้อความ
4. python main.py --send-now       # 💬 ใช้งานจริง
5. python main.py --scheduler      # ⏰ Auto send
```

---

## 📚 เอกสารเพิ่มเติม

- **README.md** - ภาพรวมโปรเจค
- **SETUP_GUIDE.md** - คู่มือติดตั้งละเอียด + แก้ปัญหา
- **IMPROVEMENTS.md** - เทคนิคที่ใช้ (ldconsole vs ADB vs OpenCV)

---

## 🆘 ขอความช่วยเหลือ

ถ้าติดปัญหา:
1. รัน `python check_setup.py` ดูว่าผิดตรงไหน
2. อ่าน error message ให้ดี
3. ดู `SETUP_GUIDE.md` ส่วน "แก้ปัญหา"
4. ตรวจสอบ log ที่ `data/logs/automation.log`

---

**พร้อมแล้ว! ลองใช้งานได้เลย** 🚀

```bash
quick_start.bat
```
