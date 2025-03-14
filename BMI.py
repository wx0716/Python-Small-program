import tkinter as tk
from tkinter import messagebox


def calculate_bmi():
    try:
        weight = float(entry_weight.get())
        height = float(entry_height.get())

        if weight <= 0 or height <= 0:
            messagebox.showerror("错误", "请输入有效的正数值")
            return

        bmi = weight / (height ** 2)
        result = f"BMI指数: {bmi:.2f}\n"

        if bmi < 18.5:
            category = "体重过轻"
            advice = "请注意营养摄入"
            color = "orange"
        elif 18.5 <= bmi < 24:
            category = "正常范围"
            advice = "请保持健康的生活方式！"
            color = "green"
        elif 24 <= bmi < 28:
            category = "超重"
            advice = "建议适当运动和控制饮食"
            color = "#FFD700"  # 金色
        else:
            category = "肥胖"
            advice = "建议咨询医生或营养师"
            color = "red"

        label_result.config(text=f"{result}状态: {category}\n建议: {advice}", fg=color)

    except ValueError:
        messagebox.showerror("错误", "请输入有效的数字")


# 创建主窗口
window = tk.Tk()
window.title("BMI计算器")
window.geometry("400x300")

# 设置字体样式
font_style = ("Microsoft YaHei", 10)

# 输入区域框架
frame_input = tk.Frame(window)
frame_input.pack(pady=20)

tk.Label(frame_input, text="体重 (kg):", font=font_style).grid(row=0, column=0, padx=5, pady=5)
entry_weight = tk.Entry(frame_input, font=font_style, width=15)
entry_weight.grid(row=0, column=1, padx=5, pady=5)

tk.Label(frame_input, text="身高 (m):", font=font_style).grid(row=1, column=0, padx=5, pady=5)
entry_height = tk.Entry(frame_input, font=font_style, width=15)
entry_height.grid(row=1, column=1, padx=5, pady=5)

# 计算按钮
btn_calculate = tk.Button(window, text="计算BMI", command=calculate_bmi,
                          font=("Microsoft YaHei", 10, "bold"), bg="#4CAF50", fg="white")
btn_calculate.pack(pady=10)

# 结果展示区域
label_result = tk.Label(window, font=("Microsoft YaHei", 12), justify="left")
label_result.pack(pady=20)

# 版权信息
tk.Label(window, text="© BMI计算器 1.0", font=("Microsoft YaHei", 8), fg="gray").pack(side="bottom", pady=5)

window.mainloop()