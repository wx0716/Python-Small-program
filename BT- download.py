import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import libtorrent as lt
import threading
import time
import os

class BitTorrentDownloaderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("BT Downloader")
        self.root.geometry("600x400")
        self.root.configure(bg="#f0f0f0")

        # 初始化 libtorrent 会话
        self.session = lt.session()
        self.session.listen_on(6881, 6891)
        self.handles = {}  # 存储所有下载任务的句柄
        self.load_resume_data()  # 加载断点续传数据

        # 创建 GUI 组件
        self.create_widgets()

    def create_widgets(self):
        """创建 GUI 组件"""
        # 顶部工具栏
        toolbar = tk.Frame(self.root, bg="#e0e0e0", bd=1, relief=tk.RAISED)
        toolbar.pack(side=tk.TOP, fill=tk.X)

        # 添加 Torrent 文件按钮
        btn_add_torrent = tk.Button(
            toolbar, text="Add Torrent", command=self.add_torrent, bg="#4CAF50", fg="white"
        )
        btn_add_torrent.pack(side=tk.LEFT, padx=5, pady=5)

        # 添加磁力链接按钮
        btn_add_magnet = tk.Button(
            toolbar, text="Add Magnet", command=self.add_magnet, bg="#2196F3", fg="white"
        )
        btn_add_magnet.pack(side=tk.LEFT, padx=5, pady=5)

        # 下载速度限制输入框
        self.dl_limit_var = tk.StringVar()
        tk.Label(toolbar, text="DL Limit (kB/s):", bg="#e0e0e0").pack(side=tk.LEFT, padx=5, pady=5)
        entry_dl_limit = tk.Entry(toolbar, textvariable=self.dl_limit_var, width=10)
        entry_dl_limit.pack(side=tk.LEFT, padx=5, pady=5)
        btn_set_dl_limit = tk.Button(
            toolbar, text="Set", command=self.set_download_limit, bg="#FF9800", fg="white"
        )
        btn_set_dl_limit.pack(side=tk.LEFT, padx=5, pady=5)

        # 上传速度限制输入框
        self.ul_limit_var = tk.StringVar()
        tk.Label(toolbar, text="UL Limit (kB/s):", bg="#e0e0e0").pack(side=tk.LEFT, padx=5, pady=5)
        entry_ul_limit = tk.Entry(toolbar, textvariable=self.ul_limit_var, width=10)
        entry_ul_limit.pack(side=tk.LEFT, padx=5, pady=5)
        btn_set_ul_limit = tk.Button(
            toolbar, text="Set", command=self.set_upload_limit, bg="#FF9800", fg="white"
        )
        btn_set_ul_limit.pack(side=tk.LEFT, padx=5, pady=5)

        # 下载任务列表
        self.tree = ttk.Treeview(
            self.root, columns=("Name", "Progress", "DL Rate", "UL Rate", "Peers"), show="headings"
        )
        self.tree.heading("Name", text="Name")
        self.tree.heading("Progress", text="Progress")
        self.tree.heading("DL Rate", text="DL Rate (kB/s)")
        self.tree.heading("UL Rate", text="UL Rate (kB/s)")
        self.tree.heading("Peers", text="Peers")
        self.tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 底部状态栏
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        status_bar = tk.Label(
            self.root, textvariable=self.status_var, bd=1, relief=tk.SUNKEN, anchor=tk.W, bg="#e0e0e0"
        )
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        # 启动下载监控线程
        self.monitor_thread = threading.Thread(target=self.monitor_downloads, daemon=True)
        self.monitor_thread.start()

    def add_torrent(self):
        """添加 Torrent 文件"""
        torrent_file = filedialog.askopenfilename(filetypes=[("Torrent files", "*.torrent")])
        if torrent_file:
            try:
                info = lt.torrent_info(torrent_file)
                params = {
                    'ti': info,
                    'save_path': os.getcwd(),
                    'storage_mode': lt.storage_mode_t.storage_mode_sparse,
                }
                handle = self.session.add_torrent(params)
                self.handles[torrent_file] = handle
                self.tree.insert("", "end", values=(handle.name(), "0%", "0", "0", "0"))
                self.status_var.set(f"Added torrent: {handle.name()}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to add torrent: {e}")

    def add_magnet(self):
        """添加磁力链接"""
        magnet_link = tk.simpledialog.askstring("Add Magnet", "Enter magnet link:")
        if magnet_link:
            try:
                params = {
                    'url': magnet_link,
                    'save_path': os.getcwd(),
                    'storage_mode': lt.storage_mode_t.storage_mode_sparse,
                }
                handle = self.session.add_torrent(params)
                self.handles[magnet_link] = handle
                self.tree.insert("", "end", values=(handle.name(), "0%", "0", "0", "0"))
                self.status_var.set(f"Added magnet link: {magnet_link}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to add magnet link: {e}")

    def set_download_limit(self):
        """设置下载速度限制"""
        try:
            rate_kbps = int(self.dl_limit_var.get())
            self.session.set_download_rate_limit(rate_kbps * 1024)
            self.status_var.set(f"Download rate limit set to {rate_kbps} kB/s")
        except ValueError:
            messagebox.showerror("Error", "Invalid download rate limit")

    def set_upload_limit(self):
        """设置上传速度限制"""
        try:
            rate_kbps = int(self.ul_limit_var.get())
            self.session.set_upload_rate_limit(rate_kbps * 1024)
            self.status_var.set(f"Upload rate limit set to {rate_kbps} kB/s")
        except ValueError:
            messagebox.showerror("Error", "Invalid upload rate limit")

    def monitor_downloads(self):
        """监控下载进度"""
        while True:
            for item in self.tree.get_children():
                torrent_input = self.tree.item(item, "text")
                if torrent_input in self.handles:
                    handle = self.handles[torrent_input]
                    s = handle.status()
                    self.tree.item(
                        item,
                        values=(
                            handle.name(),
                            f"{s.progress * 100:.2f}%",
                            f"{s.download_rate / 1000:.2f}",
                            f"{s.upload_rate / 1000:.2f}",
                            s.num_peers,
                        ),
                    )
            time.sleep(1)

    def save_resume_data(self):
        """保存断点续传数据"""
        resume_data = {}
        for torrent_input, handle in self.handles.items():
            if handle.is_valid() and handle.has_metadata():
                resume_data[torrent_input] = lt.bencode(handle.write_resume_data())
        with open("resume_data.dat", "wb") as f:
            f.write(lt.bencode(resume_data))

    def load_resume_data(self):
        """加载断点续传数据"""
        if os.path.exists("resume_data.dat"):
            with open("resume_data.dat", "rb") as f:
                resume_data = lt.bdecode(f.read())
                for torrent_input, data in resume_data.items():
                    params = {
                        'resume_data': data,
                        'save_path': os.getcwd(),
                        'storage_mode': lt.storage_mode_t.storage_mode_sparse,
                    }
                    handle = self.session.add_torrent(params)
                    self.handles[torrent_input] = handle
                    self.tree.insert("", "end", values=(handle.name(), "0%", "0", "0", "0"))

    def on_closing(self):
        """关闭窗口时保存断点续传数据"""
        self.save_resume_data()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = BitTorrentDownloaderApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()