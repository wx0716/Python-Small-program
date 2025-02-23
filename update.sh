#!/usr/bin/bash
# author: David Wang

# 定义颜色输出函数
blue() {
    echo -e "\033[34m\033[01m$1\033[0m"  # 蓝色字体
}

# 定义安装或更新函数
install_or_update() {
    local name=$1
    local command=$2
    local install_command=$3

    blue "======================================================================="
    blue "开始检测是否安装了$name，若无则安装，如有则更新!"
    blue "======================================================================="

    if command -v $command &> /dev/null; then
        blue "$name 已安装，正在更新..."
        sudo apt upgrade -y $command
    else
        blue "$name 未安装，正在安装..."
        sudo apt install -y $install_command
    fi
}

# 更新系统组件
blue "======================================================================="
blue "欢迎使用此脚本，脚本开始运行"
blue "开始更新系统组件，若没有则自动跳过!"
blue "======================================================================="

sudo apt update -y && sudo apt full-upgrade -y

# 安装或更新 curl
install_or_update "curl" "curl" "curl"

# 安装或更新 wget
install_or_update "wget" "wget" "wget"

# 安装或更新 Python3 和 pip
blue "======================================================================="
blue "开始检测是否安装了python3和pip，若无则安装如有则更新!"
blue "======================================================================="

if command -v python3 &> /dev/null; then
    blue "Python3 已安装，正在更新..."
    sudo apt upgrade -y python3
else
    blue "Python3 未安装，正在安装..."
    sudo apt install -y python3
fi

if command -v pip3 &> /dev/null; then
    blue "pip3 已安装，正在更新..."
    sudo python3 -m pip install --upgrade pip
else
    blue "pip3 未安装，正在安装..."
    sudo apt install -y python3-pip
fi

# 更新 Python 包
blue "======================================================================="
blue "正在更新 Python 包..."
blue "======================================================================="

sudo python3 -m pip freeze > requirements.txt
sudo python3 -m pip install -r requirements.txt --upgrade
rm -f requirements.txt

# 清除垃圾文件
blue "======================================================================="
blue "开始清除垃圾文件"
blue "======================================================================="

sudo apt autoremove -y
sudo apt autoclean -y

# 脚本结束
blue "======================================================================="
blue "一键更新全部更新安装完毕，感谢您使用此脚本，欢迎再次使用此脚本。"
blue "如需再次使用此脚本，只需输入 bash update.sh 命令即可再次使用。"
blue "======================================================================="