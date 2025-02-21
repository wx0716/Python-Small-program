import os
import subprocess
import sys
import tkinter as tk
from tkinter import messagebox, scrolledtext, filedialog

# frp 客户端配置文件路径
FRP_CONFIG_PATH = "frpc.ini"

# 启动 frp 客户端
def start_frp():
    if not os.path.exists(FRP_CONFIG_PATH):
        messagebox.showerror("错误", f"未找到配置文件: {FRP_CONFIG_PATH}")
        return

    try:
        # 启动 frp 客户端
        process = subprocess.Popen(
            ["frpc", "-c", FRP_CONFIG_PATH],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
        )

        # 实时显示日志
        def read_output():
            while True:
                output = process.stdout.readline()
                if output == "" and process.poll() is not None:
                    break
                if output:
                    log_text.insert(tk.END, output)
                    log_text.see(tk.END)
            process.stdout.close()

        # 启动日志读取线程
        import threading
        threading.Thread(target=read_output, daemon=True).start()

        messagebox.showinfo("成功", "frp 客户端已启动！")
    except Exception as e:
        messagebox.showerror("错误", f"启动 frp 客户端时出错:\n{str(e)}")

# 停止 frp 客户端
def stop_frp():
    try:
        if sys.platform == "win32":
            subprocess.run(["taskkill", "/IM", "frpc.exe", "/F"], check=True)
        else:
            subprocess.run(["pkill", "frpc"], check=True)
        messagebox.showinfo("成功", "frp 客户端已停止！")
    except subprocess.CalledProcessError:
        messagebox.showerror("错误", "未找到运行的 frp 客户端进程！")
    except Exception as e:
        messagebox.showerror("错误", f"停止 frp 客户端时出错:\n{str(e)}")

# 编辑配置文件
def edit_config():
    try:
        if not os.path.exists(FRP_CONFIG_PATH):
            with open(FRP_CONFIG_PATH, "w") as f:
                f.write("[common]\nserver_addr = x.x.x.x\nserver_port = 7000\n")

        # 使用系统默认编辑器打开配置文件
        if sys.platform == "win32":
            os.startfile(FRP_CONFIG_PATH)
        elif sys.platform == "darwin":
            subprocess.run(["open", FRP_CONFIG_PATH])
        else:
            subprocess.run(["xdg-open", FRP_CONFIG_PATH])
    except Exception as e:
        messagebox.showerror("错误", f"打开配置文件时出错:\n{str(e)}")

# 创建 GUI
def create_gui():
    root = tk.Tk()
    root.title("内网穿透工具")
    root.geometry("600x400")

    # 标题
    title_label = tk.Label(root, text="内网穿透工具", font=("Arial", 16))
    title_label.pack(pady=10)

    # 启动按钮
    start_button = tk.Button(root, text="启动 frp", command=start_frp, width=20, height=2)
    start_button.pack(pady=5)

    # 停止按钮
    stop_button = tk.Button(root, text="停止 frp", command=stop_frp, width=20, height=2)
    stop_button.pack(pady=5)

    # 编辑配置文件按钮
    edit_button = tk.Button(root, text="编辑配置文件", command=edit_config, width=20, height=2)
    edit_button.pack(pady=5)

    # 日志显示区域
    global log_text
    log_text = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=70, height=15)
    log_text.pack(pady=10)

    # 退出按钮
    exit_button = tk.Button(root, text="退出", command=root.quit, width=20, height=2)
    exit_button.pack(pady=5)

    root.mainloop()

# 主程序
if __name__ == "__main__":
    create_gui()