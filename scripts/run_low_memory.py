#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
低内存模式运行脚本
专门为内存受限环境（如2GB内存服务器）设计
通过分阶段执行和增加延迟来减少内存峰值使用
"""

import time
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/../')

from app_config.constant import DIR_DOWNLOAD_ZONEFILES, DIR_OUTPUT_DOMAINS_002
from util.util import FILE_OUTPUT_DOMAINS_NEW_ALL


def run_task_low_memory():
    """
    低内存模式运行任务
    分阶段执行，每个阶段之间增加延迟以释放内存
    """
    print("【1】******* 提取第一列域名 ********")
    try:
        # 动态导入以减少初始内存占用
        from scripts.extract_first_column import extract_first_column_from_directory
        # 使用较小的批处理大小以减少内存使用
        extract_first_column_from_directory(DIR_DOWNLOAD_ZONEFILES, DIR_OUTPUT_DOMAINS_002, batch_size=2000)
        print("第一列域名提取完成")
    except Exception as e:
        print(f"提取第一列域名时出错: {e}")
        return False
    
    # 增加延迟以释放内存
    print("等待5秒以释放内存...")
    time.sleep(5)
    
    print("【2】******* 查找差异域名 ********")
    try:
        # 动态导入以减少初始内存占用
        from scripts.chunked_diff_domain import diff_domains
        diff_domains()
        print("差异域名查找完成")
    except Exception as e:
        print(f"查找差异域名时出错: {e}")
        return False
    
    # 增加延迟以释放内存
    print("等待5秒以释放内存...")
    time.sleep(5)
    
    print("【3】******* 合并所有域名 ********")
    try:
        # 动态导入以减少初始内存占用
        from scripts.merge2all import merge2all
        merge2all(batch_size=2048)
        print("域名合并完成")
    except Exception as e:
        print(f"合并域名时出错: {e}")
        return False
    
    # 增加延迟以释放内存
    print("等待5秒以释放内存...")
    time.sleep(5)
    
    print("【4】******* 保存域名到数据库 ********")
    try:
        from scripts.store_domains_db import save_domains_to_db
        # 使用较小的批处理大小以减少内存使用
        save_domains_to_db(FILE_OUTPUT_DOMAINS_NEW_ALL, batch_size=200)
        print("域名保存到数据库完成")
    except Exception as e:
        print(f"保存域名到数据库时出错: {e}")
        return False
    
    # 增加延迟以释放内存
    print("等待5秒以释放内存...")
    time.sleep(5)
    
    print("【5】******* 查找重复域名 ********")
    try:
        # 动态导入以减少初始内存占用
        from scripts.find_duplicate_domains import find_duplicate
        find_duplicate(1)
        print("重复域名查找完成")
    except Exception as e:
        print(f"查找重复域名时出错: {e}")
        return False
    
    print("所有任务完成！")
    return True


if __name__ == "__main__":
    print("开始以低内存模式运行任务...")
    success = run_task_low_memory()
    if success:
        print("任务成功完成！")
        sys.exit(0)
    else:
        print("任务执行失败！")
        sys.exit(1)