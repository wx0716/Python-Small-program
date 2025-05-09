# 配置区
LOG_FILE="${HOME}/system_maintenance.log"
TIMESTAMP=$(date "+%Y-%m-%d %H:%M:%S")

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # 重置颜色

# 初始化日志
echo "=== 维护开始于 ${TIMESTAMP} ===" | tee -a "${LOG_FILE}"

# 函数定义
show_help() {
    echo "用法: $0 [选项]"
    echo "选项:"
    echo "  --all       执行完整维护流程"
    echo "  --update    仅执行更新操作"
    echo "  --clean     仅执行清理操作"
    echo "  --security  仅执行安全检查"
    echo "  --help      显示帮助信息"
}

header() {
    echo -e "\n${YELLOW}▶ $1${NC}" | tee -a "${LOG_FILE}"
}

success() {
    echo -e "${GREEN}✓ $1${NC}" | tee -a "${LOG_FILE}"
}

warning() {
    echo -e "${YELLOW}⚠ $1${NC}" | tee -a "${LOG_FILE}"
}

error() {
    echo -e "${RED}✗ $1${NC}" | tee -a "${LOG_FILE}"
}

# 安装Homebrew
install_homebrew() {
    header "尝试安装Homebrew"
    
    if [ -n "$CI" ]; then
        warning "CI环境跳过交互式安装"
        return 1
    fi

    echo -e "${YELLOW}请根据提示完成Homebrew安装（需要管理员权限）${NC}"
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    
    # 配置环境变量
    if [[ -x /opt/homebrew/bin/brew ]]; then
        eval "$(/opt/homebrew/bin/brew shellenv)"
        echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zshrc
    elif [[ -x /usr/local/bin/brew ]]; then
        eval "$(/usr/local/bin/brew shellenv)"
    fi
    
    if command -v brew &> /dev/null; then
        success "Homebrew安装成功"
        return 0
    else
        error "Homebrew安装失败，请手动安装"
        return 1
    fi
}

# 安装Python
install_python() {
    header "尝试通过Homebrew安装Python"
    
    if ! command -v brew &> /dev/null; then
        error "Homebrew不可用，无法安装Python"
        return 1
    fi

    if brew install python@3.11 2>&1 | tee -a "${LOG_FILE}"; then
        # 配置环境变量
        export PATH="/usr/local/opt/python@3.11/bin:$PATH"
        echo 'export PATH="/usr/local/opt/python@3.11/bin:$PATH"' >> ~/.zshrc
        success "Python安装成功"
        
        if ! command -v python3 &> /dev/null; then
            error "Python二进制文件未找到"
            return 1
        fi
        return 0
    else
        error "Python安装失败"
        return 1
    fi
}

# 系统更新
system_update() {
    header "系统更新检查"
    if softwareupdate -l 2>&1 | tee -a "${LOG_FILE}"; then
        success "系统更新检查完成"
    else
        error "系统更新检查失败"
        return 1
    fi
}

# Homebrew维护
brew_maintenance() {
    header "Homebrew 维护"
    
    if ! command -v brew &> /dev/null; then
        warning "Homebrew未安装"
        if install_homebrew; then
            success "Homebrew已成功安装"
        else
            error "Homebrew安装失败，跳过维护"
            return 1
        fi
    fi
    
    echo "→ 更新公式列表..." | tee -a "${LOG_FILE}"
    if ! brew update 2>&1 | tee -a "${LOG_FILE}"; then
        error "brew 更新失败，中止Homebrew维护。"
        return 1
    fi
    
    echo "→ 升级软件包..." | tee -a "${LOG_FILE}"
    brew upgrade 2>&1 | tee -a "${LOG_FILE}"
    
    echo "→ 升级 GUI 应用..." | tee -a "${LOG_FILE}"
    brew upgrade --cask 2>&1 | tee -a "${LOG_FILE}"
    
    echo "→ 执行深度清理..." | tee -a "${LOG_FILE}"
    brew cleanup --prune=all 2>&1 | tee -a "${LOG_FILE}"
    success "Homebrew 维护完成"
}

# Python维护
pip_maintenance() {
    header "Python 环境维护"
    
    if ! command -v python3 &> /dev/null; then
        warning "Python 3未安装"
        if install_python; then
            success "Python已成功安装"
        else
            error "Python安装失败，跳过维护"
            return 1
        fi
    fi

    if ! command -v pip3 &> /dev/null; then
        error "pip3不可用，尝试修复..."
        if python3 -m ensurepip --upgrade 2>&1 | tee -a "${LOG_FILE}"; then
            success "pip修复成功"
        else
            error "pip修复失败"
            return 1
        fi
    fi
    
    echo "→ 升级 pip 工具链..." | tee -a "${LOG_FILE}"
    pip3 install --upgrade pip setuptools wheel 2>&1 | tee -a "${LOG_FILE}"
    
    echo "→ 批量更新 Python 包..." | tee -a "${LOG_FILE}"
    outdated_packages=$(pip3 list --outdated --format=freeze | cut -d= -f1)
    if [ -n "$outdated_packages" ]; then
        echo "检测到可升级的包: $outdated_packages" | tee -a "${LOG_FILE}"
        pip3 install -U $outdated_packages 2>&1 | tee -a "${LOG_FILE}"
    else
        success "所有 Python 包均为最新版本"
    fi
    
    success "Python 维护完成"
}

