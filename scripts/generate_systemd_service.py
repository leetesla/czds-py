#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
动态生成 systemd 服务文件的脚本
支持根据不同的配置生成定制化的服务文件
"""

import os
import sys
import argparse
from pathlib import Path


def generate_service_content(
    description="Daily Domain Update Service (Low Memory Mode)",
    user="ubuntu",
    group="ubuntu",
    working_directory="/var/www/czds-py",
    memory_limit="1G",
    cpu_quota=None,
    python_path=None,
    script_path=None,
    restart_policy="always",
    restart_sec=5,
    service_name="czds.service"
):
    """
    生成 systemd 服务文件内容
    
    Args:
        description: 服务描述
        user: 运行服务的用户
        group: 运行服务的用户组
        working_directory: 工作目录
        memory_limit: 内存限制
        cpu_quota: CPU 配额 (例如 "50%")
        python_path: Python 解释器路径
        script_path: 要执行的脚本路径
        restart_policy: 重启策略
        restart_sec: 重启间隔秒数
        service_name: 服务文件名
    
    Returns:
        str: 生成的服务文件内容
    """
    
    # 构建 ExecStart 命令
    exec_start = f"{python_path} {script_path}"
    
    # 生成服务文件内容
    service_content = f"""[Unit]
Description={description}
# 启动顺序和依赖关系
After=network.target

[Service]
# 1. 用户和工作目录
# 确保服务以非 root 用户运行以增加安全性
User={user}
Group={group}
WorkingDirectory={working_directory}

# 2. 内存和进程限制
# 限制内存使用
MemoryLimit={memory_limit}
"""
    
    # 如果设置了 CPU 配额，则添加
    if cpu_quota:
        service_content += "# 限制CPU使用\nCPUQuota={}\n".format(cpu_quota)
    else:
        service_content += "# 限制CPU使用\n#CPUQuota=50%\n"
    
    service_content += f"""
# 3. 如何执行你的应用
# Type=simple 是最常见的类型，systemd 认为第一个执行的进程就是主进程。
Type=simple

# ExecStart: 启动命令。**强烈建议使用虚拟环境中的 Python 解释器**。
# 使用低内存模式脚本
ExecStart={exec_start}

# 4. 重启策略
# always: 无论退出代码如何，只要服务停止，就自动重启
# on-failure: 只有在非零退出码时才重启
Restart={restart_policy}
# 设定重启前等待的秒数
RestartSec={restart_sec}

# 5. 日志设置 (可选，但推荐)
# 将日志输出到 systemd journal
StandardOutput=journal
StandardError=journal

[Install]
# WantedBy: 定义了该服务应该在哪个目标（target）被启动，
# multi-user.target 表示在系统正常启动后（非图形界面登录）启动。
WantedBy=multi-user.target
"""
    
    return service_content


def save_service_file(content, output_path, service_name="czds.service"):
    """
    保存服务文件
    
    Args:
        content: 服务文件内容
        output_path: 输出目录路径
        service_name: 服务文件名
    """
    # 确保输出目录存在
    Path(output_path).mkdir(parents=True, exist_ok=True)
    
    # 构建完整路径
    service_file_path = os.path.join(output_path, service_name)
    
    # 写入文件
    with open(service_file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    # 设置文件权限为 644
    os.chmod(service_file_path, 0o644)
    
    print(f"服务文件已生成: {service_file_path}")


def main():
    """主函数"""
    # 获取当前工作目录
    current_dir = os.getcwd()
    
    # 默认脚本路径为当前目录下的 schedule_daily_task.py
    default_script_path = os.path.join(current_dir, "schedule_daily_task.py")
    
    parser = argparse.ArgumentParser(description="动态生成 systemd 服务文件")
    parser.add_argument(
        "--description",
        default="Daily Domain Update Service (Low Memory Mode)",
        help="服务描述"
    )
    parser.add_argument(
        "--user",
        default="ubuntu",
        help="运行服务的用户"
    )
    parser.add_argument(
        "--group",
        default="ubuntu",
        help="运行服务的用户组"
    )
    parser.add_argument(
        "--working-directory",
        default=current_dir,
        help="工作目录"
    )
    parser.add_argument(
        "--memory-limit",
        default="1G",
        help="内存限制"
    )
    parser.add_argument(
        "--cpu-quota",
        help="CPU 配额 (例如 50%%)"
    )
    parser.add_argument(
        "--python-path",
        default=sys.executable,  # 使用当前 Python 解释器
        help="Python 解释器路径"
    )
    parser.add_argument(
        "--script-path",
        default=default_script_path,
        help="要执行的脚本路径"
    )
    parser.add_argument(
        "--restart-policy",
        default="always",
        help="重启策略"
    )
    parser.add_argument(
        "--restart-sec",
        type=int,
        default=5,
        help="重启间隔秒数"
    )
    parser.add_argument(
        "--output-path",
        default=".",
        help="输出目录路径"
    )
    parser.add_argument(
        "--service-name",
        default="czds.service",
        help="服务文件名"
    )
    
    args = parser.parse_args()
    
    # 生成服务文件内容
    content = generate_service_content(
        description=args.description,
        user=args.user,
        group=args.group,
        working_directory=args.working_directory,
        memory_limit=args.memory_limit,
        cpu_quota=args.cpu_quota,
        python_path=args.python_path,
        script_path=args.script_path,
        restart_policy=args.restart_policy,
        restart_sec=args.restart_sec,
        service_name=args.service_name
    )
    
    # 保存服务文件
    save_service_file(content, args.output_path, args.service_name)
    
    # 输出生成的服务文件内容
    print("\n生成的服务文件内容:")
    print("=" * 50)
    print(content)
    print("=" * 50)


if __name__ == "__main__":
    print(f"python path: {sys.executable}")
    main()