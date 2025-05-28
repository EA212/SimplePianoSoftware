![image](https://github.com/user-attachments/assets/534ddd83-2ae1-4c9e-947c-8a51ac3aef11)
![image](https://github.com/user-attachments/assets/39dc1f7e-8de5-4d89-8a54-3eb411474ff6)
![image](https://github.com/user-attachments/assets/6edb53b3-e71e-4929-b48b-5d2c6562f364)
### **一、Simple Piano Software**
### **一、简易钢琴软件介绍**
#### **1. 软件定位**  
这是一款基于Python的**交互式MIDI音乐软件**，通过文本输入或剪贴板快速触发音符/和弦播放，支持多乐器音色切换和参数调整，适合音乐初学者学习乐理、快速验证和弦组合，或作为编程爱好者的趣味音乐工具。

#### **2. 核心优势**  
- **零硬件依赖**：仅需电脑声卡和MIDI合成器（系统默认即可）。  
- **文本化交互**：通过简单字符映射音符/和弦，无需复杂乐谱知识。  
- **灵活扩展**：可自定义音符映射、添加新和弦或扩展乐器库。


### **二、设计思路**
#### **1. 架构设计**  
- **界面层**：使用Tkinter构建GUI，分离控制面板（参数调整）、输入区（文本/剪贴板）和状态显示，确保操作逻辑清晰。  
- **功能层**：  
  - **MIDI模块**：通过Pygame.midi实现音符发送与乐器切换。  
  - **多线程**：播放逻辑独立于界面线程，避免阻塞UI交互。  
  - **剪贴板监控**：通过`pyperclip`实现实时文本捕获，提升输入效率。  

- **数据层**：使用字典映射字符与MIDI音符/和弦（`self.notes`/`self.chords`），便于快速扩展键位。

#### **2. 交互逻辑**  
1. **单字符触发**：输入单个字符（如`1`或`q`）直接播放对应音符/和弦。  
2. **序列播放**：输入用空格分隔的字符序列（如`1 3 5 q`），按顺序自动演奏。  
3. **参数联动**：滑动条调整音符持续时间和间隔时间，实时更新播放效果。


### **三、GUI功能介绍**
#### **1. 控制面板**  
| **组件**         | **功能描述**                                                                 |
|------------------|-----------------------------------------------------------------------------|
| **音符持续时间**  | 滑动条（0.1-1.5秒），控制单个音符/和弦的发声时长，默认0.5秒。               |
| **音符间隔时间**  | 滑动条（0.0-0.5秒），控制连续音符/和弦之间的停顿，默认0.1秒。               |
| **乐器选择**      | 下拉菜单（128种GM音色），支持钢琴、小提琴、萨克斯等，默认钢琴（音色ID 0）。 |
| **播放/停止按钮** | 播放：启动文本解析与演奏；停止：中断播放并重置状态。                         |
| **帮助按钮**      | 显示快捷键说明与输入格式指南。                                               |

#### **2. 输入与控制区**  
| **组件**         | **功能描述**                                                                 |
|------------------|-----------------------------------------------------------------------------|
| **文本输入框**    | 支持手动输入或粘贴音符/和弦文本，支持多行输入。                               |
| **粘贴剪贴板**    | 手动将剪贴板内容导入文本框。                                                 |
| **自动检测剪贴板**| 勾选后每秒检查剪贴板，自动更新文本框内容（需内容非空）。                     |
| **清空按钮**      | 清除文本框内容。                                                             |

#### **3. 状态显示**  
- **连接状态**：显示MIDI设备连接情况（如“MIDI设备已连接”）。  
- **播放状态**：实时显示当前播放的字符、进度（如“正在播放 'q' (1/3)”）。  
- **错误提示**：捕获MIDI初始化失败、无效字符等异常并弹窗提醒。


### **四、代码实现细节**
#### **1. 关键类与方法**  
```python
class PianoApp:
    def __init__(self, root):
        # 初始化界面、MIDI设备、字符映射
        self.notes = {'1':60, '2':62, ...}  # 单音映射（C4-C6）
        self.chords = {'q':[60,64,67], ...} # 和弦映射（C大三和弦等）
        self.create_widgets()  # 创建GUI组件
        self.init_midi()       # 初始化MIDI输出
        self.monitor_clipboard()  # 启动剪贴板监控线程

    def init_midi(self):
        pygame.midi.init()
        output_id = pygame.midi.get_default_output_id()
        if output_id == -1:
            raise Exception("未找到MIDI设备")
        self.midi_out = pygame.midi.Output(output_id)
        self.midi_out.set_instrument(0)  # 默认钢琴音色

    def _play_thread(self, text):
        elements = text.split()
        for i, elem in enumerate(elements):
            if elem in self.notes:
                # 播放单音
                self.midi_out.note_on(self.notes[elem], 80)
                time.sleep(self.note_duration)
                self.midi_out.note_off(...)
            elif elem in self.chords:
                # 播放和弦（同时触发多个音符）
                for note in self.chords[elem]:
                    self.midi_out.note_on(note, 80)
                time.sleep(...)
                for note in self.chords[elem]:
                    self.midi_out.note_off(...)
            time.sleep(self.interval)  # 间隔时间
```

#### **2. 字符映射表**  
| **按键** | **单音（MIDI音符）** | **和弦（MIDI音符列表）**       | **说明**               |
|----------|----------------------|--------------------------------|------------------------|
| `1`      | 60（C4）             | -                              | C大调音阶             |
| `!`      | 61（C#4）            | -                              | 黑键（升C）           |
| `q`      | -                    | [60,64,67]（C-E-G）            | C大三和弦              |
| `w`      | -                    | [62,65,69]（D-F-A）            | D小三和弦              |
| `i`      | -                    | [60,64,67,71]（C-E-G-Bb）      | C七和弦                |


### **五、使用方法**
#### **1. 基础操作流程**  
1. **安装依赖**：  
   ```bash
   pip install pygame pyperclip
   ```  
2. **运行软件**：  
   直接执行脚本，弹出GUI窗口，确保系统MIDI合成器可用（Windows默认支持）。  
3. **输入乐谱文本**：  
   - 手动输入：如`"1 3 5 q w e"`（C-E-G和弦→C→Dm→Em）。  
   - 剪贴板输入：复制文本后点击“粘贴”或勾选“自动检测”。  
4. **调整参数**：  
   - 拖动滑动条设置时长和间隔，下拉菜单选择乐器（如“40-小提琴”）。  
5. **播放/停止**：  
   点击“▶️ 播放”开始演奏，“⏹️ 停止”可中断。


#### **2. 用AI生成适配的文本乐谱**  
##### **方法一：直接提示AI生成指定格式文本**  
向AI（如ChatGPT）输入以下提示：  
> 请生成一段适合智能钢琴软件的文本乐谱，要求：  
> 1. 使用数字（1-0）和字母（q-w-e-r-t-y-u-i-o-p）输入  
> 2. 包含至少3个和弦（如q/w/e）和5个单音  
> 3. 用空格分隔音符/和弦，示例格式："1 q 3 w 5 e"  

**示例输出**：  
```
2 w 4 r 6 t 8 y u 0 p
```  
（对应音符：D→Dm→F→F→A→G→C高→Am→Bdim→G7）

##### **方法二：AI解析乐谱图片生成文本**  
1. 使用OCR工具（如百度AI开放平台）识别乐谱图片，转换为音符名称（如C4、E4、G4）。  
2. 将音符名称映射为软件支持的字符：  
   - C4 → `1`，E4 → `3`，G4 → `5`（单音）  
   - C和弦（C-E-G）→ `q`，Dm和弦（D-F-A）→ `w`  
3. 组合为空格分隔的字符串（如`"1 3 5 q w e"`）。

##### **方法三：AI生成MIDI文件并转换为文本**  
1. 使用AI音乐工具（如Amper Music）生成MIDI文件。  
2. 用Python解析MIDI文件，提取音符序列和和弦：  
   ```python
   from mido import MidiFile
   mid = MidiFile('music.mid')
   text_notes = []
   for msg in mid.play():
       if msg.type == 'note_on' and msg.velocity > 0:
           # 映射MIDI音符到软件字符（需自定义映射逻辑）
           note_char = get_char_from_note(msg.note)
           text_notes.append(note_char)
   print(' '.join(text_notes))
   ```


### **六、扩展与自定义**
1. **修改字符映射**：  
   在`self.notes`和`self.chords`字典中添加新键值对，例如：  
   ```python
   self.notes['a'] = 60  # 新增A键映射C4
   self.chords['s'] = [62, 65, 69]  # 新增S键映射Dm和弦
   ```  
2. **添加新乐器**：  
   查询GM音色表（如钢琴=0，小提琴=40），在乐器选择菜单中添加选项：  
   ```python
   self.instrument_menu['values'].append("41 - 中提琴")
   ```  
3. **优化播放逻辑**：  
   添加连音（无间隔）、力度控制（`velocity`参数）等高级功能。
