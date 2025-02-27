#!/usr/bin/env python3
# author: David wang

import subprocess
import sys
from colorama import Fore, Style, init

# 初始化colorama
init(autoreset=True)


def blue(text):
    print(Fore.BLUE + Style.BRIGHT + text + Style.RESET_ALL)


def run_command(command, sudo=False):
    """执行系统命令并处理输出"""
    try:
        if sudo:
            command = ["sudo"] + command
        result = subprocess.run(
            command,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"命令执行失败: {' '.join(command)}")
        print(f"错误信息: {e.output}")
        return False


def main():
    blue("=======================================================================")
    blue("欢迎使用此脚本，脚本开始运行")
    blue("开始更新系统组件，若没有则自动跳过!")
    blue("=======================================================================")

    # 更新系统组件
    run_command(["yum", "-y", "update"], sudo=True)
    run_command(["yum", "-y", "upgrade"], sudo=True)

    blue("\n=======================================================================")
    blue("开始检测/安装curl")
    blue("=======================================================================")
    run_command(["yum", "-y", "install", "curl"], sudo=True)
    run_command(["yum", "-y", "update", "curl"], sudo=True)

    blue("\n=======================================================================")
    blue("开始检测/安装wget")
    blue("=======================================================================")
    run_command(["yum", "-y", "install", "wget"], sudo=True)

    blue("\n=======================================================================")
    blue("检测Python环境")
    blue("=======================================================================")
    run_command(["yum", "-y", "update", "python3"], sudo=True)

    blue("\n=======================================================================")
    blue("安装/更新pip3")
    blue("=======================================================================")
    run_command(["yum", "-y", "install", "python3-pip"], sudo=True)

    # 生成并更新requirements
    if run_command(["python3", "-m", "pip", "freeze", ">", "requirements.txt"], sudo=True):
        run_command(["python3", "-m", "pip", "install", "-r", "requirements.txt", "--upgrade"], sudo=True)

    blue("\n=======================================================================")
    blue("清理系统")
    blue("=======================================================================")
    run_command(["yum", "-y", "autoremove"], sudo=True)
    run_command(["rm", "-f", "requirements.txt"], sudo=True)

    blue("\n=======================================================================")
    blue("一键更新全部完成，感谢使用本脚本！")
    blue("如需再次使用，请运行本脚本即可")
    blue("=======================================================================")


if __name__ == "__main__":
    # 检测是否为root用户
    if subprocess.run(["id", "-u"], stdout=subprocess.PIPE).stdout.decode().strip() != "0":
        print("请使用sudo权限运行本脚本！")
        sys.exit(1)

    # 检查操作系统是否为CentOS
    try:
        with open("/etc/redhat-release", "r") as f:
            if "centos" not in f.read().lower():
                print("本脚本仅适用于CentOS系统！")
                sys.exit(1)
    except FileNotFoundError:
        print("未找到系统版本信息！")
        sys.exit(1)

    main()