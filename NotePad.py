import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog, font, colorchooser, ttk
import os
from spellchecker import SpellChecker
import difflib
import importlib

class Notepad:
    def __init__(self, root):
        self.root = root
        self.root.title("记事本")
        self.root.geometry("800x600")

        # 设置窗口图标
        self.set_icon()

        # 使用 ttk 主题
        self.style = ttk.Style()
        self.style.theme_use("clam")  # 可选主题: 'clam', 'alt', 'default', 'classic'

        # 标签页控件
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(expand=True, fill="both")

        # 状态栏
        self.status_bar = ttk.Label(self.root, text="行: 1, 列: 1", relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        # 菜单栏
        self.menu_bar = tk.Menu(self.root)
        self.root.config(menu=self.menu_bar)

        # 文件菜单
        self.file_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="文件", menu=self.file_menu)
        self.file_menu.add_command(label="新建", command=self.new_file, accelerator="Ctrl+N")
        self.file_menu.add_command(label="打开", command=self.open_file, accelerator="Ctrl+O")
        self.file_menu.add_command(label="保存", command=self.save_file, accelerator="Ctrl+S")
        self.file_menu.add_separator()
        self.file_menu.add_command(label="打印", command=self.print_file, accelerator="Ctrl+P")
        self.file_menu.add_separator()
        self.file_menu.add_command(label="退出", command=self.exit_app, accelerator="Ctrl+Q")

        # 编辑菜单
        self.edit_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="编辑", menu=self.edit_menu)
        self.edit_menu.add_command(label="撤销", command=self.undo_text, accelerator="Ctrl+Z")
        self.edit_menu.add_command(label="重做", command=self.redo_text, accelerator="Ctrl+Y")
        self.edit_menu.add_separator()
        self.edit_menu.add_command(label="剪切", command=self.cut_text, accelerator="Ctrl+X")
        self.edit_menu.add_command(label="复制", command=self.copy_text, accelerator="Ctrl+C")
        self.edit_menu.add_command(label="粘贴", command=self.paste_text, accelerator="Ctrl+V")
        self.edit_menu.add_separator()
        self.edit_menu.add_command(label="查找", command=self.find_text, accelerator="Ctrl+F")
        self.edit_menu.add_command(label="替换", command=self.replace_text, accelerator="Ctrl+H")

        # 格式菜单
        self.format_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="格式", menu=self.format_menu)
        self.format_menu.add_command(label="字体", command=self.change_font)
        self.format_menu.add_command(label="颜色", command=self.change_color)
        self.format_menu.add_command(label="切换主题", command=self.toggle_theme)

        # 工具菜单
        self.tools_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="工具", menu=self.tools_menu)
        self.tools_menu.add_command(label="拼写检查", command=self.check_spelling)
        self.tools_menu.add_command(label="文件比较", command=self.compare_files)

        # 插件菜单
        self.plugin_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="插件", menu=self.plugin_menu)
        self.plugin_menu.add_command(label="加载插件", command=self.load_plugin)

        # 绑定快捷键
        self.root.bind("<Control-n>", lambda event: self.new_file())
        self.root.bind("<Control-o>", lambda event: self.open_file())
        self.root.bind("<Control-s>", lambda event: self.save_file())
        self.root.bind("<Control-p>", lambda event: self.print_file())
        self.root.bind("<Control-q>", lambda event: self.exit_app())
        self.root.bind("<Control-z>", lambda event: self.undo_text())
        self.root.bind("<Control-y>", lambda event: self.redo_text())
        self.root.bind("<Control-x>", lambda event: self.cut_text())
        self.root.bind("<Control-c>", lambda event: self.copy_text())
        self.root.bind("<Control-v>", lambda event: self.paste_text())
        self.root.bind("<Control-f>", lambda event: self.find_text())
        self.root.bind("<Control-h>", lambda event: self.replace_text())

        # 初始化第一个标签页
        self.new_file()

        # 自动保存功能
        self.auto_save_interval = 60000  # 60秒
        self.auto_save()

        # 主题
        self.theme = "light"

        # 文件历史记录
        self.recent_files = []

        # 行号显示
        self.add_line_numbers()

    def set_icon(self):
        # 设置窗口图标（需要准备一个 .ico 文件）
        icon_path = "notepad.ico"  # 替换为你的图标路径
        if os.path.exists(icon_path):
            self.root.iconbitmap(icon_path)

    def new_file(self, event=None):
        text_area = tk.Text(self.notebook, wrap="word", undo=True, font=("Consolas", 12))
        text_area.pack(expand=True, fill="both")
        self.notebook.add(text_area, text="未命名")
        self.notebook.select(text_area)
        text_area.bind("<KeyRelease>", self.update_status_bar)
        text_area.bind("<ButtonRelease>", self.update_status_bar)

    def open_file(self, event=None):
        file_path = filedialog.askopenfilename(filetypes=[("文本文件", "*.txt"), ("所有文件", "*.*")])
        if file_path:
            with open(file_path, "r") as file:
                text_area = tk.Text(self.notebook, wrap="word", undo=True, font=("Consolas", 12))
                text_area.pack(expand=True, fill="both")
                text_area.insert(1.0, file.read())
                self.notebook.add(text_area, text=file_path.split("/")[-1])
                self.notebook.select(text_area)
                text_area.bind("<KeyRelease>", self.update_status_bar)
                text_area.bind("<ButtonRelease>", self.update_status_bar)
                self.update_recent_files(file_path)

    def save_file(self, event=None):
        current_tab = self.notebook.select()
        if current_tab:
            text_area = self.notebook.nametowidget(current_tab)
            file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("文本文件", "*.txt"), ("所有文件", "*.*")])
            if file_path:
                with open(file_path, "w") as file:
                    file.write(text_area.get(1.0, tk.END))
                self.notebook.tab(current_tab, text=file_path.split("/")[-1])

    def print_file(self):
        current_tab = self.notebook.select()
        if current_tab:
            text_area = self.notebook.nametowidget(current_tab)
            file_path = "temp_print_file.txt"
            with open(file_path, "w") as file:
                file.write(text_area.get(1.0, tk.END))
            os.startfile(file_path, "print")

    def exit_app(self, event=None):
        if messagebox.askokcancel("退出", "确定要退出吗？"):
            self.root.destroy()

    def cut_text(self, event=None):
        self.get_current_text_area().event_generate("<<Cut>>")

    def copy_text(self, event=None):
        self.get_current_text_area().event_generate("<<Copy>>")

    def paste_text(self, event=None):
        self.get_current_text_area().event_generate("<<Paste>>")

    def undo_text(self, event=None):
        self.get_current_text_area().edit_undo()

    def redo_text(self, event=None):
        self.get_current_text_area().edit_redo()

    def find_text(self, event=None):
        find_string = simpledialog.askstring("查找", "输入查找内容:")
        if find_string:
            text_area = self.get_current_text_area()
            start_pos = text_area.search(find_string, 1.0, stopindex=tk.END)
            if start_pos:
                end_pos = f"{start_pos}+{len(find_string)}c"
                text_area.tag_add(tk.SEL, start_pos, end_pos)
                text_area.mark_set(tk.INSERT, end_pos)
                text_area.see(tk.INSERT)

    def replace_text(self, event=None):
        find_string = simpledialog.askstring("替换", "输入查找内容:")
        if find_string:
            replace_string = simpledialog.askstring("替换", "输入替换内容:")
            if replace_string:
                text_area = self.get_current_text_area()
                start_pos = text_area.search(find_string, 1.0, stopindex=tk.END)
                while start_pos:
                    end_pos = f"{start_pos}+{len(find_string)}c"
                    text_area.delete(start_pos, end_pos)
                    text_area.insert(start_pos, replace_string)
                    start_pos = text_area.search(find_string, end_pos, stopindex=tk.END)

    def change_font(self):
        font_tuple = font.families()
        selected_font = simpledialog.askstring("字体", "输入字体名称:", initialvalue="Consolas")
        if selected_font and selected_font in font_tuple:
            current_font = font.Font(font=self.get_current_text_area()["font"])
            self.get_current_text_area().configure(font=(selected_font, current_font["size"]))

    def change_color(self):
        color = colorchooser.askcolor()[1]
        if color:
            self.get_current_text_area().configure(fg=color)

    def toggle_theme(self):
        if self.theme == "light":
            self.theme = "dark"
            self.root.configure(bg="#2d2d2d")
            self.get_current_text_area().configure(bg="#2d2d2d", fg="#ffffff", insertbackground="white")
        else:
            self.theme = "light"
            self.root.configure(bg="white")
            self.get_current_text_area().configure(bg="white", fg="black", insertbackground="black")

    def update_status_bar(self, event=None):
        text_area = self.get_current_text_area()
        if text_area:
            cursor_index = text_area.index(tk.INSERT)
            line, column = cursor_index.split(".")
            self.status_bar.config(text=f"行: {line}, 列: {column}")

    def auto_save(self):
        current_tab = self.notebook.select()
        if current_tab:
            text_area = self.notebook.nametowidget(current_tab)
            file_path = self.notebook.tab(current_tab, "text")
            if file_path != "未命名":
                with open(file_path, "w") as file:
                    file.write(text_area.get(1.0, tk.END))
        self.root.after(self.auto_save_interval, self.auto_save)

    def get_current_text_area(self):
        current_tab = self.notebook.select()
        if current_tab:
            return self.notebook.nametowidget(current_tab)
        return None

    def update_recent_files(self, file_path):
        if file_path in self.recent_files:
            self.recent_files.remove(file_path)
        self.recent_files.insert(0, file_path)
        if len(self.recent_files) > 5:
            self.recent_files.pop()
        self.update_file_menu()

    def update_file_menu(self):
        self.file_menu.delete(6, tk.END)  # 删除旧的记录
        for i, file_path in enumerate(self.recent_files):
            self.file_menu.add_command(label=f"{i+1}. {file_path}", command=lambda p=file_path: self.open_recent_file(p))

    def open_recent_file(self, file_path):
        with open(file_path, "r") as file:
            text_area = tk.Text(self.notebook, wrap="word", undo=True, font=("Consolas", 12))
            text_area.pack(expand=True, fill="both")
            text_area.insert(1.0, file.read())
            self.notebook.add(text_area, text=file_path.split("/")[-1])
            self.notebook.select(text_area)
            text_area.bind("<KeyRelease>", self.update_status_bar)
            text_area.bind("<ButtonRelease>", self.update_status_bar)

    def add_line_numbers(self):
        line_numbers = tk.Text(self.root, width=4, padx=5, pady=5, wrap=tk.NONE, state="disabled", bg="#f0f0f0")
        line_numbers.pack(side=tk.LEFT, fill=tk.Y)

        def update_line_numbers(event=None):
            lines = self.get_current_text_area().get(1.0, tk.END).count("\n") + 1
            line_numbers.config(state="normal")
            line_numbers.delete(1.0, tk.END)
            line_numbers.insert(1.0, "\n".join(str(i) for i in range(1, lines + 1)))
            line_numbers.config(state="disabled")

        self.get_current_text_area().bind("<KeyRelease>", update_line_numbers)
        self.get_current_text_area().bind("<MouseWheel>", update_line_numbers)

    def check_spelling(self):
        spell = SpellChecker()
        text_area = self.get_current_text_area()
        text = text_area.get(1.0, tk.END)
        for word in text.split():
            if word not in spell:
                start = text_area.search(word, 1.0, stopindex=tk.END)
                end = f"{start}+{len(word)}c"
                text_area.tag_add("misspelled", start, end)
                text_area.tag_config("misspelled", underline=True, underlinefg="red")

    def compare_files(self):
        file1 = filedialog.askopenfilename()
        file2 = filedialog.askopenfilename()
        with open(file1, "r") as f1, open(file2, "r") as f2:
            diff = difflib.unified_diff(f1.readlines(), f2.readlines())
            text_area = self.get_current_text_area()
            text_area.insert(tk.END, "".join(diff))

    def load_plugin(self):
        plugin_name = simpledialog.askstring("加载插件", "输入插件名称:")
        if plugin_name:
            try:
                plugin = importlib.import_module(plugin_name)
                plugin.run(self)
            except ImportError:
                messagebox.showerror("错误", f"无法加载插件: {plugin_name}")

if __name__ == "__main__":
    root = tk.Tk()
    notepad = Notepad(root)
    root.mainloop()