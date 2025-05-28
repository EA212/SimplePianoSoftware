import pygame
import sys
import tkinter as tk
from tkinter import scrolledtext, messagebox, ttk
import threading
import time
import pyperclip
from pygame import midi

class PianoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🎹 智能钢琴软件")
        self.root.geometry("800x600")
        self.root.configure(bg="#f5f5f5")
        self.root.resizable(True, True)
        
        # 设置中文字体支持
        self.font_family = ("SimHei", "WenQuanYi Micro Hei", "Heiti TC", "Arial")
        
        # 初始化MIDI
        self.midi_out = None
        self.velocity = 80
        self.note_duration = 0.5
        self.interval = 0.1
        self.is_playing = False
        
        # 音符和和弦映射
        self.notes = {
            '1': 60, '2': 62, '3': 64, '4': 65, '5': 67, 
            '6': 69, '7': 71, '8': 72, '9': 74, '0': 76,
            '!': 61, '@': 63, '$': 66, '%': 68, '^': 70
        }
        
        self.chords = {
            'q': [60, 64, 67], 'w': [62, 65, 69], 'e': [64, 67, 71], 
            'r': [65, 69, 72], 't': [67, 71, 74], 'y': [69, 72, 76], 
            'u': [71, 74, 77], 'i': [60, 64, 67, 71], 'o': [62, 65, 69, 72], 
            'p': [67, 71, 74, 77]
        }
        
        # 创建界面
        self.create_widgets()
        
        # 初始化MIDI
        self.init_midi()
        
        # 启动剪贴板监控
        self.last_clipboard = ""
        self.monitor_clipboard()
    
    def init_midi(self):
        try:
            pygame.init()
            midi.init()
            output_id = midi.get_default_output_id()
            if output_id == -1:
                messagebox.showerror("错误", "未找到默认MIDI输出设备，请确保已安装并配置好MIDI synthesizer。")
                sys.exit(1)
            self.midi_out = midi.Output(output_id, 0)
            self.midi_out.set_instrument(0)
            self.status_var.set("状态: MIDI设备已连接，使用钢琴音色")
        except pygame.midi.MidiException as e:
            messagebox.showerror("MIDI初始化错误", str(e))
            sys.exit(1)
    
    def create_widgets(self):
        # 顶部标题
        header_frame = tk.Frame(self.root, bg="#2c3e50", height=60)
        header_frame.pack(fill="x", side="top")
        
        title_label = tk.Label(header_frame, text="🎹 智能钢琴软件", 
                              font=(self.font_family[0], 24, "bold"), 
                              bg="#2c3e50", fg="white")
        title_label.pack(pady=10)
        
        # 主内容区域
        main_frame = tk.Frame(self.root, bg="#f5f5f5")
        main_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # 左侧控制面板
        control_frame = tk.LabelFrame(main_frame, text="控制面板", 
                                     font=(self.font_family[0], 12), 
                                     bg="#f5f5f5", fg="#2c3e50", padx=10, pady=10)
        control_frame.pack(side="left", fill="y", padx=(0, 10))
        
        # 速度控制
        tk.Label(control_frame, text="音符持续时间:", 
                font=(self.font_family[0], 10), bg="#f5f5f5").pack(anchor="w")
        duration_frame = tk.Frame(control_frame, bg="#f5f5f5")
        duration_frame.pack(fill="x", pady=5)
        
        self.duration_scale = ttk.Scale(duration_frame, from_=0.1, to=1.5, 
                                       orient="horizontal", length=150,
                                       value=self.note_duration,
                                       command=self.update_duration_label)
        self.duration_scale.pack(side="left", padx=(0, 10))
        
        self.duration_label = tk.Label(duration_frame, text=f"{self.note_duration:.1f}秒",
                                      font=(self.font_family[0], 10), bg="#f5f5f5", width=5)
        self.duration_label.pack(side="left")
        
        # 间隔控制
        tk.Label(control_frame, text="音符间隔时间:", 
                font=(self.font_family[0], 10), bg="#f5f5f5").pack(anchor="w")
        interval_frame = tk.Frame(control_frame, bg="#f5f5f5")
        interval_frame.pack(fill="x", pady=5)
        
        self.interval_scale = ttk.Scale(interval_frame, from_=0.0, to=0.5, 
                                       orient="horizontal", length=150,
                                       value=self.interval,
                                       command=self.update_interval_label)
        self.interval_scale.pack(side="left", padx=(0, 10))
        
        self.interval_label = tk.Label(interval_frame, text=f"{self.interval:.1f}秒",
                                      font=(self.font_family[0], 10), bg="#f5f5f5", width=5)
        self.interval_label.pack(side="left")
        
        # 乐器选择
        tk.Label(control_frame, text="乐器选择:", 
                font=(self.font_family[0], 10), bg="#f5f5f5").pack(anchor="w", pady=(10, 5))
        
        self.instrument_var = tk.StringVar(value="000 - 钢琴")
        self.instrument_menu = ttk.Combobox(control_frame, textvariable=self.instrument_var,
                                           width=25, state="readonly")
        self.instrument_menu['values'] = [
            "000 - 钢琴", "001 - 明亮钢琴", "002 - 电钢琴1", "003 - 电钢琴2", 
            "004 - 羽管键琴", "005 - 电颤琴", "006 - 钟琴", "007 - 钢片琴",
            "008 - 风琴", "009 - 簧风琴", "010 - 手风琴", "011 - 口琴",
            "012 - 电风琴", "013 - 摇滚风琴", "014 - 教堂管风琴", "015 - 大管风琴",
            "040 - 小提琴", "041 - 中提琴", "042 - 大提琴", "043 - 低音提琴",
            "044 - 拨弦提琴", "045 - 竖琴", "046 - 电小提琴", "047 - 电中提琴",
            "048 - 弦乐合奏", "049 - 慢弦乐", "050 - 合成弦乐", "051 - 合成弦乐2",
            "052 - 合唱团", "053 - 人声", "054 - 合成人声", "055 - 管弦乐打击乐",
            "056 - 小号", "057 - 长号", "058 - 大号", "059 - 圆号",
            "060 - 次中音号", "061 - 富鲁格号", "062 - 电号", "063 - 合成号",
            "064 - 萨克斯", "065 - 萨克斯", "066 - 萨克斯", "067 - 萨克斯",
            "068 - 长笛", "069 - 短笛", "070 - 双簧管", "071 - 英国管",
            "072 - 巴松管", "073 - 萨克斯管", "074 - 竖笛", "075 - 班卓琴",
            "076 - 吉他", "077 - 电吉他", "078 - 尼龙弦吉他", "079 - 钢弦吉他",
            "080 - 电吉他", "081 - 电吉他", "082 - 失真吉他", "083 - 强力和弦",
            "084 - 贝斯", "085 - 电贝斯", "086 - 电贝斯", "087 - 无品贝斯",
            "088 - 合成贝斯", "089 - 合成贝斯", "090 - 小提琴", "091 - 弦乐",
            "092 - 合成主音", "093 - 合成主音", "094 - 合成主音", "095 - 合成主音",
            "096 - 合成垫", "097 - 合成垫", "098 - 合成垫", "099 - 合成垫",
            "100 - 合成效果", "101 - 合成效果", "102 - 合成效果", "103 - 合成效果",
            "104 - 幻想音效", "105 - 科幻音效", "106 - 回声", "107 - 宇宙声",
            "108 - 打击乐器", "109 - 打击乐器", "110 - 打击乐器", "111 - 打击乐器",
            "112 - 鼓组", "113 - 电子鼓", "114 - 电子鼓", "115 - 电子鼓",
            "116 - 电子鼓", "117 - 电子鼓", "118 - 电子鼓", "119 - 电子鼓",
            "120 - 钢鼓", "121 - 邦戈鼓", "122 - 康加鼓", "123 - 响板",
            "124 - 沙锤", "125 - 牛铃", "126 - 木鱼", "127 - 合成打击"
        ]
        self.instrument_menu.pack(fill="x")
        self.instrument_menu.bind("<<ComboboxSelected>>", self.change_instrument)
        
        # 控制按钮
        button_frame = tk.Frame(control_frame, bg="#f5f5f5")
        button_frame.pack(fill="x", pady=20)
        
        self.play_button = tk.Button(button_frame, text="▶️ 播放", 
                                    font=(self.font_family[0], 12), 
                                    bg="#27ae60", fg="white",
                                    command=self.play_text)
        self.play_button.pack(side="left", fill="x", expand=True, padx=(0, 5))
        
        self.stop_button = tk.Button(button_frame, text="⏹️ 停止", 
                                    font=(self.font_family[0], 12), 
                                    bg="#e74c3c", fg="white",
                                    command=self.stop_playback,
                                    state="disabled")
        self.stop_button.pack(side="left", fill="x", expand=True, padx=(5, 0))
        
        # 帮助按钮
        self.help_button = tk.Button(control_frame, text="ℹ️ 帮助", 
                                    font=(self.font_family[0], 10), 
                                    bg="#3498db", fg="white",
                                    command=self.show_help)
        self.help_button.pack(fill="x", pady=(10, 0))
        
        # 右侧文本输入和显示区域
        text_frame = tk.LabelFrame(main_frame, text="音符/和弦文本", 
                                  font=(self.font_family[0], 12), 
                                  bg="#f5f5f5", fg="#2c3e50", padx=10, pady=10)
        text_frame.pack(side="right", fill="both", expand=True)
        
        # 文本输入框
        self.text_area = scrolledtext.ScrolledText(text_frame, 
                                                  font=(self.font_family[0], 12),
                                                  wrap=tk.WORD, height=10)
        self.text_area.pack(fill="both", expand=True, pady=(0, 10))
        
        # 功能按钮
        btn_frame = tk.Frame(text_frame, bg="#f5f5f5")
        btn_frame.pack(fill="x", pady=5)
        
        self.paste_button = tk.Button(btn_frame, text="📋 粘贴剪贴板", 
                                     font=(self.font_family[0], 10), 
                                     bg="#9b59b6", fg="white",
                                     command=self.paste_clipboard)
        self.paste_button.pack(side="left", padx=(0, 5))
        
        self.clear_button = tk.Button(btn_frame, text="🗑️ 清空", 
                                     font=(self.font_family[0], 10), 
                                     bg="#e67e22", fg="white",
                                     command=self.clear_text)
        self.clear_button.pack(side="left")
        
        self.auto_detect_var = tk.BooleanVar(value=True)
        self.auto_detect_check = tk.Checkbutton(btn_frame, text="自动检测剪贴板",
                                               variable=self.auto_detect_var,
                                               font=(self.font_family[0], 10),
                                               bg="#f5f5f5")
        self.auto_detect_check.pack(side="right")
        
        # 状态显示
        self.status_var = tk.StringVar(value="状态: 就绪")
        self.status_bar = tk.Label(self.root, textvariable=self.status_var,
                                 bd=1, relief=tk.SUNKEN, anchor=tk.W,
                                 font=(self.font_family[0], 10), bg="#ecf0f1")
        self.status_bar.pack(side="bottom", fill="x")
    
    def update_duration_label(self, value):
        """更新音符持续时间的显示标签"""
        self.note_duration = float(value)
        self.duration_label.config(text=f"{self.note_duration:.1f}秒")
    
    def update_interval_label(self, value):
        """更新音符间隔时间的显示标签"""
        self.interval = float(value)
        self.interval_label.config(text=f"{self.interval:.1f}秒")
    
    def change_instrument(self, event=None):
        try:
            instrument_id = int(self.instrument_var.get().split()[0])
            self.midi_out.set_instrument(instrument_id)
            self.status_var.set(f"状态: 已更改为乐器 {self.instrument_var.get()}")
        except Exception as e:
            messagebox.showerror("错误", f"更改乐器失败: {str(e)}")
    
    def paste_clipboard(self):
        try:
            clipboard_text = pyperclip.paste()
            self.text_area.delete(1.0, tk.END)
            self.text_area.insert(tk.END, clipboard_text)
            self.status_var.set("状态: 已从剪贴板粘贴文本")
        except Exception as e:
            messagebox.showerror("错误", f"获取剪贴板内容失败: {str(e)}")
    
    def clear_text(self):
        self.text_area.delete(1.0, tk.END)
        self.status_var.set("状态: 文本已清空")
    
    def show_help(self):
        help_text = """
钢琴软件使用说明:

【单音】
1-0: C大调音阶 (1=C, 2=D, 3=E, ..., 0=E高八度)
!@$%^: 黑键 (升号, 需按Shift输入)

【和弦】
q: C和弦 (C-E-G)       w: Dm和弦 (D-F-A)
e: Em和弦 (E-G-B)       r: F和弦 (F-A-C)
t: G和弦 (G-B-D)       y: Am和弦 (A-C-E)
u: Bdim和弦 (B-D-F)    i: C7和弦 (C-E-G-Bb)
o: Dm7和弦 (D-F-A-C)   p: G7和弦 (G-B-D-F)

【输入格式】
- 单独输入一个字符: 立即播放对应的音符/和弦
- 输入一串字符: 按顺序播放所有音符/和弦，字符间用空格分隔
  例如: '1 3 5' 会依次播放C-E-G
  例如: 'q w e r' 会依次播放C-Dm-Em-F

【操作指南】
1. 将音符/和弦文本复制到剪贴板
2. 点击"📋 粘贴剪贴板"按钮或启用"自动检测剪贴板"
3. 调整速度和间隔滑块控制演奏效果
4. 点击"▶️ 播放"按钮开始演奏
5. 点击"⏹️ 停止"按钮停止演奏
6. 从下拉菜单选择不同乐器音色
"""
        messagebox.showinfo("帮助信息", help_text)
    
    def monitor_clipboard(self):
        if self.auto_detect_var.get():
            current_clipboard = pyperclip.paste()
            if current_clipboard != self.last_clipboard and current_clipboard.strip():
                self.last_clipboard = current_clipboard
                self.text_area.delete(1.0, tk.END)
                self.text_area.insert(tk.END, current_clipboard)
                self.status_var.set("状态: 已自动检测并粘贴剪贴板内容")
        self.root.after(1000, self.monitor_clipboard)  # 每秒检查一次
    
    def play_text(self):
        if self.is_playing:
            return
        
        text = self.text_area.get(1.0, tk.END).strip()
        if not text:
            messagebox.showwarning("警告", "请输入音符/和弦文本后再播放")
            return
        
        self.is_playing = True
        self.play_button.config(state="disabled")
        self.stop_button.config(state="normal")
        self.status_var.set("状态: 正在播放...")
        
        # 在新线程中播放
        threading.Thread(target=self._play_thread, args=(text,)).start()
    
    def _play_thread(self, text):
        try:
            elements = text.strip().split()
            for i, element in enumerate(elements):
                if not self.is_playing:
                    break
                
                # 更新状态栏显示当前播放的音符/和弦
                self.root.after(0, lambda s=element: self.status_var.set(f"状态: 正在播放 '{s}' ({i+1}/{len(elements)})"))
                
                if element in self.notes:
                    self.midi_out.note_on(self.notes[element], self.velocity)
                    time.sleep(self.note_duration)
                    self.midi_out.note_off(self.notes[element], self.velocity)
                elif element in self.chords:
                    for note in self.chords[element]:
                        self.midi_out.note_on(note, self.velocity)
                    time.sleep(self.note_duration)
                    for note in self.chords[element]:
                        self.midi_out.note_off(note, self.velocity)
                else:
                    self.root.after(0, lambda s=element: self.status_var.set(f"状态: 忽略未知字符 '{s}'"))
                
                # 音符/和弦之间的间隔
                if element != elements[-1] and self.is_playing:
                    time.sleep(self.interval)
            
            self.root.after(0, lambda: self.status_var.set("状态: 播放完成"))
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("播放错误", str(e)))
        finally:
            self.root.after(0, self.stop_playback)
    
    def stop_playback(self):
        self.is_playing = False
        self.play_button.config(state="normal")
        self.stop_button.config(state="disabled")
        self.status_var.set("状态: 已停止")

if __name__ == "__main__":
    root = tk.Tk()
    app = PianoApp(root)
    root.mainloop()
