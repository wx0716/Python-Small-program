import tkinter as tk
from tkinter import ttk, messagebox
import time
import winsound  # 用于播放声音（仅适用于Windows）
from datetime import datetime, timedelta

# 闹钟功能
def set_alarm():
    try:
        # 获取用户输入的时间
        alarm_hour = hour_entry.get()
        alarm_minute = minute_entry.get()
        alarm_second = second_entry.get()

        # 检查输入是否为空
        if not alarm_hour or not alarm_minute or not alarm_second:
            raise ValueError("请输入完整的时间（小时、分钟、秒）！")

        # 转换为整数
        alarm_hour = int(alarm_hour)
        alarm_minute = int(alarm_minute)
        alarm_second = int(alarm_second)

        # 验证输入是否有效
        if not (0 <= alarm_hour < 24 and 0 <= alarm_minute < 60 and 0 <= alarm_second < 60):
            raise ValueError("请输入有效的时间（小时: 0-23, 分钟: 0-59, 秒: 0-59）！")

        # 计算目标时间
        now = datetime.now()
        alarm_time = now.replace(hour=alarm_hour, minute=alarm_minute, second=alarm_second, microsecond=0)

        # 如果目标时间已经过去，则设置为第二天
        if alarm_time < now:
            alarm_time += timedelta(days=1)

        # 计算剩余时间（秒）
        delta = (alarm_time - now).total_seconds()
        messagebox.showinfo("闹钟设置", f"闹钟已设置，将在 {int(delta)} 秒后响铃。")
        root.after(int(delta * 1000), trigger_alarm)
    except ValueError as e:
        messagebox.showerror("错误", str(e))

def trigger_alarm():
    messagebox.showinfo("时间到", "时间到！")
    winsound.Beep(1000, 2000)  # 播放声音（频率1000Hz，持续2秒）

# 计时器功能
def start_timer():
    try:
        timer_time = timer_entry.get()

        # 检查输入是否为空
        if not timer_time:
            raise ValueError("请输入计时器时间！")

        # 转换为整数
        timer_time = int(timer_time)

        # 验证输入是否有效
        if timer_time <= 0:
            raise ValueError("请输入有效的正整数！")

        timer_label.config(text=f"剩余时间: {timer_time} 秒")
        countdown(timer_time)
    except ValueError as e:
        messagebox.showerror("错误", str(e))

def countdown(remaining):
    if remaining > 0:
        timer_label.config(text=f"剩余时间: {remaining} 秒")
        root.after(1000, countdown, remaining - 1)
    else:
        timer_label.config(text="时间到！")
        winsound.Beep(1000, 2000)  # 播放声音（频率1000Hz，持续2秒）

# 秒表功能
def start_stopwatch():
    global stopwatch_running, start_time
    if not stopwatch_running:
        stopwatch_running = True
        start_time = time.time()
        stopwatch_label.config(text="秒表已启动...")
        update_stopwatch()
    else:
        stopwatch_running = False
        elapsed_time = time.time() - start_time
        stopwatch_label.config(text=f"经过时间: {elapsed_time:.2f} 秒")

def update_stopwatch():
    if stopwatch_running:
        elapsed_time = time.time() - start_time
        stopwatch_label.config(text=f"经过时间: {elapsed_time:.2f} 秒")
        root.after(100, update_stopwatch)

# 创建主窗口
root = tk.Tk()
root.title("多功能闹钟程序")
root.geometry("500x400")
root.configure(bg="#f0f0f0")

# 设置现代主题
style = ttk.Style()
style.theme_use("clam")  # 使用现代主题
style.configure("TFrame", background="#f0f0f0")
style.configure("TLabel", background="#f0f0f0", font=("Helvetica", 12))
style.configure("TButton", font=("Helvetica", 12), padding=5)
style.configure("TEntry", font=("Helvetica", 12), padding=5)

# 设置字体样式
font_style = ("Helvetica", 12)

# 闹钟部分
alarm_frame = ttk.LabelFrame(root, text="闹钟", padding=10)
alarm_frame.pack(pady=10, fill="x", padx=10)

ttk.Label(alarm_frame, text="小时:").grid(row=0, column=0, padx=5, pady=5)
hour_entry = ttk.Entry(alarm_frame, width=5, font=font_style)
hour_entry.grid(row=0, column=1, padx=5, pady=5)

ttk.Label(alarm_frame, text="分钟:").grid(row=0, column=2, padx=5, pady=5)
minute_entry = ttk.Entry(alarm_frame, width=5, font=font_style)
minute_entry.grid(row=0, column=3, padx=5, pady=5)

ttk.Label(alarm_frame, text="秒:").grid(row=0, column=4, padx=5, pady=5)
second_entry = ttk.Entry(alarm_frame, width=5, font=font_style)
second_entry.grid(row=0, column=5, padx=5, pady=5)

ttk.Button(alarm_frame, text="设置闹钟", command=set_alarm).grid(row=0, column=6, padx=10)

# 计时器部分
timer_frame = ttk.LabelFrame(root, text="计时器", padding=10)
timer_frame.pack(pady=10, fill="x", padx=10)

ttk.Label(timer_frame, text="设置计时器时间（秒）:").grid(row=0, column=0, padx=5, pady=5)
timer_entry = ttk.Entry(timer_frame, width=10, font=font_style)
timer_entry.grid(row=0, column=1, padx=5, pady=5)
ttk.Button(timer_frame, text="启动计时器", command=start_timer).grid(row=0, column=2, padx=10)

timer_label = ttk.Label(timer_frame, text="剩余时间: 0 秒", font=font_style)
timer_label.grid(row=1, column=0, columnspan=3, pady=5)

# 秒表部分
stopwatch_frame = ttk.LabelFrame(root, text="秒表", padding=10)
stopwatch_frame.pack(pady=10, fill="x", padx=10)

stopwatch_running = False
start_time = 0
ttk.Button(stopwatch_frame, text="启动/停止秒表", command=start_stopwatch).pack(pady=5)
stopwatch_label = ttk.Label(stopwatch_frame, text="经过时间: 0.00 秒", font=font_style)
stopwatch_label.pack(pady=5)

# 运行主循环
root.mainloop()