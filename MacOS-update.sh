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

# 检查并安装缺失的命令
install_missing_commands() {
    local missing_commands=()
    for cmd in brew pip3; do
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
    if brew update; then
        log "Homebrew 更新成功。"
    else
        log "Homebrew 更新失败。"
        exit 1
    fi
}

# 升级 Homebrew 包
upgrade_brew() {
    log "正在升级 Homebrew 包..."
    if brew upgrade; then
        log "Homebrew 包升级成功。"
    else
        log "Homebrew 包升级失败。"
        exit 1
    fi
}

# 清理 Homebrew
cleanup_brew() {
    log "正在清理 Homebrew..."
    if brew cleanup; then
        log "Homebrew 清理成功。"
    else
        log "Homebrew 清理失败。"
        exit 1
    fi
}

# 更新 pip3
update_pip() {
    log "正在更新 pip3..."
    if pip3 install --upgrade pip; then
        log "pip3 更新成功。"
    else
        log "pip3 更新失败。"
        exit 1
    fi
}

# 主函数
main() {
    log "开始系统更新和维护..."

    # 检查必要的命令是否存在
    install_missing_commands

    # 并行执行 brew update 和 pip3 install --upgrade pip
    log "并行执行 brew update 和 pip3 install --upgrade pip..."
    if (update_brew & update_pip & wait); then
        log "并行任务执行完成。"
    else
        log "并行任务执行失败。"
        exit 1
    fi

    # 升级 Homebrew 包
    upgrade_brew

    # 清理 Homebrew
    cleanup_brew

    log "系统更新和维护完成。"
}

# 执行主函数
main
