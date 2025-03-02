#!/bin/bash

# 日志文件路径
LOG_FILE="/tmp/system_update_$(date +%Y%m%d_%H%M%S).log"

# 函数：记录日志
log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a "$LOG_FILE"
}

# 函数：检查命令是否存在
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# 函数：带重试的命令执行
run_with_retry() {
    local cmd="$1"
    local max_retries=${2:-3}
    local retry_count=0

    while [ $retry_count -lt $max_retries ]; do
        if eval "$cmd"; then
            return 0
        else
            ((retry_count++))
            log "命令执行失败，正在重试 ($retry_count/$max_retries)..."
            sleep $((retry_count * 2))
        fi
    done
    log "命令重试 $max_retries 次后仍然失败"
    return 1
}

# 检查并安装缺失的命令
install_missing_commands() {
    local required_commands=(brew pip3)
    local missing_commands=()

    for cmd in "${required_commands[@]}"; do
        if ! command_exists "$cmd"; then
            missing_commands+=("$cmd")
        fi
    done

    if [ ${#missing_commands[@]} -gt 0 ]; then
        log "以下命令未安装: ${missing_commands[*]}"
        log "请先安装这些命令后再运行脚本。"
        exit 1
    fi
}

# 更新 Homebrew
update_brew() {
    log "正在更新 Homebrew..."
    if run_with_retry "brew update"; then
        log "Homebrew 更新成功。"
    else
        log "Homebrew 更新失败。"
        exit 1
    fi
}

# 升级 Homebrew 包
upgrade_brew() {
    log "正在升级 Homebrew 包..."
    if run_with_retry "brew upgrade"; then
        log "Homebrew 包升级成功。"
    else
        log "Homebrew 包升级失败。"
        exit 1
    fi
}

# 清理 Homebrew
cleanup_brew() {
    log "正在执行 Homebrew 清理..."
    brew cleanup -s 2>/dev/null
    brew autoremove 2>/dev/null
    log "Homebrew 清理完成"
}

# 更新 pip3
update_pip() {
    log "正在更新 pip3..."
    if run_with_retry "pip3 install --upgrade pip"; then
        log "pip3 更新成功。"
    else
        log "pip3 更新失败。"
        exit 1
    fi
}

# 更新 Mac App Store 应用
update_mas_apps() {
    if command_exists mas; then
        log "正在检查 Mac App Store 更新..."
        mas outdated | while read -r app; do
            app_id=$(echo "$app" | awk '{print $1}')
            app_name=$(echo "$app" | awk '{for(i=2;i<NF;i++) printf $i" "; print $NF}')
            log "正在更新 $app_name..."
            mas upgrade "$app_id"
        done
        log "Mac App Store 应用更新完成"
    else
        log "mas 未安装，跳过 Mac App Store 更新"
        log "可通过以下命令安装mas: brew install mas"
    fi
}

# 检查并安装 macOS 更新
update_macos() {
    log "正在检查 macOS 系统更新..."
    updates=$(softwareupdate -l 2>&1)

    if echo "$updates" | grep -q "No new software available"; then
        log "系统已经是最新版本"
    else
        log "发现可用系统更新:"
        echo "$updates" | grep -iB 1 "restart"
        read -rp "是否要安装系统更新？(y/n) " choice
        if [[ "$choice" =~ [Yy] ]]; then
            log "正在安装系统更新..."
            sudo softwareupdate -i -a
            log "系统更新安装完成，可能需要重启计算机"
        else
            log "已跳过系统更新"
        fi
    fi
}

# 磁盘空间检查
check_disk_space() {
    log "正在检查磁盘空间..."
    local threshold=90
    local disk_usage=$(df / | tail -1 | awk '{print $5}' | tr -d '%')

    if [ "$disk_usage" -gt "$threshold" ]; then
        log "警告：磁盘使用率超过 ${threshold}%!"
        log "建议清理磁盘空间"
    else
        log "磁盘空间正常 (使用率: ${disk_usage}%)"
    fi
}

# 配置文件备份
backup_configs() {
    local backup_dir="$HOME/ConfigBackup_$(date +%Y%m%d)"
    local config_files=(
        ~/.bash_profile
        ~/.zshrc
        ~/.ssh/config
        ~/.vimrc
    )

    log "正在备份配置文件..."
    mkdir -p "$backup_dir"

    for file in "${config_files[@]}"; do
        if [ -f "$file" ]; then
            cp -v "$file" "$backup_dir" | tee -a "$LOG_FILE"
        fi
    done

    log "配置文件备份至: $backup_dir"
}

# 清理临时文件
clean_temporary_files() {
    log "正在清理临时文件..."
    sudo rm -rf /Volumes/*/.Trashes 2>/dev/null
    sudo rm -rf ~/.Trash/* 2>/dev/null
    sudo rm -rf /private/var/log/asl/*.asl 2>/dev/null
    log "临时文件清理完成"
}

# 发送系统通知
send_notification() {
    local message="系统维护完成于 $(date +%H:%M:%S)"
    osascript -e "display notification \"$message\" with title \"系统维护\""
}

# 安全更新检查
check_security_updates() {
    log "正在检查安全更新..."
    brew update &>/dev/null
    local outdated=$(brew outdated --formula | grep -iE 'security|openssl|openssh')

    if [ -n "$outdated" ]; then
        log "发现以下安全相关更新:"
        echo "$outdated" | tee -a "$LOG_FILE"
        log "建议立即更新这些软件"
    else
        log "未发现待处理的安全更新"
    fi
}

check_internet_connection() {
    log "检查网络连接..."
    if ping -c 3 8.8.8.8 &> /dev/null; then
        log "网络连接正常"
    else
        log "网络连接失败，请检查网络设置"
        exit 1
    fi
}

update_npm_packages() {
    if command_exists npm; then
        log "更新全局npm包..."
        npm outdated -g --parseable | cut -d: -f4 | xargs npm install -g | tee -a "$LOG_FILE"
    fi
}

check_ssh_keys() {
    log "检查SSH密钥权限..."
    find ~/.ssh -type f -exec ls -l {} \; | tee -a "$LOG_FILE"

    # 检查是否存在未加密的私钥
    log "检查未加密的私钥..."
    grep -L ENCRYPTED ~/.ssh/id_* | tee -a "$LOG_FILE"
}

monitor_performance() {
    log "记录当前资源使用情况："
    top -l 1 -s 0 | head -n 10 | tee -a "$LOG_FILE"
    log "记录内存使用情况："
    vm_stat | tee -a "$LOG_FILE"
}

clean_browser_caches() {
    log "清理浏览器缓存..."
    # Chrome
    rm -rf ~/Library/Caches/Google/Chrome/* 2>/dev/null
    # Firefox
    rm -rf ~/Library/Caches/Firefox/* 2>/dev/null
    # Safari
    rm -rf ~/Library/Caches/com.apple.Safari/* 2>/dev/null
}

generate_summary() {
    log "生成维护摘要..."
    echo -e "\n=== 维护摘要 ===" | tee -a "$LOG_FILE"
    grep -E '成功|失败|警告|建议' "$LOG_FILE" | tee -a "$LOG_FILE"
    echo "完整日志请查看: $LOG_FILE" | tee -a "$LOG_FILE"
}

# 主函数
main() {
    log "=== 开始系统维护 ==="
    log "维护日志文件: $LOG_FILE"

    # 初始检查
    install_missing_commands
    check_disk_space
    backup_configs
    check_internet_connection
    update_npm_packages
    check_ssh_keys
    monitor_performance
    clean_browser_caches
    generate_summary

    # 并行执行独立任务
    log "启动并行更新任务..."
    (update_brew) &
    (update_pip) &
    (update_mas_apps) &
    wait
    log "并行更新任务完成"

    # 顺序执行依赖任务
    upgrade_brew
    cleanup_brew
    check_security_updates
    update_macos
    clean_temporary_files

    # 最终检查
    check_disk_space
    send_notification
    log "=== 系统维护完成 ==="

    # 打开日志文件
    open -a TextEdit "$LOG_FILE" 2>/dev/null || echo "可以使用以下命令查看日志: less $LOG_FILE"
}



# 执行主函数
main