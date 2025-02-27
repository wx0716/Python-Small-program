#!/usr/bin/env python3
# author: David Wang

import subprocess
import sys
import os
import json
import logging
import argparse
from datetime import datetime
from time import sleep
from colorama import Fore, Style, init

try:
    from tqdm import tqdm
except ImportError:
    tqdm = None

# 初始化colorama
init(autoreset=True)

# 配置文件默认路径
CONFIG_FILE = "/etc/auto_updater.conf"
BACKUP_DIR = "/var/backups/auto_updater"


def setup_logging():
    """配置日志记录系统"""
    log_format = "%(asctime)s - %(levelname)s - %(message)s"
    logging.basicConfig(
        level=logging.INFO,
        format=log_format,
        handlers=[
            logging.FileHandler("updater.log"),
            logging.StreamHandler()
        ]
    )


class EnhancedUpdater:
    def __init__(self, config_path=None):
        # 初始化日志
        self.logger = logging.getLogger(__name__)
        setup_logging()

        # 加载配置
        self.config = self.load_config(config_path)

        # 初始化进度条
        self.progress = None

    def blue(self, text):
        """带时间戳的彩色输出"""
        message = f"[{datetime.now().strftime('%H:%M:%S')}] {text}"
        print(Fore.BLUE + Style.BRIGHT + message + Style.RESET_ALL)
        self.logger.info(text)

    def run_command(self, command, sudo=False):
        """执行系统命令并处理输出"""
        try:
            if sudo:
                command = ["sudo"] + command

            self.logger.debug(f"执行命令: {' '.join(command)}")

            # 带进度显示的执行
            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True
            )

            # 实时输出处理
            while True:
                output = process.stdout.readline()
                if output == '' and process.poll() is not None:
                    break
                if output:
                    self.logger.debug(output.strip())

            if process.returncode != 0:
                raise subprocess.CalledProcessError(
                    process.returncode, command)

            return True
        except subprocess.CalledProcessError as e:
            self.logger.error(f"命令执行失败: {' '.join(e.cmd)}")
            self.logger.error(f"错误代码: {e.returncode}")
            return False

    def check_network(self):
        """网络连接检查"""
        self.blue("检查网络连接...")
        try:
            subprocess.run(
                ["ping", "-c", "3", "8.8.8.8"],
                check=True,
                stdout=subprocess.DEVNULL
            )
            return True
        except subprocess.CalledProcessError:
            self.logger.error("网络连接不可用！")
            return False

    def load_config(self, config_path=None):
        """加载配置文件"""
        default_config = {
            "packages": ["curl", "wget", "python3", "python3-pip"],
            "enable_cleanup": True,
            "backup_enabled": False,
            "exclude_packages": []
        }

        config_path = config_path or CONFIG_FILE
        try:
            with open(config_path) as f:
                return {**default_config, **json.load(f)}
        except FileNotFoundError:
            self.logger.warning(f"未找到配置文件 {config_path}，使用默认配置")
            return default_config
        except json.JSONDecodeError:
            self.logger.error("配置文件格式错误！")
            return default_config

    def create_backup(self):
        """创建系统备份"""
        if not self.config.get("backup_enabled"):
            return True

        self.blue("创建系统备份...")
        os.makedirs(BACKUP_DIR, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = os.path.join(BACKUP_DIR, f"backup_{timestamp}.tar.gz")

        cmd = [
            "tar", "czf", backup_file,
            "--exclude=/var/cache",
            "--exclude=/tmp",
            "/etc/apt/sources.list*",
            "/etc/apt/trusted.gpg*"
        ]

        if self.run_command(cmd, sudo=True):
            self.logger.info(f"备份已创建: {backup_file}")
            return True
        return False

    def show_progress(self, total):
        """显示进度条"""
        if tqdm and sys.stdout.isatty():
            self.progress = tqdm(total=total, desc="处理进度", unit="step")
        else:
            self.blue(f"开始处理（共 {total} 步）")

    def update_progress(self):
        """更新进度"""
        if self.progress:
            self.progress.update(1)
        else:
            print(".", end="", flush=True)

    def install_packages(self):
        """安装/更新软件包"""
        total_steps = len(self.config["packages"]) + 3  # 系统更新 + 清理 + 其他
        self.show_progress(total_steps)

        # 系统更新
        self.blue("\n执行系统更新")
        self.run_command(["apt", "update", "-y"], sudo=True)
        self.run_command(["apt", "full-upgrade", "-y"], sudo=True)
        self.update_progress()

        # 安装/更新软件包
        for pkg in self.config["packages"]:
            if pkg in self.config["exclude_packages"]:
                continue

            self.blue(f"\n处理软件包: {pkg}")
            if self.run_command(["apt", "install", "-y", pkg], sudo=True):
                self.run_command(["apt", "upgrade", "-y", pkg], sudo=True)
            self.update_progress()

        # Python包更新
        self.blue("\n更新Python依赖")
        self.run_command(["python3", "-m", "pip", "freeze", ">", "requirements.txt"], sudo=True)
        self.run_command(["python3", "-m", "pip", "install", "-r", "requirements.txt", "--upgrade"], sudo=True)
        os.remove("requirements.txt")
        self.update_progress()

        # 清理
        if self.config["enable_cleanup"]:
            self.blue("\n执行系统清理")
            self.run_command(["apt", "autoremove", "-y"], sudo=True)
            self.run_command(["apt", "autoclean", "-y"], sudo=True)
            self.update_progress()

        if self.progress:
            self.progress.close()

    def send_notification(self, success=True):
        """发送桌面通知（需要libnotify）"""
        if not self.config.get("enable_notifications"):
            return

        title = "系统更新完成" if success else "更新失败"
        message = "所有操作已成功完成" if success else "遇到错误，请检查日志"

        subprocess.run(
            ["notify-send", "-i", "system-software-update", title, message],
            stdout=subprocess.DEVNULL
        )

    def run(self):
        """主执行流程"""
        try:
            if not self.check_network():
                return False

            if not self.create_backup():
                self.logger.error("备份创建失败，中止操作！")
                return False

            self.install_packages()
            self.send_notification(success=True)
            return True
        except Exception as e:
            self.logger.exception("发生未处理的异常！")
            self.send_notification(success=False)
            return False


if __name__ == "__main__":
    # 解析命令行参数
    parser = argparse.ArgumentParser(description="系统自动更新工具")
    parser.add_argument("-c", "--config", help="指定配置文件路径")
    parser.add_argument("-v", "--verbose", action="store_true", help="显示详细输出")
    args = parser.parse_args()

    # 系统验证
    if os.geteuid() != 0:
        print("请使用sudo权限运行本脚本！")
        sys.exit(1)

    if not os.path.exists("/etc/debian_version"):
        print("本脚本仅适用于Debian/Ubuntu系统！")
        sys.exit(1)

    # 初始化更新器
    updater = EnhancedUpdater(args.config)
    if args.verbose:
        updater.logger.setLevel(logging.DEBUG)

    # 执行更新
    success = updater.run()
    sys.exit(0 if success else 1)