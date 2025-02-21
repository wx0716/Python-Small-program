import tkinter as tk
from tkinter import ttk

# 创建主窗口
root = tk.Tk()
root.title("计算器")
root.geometry("400x500")
root.configure(bg="#2E3440")  # 设置背景颜色

# 定义颜色和字体
BG_COLOR = "#2E3440"  # 背景颜色
BUTTON_COLOR = "#4C566A"  # 按钮颜色
TEXT_COLOR = "#ff7300"  # 文本颜色
BUTTON_ACTIVE_COLOR = "#5E81AC"  # 按钮点击时的颜色
FONT = ('Aria', 23, 'bold')  # 字体

# 创建显示结果的文本框
entry = ttk.Entry(root, font=FONT, justify='right', foreground=TEXT_COLOR, background=BUTTON_COLOR)
entry.grid(row=0, column=0, columnspan=4, padx=10, pady=10, sticky="nsew")

# 定义按钮的布局
buttons = [
    '1', '2', '3', '+',
    '4', '5', '6', '-',
    '7', '8', '9', '*',
    '0', '.', '=', '/'
]

# 定义按钮点击事件
def button_click(value):
    if value == '=':
        try:
            result = eval(entry.get())
            entry.delete(0, tk.END)
            entry.insert(tk.END, str(result))
        except Exception as e:
            entry.delete(0, tk.END)
            entry.insert(tk.END, "错误")
    else:
        entry.insert(tk.END, value)

# 创建按钮并添加到界面
row = 1
col = 0
for button in buttons:
    btn = tk.Button(root, text=button, font=FONT, width=5, bg=BUTTON_COLOR, fg=TEXT_COLOR,
                    activebackground=BUTTON_ACTIVE_COLOR, activeforeground=TEXT_COLOR,
                    relief='flat', borderwidth=0,
                    command=lambda b=button: button_click(b))
    btn.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")
    col += 1
    if col > 3:
        col = 0
        row += 1

# 设置网格布局的权重，使按钮可以随窗口大小调整
for i in range(4):
    root.grid_columnconfigure(i, weight=1)
for i in range(5):
    root.grid_rowconfigure(i, weight=1)

# 运行主循环
root.mainloop()