# 系统清理
system_cleanup() {
    header "系统清理"
    
    echo "→ 清理用户缓存..." | tee -a "${LOG_FILE}"
    if [ -d "${HOME}/Library/Caches" ]; then
        rm -rfv ~/Library/Caches/* 2>&1 | tee -a "${LOG_FILE}"
    else
        warning "用户缓存目录不存在，跳过清理。"
    fi
    
    echo "→ 清空下载目录30天前的文件..." | tee -a "${LOG_FILE}"
    if [ -d "${HOME}/Downloads" ]; then
        find ~/Downloads -type f -mtime +30 -exec rm -v {} \; 2>&1 | tee -a "${LOG_FILE}"
    else
        warning "下载目录不存在，跳过清理。"
    fi
    
    echo "→ 清空废纸篓..." | tee -a "${LOG_FILE}"
    if osascript -e 'tell app "Finder" to empty trash' 2>&1 | tee -a "${LOG_FILE}"; then
        success "废纸篓已清空"
    else
        error "清空废纸篓失败"
    fi
    
    success "系统清理完成"
}

# 安全检查
security_check() {
    header "安全检查"
    
    important_dirs=("/usr/local" "/usr/local/bin" "/usr/local/etc" "/Library/LaunchDaemons")
    for dir in "${important_dirs[@]}"; do
        if [ -d "$dir" ]; then
            ls -ld "$dir" | tee -a "${LOG_FILE}"
            if [ -w "$dir" ]; then
                warning "目录可写: $dir"
            fi
        else
            warning "目录不存在: $dir"
        fi
    done
    
    echo "→ 检查Python依赖漏洞..." | tee -a "${LOG_FILE}"
    
    if ! command -v safety &> /dev/null; then
        warning "safety 未安装，尝试自动安装..."
        
        if ! command -v pip3 &> /dev/null; then
            error "pip3 不可用，无法安装 safety"
            return 1
        fi
        
        install_cmd="pip3 install safety"
        echo "→ 执行安装命令: $install_cmd" | tee -a "${LOG_FILE}"
        if $install_cmd 2>&1 | tee -a "${LOG_FILE}"; then
            success "safety 安装成功"
            
            if [[ ! "$PATH" == *"$HOME/.local/bin"* ]]; then
                export PATH="$HOME/.local/bin:$PATH"
                echo "→ 临时添加用户 bin 目录到 PATH" | tee -a "${LOG_FILE}"
            fi
            
            if ! command -v safety &> /dev/null; then
                error "safety 安装后仍不可用，请尝试："
                echo "1. 重启终端会话" | tee -a "${LOG_FILE}"
                echo "2. 手动运行: source ~/.zshrc" | tee -a "${LOG_FILE}"
                return 1
            fi
        else
            error "safety 安装失败"
            echo "建议解决方法：" | tee -a "${LOG_FILE}"
            echo "1. 检查网络连接" | tee -a "${LOG_FILE}"
            echo "2. 尝试管理员安装: sudo pip3 install safety" | tee -a "${LOG_FILE}"
            return 1
        fi
    fi
    
    echo "→ 正在扫描Python依赖漏洞..." | tee -a "${LOG_FILE}"
    if safety check --full-report 2>&1 | tee -a "${LOG_FILE}"; then
        success "未发现已知漏洞"
    else
        error "发现安全漏洞或检查失败"
        return 1
    fi
    
    success "安全检查完成"
}

# 主逻辑
if [ $# -eq 0 ]; then
    show_help
    exit 1
fi

while [[ $# -gt 0 ]]; do
    case $1 in
        --all)
            system_update
            brew_maintenance
            pip_maintenance
            system_cleanup
            security_check
            shift
            ;;
        --update)
            system_update
            brew_maintenance
            pip_maintenance
            shift
            ;;
        --clean)
            system_cleanup
            shift
            ;;
        --security)
            security_check
            shift
            ;;
        --help)
            show_help
            exit 0
            ;;
        *)
            error "未知选项: $1"
            show_help
            exit 1
            ;;
    esac
done

# 收尾工作
echo -e "\n${GREEN}=== 维护完成 耗时: $SECONDS 秒 ===${NC}" | tee -a "${LOG_FILE}"
exit 0
