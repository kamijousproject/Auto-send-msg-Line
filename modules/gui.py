"""
GUI สำหรับ LINE LDPlayer Automation
ใช้ Tkinter + ttk สำหรับ modern look
"""
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog, simpledialog
import json
import os
import threading
import logging
from datetime import datetime
from typing import Optional, Dict, List

logger = logging.getLogger(__name__)


class ModernGUI:
    """GUI หลัก - ใช้ ttk.Notebook สำหรับ tabs"""
    
    def __init__(self, config_path="config.json", messages_path="messages.json"):
        """
        Args:
            config_path: path to config.json
            messages_path: path to messages.json
        """
        self.config_path = config_path
        self.messages_path = messages_path
        
        # Load config
        self.config = self.load_config()
        self.messages_data = self.load_messages()
        
        # Controllers (จะ initialize ภายหลัง)
        self.ldconsole = None
        self.adb = None
        self.line_automation = None
        self.scheduler = None
        
        # State
        self.is_connected = False
        self.scheduler_running = False
        
        # สร้าง GUI
        self.create_gui()
    
    def load_config(self) -> dict:
        """Load configuration"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load config: {e}")
            return {}
    
    def load_messages(self) -> dict:
        """Load messages"""
        try:
            with open(self.messages_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load messages: {e}")
            return {"message_templates": [], "schedules": []}
    
    def save_config(self):
        """Save configuration"""
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            self.log("✅ Config saved")
        except Exception as e:
            self.log(f"❌ Failed to save config: {e}")
    
    def save_messages(self):
        """Save messages"""
        try:
            with open(self.messages_path, 'w', encoding='utf-8') as f:
                json.dump(self.messages_data, f, indent=2, ensure_ascii=False)
            self.log("✅ Messages saved")
        except Exception as e:
            self.log(f"❌ Failed to save messages: {e}")
    
    def create_gui(self):
        """สร้าง GUI หลัก"""
        self.root = tk.Tk()
        self.root.title("LINE LDPlayer Automation 🤖")
        self.root.geometry("900x700")
        
        # Style
        style = ttk.Style()
        style.theme_use('clam')  # Modern theme
        
        # สี
        self.colors = {
            'primary': '#2563eb',
            'success': '#10b981',
            'warning': '#f59e0b',
            'danger': '#ef4444',
            'bg': '#f9fafb',
            'card': '#ffffff'
        }
        
        # Main container
        main_container = ttk.Frame(self.root)
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Header
        self.create_header(main_container)
        
        # Tabs
        self.create_tabs(main_container)
        
        # Status bar
        self.create_status_bar(main_container)
    
    def create_header(self, parent):
        """สร้าง Header"""
        header = ttk.Frame(parent)
        header.pack(fill=tk.X, pady=(0, 10))
        
        # Title
        title_label = ttk.Label(
            header,
            text="🤖 LINE LDPlayer Automation",
            font=('Arial', 16, 'bold')
        )
        title_label.pack(side=tk.LEFT)
        
        # Connection status
        self.status_label = ttk.Label(
            header,
            text="⚪ ไม่ได้เชื่อมต่อ",
            font=('Arial', 10)
        )
        self.status_label.pack(side=tk.RIGHT)
    
    def create_tabs(self, parent):
        """สร้าง Tabs"""
        # Notebook (tabs container)
        self.notebook = ttk.Notebook(parent)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Tab 1: Dashboard
        self.tab_dashboard = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_dashboard, text="📊 Dashboard")
        self.create_dashboard_tab()
        
        # Tab 2: LDPlayer Management (ใหม่!)
        self.tab_ldplayer = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_ldplayer, text="🎮 จัดการ LD")
        self.create_ldplayer_tab()
        
        # Tab 3: Messages
        self.tab_messages = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_messages, text="💬 ข้อความ")
        self.create_messages_tab()
        
        # Tab 4: Scheduler
        self.tab_scheduler = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_scheduler, text="⏰ ตั้งเวลา")
        self.create_scheduler_tab()
        
        # Tab 5: Settings
        self.tab_settings = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_settings, text="⚙️ ตั้งค่า")
        self.create_settings_tab()
        
        # Tab 6: Logs
        self.tab_logs = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_logs, text="📝 Logs")
        self.create_logs_tab()
    
    def create_ldplayer_tab(self):
        """Tab: LDPlayer Management (Multi-Account)"""
        
        # Top toolbar
        toolbar = ttk.Frame(self.tab_ldplayer)
        toolbar.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(
            toolbar,
            text="🔄 รีเฟรชรายการ",
            command=self.refresh_ld_list,
            width=20
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            toolbar,
            text="➕ สร้าง LD ใหม่",
            command=self.create_new_ld,
            width=20
        ).pack(side=tk.LEFT, padx=5)
        
        # Main content (split into 2 parts)
        main_paned = ttk.PanedWindow(self.tab_ldplayer, orient=tk.HORIZONTAL)
        main_paned.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Left: LD List
        left_frame = ttk.LabelFrame(main_paned, text="📱 รายการ LDPlayer", padding=10)
        main_paned.add(left_frame, weight=1)
        
        # Treeview for LD list
        columns = ('index', 'name', 'status', 'pid', 'adb')
        self.ld_tree = ttk.Treeview(left_frame, columns=columns, show='headings', height=15)
        
        self.ld_tree.heading('index', text='Index')
        self.ld_tree.heading('name', text='ชื่อ')
        self.ld_tree.heading('status', text='สถานะ')
        self.ld_tree.heading('pid', text='PID')
        self.ld_tree.heading('adb', text='ADB Address')
        
        self.ld_tree.column('index', width=50)
        self.ld_tree.column('name', width=150)
        self.ld_tree.column('status', width=100)
        self.ld_tree.column('pid', width=80)
        self.ld_tree.column('adb', width=150)
        
        self.ld_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Scrollbar
        ld_scrollbar = ttk.Scrollbar(left_frame, orient=tk.VERTICAL, command=self.ld_tree.yview)
        ld_scrollbar.pack(side=tk.LEFT, fill=tk.Y)
        self.ld_tree.config(yscrollcommand=ld_scrollbar.set)
        
        # Bind selection
        self.ld_tree.bind('<<TreeviewSelect>>', self.on_ld_select)
        
        # Right: Control Panel
        right_frame = ttk.LabelFrame(main_paned, text="🎮 ควบคุม", padding=10)
        main_paned.add(right_frame, weight=1)
        
        # Selected LD info
        info_frame = ttk.LabelFrame(right_frame, text="ℹ️ ข้อมูล LD ที่เลือก", padding=10)
        info_frame.pack(fill=tk.X, pady=10)
        
        self.selected_ld_label = ttk.Label(info_frame, text="ยังไม่ได้เลือก", font=('Arial', 10, 'bold'))
        self.selected_ld_label.pack()
        
        # LD Control buttons
        control_frame = ttk.LabelFrame(right_frame, text="⚙️ ควบคุม LD", padding=10)
        control_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(
            control_frame,
            text="🚀 เปิด",
            command=self.launch_selected_ld,
            width=25
        ).pack(pady=5)
        
        ttk.Button(
            control_frame,
            text="⏹️ ปิด",
            command=self.close_selected_ld,
            width=25
        ).pack(pady=5)
        
        ttk.Button(
            control_frame,
            text="🔄 รีบูต",
            command=self.reboot_selected_ld,
            width=25
        ).pack(pady=5)
        
        ttk.Button(
            control_frame,
            text="🗑️ ลบ",
            command=self.delete_selected_ld,
            width=25
        ).pack(pady=5)
        
        # Message sending
        msg_frame = ttk.LabelFrame(right_frame, text="💬 ส่งข้อความ", padding=10)
        msg_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        ttk.Label(msg_frame, text="เลือกข้อความ:").pack(anchor=tk.W, pady=5)
        
        self.ld_msg_var = tk.StringVar()
        self.ld_msg_combo = ttk.Combobox(msg_frame, textvariable=self.ld_msg_var, width=35)
        self.ld_msg_combo.pack(fill=tk.X, pady=5)
        
        ttk.Label(msg_frame, text="จำนวนเพื่อน:").pack(anchor=tk.W, pady=5)
        self.ld_friend_count_spinbox = ttk.Spinbox(msg_frame, from_=1, to=10, width=10)
        self.ld_friend_count_spinbox.set(3)
        self.ld_friend_count_spinbox.pack(anchor=tk.W, pady=5)
        
        ttk.Button(
            msg_frame,
            text="📤 ส่งข้อความ (LD นี้)",
            command=self.send_message_selected_ld,
            width=25
        ).pack(pady=10)
        
        ttk.Button(
            msg_frame,
            text="📤 ส่งข้อความ (ทุก LD ที่เปิดอยู่)",
            command=self.send_message_all_running_ld,
            width=25
        ).pack(pady=5)
        
        # Auto refresh LD list
        self.refresh_ld_list()
    
    def create_dashboard_tab(self):
        """Tab: Dashboard"""
        # Connection card
        conn_frame = ttk.LabelFrame(self.tab_dashboard, text="🔌 การเชื่อมต่อ", padding=10)
        conn_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Row 1: LDPlayer control
        ld_control_frame = ttk.Frame(conn_frame)
        ld_control_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(
            ld_control_frame,
            text="🚀 เปิด LDPlayer",
            command=self.launch_ldplayer,
            width=20
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            ld_control_frame,
            text="⏹️ ปิด LDPlayer",
            command=self.close_ldplayer,
            width=20
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            ld_control_frame,
            text="🔄 ตรวจสอบสถานะ",
            command=self.check_emulator_status,
            width=20
        ).pack(side=tk.LEFT, padx=5)
        
        # Row 2: Connection
        conn_control_frame = ttk.Frame(conn_frame)
        conn_control_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(
            conn_control_frame,
            text="🔌 เชื่อมต่อ ADB",
            command=self.connect_ldplayer,
            width=20
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            conn_control_frame,
            text="🔌 ตัดการเชื่อมต่อ",
            command=self.disconnect_ldplayer,
            width=20
        ).pack(side=tk.LEFT, padx=5)
        
        # Quick actions
        actions_frame = ttk.LabelFrame(self.tab_dashboard, text="⚡ การทำงานด่วน", padding=10)
        actions_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(
            actions_frame,
            text="📤 ส่งข้อความทันที",
            command=self.send_now,
            width=25
        ).pack(pady=5)
        
        ttk.Button(
            actions_frame,
            text="🔍 ตรวจสอบความพร้อม",
            command=self.check_setup,
            width=25
        ).pack(pady=5)
        
        ttk.Button(
            actions_frame,
            text="🧪 ทดสอบ LDConsole",
            command=self.test_ldconsole,
            width=25
        ).pack(pady=5)
        
        # Stats
        stats_frame = ttk.LabelFrame(self.tab_dashboard, text="📊 สถิติ", padding=10)
        stats_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.stats_text = scrolledtext.ScrolledText(
            stats_frame,
            height=10,
            font=('Courier', 10)
        )
        self.stats_text.pack(fill=tk.BOTH, expand=True)
        self.update_stats()
    
    def create_messages_tab(self):
        """Tab: Messages Management"""
        # List frame
        list_frame = ttk.LabelFrame(self.tab_messages, text="📝 ข้อความทั้งหมด", padding=10)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Listbox
        self.messages_listbox = tk.Listbox(list_frame, height=10, font=('Arial', 10))
        self.messages_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.messages_listbox.bind('<<ListboxSelect>>', self.on_message_select)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.messages_listbox.yview)
        scrollbar.pack(side=tk.LEFT, fill=tk.Y)
        self.messages_listbox.config(yscrollcommand=scrollbar.set)
        
        # Details frame
        details_frame = ttk.LabelFrame(self.tab_messages, text="✏️ รายละเอียด", padding=10)
        details_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Name
        ttk.Label(details_frame, text="ชื่อ:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.msg_name_entry = ttk.Entry(details_frame, width=40)
        self.msg_name_entry.grid(row=0, column=1, pady=5, padx=5)
        
        # Content
        ttk.Label(details_frame, text="ข้อความ:").grid(row=1, column=0, sticky=tk.NW, pady=5)
        self.msg_content_text = scrolledtext.ScrolledText(details_frame, height=5, width=40)
        self.msg_content_text.grid(row=1, column=1, pady=5, padx=5)
        
        # Enabled
        self.msg_enabled_var = tk.BooleanVar()
        ttk.Checkbutton(
            details_frame,
            text="เปิดใช้งาน",
            variable=self.msg_enabled_var
        ).grid(row=2, column=1, sticky=tk.W, pady=5)
        
        # Buttons
        btn_frame = ttk.Frame(details_frame)
        btn_frame.grid(row=3, column=1, pady=10)
        
        ttk.Button(btn_frame, text="➕ เพิ่มใหม่", command=self.add_message).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="💾 บันทึก", command=self.save_message).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="🗑️ ลบ", command=self.delete_message).pack(side=tk.LEFT, padx=5)
        
        # Load messages
        self.refresh_messages_list()
    
    def create_scheduler_tab(self):
        """Tab: Scheduler"""
        # List frame
        list_frame = ttk.LabelFrame(self.tab_scheduler, text="📅 ตารางเวลา", padding=10)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Listbox
        self.schedules_listbox = tk.Listbox(list_frame, height=10, font=('Arial', 10))
        self.schedules_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.schedules_listbox.bind('<<ListboxSelect>>', self.on_schedule_select)
        
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.schedules_listbox.yview)
        scrollbar.pack(side=tk.LEFT, fill=tk.Y)
        self.schedules_listbox.config(yscrollcommand=scrollbar.set)
        
        # Details frame
        details_frame = ttk.LabelFrame(self.tab_scheduler, text="✏️ รายละเอียด", padding=10)
        details_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Time
        ttk.Label(details_frame, text="เวลา (HH:MM):").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.sch_time_entry = ttk.Entry(details_frame, width=20)
        self.sch_time_entry.grid(row=0, column=1, pady=5, padx=5, sticky=tk.W)
        
        # Message template
        ttk.Label(details_frame, text="ข้อความ:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.sch_msg_var = tk.StringVar()
        self.sch_msg_combo = ttk.Combobox(details_frame, textvariable=self.sch_msg_var, width=40)
        self.sch_msg_combo.grid(row=1, column=1, pady=5, padx=5, sticky=tk.W)
        
        # Days
        ttk.Label(details_frame, text="วัน:").grid(row=2, column=0, sticky=tk.NW, pady=5)
        days_frame = ttk.Frame(details_frame)
        days_frame.grid(row=2, column=1, pady=5, padx=5, sticky=tk.W)
        
        self.days_vars = {}
        days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
        days_thai = ['จันทร์', 'อังคาร', 'พุธ', 'พฤหัส', 'ศุกร์', 'เสาร์', 'อาทิตย์']
        
        for i, (day, day_thai) in enumerate(zip(days, days_thai)):
            var = tk.BooleanVar()
            self.days_vars[day] = var
            ttk.Checkbutton(days_frame, text=day_thai, variable=var).grid(
                row=i//4, column=i%4, sticky=tk.W, padx=5
            )
        
        # Enabled
        self.sch_enabled_var = tk.BooleanVar()
        ttk.Checkbutton(
            details_frame,
            text="เปิดใช้งาน",
            variable=self.sch_enabled_var
        ).grid(row=3, column=1, sticky=tk.W, pady=5)
        
        # Buttons
        btn_frame = ttk.Frame(details_frame)
        btn_frame.grid(row=4, column=1, pady=10)
        
        ttk.Button(btn_frame, text="➕ เพิ่มใหม่", command=self.add_schedule).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="💾 บันทึก", command=self.save_schedule).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="🗑️ ลบ", command=self.delete_schedule).pack(side=tk.LEFT, padx=5)
        
        # Control buttons
        control_frame = ttk.LabelFrame(self.tab_scheduler, text="🎮 ควบคุม", padding=10)
        control_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(
            control_frame,
            text="▶️ เริ่ม Scheduler",
            command=self.start_scheduler,
            width=20
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            control_frame,
            text="⏹️ หยุด Scheduler",
            command=self.stop_scheduler,
            width=20
        ).pack(side=tk.LEFT, padx=5)
        
        self.refresh_schedules_list()
        self.refresh_message_combo()
    
    def create_settings_tab(self):
        """Tab: Settings"""
        settings_frame = ttk.Frame(self.tab_settings, padding=10)
        settings_frame.pack(fill=tk.BOTH, expand=True)
        
        # LDPlayer settings
        ld_frame = ttk.LabelFrame(settings_frame, text="🎮 LDPlayer", padding=10)
        ld_frame.pack(fill=tk.X, pady=10)
        
        # LDConsole path
        ttk.Label(ld_frame, text="ldconsole.exe:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.ldconsole_path_entry = ttk.Entry(ld_frame, width=50)
        self.ldconsole_path_entry.grid(row=0, column=1, pady=5, padx=5)
        ttk.Button(ld_frame, text="📁", command=lambda: self.browse_file('ldconsole')).grid(row=0, column=2)
        
        # ADB path
        ttk.Label(ld_frame, text="adb.exe:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.adb_path_entry = ttk.Entry(ld_frame, width=50)
        self.adb_path_entry.grid(row=1, column=1, pady=5, padx=5)
        ttk.Button(ld_frame, text="📁", command=lambda: self.browse_file('adb')).grid(row=1, column=2)
        
        # Emulator name
        ttk.Label(ld_frame, text="Emulator:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.emulator_name_entry = ttk.Entry(ld_frame, width=50)
        self.emulator_name_entry.grid(row=2, column=1, pady=5, padx=5)
        
        # Automation settings
        auto_frame = ttk.LabelFrame(settings_frame, text="🤖 Automation", padding=10)
        auto_frame.pack(fill=tk.X, pady=10)
        
        # Target friends count
        ttk.Label(auto_frame, text="จำนวนเพื่อน:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.target_friends_spinbox = ttk.Spinbox(auto_frame, from_=1, to=10, width=10)
        self.target_friends_spinbox.grid(row=0, column=1, pady=5, padx=5, sticky=tk.W)
        
        # Message delay
        ttk.Label(auto_frame, text="หน่วงเวลา (วินาที):").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.message_delay_spinbox = ttk.Spinbox(auto_frame, from_=1, to=10, width=10)
        self.message_delay_spinbox.grid(row=1, column=1, pady=5, padx=5, sticky=tk.W)
        
        # Buttons
        btn_frame = ttk.Frame(settings_frame)
        btn_frame.pack(pady=20)
        
        ttk.Button(btn_frame, text="💾 บันทึกการตั้งค่า", command=self.save_settings).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="🔄 โหลดค่าเดิม", command=self.load_settings).pack(side=tk.LEFT, padx=5)
        
        # Load current settings
        self.load_settings()
    
    def create_logs_tab(self):
        """Tab: Logs"""
        # Log viewer
        self.log_text = scrolledtext.ScrolledText(
            self.tab_logs,
            font=('Courier', 9),
            bg='#1e1e1e',
            fg='#d4d4d4'
        )
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Buttons
        btn_frame = ttk.Frame(self.tab_logs)
        btn_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        ttk.Button(btn_frame, text="🔄 รีเฟรช", command=self.refresh_logs).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="🗑️ ล้าง", command=self.clear_logs).pack(side=tk.LEFT, padx=5)
    
    def create_status_bar(self, parent):
        """สร้าง Status bar"""
        self.status_bar = ttk.Label(
            parent,
            text="พร้อมใช้งาน",
            relief=tk.SUNKEN,
            anchor=tk.W
        )
        self.status_bar.pack(fill=tk.X, pady=(10, 0))
    
    # ========== Helper Methods ==========
    
    def log(self, message: str):
        """เพิ่มข้อความใน log"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_message = f"[{timestamp}] {message}\n"
        
        # เช็คว่า log_text ถูกสร้างแล้วหรือยัง
        if hasattr(self, 'log_text'):
            self.log_text.insert(tk.END, log_message)
            self.log_text.see(tk.END)
        
        # เช็คว่า status_bar ถูกสร้างแล้วหรือยัง
        if hasattr(self, 'status_bar'):
            self.status_bar.config(text=message)
        
        # Print to console as fallback
        print(log_message.strip())
    
    def update_stats(self):
        """อัพเดทสถิติ"""
        stats = f"""
📊 สถิติระบบ
{'='*50}

💬 ข้อความ:
   • ทั้งหมด: {len(self.messages_data.get('message_templates', []))} ข้อความ
   • เปิดใช้งาน: {len([m for m in self.messages_data.get('message_templates', []) if m.get('enabled', True)])} ข้อความ

⏰ ตารางเวลา:
   • ทั้งหมด: {len(self.messages_data.get('schedules', []))} ตาราง
   • เปิดใช้งาน: {len([s for s in self.messages_data.get('schedules', []) if s.get('enabled', True)])} ตาราง

🎮 LDPlayer:
   • สถานะ: {'🟢 เชื่อมต่อแล้ว' if self.is_connected else '⚪ ไม่ได้เชื่อมต่อ'}
   • Scheduler: {'🟢 กำลังทำงาน' if self.scheduler_running else '⚪ หยุด'}

{'='*50}
        """
        
        # เช็คว่า stats_text ถูกสร้างแล้วหรือยัง
        if hasattr(self, 'stats_text'):
            self.stats_text.delete('1.0', tk.END)
            self.stats_text.insert('1.0', stats)
    
    def refresh_messages_list(self):
        """รีเฟรชรายการข้อความ"""
        if not hasattr(self, 'messages_listbox'):
            return
        
        self.messages_listbox.delete(0, tk.END)
        
        for msg in self.messages_data.get('message_templates', []):
            status = "✅" if msg.get('enabled', True) else "⭕"
            self.messages_listbox.insert(
                tk.END,
                f"{status} {msg.get('name', 'ไม่มีชื่อ')}"
            )
    
    def refresh_schedules_list(self):
        """รีเฟรชรายการตารางเวลา"""
        if not hasattr(self, 'schedules_listbox'):
            return
        
        self.schedules_listbox.delete(0, tk.END)
        
        for sch in self.messages_data.get('schedules', []):
            status = "✅" if sch.get('enabled', True) else "⭕"
            self.schedules_listbox.insert(
                tk.END,
                f"{status} {sch.get('time', '??:??')} - {sch.get('description', 'ไม่มีคำอธิบาย')}"
            )
    
    def refresh_message_combo(self):
        """รีเฟรช combobox ข้อความ"""
        if not hasattr(self, 'sch_msg_combo'):
            return
        
        messages = self.messages_data.get('message_templates', [])
        values = [f"{m.get('id')}: {m.get('name')}" for m in messages]
        self.sch_msg_combo['values'] = values
        
        # Refresh LD message combo too
        if hasattr(self, 'ld_msg_combo'):
            self.ld_msg_combo['values'] = values
    
    def refresh_ld_list(self):
        """รีเฟรชรายการ LDPlayer"""
        if not hasattr(self, 'ld_tree'):
            return
        
        def refresh():
            try:
                from modules.ldconsole_controller import LDConsoleController
                
                ldconsole_path = self.config.get('ldplayer', {}).get('ldconsole_path')
                
                if not ldconsole_path:
                    self.log("❌ ไม่พบ ldconsole_path ใน config")
                    return
                
                ldconsole = LDConsoleController(ldconsole_path)
                
                # ดูรายการทั้งหมด
                devices = ldconsole.list_devices()
                
                # สร้าง ADB address map (port = 5555 + index)
                adb_map = {}
                for device in devices:
                    idx = device['index']
                    adb_port = 5555 + int(idx)
                    adb_map[idx] = f"127.0.0.1:{adb_port}"
                
                # Clear tree
                for item in self.ld_tree.get_children():
                    self.ld_tree.delete(item)
                
                # Add items
                for device in devices:
                    status = "🟢 Running" if device['running'] else "⚪ Stopped"
                    adb_addr = adb_map.get(device['index'], '-')
                    
                    self.ld_tree.insert('', tk.END, values=(
                        device['index'],
                        device['name'],
                        status,
                        device['pid'],
                        adb_addr
                    ))
                
                self.log(f"✅ รีเฟรชรายการ LD แล้ว ({len(devices)} ตัว)")
                
            except Exception as e:
                self.log(f"❌ Error refreshing LD list: {e}")
        
        threading.Thread(target=refresh, daemon=True).start()
    
    # ========== Event Handlers ==========
    
    def on_message_select(self, event):
        """เมื่อเลือกข้อความ"""
        selection = self.messages_listbox.curselection()
        if not selection:
            return
        
        idx = selection[0]
        messages = self.messages_data.get('message_templates', [])
        
        if idx < len(messages):
            msg = messages[idx]
            self.msg_name_entry.delete(0, tk.END)
            self.msg_name_entry.insert(0, msg.get('name', ''))
            
            self.msg_content_text.delete('1.0', tk.END)
            self.msg_content_text.insert('1.0', msg.get('content', ''))
            
            self.msg_enabled_var.set(msg.get('enabled', True))
    
    def on_schedule_select(self, event):
        """เมื่อเลือกตารางเวลา"""
        selection = self.schedules_listbox.curselection()
        if not selection:
            return
        
        idx = selection[0]
        schedules = self.messages_data.get('schedules', [])
        
        if idx < len(schedules):
            sch = schedules[idx]
            
            self.sch_time_entry.delete(0, tk.END)
            self.sch_time_entry.insert(0, sch.get('time', ''))
            
            # Set message
            msg_id = sch.get('message_template_id')
            messages = self.messages_data.get('message_templates', [])
            for msg in messages:
                if msg.get('id') == msg_id:
                    self.sch_msg_var.set(f"{msg.get('id')}: {msg.get('name')}")
                    break
            
            # Set days
            days = sch.get('days', [])
            for day, var in self.days_vars.items():
                var.set(day in days)
            
            self.sch_enabled_var.set(sch.get('enabled', True))
    
    # ========== Actions ==========
    
    def launch_ldplayer(self):
        """เปิด LDPlayer emulator"""
        self.log("🚀 กำลังเปิด LDPlayer...")
        
        def launch():
            try:
                from modules.ldconsole_controller import LDConsoleController
                
                ldconsole_path = self.config.get('ldplayer', {}).get('ldconsole_path')
                emulator_name = self.config.get('ldplayer', {}).get('emulator_name', '0')
                
                if not ldconsole_path:
                    self.log("❌ ไม่พบ ldconsole_path ใน config")
                    messagebox.showerror("Error", "กรุณาตั้งค่า ldconsole_path ใน Tab: ตั้งค่า")
                    return
                
                ldconsole = LDConsoleController(ldconsole_path)
                
                # แปลง emulator_name เป็น string (กรณีเป็น int)
                emulator_name = str(emulator_name)
                
                # เช็คว่าเปิดอยู่หรือยัง
                if ldconsole.is_running(emulator_name):
                    self.log("ℹ️ LDPlayer เปิดอยู่แล้ว")
                    messagebox.showinfo("Info", "LDPlayer เปิดอยู่แล้ว")
                    return
                
                # เปิด emulator
                if ldconsole.launch(emulator_name):
                    self.log("✅ เปิด LDPlayer แล้ว")
                    self.log("⏳ กำลัง boot... (รอ 15 วินาที)")
                    messagebox.showinfo("Success", "เปิด LDPlayer แล้ว\nกรุณารอให้ boot เสร็จ (~15 วินาที)")
                else:
                    self.log("❌ ไม่สามารถเปิด LDPlayer ได้")
                    messagebox.showerror("Error", "ไม่สามารถเปิด LDPlayer ได้")
                    
            except Exception as e:
                self.log(f"❌ Error: {e}")
                messagebox.showerror("Error", f"เปิด LDPlayer ล้มเหลว:\n{e}")
        
        threading.Thread(target=launch, daemon=True).start()
    
    def close_ldplayer(self):
        """ปิด LDPlayer emulator"""
        if not messagebox.askyesno("Confirm", "ต้องการปิด LDPlayer?"):
            return
        
        self.log("⏹️ กำลังปิด LDPlayer...")
        
        def close():
            try:
                from modules.ldconsole_controller import LDConsoleController
                
                ldconsole_path = self.config.get('ldplayer', {}).get('ldconsole_path')
                emulator_name = self.config.get('ldplayer', {}).get('emulator_name', '0')
                
                if not ldconsole_path:
                    self.log("❌ ไม่พบ ldconsole_path ใน config")
                    return
                
                ldconsole = LDConsoleController(ldconsole_path)
                
                # แปลง emulator_name เป็น string
                emulator_name = str(emulator_name)
                
                if ldconsole.quit(emulator_name):
                    self.log("✅ ปิด LDPlayer แล้ว")
                    
                    # ตัดการเชื่อมต่อ ADB ด้วย
                    if self.is_connected:
                        self.disconnect_ldplayer()
                else:
                    self.log("❌ ไม่สามารถปิด LDPlayer ได้")
                    
            except Exception as e:
                self.log(f"❌ Error: {e}")
                messagebox.showerror("Error", f"ปิด LDPlayer ล้มเหลว:\n{e}")
        
        threading.Thread(target=close, daemon=True).start()
    
    def check_emulator_status(self):
        """ตรวจสอบสถานะ emulator"""
        self.log("🔄 กำลังตรวจสอบสถานะ...")
        
        def check():
            try:
                from modules.ldconsole_controller import LDConsoleController
                
                ldconsole_path = self.config.get('ldplayer', {}).get('ldconsole_path')
                emulator_name = self.config.get('ldplayer', {}).get('emulator_name', '0')
                
                if not ldconsole_path:
                    self.log("❌ ไม่พบ ldconsole_path ใน config")
                    return
                
                ldconsole = LDConsoleController(ldconsole_path)
                
                # แปลง emulator_name เป็น string
                emulator_name = str(emulator_name)
                
                # ดูรายการทั้งหมด
                devices = ldconsole.list_devices()
                
                self.log(f"\n📊 พบ {len(devices)} emulators:")
                
                for device in devices:
                    status = "🟢 Running" if device['running'] else "⚪ Stopped"
                    self.log(f"  {status} - {device['name']} (index: {device['index']})")
                
                # เช็ค emulator ที่กำลังใช้
                is_running = ldconsole.is_running(emulator_name)
                
                if is_running:
                    self.log(f"\n✅ Emulator '{emulator_name}' กำลังทำงาน")
                    
                    # ดู ADB address
                    adb_devices = ldconsole.get_adb_devices()
                    if adb_devices:
                        self.log(f"📡 ADB Addresses:")
                        for addr in adb_devices:
                            self.log(f"  • {addr}")
                    
                    messagebox.showinfo(
                        "Status",
                        f"✅ Emulator '{emulator_name}' กำลังทำงาน\n\nสามารถเชื่อมต่อ ADB ได้แล้ว"
                    )
                else:
                    self.log(f"\n⚪ Emulator '{emulator_name}' หยุดทำงาน")
                    messagebox.showinfo(
                        "Status",
                        f"⚪ Emulator '{emulator_name}' หยุดทำงาน\n\nคลิก '🚀 เปิด LDPlayer' เพื่อเปิด"
                    )
                    
            except Exception as e:
                self.log(f"❌ Error: {e}")
                messagebox.showerror("Error", str(e))
        
        threading.Thread(target=check, daemon=True).start()
    
    def connect_ldplayer(self):
        """เชื่อมต่อ LDPlayer"""
        self.log("🔌 กำลังเชื่อมต่อ LDPlayer...")
        
        def connect():
            try:
                from modules.ldconsole_controller import LDConsoleController
                from modules.adb_controller import ADBController
                from modules.line_automation import LINEAutomation
                
                # Initialize
                self.ldconsole = LDConsoleController(
                    self.config['ldplayer']['ldconsole_path']
                )
                
                self.adb = ADBController(
                    self.config['ldplayer']['adb_path'],
                    self.config['ldplayer']['adb_host'],
                    self.config['ldplayer']['adb_port']
                )
                
                if not self.adb.connect():
                    raise Exception("Failed to connect ADB")
                
                self.line_automation = LINEAutomation(
                    self.adb,
                    self.config['line'],
                    self.ldconsole
                )
                
                self.is_connected = True
                self.log("✅ เชื่อมต่อสำเร็จ!")
                self.status_label.config(text="🟢 เชื่อมต่อแล้ว")
                self.update_stats()
                
            except Exception as e:
                self.log(f"❌ เชื่อมต่อล้มเหลว: {e}")
                messagebox.showerror("Error", f"เชื่อมต่อล้มเหลว:\n{e}")
        
        threading.Thread(target=connect, daemon=True).start()
    
    def disconnect_ldplayer(self):
        """ตัดการเชื่อมต่อ"""
        if self.adb:
            self.adb.disconnect()
        
        self.is_connected = False
        self.log("🔌 ตัดการเชื่อมต่อแล้ว")
        self.status_label.config(text="⚪ ไม่ได้เชื่อมต่อ")
        self.update_stats()
    
    def send_now(self):
        """ส่งข้อความทันที"""
        if not self.is_connected:
            messagebox.showwarning("Warning", "กรุณาเชื่อมต่อ LDPlayer ก่อน!")
            return
        
        self.log("📤 กำลังส่งข้อความ...")
        
        def send():
            try:
                messages = self.messages_data.get('message_templates', [])
                enabled = [m for m in messages if m.get('enabled', True)]
                
                if not enabled:
                    self.log("❌ ไม่มีข้อความที่เปิดใช้งาน")
                    return
                
                message = enabled[0]['content']
                count = int(self.target_friends_spinbox.get())
                
                results = self.line_automation.send_to_first_n_friends(message, count)
                
                self.log(f"✅ ส่งสำเร็จ {results['success']}/{results['total']}")
                messagebox.showinfo("Success", f"ส่งสำเร็จ {results['success']}/{results['total']} คน")
                
            except Exception as e:
                self.log(f"❌ Error: {e}")
                messagebox.showerror("Error", str(e))
        
        threading.Thread(target=send, daemon=True).start()
    
    def check_setup(self):
        """ตรวจสอบความพร้อม"""
        self.log("🔍 กำลังตรวจสอบความพร้อม...")
        
        import subprocess
        try:
            result = subprocess.run(
                ['python', 'check_setup.py'],
                capture_output=True,
                text=True,
                timeout=30
            )
            self.log(result.stdout)
        except Exception as e:
            self.log(f"❌ Error: {e}")
    
    def test_ldconsole(self):
        """ทดสอบ LDConsole"""
        self.log("🧪 กำลังทดสอบ LDConsole...")
        
        import subprocess
        try:
            subprocess.Popen(['python', 'demo_ldconsole.py'])
            self.log("✅ เปิด demo_ldconsole.py แล้ว")
        except Exception as e:
            self.log(f"❌ Error: {e}")
    
    def add_message(self):
        """เพิ่มข้อความใหม่"""
        messages = self.messages_data.get('message_templates', [])
        new_id = max([m.get('id', 0) for m in messages], default=0) + 1
        
        messages.append({
            'id': new_id,
            'name': 'ข้อความใหม่',
            'content': '',
            'enabled': True
        })
        
        self.messages_data['message_templates'] = messages
        self.refresh_messages_list()
        self.refresh_message_combo()
        self.log("➕ เพิ่มข้อความใหม่แล้ว")
    
    def save_message(self):
        """บันทึกข้อความ"""
        selection = self.messages_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "กรุณาเลือกข้อความที่จะบันทึก!")
            return
        
        idx = selection[0]
        messages = self.messages_data.get('message_templates', [])
        
        if idx < len(messages):
            messages[idx]['name'] = self.msg_name_entry.get()
            messages[idx]['content'] = self.msg_content_text.get('1.0', tk.END).strip()
            messages[idx]['enabled'] = self.msg_enabled_var.get()
            
            self.save_messages()
            self.refresh_messages_list()
            self.refresh_message_combo()
            self.log("💾 บันทึกข้อความแล้ว")
    
    def delete_message(self):
        """ลบข้อความ"""
        selection = self.messages_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "กรุณาเลือกข้อความที่จะลบ!")
            return
        
        if messagebox.askyesno("Confirm", "ต้องการลบข้อความนี้?"):
            idx = selection[0]
            messages = self.messages_data.get('message_templates', [])
            
            if idx < len(messages):
                del messages[idx]
                self.save_messages()
                self.refresh_messages_list()
                self.refresh_message_combo()
                self.log("🗑️ ลบข้อความแล้ว")
    
    def add_schedule(self):
        """เพิ่มตารางเวลาใหม่"""
        schedules = self.messages_data.get('schedules', [])
        new_id = max([s.get('id', 0) for s in schedules], default=0) + 1
        
        schedules.append({
            'id': new_id,
            'enabled': True,
            'time': '09:00',
            'days': ['monday', 'tuesday', 'wednesday', 'thursday', 'friday'],
            'message_template_id': 1,
            'description': 'ตารางใหม่'
        })
        
        self.messages_data['schedules'] = schedules
        self.refresh_schedules_list()
        self.log("➕ เพิ่มตารางเวลาใหม่แล้ว")
    
    def save_schedule(self):
        """บันทึกตารางเวลา"""
        selection = self.schedules_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "กรุณาเลือกตารางเวลาที่จะบันทึก!")
            return
        
        idx = selection[0]
        schedules = self.messages_data.get('schedules', [])
        
        if idx < len(schedules):
            schedules[idx]['time'] = self.sch_time_entry.get()
            schedules[idx]['enabled'] = self.sch_enabled_var.get()
            
            # Get message ID
            msg_text = self.sch_msg_var.get()
            if msg_text and ':' in msg_text:
                schedules[idx]['message_template_id'] = int(msg_text.split(':')[0])
            
            # Get days
            days = [day for day, var in self.days_vars.items() if var.get()]
            schedules[idx]['days'] = days
            
            self.save_messages()
            self.refresh_schedules_list()
            self.log("💾 บันทึกตารางเวลาแล้ว")
    
    def delete_schedule(self):
        """ลบตารางเวลา"""
        selection = self.schedules_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "กรุณาเลือกตารางเวลาที่จะลบ!")
            return
        
        if messagebox.askyesno("Confirm", "ต้องการลบตารางเวลานี้?"):
            idx = selection[0]
            schedules = self.messages_data.get('schedules', [])
            
            if idx < len(schedules):
                del schedules[idx]
                self.save_messages()
                self.refresh_schedules_list()
                self.log("🗑️ ลบตารางเวลาแล้ว")
    
    def start_scheduler(self):
        """เริ่ม Scheduler"""
        if not self.is_connected:
            messagebox.showwarning("Warning", "กรุณาเชื่อมต่อ LDPlayer ก่อน!")
            return
        
        self.log("▶️ เริ่ม Scheduler...")
        
        def start():
            try:
                from modules.scheduler import MessageScheduler
                
                self.scheduler = MessageScheduler(
                    timezone=self.config['scheduler']['timezone']
                )
                
                # Add schedules
                for sch in self.messages_data.get('schedules', []):
                    if not sch.get('enabled', True):
                        continue
                    
                    msg_id = sch.get('message_template_id')
                    messages = self.messages_data.get('message_templates', [])
                    message = next((m['content'] for m in messages if m['id'] == msg_id), '')
                    
                    if message:
                        def send_callback(msg=message):
                            count = int(self.target_friends_spinbox.get())
                            self.line_automation.send_to_first_n_friends(msg, count)
                        
                        self.scheduler.add_schedule(
                            time_str=sch['time'],
                            callback=send_callback,
                            days=sch.get('days', [])
                        )
                
                self.scheduler.start()
                self.scheduler_running = True
                self.log("✅ Scheduler เริ่มทำงานแล้ว")
                self.update_stats()
                
            except Exception as e:
                self.log(f"❌ Error: {e}")
                messagebox.showerror("Error", str(e))
        
        threading.Thread(target=start, daemon=True).start()
    
    def stop_scheduler(self):
        """หยุด Scheduler"""
        if self.scheduler:
            self.scheduler.stop()
            self.scheduler_running = False
            self.log("⏹️ หยุด Scheduler แล้ว")
            self.update_stats()
    
    def browse_file(self, file_type: str):
        """เลือกไฟล์"""
        filename = filedialog.askopenfilename(
            title=f"เลือก {file_type}",
            filetypes=[("Executable files", "*.exe"), ("All files", "*.*")]
        )
        
        if filename:
            if file_type == 'ldconsole':
                self.ldconsole_path_entry.delete(0, tk.END)
                self.ldconsole_path_entry.insert(0, filename)
            elif file_type == 'adb':
                self.adb_path_entry.delete(0, tk.END)
                self.adb_path_entry.insert(0, filename)
    
    def load_settings(self):
        """โหลดการตั้งค่า"""
        self.ldconsole_path_entry.delete(0, tk.END)
        self.ldconsole_path_entry.insert(
            0,
            self.config.get('ldplayer', {}).get('ldconsole_path', '')
        )
        
        self.adb_path_entry.delete(0, tk.END)
        self.adb_path_entry.insert(
            0,
            self.config.get('ldplayer', {}).get('adb_path', '')
        )
        
        self.emulator_name_entry.delete(0, tk.END)
        self.emulator_name_entry.insert(
            0,
            self.config.get('ldplayer', {}).get('emulator_name', '')
        )
        
        self.target_friends_spinbox.delete(0, tk.END)
        self.target_friends_spinbox.insert(
            0,
            self.config.get('automation', {}).get('target_friends_count', 3)
        )
        
        self.message_delay_spinbox.delete(0, tk.END)
        self.message_delay_spinbox.insert(
            0,
            self.config.get('automation', {}).get('message_delay_seconds', 2)
        )
        
        self.log("🔄 โหลดการตั้งค่าแล้ว")
    
    def save_settings(self):
        """บันทึกการตั้งค่า"""
        self.config['ldplayer']['ldconsole_path'] = self.ldconsole_path_entry.get()
        self.config['ldplayer']['adb_path'] = self.adb_path_entry.get()
        self.config['ldplayer']['emulator_name'] = self.emulator_name_entry.get()
        
        self.config['automation']['target_friends_count'] = int(self.target_friends_spinbox.get())
        self.config['automation']['message_delay_seconds'] = int(self.message_delay_spinbox.get())
        
        self.save_config()
        messagebox.showinfo("Success", "บันทึกการตั้งค่าเรียบร้อย!")
    
    def refresh_logs(self):
        """รีเฟรช logs"""
        try:
            log_file = self.config.get('logging', {}).get('log_file', 'data/logs/automation.log')
            if os.path.exists(log_file):
                with open(log_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    self.log_text.delete('1.0', tk.END)
                    self.log_text.insert('1.0', content)
                    self.log_text.see(tk.END)
                self.log("🔄 รีเฟรช logs แล้ว")
            else:
                self.log("⚠️ ไม่พบไฟล์ log")
        except Exception as e:
            self.log(f"❌ Error: {e}")
    
    def clear_logs(self):
        """ล้าง logs"""
        if messagebox.askyesno("Confirm", "ต้องการล้าง logs?"):
            self.log_text.delete('1.0', tk.END)
            self.log("🗑️ ล้าง logs แล้ว")
    
    # ========== LDPlayer Management Actions ==========
    
    def on_ld_select(self, event):
        """เมื่อเลือก LD"""
        selection = self.ld_tree.selection()
        if not selection:
            return
        
        item = self.ld_tree.item(selection[0])
        values = item['values']
        
        if values:
            index, name, status, pid, adb = values
            self.selected_ld_label.config(
                text=f"{name} (Index: {index})\n{status}"
            )
            
            # Store selected LD
            self.selected_ld_index = index
            self.selected_ld_name = name
    
    def launch_selected_ld(self):
        """เปิด LD ที่เลือก"""
        if not hasattr(self, 'selected_ld_index'):
            messagebox.showwarning("Warning", "กรุณาเลือก LD ก่อน!")
            return
        
        self.log(f"🚀 กำลังเปิด {self.selected_ld_name}...")
        
        def launch():
            try:
                from modules.ldconsole_controller import LDConsoleController
                
                ldconsole_path = self.config.get('ldplayer', {}).get('ldconsole_path')
                ldconsole = LDConsoleController(ldconsole_path)
                
                # แปลง index เป็น string
                index = str(self.selected_ld_index)
                
                if ldconsole.launch(index):
                    self.log(f"✅ เปิด {self.selected_ld_name} แล้ว")
                    messagebox.showinfo("Success", f"เปิด {self.selected_ld_name} แล้ว")
                    # Refresh list after 2 seconds
                    self.root.after(2000, self.refresh_ld_list)
                else:
                    self.log(f"❌ ไม่สามารถเปิด {self.selected_ld_name}")
                    
            except Exception as e:
                self.log(f"❌ Error: {e}")
                messagebox.showerror("Error", str(e))
        
        threading.Thread(target=launch, daemon=True).start()
    
    def close_selected_ld(self):
        """ปิด LD ที่เลือก"""
        if not hasattr(self, 'selected_ld_index'):
            messagebox.showwarning("Warning", "กรุณาเลือก LD ก่อน!")
            return
        
        if not messagebox.askyesno("Confirm", f"ต้องการปิด {self.selected_ld_name}?"):
            return
        
        self.log(f"⏹️ กำลังปิด {self.selected_ld_name}...")
        
        def close():
            try:
                from modules.ldconsole_controller import LDConsoleController
                
                ldconsole_path = self.config.get('ldplayer', {}).get('ldconsole_path')
                ldconsole = LDConsoleController(ldconsole_path)
                
                # แปลง index เป็น string
                index = str(self.selected_ld_index)
                
                if ldconsole.quit(index):
                    self.log(f"✅ ปิด {self.selected_ld_name} แล้ว")
                    # Refresh list
                    self.root.after(1000, self.refresh_ld_list)
                else:
                    self.log(f"❌ ไม่สามารถปิด {self.selected_ld_name}")
                    
            except Exception as e:
                self.log(f"❌ Error: {e}")
                messagebox.showerror("Error", f"ปิด LDPlayer ล้มเหลว:\n{e}")
        
        threading.Thread(target=close, daemon=True).start()
    
    def reboot_selected_ld(self):
        """รีบูต LD ที่เลือก"""
        if not hasattr(self, 'selected_ld_index'):
            messagebox.showwarning("Warning", "กรุณาเลือก LD ก่อน!")
            return
        
        if not messagebox.askyesno("Confirm", f"ต้องการรีบูต {self.selected_ld_name}?"):
            return
        
        self.log(f"🔄 กำลังรีบูต {self.selected_ld_name}...")
        
        def reboot():
            try:
                from modules.ldconsole_controller import LDConsoleController
                
                ldconsole_path = self.config.get('ldplayer', {}).get('ldconsole_path')
                ldconsole = LDConsoleController(ldconsole_path)
                
                # แปลง index เป็น string
                index = str(self.selected_ld_index)
                
                if ldconsole.reboot(index):
                    self.log(f"✅ รีบูต {self.selected_ld_name} แล้ว")
                    # Refresh list after 10 seconds
                    self.root.after(10000, self.refresh_ld_list)
                else:
                    self.log(f"❌ ไม่สามารถรีบูต {self.selected_ld_name}")
                    
            except Exception as e:
                self.log(f"❌ Error: {e}")
                messagebox.showerror("Error", str(e))
        
        threading.Thread(target=reboot, daemon=True).start()
    
    def delete_selected_ld(self):
        """ลบ LD ที่เลือก"""
        if not hasattr(self, 'selected_ld_index'):
            messagebox.showwarning("Warning", "กรุณาเลือก LD ก่อน!")
            return
        
        if not messagebox.askyesno("Confirm", f"ต้องการลบ {self.selected_ld_name}?\n\n⚠️ การกระทำนี้ไม่สามารถย้อนกลับได้!"):
            return
        
        self.log(f"🗑️ กำลังลบ {self.selected_ld_name}...")
        
        def delete():
            try:
                from modules.ldconsole_controller import LDConsoleController
                
                ldconsole_path = self.config.get('ldplayer', {}).get('ldconsole_path')
                ldconsole = LDConsoleController(ldconsole_path)
                
                # Delete using ldconsole (แปลง index เป็น string)
                index = str(self.selected_ld_index)
                result = ldconsole._run_command(["remove", "--index", index])
                
                self.log(f"✅ ลบ {self.selected_ld_name} แล้ว")
                messagebox.showinfo("Success", f"ลบ {self.selected_ld_name} แล้ว")
                
                # Refresh list
                self.root.after(1000, self.refresh_ld_list)
                    
            except Exception as e:
                self.log(f"❌ Error: {e}")
                messagebox.showerror("Error", str(e))
        
        threading.Thread(target=delete, daemon=True).start()
    
    def create_new_ld(self):
        """สร้าง LD ใหม่ (คัดลอกจาก LD ที่มีอยู่)"""
        
        try:
            from modules.ldconsole_controller import LDConsoleController
            
            ldconsole_path = self.config.get('ldplayer', {}).get('ldconsole_path')
            ldconsole = LDConsoleController(ldconsole_path)
            
            # Get existing devices
            devices = ldconsole.list_devices()
            
            if not devices:
                messagebox.showwarning(
                    "Warning",
                    "ไม่มี LD ที่มีอยู่!\n\n"
                    "กรุณาสร้าง LD ตัวแรกผ่าน LDPlayer โปรแกรมก่อน\n"
                    "แล้วค่อยใช้ฟีเจอร์นี้คัดลอกเพิ่ม"
                )
                return
            
            # สร้าง dialog ให้เลือก source LD
            dialog = tk.Toplevel(self.root)
            dialog.title("สร้าง LD ใหม่")
            dialog.geometry("400x300")
            dialog.transient(self.root)
            dialog.grab_set()
            
            ttk.Label(dialog, text="เลือก LD ที่จะใช้เป็น Template:", font=('Arial', 10, 'bold')).pack(pady=10)
            
            # Listbox แสดง LD ที่มี
            listbox = tk.Listbox(dialog, height=8)
            listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
            
            for device in devices:
                status = "🟢" if device['running'] else "⚪"
                listbox.insert(tk.END, f"{status} {device['name']} (Index: {device['index']})")
            
            listbox.select_set(0)  # เลือกตัวแรก
            
            # ชื่อ LD ใหม่
            ttk.Label(dialog, text="ชื่อ LD ใหม่:").pack(pady=(10, 5))
            name_entry = ttk.Entry(dialog, width=30)
            name_entry.pack(pady=5)
            name_entry.focus()
            
            result_data = {'confirmed': False, 'source_index': None, 'name': None}
            
            def on_confirm():
                selection = listbox.curselection()
                if not selection:
                    messagebox.showwarning("Warning", "กรุณาเลือก LD ที่จะคัดลอก!")
                    return
                
                name = name_entry.get().strip()
                if not name:
                    messagebox.showwarning("Warning", "กรุณาใส่ชื่อ LD ใหม่!")
                    return
                
                result_data['confirmed'] = True
                result_data['source_index'] = devices[selection[0]]['index']
                result_data['source_name'] = devices[selection[0]]['name']
                result_data['name'] = name
                dialog.destroy()
            
            def on_cancel():
                dialog.destroy()
            
            # Buttons
            btn_frame = ttk.Frame(dialog)
            btn_frame.pack(pady=10)
            
            ttk.Button(btn_frame, text="✅ สร้าง", command=on_confirm, width=15).pack(side=tk.LEFT, padx=5)
            ttk.Button(btn_frame, text="❌ ยกเลิก", command=on_cancel, width=15).pack(side=tk.LEFT, padx=5)
            
            # Wait for dialog
            self.root.wait_window(dialog)
            
            if not result_data['confirmed']:
                return
            
            # Create LD
            name = result_data['name']
            source_index = result_data['source_index']
            source_name = result_data['source_name']
            
            self.log(f"➕ กำลังสร้าง LD ใหม่: {name}...")
            self.log(f"📋 คัดลอกจาก: {source_name}")
            
            def create():
                try:
                    # Copy command (แปลง index เป็น string)
                    result = ldconsole._run_command(["copy", "--name", name, "--from", str(source_index)])
                    
                    self.log(f"✅ สร้าง LD ใหม่ '{name}' แล้ว")
                    messagebox.showinfo("Success", f"สร้าง LD ใหม่ '{name}' แล้ว\n\nคัดลอกจาก: {source_name}")
                    
                    # Refresh list
                    self.root.after(2000, self.refresh_ld_list)
                        
                except Exception as e:
                    self.log(f"❌ Error: {e}")
                    messagebox.showerror("Error", str(e))
            
            threading.Thread(target=create, daemon=True).start()
            
        except Exception as e:
            self.log(f"❌ Error: {e}")
            messagebox.showerror("Error", str(e))
    
    def send_message_selected_ld(self):
        """ส่งข้อความจาก LD ที่เลือก"""
        if not hasattr(self, 'selected_ld_index'):
            messagebox.showwarning("Warning", "กรุณาเลือก LD ก่อน!")
            return
        
        # Get message
        msg_text = self.ld_msg_var.get()
        if not msg_text or ':' not in msg_text:
            messagebox.showwarning("Warning", "กรุณาเลือกข้อความ!")
            return
        
        msg_id = int(msg_text.split(':')[0])
        messages = self.messages_data.get('message_templates', [])
        message = next((m['content'] for m in messages if m['id'] == msg_id), None)
        
        if not message:
            messagebox.showwarning("Warning", "ไม่พบข้อความ!")
            return
        
        count = int(self.ld_friend_count_spinbox.get())
        
        self.log(f"📤 กำลังส่งข้อความจาก {self.selected_ld_name}...")
        
        def send():
            try:
                from modules.ldconsole_controller import LDConsoleController
                from modules.adb_controller import ADBController
                from modules.line_automation import LINEAutomation
                
                ldconsole_path = self.config.get('ldplayer', {}).get('ldconsole_path')
                adb_path = self.config.get('ldplayer', {}).get('adb_path')
                
                ldconsole = LDConsoleController(ldconsole_path)
                
                # Get ADB address (แปลง index เป็ string)
                index = str(self.selected_ld_index)
                
                # ใช้ list2 เพื่อหา ADB port (port = 5555 + index)
                adb_port = 5555 + int(index)
                adb_addr = f"127.0.0.1:{adb_port}"
                
                self.log(f"🔌 ADB Address: {adb_addr}")
                
                if not adb_addr or ':' not in adb_addr:
                    self.log(f"❌ ไม่พบ ADB address สำหรับ {self.selected_ld_name}")
                    messagebox.showerror("Error", "ไม่พบ ADB address")
                    return
                
                host, port = adb_addr.split(':')
                
                # Connect ADB
                adb = ADBController(adb_path, host, int(port))
                if not adb.connect():
                    self.log(f"❌ ไม่สามารถเชื่อมต่อ ADB: {adb_addr}")
                    messagebox.showerror("Error", "ไม่สามารถเชื่อมต่อ ADB")
                    return
                
                # Create LINE automation
                line_automation = LINEAutomation(adb, self.config['line'], ldconsole)
                line_automation.config.update(self.config['automation'])
                
                # Send messages
                results = line_automation.send_to_first_n_friends(message, count)
                
                self.log(f"✅ ส่งสำเร็จ {results['success']}/{results['total']} จาก {self.selected_ld_name}")
                messagebox.showinfo(
                    "Success",
                    f"ส่งสำเร็จ {results['success']}/{results['total']} คน\nจาก {self.selected_ld_name}"
                )
                
                # Disconnect
                adb.disconnect()
                
            except Exception as e:
                self.log(f"❌ Error: {e}")
                messagebox.showerror("Error", str(e))
        
        threading.Thread(target=send, daemon=True).start()
    
    def send_message_all_running_ld(self):
        """ส่งข้อความจากทุก LD ที่เปิดอยู่"""
        # Get message
        msg_text = self.ld_msg_var.get()
        if not msg_text or ':' not in msg_text:
            messagebox.showwarning("Warning", "กรุณาเลือกข้อความ!")
            return
        
        msg_id = int(msg_text.split(':')[0])
        messages = self.messages_data.get('message_templates', [])
        message = next((m['content'] for m in messages if m['id'] == msg_id), None)
        
        if not message:
            messagebox.showwarning("Warning", "ไม่พบข้อความ!")
            return
        
        count = int(self.ld_friend_count_spinbox.get())
        
        if not messagebox.askyesno("Confirm", f"ต้องการส่งข้อความจากทุก LD ที่เปิดอยู่?"):
            return
        
        self.log(f"📤 กำลังส่งข้อความจากทุก LD ที่เปิดอยู่...")
        
        def send_all():
            try:
                from modules.ldconsole_controller import LDConsoleController
                from modules.adb_controller import ADBController
                from modules.line_automation import LINEAutomation
                
                ldconsole_path = self.config.get('ldplayer', {}).get('ldconsole_path')
                adb_path = self.config.get('ldplayer', {}).get('adb_path')
                
                ldconsole = LDConsoleController(ldconsole_path)
                
                # Get running devices
                running_devices = ldconsole.get_running_devices()
                
                if not running_devices:
                    self.log("❌ ไม่มี LD ที่เปิดอยู่")
                    messagebox.showwarning("Warning", "ไม่มี LD ที่เปิดอยู่!")
                    return
                
                total_success = 0
                total_failed = 0
                
                for device in running_devices:
                    ld_name = device['name']
                    ld_index = device['index']
                    
                    try:
                        self.log(f"\n📱 กำลังส่งจาก {ld_name}...")
                        
                        # Get ADB address (port = 5555 + index)
                        adb_port = 5555 + int(ld_index)
                        adb_addr = f"127.0.0.1:{adb_port}"
                        
                        self.log(f"  🔌 ADB Address: {adb_addr}")
                        
                        if not adb_addr or ':' not in adb_addr:
                            self.log(f"  ⚠️ ไม่พบ ADB address สำหรับ {ld_name}")
                            total_failed += 1
                            continue
                        
                        host, port = adb_addr.split(':')
                        
                        # Connect ADB
                        adb = ADBController(adb_path, host, int(port))
                        if not adb.connect():
                            self.log(f"  ⚠️ ไม่สามารถเชื่อมต่อ ADB: {ld_name}")
                            total_failed += 1
                            continue
                        
                        # Create LINE automation
                        line_automation = LINEAutomation(adb, self.config['line'], ldconsole)
                        line_automation.config.update(self.config['automation'])
                        line_automation.config['emulator_name'] = ld_index
                        
                        # Send messages
                        results = line_automation.send_to_first_n_friends(message, count)
                        
                        self.log(f"  ✅ {ld_name}: {results['success']}/{results['total']}")
                        total_success += results['success']
                        total_failed += results['failed']
                        
                        # Disconnect
                        adb.disconnect()
                        
                        # Wait between LDs
                        import time
                        time.sleep(3)
                        
                    except Exception as e:
                        self.log(f"  ❌ {ld_name} Error: {e}")
                        total_failed += count
                
                self.log(f"\n✅ สรุป: ส่งสำเร็จ {total_success} ล้มเหลว {total_failed}")
                messagebox.showinfo(
                    "Summary",
                    f"ส่งข้อความจาก {len(running_devices)} LD\n\nสำเร็จ: {total_success}\nล้มเหลว: {total_failed}"
                )
                
            except Exception as e:
                self.log(f"❌ Error: {e}")
                messagebox.showerror("Error", str(e))
        
        threading.Thread(target=send_all, daemon=True).start()
    
    def run(self):
        """รัน GUI"""
        self.root.mainloop()


def main():
    """Main function"""
    gui = ModernGUI()
    gui.run()


if __name__ == "__main__":
    main()
