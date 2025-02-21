import tkinter as tk
from tkinter import ttk, messagebox
import requests


# 获取天气数据的函数
def get_weather():
    city = city_entry.get()
    api_key = "a8585d20fa711194f184e6e1f9003783"  # 替换为你的高德API密钥
    url = f"https://restapi.amap.com/v3/weather/weatherInfo?city={city}&key={api_key}&extensions=base"

    try:
        response = requests.get(url)
        response.raise_for_status()
        weather_data = response.json()

        # 检查返回状态
        if weather_data.get("status") == "1" and weather_data.get("infocode") == "10000":
            # 解析天气数据
            weather_info = weather_data['lives'][0]
            city_name = weather_info['city']
            temperature = weather_info['temperature']
            weather_description = weather_info['weather']
            humidity = weather_info['humidity']
            wind_direction = weather_info['winddirection']
            wind_power = weather_info['windpower']

            # 显示天气信息
            weather_info_str = (
                f"城市: {city_name}\n"
                f"温度: {temperature}°C\n"
                f"天气: {weather_description}\n"
                f"湿度: {humidity}%\n"
                f"风向: {wind_direction}\n"
                f"风力: {wind_power}"
            )
            messagebox.showinfo("天气信息", weather_info_str)
        else:
            messagebox.showerror("错误", "无法获取天气数据，请检查城市名称或API密钥。")
    except requests.exceptions.RequestException as e:
        messagebox.showerror("错误", "网络连接失败，请检查网络设置。")


# 创建主窗口
root = tk.Tk()
root.title("天气查询")
root.geometry("500x300")  # 设置窗口大小
root.configure(bg="#2E3440")  # 设置背景颜色为深蓝色

# 设置字体
font_style = ("Helvetica", 14)

# 添加标题
title_label = tk.Label(
    root,
    text="天气查询工具",
    font=("Helvetica", 18, "bold"),
    bg="#2E3440",
    fg="#FFFFFF"
)
title_label.pack(pady=20)

# 创建输入框和标签
input_frame = tk.Frame(root, bg="#2E3440")
input_frame.pack(pady=10)

city_label = tk.Label(
    input_frame,
    text="城市:",
    font=font_style,
    bg="#2E3440",
    fg="#FFFFFF"
)
city_label.grid(row=0, column=0, padx=5, pady=5)

city_entry = tk.Entry(
    input_frame,
    font=font_style,
    width=20,
    bg="#4C566A",
    fg="#FFFFFF",
    relief=tk.FLAT,
    insertbackground="white"  # 设置光标颜色
)
city_entry.grid(row=0, column=1, padx=5, pady=5)

# 创建查询按钮
query_button = ttk.Button(
    root,
    text="查询天气",
    command=get_weather,
    style="Custom.TButton"
)
query_button.pack(pady=20)

# 设置按钮样式
style = ttk.Style()
style.configure(
    "Custom.TButton",
    font=font_style,
    padding=10,
    background="#5E81AC",
    foreground="#FFFFFF",
    bordercolor="#5E81AC",
    focuscolor="#5E81AC",
    relief="flat"
)
style.map(
    "Custom.TButton",
    background=[("active", "#81A1C1")],  # 鼠标悬停时的颜色
    foreground=[("active", "#FFFFFF")]
)

# 运行主循环
root.mainloop()