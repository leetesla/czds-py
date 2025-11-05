#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
快速比较两个域名列表文件，找出新增的域名
使用高效的算法处理大文件，避免占用过多内存

使用方法:
python3 fast_diff_domain.py [旧日期] [新日期] [后缀]

例如: python3 fast_diff_domain.py 251019 251021 org

如果不提供参数，则默认使用 251019 和 251021 的 org 域名文件
"""

import os
import sys
from collections import defaultdict

from app_config.config import load_config


def filter_domain(domain):
    """
    过滤域名：排除点号数量超过2个的域名，以及含有双连字符的域名
    
    Args:
        domain (str): 域名
        
    Returns:
        bool: True表示保留该域名，False表示过滤掉
    """
    # 计算点号数量
    dot_count = domain.count('.')
    
    # 检查是否含有双连字符
    has_double_dash = '--' in domain
    
    # 保留点号数量不超过2个且不含有双连字符的域名
    return dot_count <= 2 and not has_double_dash

def find_new_domains(old_file, new_file, output_file):
    """
    比较两个域名文件，找出新增的域名
    
    Args:
        old_file (str): 旧域名文件路径
        new_file (str): 新域名文件路径
        output_file (str): 输出文件路径
    """
    # 检查输入文件是否存在
    if not os.path.exists(old_file):
        print(f"错误: 找不到初始域名文件 {old_file}")
        return False
        
    if not os.path.exists(new_file):
        print(f"错误: 找不到新域名文件 {new_file}")
        return False
    
    print("正在比较域名列表:")
    print(f"  初始列表: {old_file}")
    print(f"  新列表: {new_file}")
    print(f"  输出文件: {output_file}")
    
    # 获取文件行数（去重前）
    with open(old_file, 'r', encoding='utf-8') as f:
        old_lines = sum(1 for _ in f)
    
    with open(new_file, 'r', encoding='utf-8') as f:
        new_lines = sum(1 for _ in f)
    
    print(f"去重前 - 初始域名文件行数: {old_lines}")
    print(f"去重前 - 新域名文件行数: {new_lines}")
    
    print("正在查找新增域名...")
    print("这可能需要一些时间，请耐心等待...")
    
    # 使用集合存储唯一的域名以节省内存
    old_domains = set()
    new_domains = set()
    
    # 读取旧域名文件并去重
    print("正在读取并去重初始域名...")
    with open(old_file, 'r', encoding='utf-8') as f:
        for line in f:
            domain = line.strip()
            if domain:  # 忽略空行
                old_domains.add(domain)
    
    old_unique_count = len(old_domains)
    print(f"去重后 - 初始域名数量: {old_unique_count}")
    
    # 读取新域名文件并去重
    print("正在读取并去重新域名...")
    with open(new_file, 'r', encoding='utf-8') as f:
        for line in f:
            domain = line.strip()
            if domain:  # 忽略空行
                new_domains.add(domain)
    
    new_unique_count = len(new_domains)
    print(f"去重后 - 新域名数量: {new_unique_count}")
    
    # 找出新增的域名（只在新文件中出现的域名）
    print("正在查找新增域名...")
    new_only_domains = new_domains - old_domains
    
    print(f"发现 {len(new_only_domains)} 个新增域名")
    
    # 对新增域名进行过滤处理
    print("正在对新增域名进行过滤处理...")
    filtered_domains = [domain for domain in new_only_domains if filter_domain(domain)]
    
    print(f"过滤后新增域名数量: {len(filtered_domains)}")
    
    # 保存结果到输出文件
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            for domain in sorted(filtered_domains):
                f.write(domain + '\n')
        
        print(f"新增域名已保存到: {output_file}")
        
        # 显示前20个新增域名
        print("")
        print("前20个新增域名:")
        for i, domain in enumerate(sorted(filtered_domains)[:20]):
            print(f"  {i+1:2d}. {domain}")
        
        if len(filtered_domains) > 20:
            print(f"  ... 还有 {len(filtered_domains) - 20} 个域名")
        
        return True
        
    except Exception as e:
        print(f"保存文件时出错: {e}")
        return False


def diff_domains():
    try:
        config = load_config()
    except RuntimeError as exc:
        sys.stderr.write("{0}\n".format(str(exc)))
        sys.exit(1)

    tlds = config.get("tlds", [])

    # 默认参数
    OLD_DIR = "001"
    NEW_DIR = "zonefiles"
    DIFF_DIR = "diff"
    BASE_DIR = "download"
    
    # 如果提供了命令行参数，则使用参数
    if len(sys.argv) == 4:
        OLD_DIR = sys.argv[1]
        NEW_DIR = sys.argv[2]
        tlds = sys.argv[3]
    elif len(sys.argv) != 1:
        print("用法: python3 fast_diff_domain.py [旧日期] [新日期] [后缀]")
        print("例如: python3 fast_diff_domain.py 251019 251021 org")
        print(f"如果不提供参数，则默认使用 {OLD_DIR} 和 {NEW_DIR} 的 {tlds} 域名文件")
        sys.exit(1)

    for tld in tlds:
        # 构造文件名
        old_file = f"{BASE_DIR}/{OLD_DIR}/{tld}.txt"
        new_file = f"{BASE_DIR}/{NEW_DIR}/{tld}.txt"
        output_file = f"{BASE_DIR}/{DIFF_DIR}/{tld}.txt"
    
        # 执行域名比较
        find_new_domains(old_file, new_file, output_file)

if __name__ == '__main__':
    diff_domains()