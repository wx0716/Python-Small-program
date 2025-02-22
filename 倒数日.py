import tkinter as tk
from tkinter import messagebox, simpledialog, ttk, filedialog
from datetime import datetime
import json
import os
import csv
from plyer import notification

# 文件路径
SAVE_FILE = "countdown_dates.json"

# 加载保存的日期
def load_dates():
    if os.path.exists(SAVE_FILE):
        with open(SAVE_FILE, "r") as file:
            return json.load(file)
    return {}

# 保存日期到文件
def save_dates(dates):
    with open(SAVE_FILE, "w") as file:
        json.dump(dates, file)

# 计算剩余天数
def calculate_days(target_date):
    try:
        target_date = datetime.strptime(target_date, "%Y-%m-%d")
        today = datetime.now()
        delta = target_date - today
        return delta.days
    except ValueError:
        return None

# 添加倒数日
def add_countdown():
    target_date = simpledialog.askstring("添加倒数日", "请输入目标日期 (YYYY-MM-DD):")
    if target_date:
        days_left = calculate_days(target_date)
        if days_left is not None:
            label = simpledialog.askstring("添加标签", "请输入标签（如生日、节日等）：")
            if not label:
                label = "未分类"
            countdown_dates[target_date] = {"days": days_left, "label": label}
            save_dates(countdown_dates)
            update_treeview()
            check_reminders()
            update_stats()
        else:
            messagebox.showerror("错误", "请输入正确的日期格式 (YYYY-MM-DD)")

# 删除倒数日
def delete_countdown():
    selected = treeview.selection()
    if selected:
        target_date = treeview.item(selected[0])["values"][0]
        del countdown_dates[target_date]
        save_dates(countdown_dates)
        update_treeview()
        update_stats()

# 编辑倒数日
def edit_countdown():
    selected = treeview.selection()
    if selected:
        target_date = treeview.item(selected[0])["values"][0]
        new_date = simpledialog.askstring("编辑倒数日", "请输入新的目标日期 (YYYY-MM-DD):", initialvalue=target_date)
        if new_date:
            days_left = calculate_days(new_date)
            if days_left is not None:
                label = simpledialog.askstring("编辑标签", "请输入新的标签：", initialvalue=countdown_dates[target_date]["label"])
                if not label:
                    label = "未分类"
                del countdown_dates[target_date]
                countdown_dates[new_date] = {"days": days_left, "label": label}
                save_dates(countdown_dates)
                update_treeview()
                check_reminders()
                update_stats()
            else:
                messagebox.showerror("错误", "请输入正确的日期格式 (YYYY-MM-DD)")

# 更新Treeview显示
def update_treeview():
    for row in treeview.get_children():
        treeview.delete(row)
    for date, data in countdown_dates.items():
        treeview.insert("", tk.END, values=(date, data["days"], data["label"]))

# 检查提醒并发送桌面通知
def check_reminders():
    for date, data in countdown_dates.items():
        if data["days"] <= 7:
            notification_title = f"倒数日提醒: {data['label']}"
            notification_message = f"距离 {date} 还有 {data['days']} 天！"
            notification.notify(
                title=notification_title,
                message=notification_message,
                timeout=10  # 通知显示时间（秒）
            )

