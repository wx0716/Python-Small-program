#!/usr/bin/env python3
import os
import platform
import sys
from distro import id as distro_id

# 增强配置参数
CONFIG = {
    # 基础配置
    "project_dir": os.path.expanduser("~/my_project"),  # 项目目录
    "venv_name": "venv",  # 虚拟环境目录名
    "requirements_file": "requirements.txt",  # 依赖文件

    # 扩展功能配置
    "min_python_version": (3, 6),  # 最低Python版本要求
    "auto_generate_reqs": True,  # 自动生成requirements.txt
    "extra_services": {  # 可选安装的服务
        "postgresql": False,  # 安装PostgreSQL数据库
        "redis": False,  # 安装Redis缓存
        "nginx": False  # 安装Nginx Web服务器
    },

    # 发行版特定配置
    "pkg_manager": {
        "ubuntu": {
            "cmd": "apt-get",
            "python_pkg": ["python3", "python3-pip", "python3-venv"],
            "services": {
                "postgresql": "postgresql postgresql-contrib",
                "redis": "redis-server",
                "nginx": "nginx"
            }
        },
        "centos": {
            "cmd": "yum",
            "python_pkg": ["python3", "python3-pip"],
            "services": {
                "postgresql": "postgresql-server postgresql-contrib",
                "redis": "redis",
                "nginx": "nginx"
            }
        },
        "almalinux": {
            "cmd": "dnf",
            "python_pkg": ["python3", "python3-pip"],
            "services": {
                "postgresql": "postgresql-server postgresql-contrib",
                "redis": "redis",
                "nginx": "nginx"
            }
        }
    }
}


def get_linux_distro():
    """检测Linux发行版"""
    try:
        return distro_id().lower()
    except Exception as e:
        print(f"❌ 无法检测Linux发行版: {str(e)}")
        sys.exit(1)


def validate_python_version(min_version):
    """验证Python版本"""
    print("🔍 检查Python版本...")
    version_str = platform.python_version_tuple()
    current_version = tuple(map(int, version_str[:2]))

    if current_version < min_version:
        print(f"❌ Python版本过低 (需要 {'.'.join(map(str, min_version))}+，当前 {platform.python_version()})")
        sys.exit(1)
    print(f"✅ Python版本 {platform.python_version()} 符合要求")


def generate_requirements(venv_path):
    """自动生成requirements.txt"""
    req_path = os.path.join(CONFIG['project_dir'], CONFIG['requirements_file'])
    if not os.path.exists(req_path):
        print("📄 自动生成requirements.txt...")
        pip_path = os.path.join(venv_path, "bin", "pip")
        run_command(
            f"{pip_path} freeze > {CONFIG['requirements_file']}",
            "生成依赖文件",
            cwd=CONFIG['project_dir']
        )


def install_extra_services(distribution):
    """安装额外服务"""
    services = [k for k, v in CONFIG['extra_services'].items() if v]
    if not services:
        return

    print("🛠️  安装扩展服务...")
    distro_config = CONFIG['pkg_manager'].get(distribution, {})
    if not distro_config:
        print(f"❌ 不支持的发行版: {distribution}")
        return

    for service in services:
        pkg_name = distro_config['services'].get(service)
        if pkg_name:
            run_command(
                f"sudo {distro_config['cmd']} install -y {pkg_name}",
                f"安装 {service.upper()}"
            )
        else:
            print(f"⚠️  {service} 不支持当前发行版")


def run_command(command, description, cwd=None):
    """执行 shell 命令并处理错误（保持不变，此处省略完整实现）"""


def main():
    # 检查Python版本
    validate_python_version(CONFIG['min_python_version'])

    # 检测Linux发行版
    distro = get_linux_distro()
    print(f"🖥️  检测到系统发行版: {distro.capitalize()}")

    # 更新包列表（适配不同发行版）
    pkg_cmd = CONFIG['pkg_manager'][distro]['cmd']
    run_command(
        f"sudo {pkg_cmd} update -y",
        "更新系统包列表"
    )

    # 安装Python基础环境
    python_pkgs = " ".join(CONFIG['pkg_manager'][distro]['python_pkg'])
    run_command(
        f"sudo {pkg_cmd} install -y {python_pkgs}",
        "安装Python基础环境"
    )

    # 创建项目目录和虚拟环境（保持不变，此处省略）

    # 自动生成requirements.txt
    if CONFIG['auto_generate_reqs'] and not os.path.exists(req_path):
        generate_requirements(venv_path)

    # 安装额外服务
    install_extra_services(distro)

    # 输出使用说明（保持不变）


if __name__ == "__main__":
    main()