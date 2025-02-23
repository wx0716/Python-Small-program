#!/bin/bash

# 全局常量
readonly WORK_DIR="/tmp/.LemonBench"
readonly UA_BROWSER="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.87 Safari/537.36"
readonly BUILD_TIME="20200426 Intl BetaVersion"
readonly SPEEDTEST_NODES=(
    "9484:China, Jilin CU"
    "15863:China, Nanning CM"
    "26352:China, Nanjing CT"
)

# 日志函数
function log() {
    local level=$1
    local message=$2
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] [$level] $message" | tee -a "${WORK_DIR}/benchmark.log"
}

# 初始化工作目录
function init_workdir() {
    mkdir -p "$WORK_DIR"
    rm -rf "$WORK_DIR"/*
    log "INFO" "Initialized work directory: $WORK_DIR"
}

# 捕获错误并退出
function handle_error() {
    log "ERROR" "Script failed at line $1 with error code $2"
    exit 1
}
trap 'handle_error $LINENO $?' ERR

# 获取系统信息
function get_system_info() {
    log "INFO" "Collecting system information..."
    SystemInfo_GetHostname
    SystemInfo_GetCPUInfo
    SystemInfo_GetMemInfo
    SystemInfo_GetOSRelease
    SystemInfo_GetNetworkInfo
    log "INFO" "System information collected."
}

# 执行 Speedtest 测试
function run_speedtest() {
    local mode=$1
    local result_file="${WORK_DIR}/Speedtest/result.txt"

    log "INFO" "Starting Speedtest in $mode mode..."
    echo -e "\n -> Speedtest Test (${mode} Mode)\n" >>"$result_file"

    for node in "${SPEEDTEST_NODES[@]}"; do
        node_id=${node%%:*}
        node_name=${node#*:}
        log "DEBUG" "Testing node: $node_name (ID: $node_id)"
        Run_Speedtest "$node_id" "$node_name"
    done

    log "INFO" "Speedtest completed."
}

# 执行磁盘测试
function run_disk_test() {
    local mode=$1
    local result_file="${WORK_DIR}/DiskTest/result.txt"

    log "INFO" "Starting Disk Test in $mode mode..."
    echo -e "\n -> Disk Test (${mode} Mode)\n" >>"$result_file"

    if [ "$mode" = "fast" ]; then
        Run_DiskTest_DD "100MB.test" "4k" "25600" "100MB-4K Block"
        Run_DiskTest_DD "1GB.test" "1M" "1000" "1GB-1M Block"
    elif [ "$mode" = "full" ]; then
        Run_DiskTest_DD "10MB.test" "4k" "2560" "10MB-4K Block"
        Run_DiskTest_DD "10MB.test" "1M" "10" "10MB-1M Block"
        Run_DiskTest_DD "100MB.test" "4k" "25600" "100MB-4K Block"
        Run_DiskTest_DD "100MB.test" "1M" "100" "100MB-1M Block"
        Run_DiskTest_DD "1GB.test" "4k" "256000" "1GB-4K Block"
        Run_DiskTest_DD "1GB.test" "1M" "1000" "1GB-1M Block"
    fi

    log "INFO" "Disk Test completed."
}

# 主函数
function main() {
    local mode=${1:-"fast"}  # 默认模式为快速测试

    init_workdir
    get_system_info

    case "$mode" in
        fast)
            run_speedtest "fast"
            run_disk_test "fast"
            ;;
        full)
            run_speedtest "full"
            run_disk_test "full"
            ;;
        speedtest)
            run_speedtest "fast"
            ;;
        disk)
            run_disk_test "fast"
            ;;
        *)
            log "ERROR" "Invalid mode: $mode. Supported modes: fast, full, speedtest, disk"
            exit 1
            ;;
    esac

    log "INFO" "Benchmark completed successfully."
}

# 执行主函数
main "$@"