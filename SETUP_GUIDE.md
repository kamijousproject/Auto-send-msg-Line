# 🚀 คู่มือการติดตั้งและใช้งาน

## 📋 ขั้นตอนการติดตั้ง

### 1. ติดตั้ง LDPlayer

1. ดาวน์โหลด LDPlayer จาก: https://www.ldplayer.net/
2. ติดตั้งและเปิดโปรแกรม
3. ตรวจสอบว่า ADB path ถูกต้องใน `config.json`:
   ```
   C:\LDPlayer\LDPlayer9\adb.exe
   ```

### 2. ติดตั้ง LINE ใน LDPlayer

1. เปิด LDPlayer
2. เปิด Play Store
3. ค้นหา "LINE"
4. ติดตั้ง LINE
5. Login เข้า LINE

### 3. ติดตั้ง Python Dependencies

```bash
# เปิด Command Prompt/PowerShell
cd "c:\xampp\htdocs\line chat bot\line-ldplayer-automation"

# สร้าง virtual environment (แนะนำ)
python -m venv venv

# เปิดใช้งาน
venv\Scripts\activate

# ติดตั้ง packages
pip install -r requirements.txt
```

### 4. ตรวจสอบ ADB Connection

```bash
# ตรวจสอบว่า LDPlayer รันอยู่
"C:\LDPlayer\LDPlayer9\adb.exe" devices

# ควรเห็น output คล้ายนี้:
# List of devices attached
# 127.0.0.1:5555   device
```

---

## ⚙️ การตั้งค่า

### 1. แก้ไข `config.json`

```json
{
  "ldplayer": {
    "adb_path": "C:\\LDPlayer\\LDPlayer9\\adb.exe",  // ← ปรับตาม path ที่ติดตั้ง
    "adb_host": "127.0.0.1",
    "adb_port": 5555  // ← ตรวจสอบจาก LDPlayer settings
  },
  "automation": {
    "target_friends_count": 3,  // ← จำนวนเพื่อนที่จะส่ง
    "message_delay_seconds": 2   // ← หน่วงเวลาระหว่างส่ง
  }
}
```

**วิธีหา ADB Port:**
1. เปิด LDPlayer
2. ไปที่ Settings → About
3. ดูที่ "ADB Debugging Port"

### 2. แก้ไข `messages.json`

```json
{
  "message_templates": [
    {
      "id": 1,
      "name": "สวัสดีตอนเช้า",
      "content": "สวัสดีครับ ☀️\nวันนี้สบายดีไหม",  // ← แก้ข้อความตรงนี้
      "enabled": true
    }
  ],
  "schedules": [
    {
      "id": 1,
      "enabled": true,
      "time": "09:00",  // ← แก้เวลาตรงนี้
      "days": ["monday", "tuesday", "wednesday", "thursday", "friday"],
      "message_template_id": 1
    }
  ]
}
```

---

## 🚀 การใช้งาน

### วิธีที่ 1: ส่งทันที (ทดสอบ)

```bash
python main.py --send-now
```

**จะทำอะไร:**
- เปิด LINE
- ไปแท็บเพื่อน
- ส่งข้อความหาเพื่อน 3 คนแรก
- เสร็จแล้วปิด

**ใช้เมื่อ:**
- ต้องการทดสอบ
- ต้องการส่งทันที

---

### วิธีที่ 2: รัน Scheduler (ส่งตามเวลา)

```bash
python main.py --scheduler
```

**จะทำอะไร:**
- รันอยู่เบื้องหลัง
- ตรวจสอบเวลาทุก 30 วินาที
- ถึงเวลาที่กำหนด = ส่งอัตโนมัติ
- กด Ctrl+C เพื่อหยุด

**ใช้เมื่อ:**
- ต้องการส่งตามตาราง
- ต้องการ automation เต็มรูปแบบ

---

### วิธีที่ 3: Debug Mode

```bash
python main.py --send-now --debug
```

แสดงข้อมูลละเอียดมากขึ้น (ใช้เมื่อมีปัญหา)

---

## 📊 ตัวอย่างการใช้งาน

### ตัวอย่างที่ 1: ส่งข้อความทันที

