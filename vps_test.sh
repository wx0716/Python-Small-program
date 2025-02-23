#!/bin/bash

# 定义颜色输出函数
blue() {
    echo -e "\033[34m\033[01m$1\033[0m"
}
green() {
    echo -e "\033[32m\033[01m$1\033[0m"
}
yellow() {
    echo -e "\033[33m\033[01m$1\033[0m"
}
red() {
    echo -e "\033[31m\033[01m$1\033[0m"
}

# 检测系统类型
detect_system() {
    if [[ -f /etc/redhat-release ]]; then
        release="centos"
        systemPackage="yum"
        systempwd="/usr/lib/systemd/system/"
    elif grep -Eqi "debian" /etc/issue; then
        release="debian"
        systemPackage="apt-get"
        systempwd="/lib/systemd/system/"
    elif grep -Eqi "ubuntu" /etc/issue; then
        release="ubuntu"
        systemPackage="apt-get"
        systempwd="/lib/systemd/system/"
    elif grep -Eqi "centos|red hat|redhat" /etc/issue; then
        release="centos"
        systemPackage="yum"
        systempwd="/usr/lib/systemd/system/"
    elif grep -Eqi "debian" /proc/version; then
        release="debian"
        systemPackage="apt-get"
        systempwd="/lib/systemd/system/"
    elif grep -Eqi "ubuntu" /proc/version; then
        release="ubuntu"
        systemPackage="apt-get"
        systempwd="/lib/systemd/system/"
    elif grep -Eqi "centos|red hat|redhat" /proc/version; then
        release="centos"
        systemPackage="yum"
        systempwd="/usr/lib/systemd/system/"
    else
        red "不支持的系统类型！"
        exit 1
    fi
}

# 安装必要工具
install_tools() {
    green "正在安装必要工具：wget 和 curl..."
    $systemPackage -y install wget curl
    if [ $? -ne 0 ]; then
        red "安装 wget 和 curl 失败，请检查网络连接或系统配置！"
        exit 1
    fi
}

# 测速功能函数
vps_superspeed() {
    green "正在运行三网纯测速..."
    bash <(curl -Lso- https://git.io/superspeed)
}

vps_zbench() {
    green "正在运行综合性能测试..."
    wget -N --no-check-certificate https://raw.githubusercontent.com/FunctionClub/ZBench/master/ZBench-CN.sh && bash ZBench-CN.sh
}

vps_testrace() {
    green "正在运行回程路由测试..."
    wget -N --no-check-certificate https://raw.githubusercontent.com/nanqinlang-script/testrace/master/testrace.sh && bash testrace.sh
}

vps_LemonBenchIntl() {
    green "正在运行快速全方位测速..."
    curl -fsL https://ilemonra.in/LemonBenchIntl | bash -s fast
}

# 主菜单
start_menu() {
    clear
    green "=========================================================="
    red " 脚本测速会大量消耗 VPS 流量，请悉知！"
    green "=========================================================="
    blue " 1. VPS 三网纯测速    （各取部分节点 - 中文显示）"
    blue " 2. VPS 综合性能测试  （包含测速 - 英文显示）"
    blue " 3. VPS 回程路由测试  （四网测试 - 英文显示）"
    blue " 4. VPS 快速全方位测速（包含性能、回程、速度 - 英文显示）"
    yellow " 0. 退出脚本"
    echo
    read -p "请输入数字: " num
    case "$num" in
        1)
            vps_superspeed
            ;;
        2)
            vps_zbench
            ;;
        3)
            vps_testrace
            ;;
        4)
            vps_LemonBenchIntl
            ;;
        0)
            green "退出脚本。"
            exit 0
            ;;
        *)
            red "请输入正确数字！"
            sleep 2s
            start_menu
            ;;
    esac
}

# 主程序
main() {
    detect_system
    install_tools
    start_menu
}

# 执行主程序
main