#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
低内存模式运行脚本
复用 scripts.run 中的流程，并在阶段之间自动增加延迟
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/../')

from scripts.run import run_task_low_memory


if __name__ == "__main__":
    print("开始以低内存模式运行任务...")
    success = run_task_low_memory()
    if success:
        print("任务成功完成！")
        sys.exit(0)
    else:
        print("任务执行失败！")
        sys.exit(1)