```bash
# 1. เปิด LDPlayer
# 2. รันคำสั่ง:
python main.py --send-now

# Output:
# ======================================================================
# LINE LDPlayer Automation Started
# ======================================================================
# Connecting to LDPlayer...
# ✅ Connected successfully!
# Starting LINE app...
# ✅ Navigated to Friends tab
# Sending to friend 1/3...
# ✅ Message sent: สวัสดีครับ ☀️...
# ✅ Completed! Success: 3/3
```

### ตัวอย่างที่ 2: รัน Scheduler

```bash
# 1. แก้ไข messages.json ตั้งเวลาเป็น 09:00
# 2. รันคำสั่ง:
python main.py --scheduler

# Output:
# ======================================================================
# ⏰ SCHEDULER MODE
# ======================================================================
# ✅ Schedule schedule_1_xxx: 09:00 - ส่งข้อความตอนเช้าวันธรรมดา
# ✅ Scheduler is running...
# 📝 Press Ctrl+C to stop
#
# (รอจนถึงเวลา 09:00)
# ⏰ Scheduled task triggered!
# 📝 Message: สวัสดีครับ ☀️...
# ✅ Sent to 3/3 friends
```

---

## 🐛 แก้ปัญหา

### ปัญหา: ADB ไม่พบ

```
❌ Failed to connect to LDPlayer!
```

**แก้:**
1. เช็คว่า LDPlayer เปิดอยู่
2. เช็ค `adb_path` ใน `config.json`
3. ลองรันด้วยตัวเอง:
   ```bash
   "C:\LDPlayer\LDPlayer9\adb.exe" devices
   ```

### ปัญหา: LINE ไม่เปิด

```
❌ Failed to start LINE
```

**แก้:**
1. เช็คว่าติดตั้ง LINE แล้ว
2. เช็คว่า Login แล้ว
3. เปิด LINE ด้วยตัวเองใน LDPlayer ก่อน

### ปัญหา: ส่งข้อความไม่ถูกที่

**แก้:**
1. ขนาดหน้าจอต่างจาก default (540x960)
2. แก้ไขตำแหน่งใน `line_automation.py`:
   ```python
   # ใน get_friend_positions()
   start_y = 300  # ← ปรับตามหน้าจอ
   spacing = 170  # ← ปรับระยะห่าง
   ```

### ปัญหา: ข้อความมี %s แทนช่องว่าง

**สาเหตุ:** ADB จำเป็นต้องแทนช่องว่าง

**แก้:** ใช้การขึ้นบรรทัดแทน:
```json
{
  "content": "สวัสดีครับ\nวันนี้สบายดีไหม"
}
```

---

## 💡 Tips

### 1. ทดสอบก่อนใช้จริง

```bash
# เปลี่ยนจำนวนเพื่อนเป็น 1
# แก้ไข config.json:
"target_friends_count": 1

# ทดสอบ
python main.py --send-now
```

### 2. ตั้งเวลาให้ถูกต้อง

- ใช้รูปแบบ 24 ชั่วโมง: "09:00", "14:30", "21:00"
- Timezone ใน `config.json` ต้องถูกต้อง

### 3. อย่าส่งบ่อยเกินไป

- ตั้ง `message_delay_seconds` อย่างน้อย 2 วินาที
- อย่าส่งซ้ำบ่อยๆ (อาจถูก LINE แบน)

### 4. เก็บ Log ไว้

Log จะถูกเก็บที่ `data/logs/automation.log`  
ใช้ตรวจสอบว่าโปรแกรมทำงานถูกต้อง

---

## 🎯 ขั้นตอนการใช้งาน (สรุป)

1. ✅ ติดตั้ง LDPlayer และ LINE
2. ✅ Login LINE
3. ✅ แก้ไข `config.json` (ADB path, port)
4. ✅ แก้ไข `messages.json` (ข้อความ, เวลา)
5. ✅ ทดสอบ: `python main.py --send-now`
6. ✅ ใช้งานจริง: `python main.py --scheduler`

---

## ⚠️ ข้อควรระวัง

- ⚠️ ใช้เพื่อการทดสอบเท่านั้น
- ⚠️ อย่าส่ง spam
- ⚠️ อย่าส่งข้อความที่ละเมิดกฎหมาย
- ⚠️ อาจถูก LINE แบนถ้าใช้ผิดวิธี
- ⚠️ ตรวจสอบว่าเพื่อนยินยอมรับข้อความ

---

**พร้อมแล้ว! ลองใช้งานได้เลย** 🚀