# 导出为CSV
def export_to_csv():
    file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV Files", "*.csv")])
    if file_path:
        with open(file_path, mode="w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["目标日期", "剩余天数", "标签"])
            for date, data in countdown_dates.items():
                writer.writerow([date, data["days"], data["label"]])

# 按钮悬停动画
def on_enter(event):
    widget = event.widget
    current_color = widget.cget("background")
    if current_color != "#45a049":  # 避免重复触发
        animate_button(widget, current_color, "#45a049")

def on_leave(event):
    widget = event.widget
    current_color = widget.cget("background")
    if current_color != "#4CAF50":  # 避免重复触发
        animate_button(widget, current_color, "#4CAF50")

def animate_button(widget, start_color, end_color):
    if start_color == end_color:
        return
    # 计算颜色渐变
    r1, g1, b1 = widget.winfo_rgb(start_color)
    r2, g2, b2 = widget.winfo_rgb(end_color)
    r_diff = (r2 - r1) / 10
    g_diff = (g2 - g1) / 10
    b_diff = (b2 - b1) / 10

    def update_color(step):
        if step <= 10:
            r = int(r1 + r_diff * step)
            g = int(g1 + g_diff * step)
            b = int(b1 + b_diff * step)
            color = f"#{r:04x}{g:04x}{b:04x}"[:7]  # 转换为16进制颜色
            widget.config(background=color)
            widget.after(20, update_color, step + 1)

    update_color(1)

# 窗口启动动画
def fade_in(window, alpha):
    if alpha < 1.0:
        alpha += 0.02
        window.attributes("-alpha", alpha)
        window.after(20, fade_in, window, alpha)

# 窗口关闭动画
def fade_out(window, alpha):
    if alpha > 0.0:
        alpha -= 0.02
        window.attributes("-alpha", alpha)
        window.after(20, fade_out, window, alpha)
    else:
        window.destroy()

# 按钮点击动画
def on_click(event):
    widget = event.widget
    widget.config(relief=tk.SUNKEN)
    widget.after(100, lambda: widget.config(relief=tk.RAISED))

# 切换主题
def toggle_theme():
    if style.theme_use() == "clam":
        style.theme_use("alt")
        root.configure(bg="#2d2d2d")
        current_date_label.config(bg="#2d2d2d", fg="white")
        stats_label.config(bg="#2d2d2d", fg="white")
        button_frame.config(bg="#2d2d2d")
    else:
        style.theme_use("clam")
        root.configure(bg="#f0f0f0")
        current_date_label.config(bg="#f0f0f0", fg="#007acc")
        stats_label.config(bg="#f0f0f0", fg="black")
        button_frame.config(bg="#f0f0f0")

# 数据备份
def backup_data():
    file_path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON Files", "*.json")])
    if file_path:
        with open(file_path, "w") as file:
            json.dump(countdown_dates, file)
        messagebox.showinfo("备份成功", f"数据已备份到 {file_path}")

# 数据恢复
def restore_data():
    file_path = filedialog.askopenfilename(filetypes=[("JSON Files", "*.json")])
    if file_path:
        with open(file_path, "r") as file:
            global countdown_dates
            countdown_dates = json.load(file)
        save_dates(countdown_dates)
        update_treeview()
        update_stats()
        messagebox.showinfo("恢复成功", f"数据已从 {file_path} 恢复")

# 更新统计数据
def update_stats():
    total_count = len(countdown_dates)
    upcoming_count = sum(1 for data in countdown_dates.values() if data["days"] <= 7)
    stats_label.config(text=f"总数量: {total_count} | 即将到期: {upcoming_count}")

# 创建主窗口
root = tk.Tk()
root.title("倒数日管理器")
root.geometry("800x600")
root.configure(bg="#f0f0f0")  # 设置背景颜色

# 窗口启动动画
root.attributes("-alpha", 0.0)  # 初始透明度为0
fade_in(root, 0.0)

# 加载保存的日期
countdown_dates = load_dates()

# 设置主题
style = ttk.Style()
style.theme_use("clam")  # 使用现代主题
style.configure("TButton", font=("Segoe UI", 10), background="#4CAF50", foreground="white", anchor="center", borderwidth=0, focusthickness=0, focuscolor="none", padding=10, relief="flat")  # 按钮样式
style.map("TButton", background=[("active", "#45a049")])  # 按钮悬停效果
style.configure("Treeview", font=("Segoe UI", 10), rowheight=25, anchor="center", background="#ffffff", fieldbackground="#ffffff", foreground="#000000")  # Treeview样式
style.configure("Treeview.Heading", font=("Segoe UI", 12, "bold"), anchor="center", background="#4CAF50", foreground="white")  # Treeview标题样式

# 顶部区域
top_frame = tk.Frame(root, bg="#f0f0f0")
top_frame.pack(fill=tk.X, padx=10, pady=10)

# 当前日期标签
current_date_label = tk.Label(
    top_frame,
    text=f"当前日期: {datetime.now().strftime('%Y-%m-%d')}",
    font=("Segoe UI", 12),
    bg="#f0f0f0",  # 背景颜色
    fg="#007acc"   # 字体颜色调整为浅蓝色
)
current_date_label.pack(side=tk.LEFT, padx=10)

# 统计数据标签
stats_label = tk.Label(
    top_frame,
    text="",
    font=("Segoe UI", 12),
    bg="#f0f0f0",
    fg="black"
)
stats_label.pack(side=tk.RIGHT, padx=10)

# 中部区域
middle_frame = tk.Frame(root, bg="#f0f0f0")
middle_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

# Treeview显示倒数日
columns = ("目标日期", "剩余天数", "标签")
treeview = ttk.Treeview(middle_frame, columns=columns, show="headings")
treeview.heading("目标日期", text="目标日期", anchor="center")
treeview.heading("剩余天数", text="剩余天数", anchor="center")
treeview.heading("标签", text="标签", anchor="center")
treeview.column("目标日期", anchor="center")
treeview.column("剩余天数", anchor="center")
treeview.column("标签", anchor="center")
treeview.pack(fill=tk.BOTH, expand=True)

# 底部区域
bottom_frame = tk.Frame(root, bg="#f0f0f0")
bottom_frame.pack(fill=tk.X, padx=10, pady=10)

# 按钮框架
button_frame = tk.Frame(bottom_frame, bg="#f0f0f0")
button_frame.pack()

# 添加按钮
add_button = ttk.Button(button_frame, text="添加倒数日", command=add_countdown)
add_button.grid(row=0, column=0, padx=5, pady=5)
add_button.bind("<Enter>", on_enter)
add_button.bind("<Leave>", on_leave)
add_button.bind("<Button-1>", on_click)

# 删除按钮
delete_button = ttk.Button(button_frame, text="删除倒数日", command=delete_countdown)
delete_button.grid(row=0, column=1, padx=5, pady=5)
delete_button.bind("<Enter>", on_enter)
delete_button.bind("<Leave>", on_leave)
delete_button.bind("<Button-1>", on_click)

# 编辑按钮
edit_button = ttk.Button(button_frame, text="编辑倒数日", command=edit_countdown)
edit_button.grid(row=0, column=2, padx=5, pady=5)
edit_button.bind("<Enter>", on_enter)
edit_button.bind("<Leave>", on_leave)
edit_button.bind("<Button-1>", on_click)

# 导出按钮
export_button = ttk.Button(button_frame, text="导出为CSV", command=export_to_csv)
export_button.grid(row=0, column=3, padx=5, pady=5)
export_button.bind("<Enter>", on_enter)
export_button.bind("<Leave>", on_leave)
export_button.bind("<Button-1>", on_click)

# 主题切换按钮
theme_button = ttk.Button(button_frame, text="切换主题", command=toggle_theme)
theme_button.grid(row=0, column=4, padx=5, pady=5)
theme_button.bind("<Enter>", on_enter)
theme_button.bind("<Leave>", on_leave)
theme_button.bind("<Button-1>", on_click)

# 数据备份按钮
backup_button = ttk.Button(button_frame, text="备份数据", command=backup_data)
backup_button.grid(row=0, column=5, padx=5, pady=5)
backup_button.bind("<Enter>", on_enter)
backup_button.bind("<Leave>", on_leave)
backup_button.bind("<Button-1>", on_click)

# 数据恢复按钮
restore_button = ttk.Button(button_frame, text="恢复数据", command=restore_data)
restore_button.grid(row=0, column=6, padx=5, pady=5)
restore_button.bind("<Enter>", on_enter)
restore_button.bind("<Leave>", on_leave)
restore_button.bind("<Button-1>", on_click)

# 初始化Treeview
update_treeview()

# 更新统计数据
update_stats()

# 检查提醒
check_reminders()

# 窗口关闭动画
root.protocol("WM_DELETE_WINDOW", lambda: fade_out(root, 1.0))

# 运行主循环
root.mainloop()