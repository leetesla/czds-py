#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
快速比较两个域名列表文件，找出新增的域名
使用高效的算法处理大文件，避免占用过多内存

使用方法:
python3 fast_diff_domain.py [旧日期] [新日期] [后缀]

例如: python3 fast_diff_domain.py 251019 251021 org

"""

import os
import subprocess
import sys
import time

from app_config.config import load_config
from app_config.constant import DIR_OUTPUT_DOMAINS_001, DIR_OUTPUT_DOMAINS_002, DIR_OUTPUT_DOMAINS_DIFF


def filter_domain(domain):
    """
    过滤域名：排除点号数量超过2个的域名，以及含有双连字符的域名，以及含有数字超过2个的域名
    
    Args:
        domain (str): 域名
        
    Returns:
        bool: True表示保留该域名，False表示过滤掉
    """
    # 计算点号数量
    dot_count = domain.count('.')
    
    # 检查是否含有双连字符
    has_double_dash = '--' in domain
    
    # 计算数字数量
    digit_count = sum(1 for char in domain if char.isdigit())
    
    # 保留点号数量不超过2个且不含有双连字符且数字数量不超过2个的域名
    return dot_count < 2 and not has_double_dash and digit_count <= 2


def find_new_domains(old_file, new_file, output_file):
    """
    比较两个域名文件，找出新增的域名
    
    Args:
        old_file (str): 旧域名文件路径
        new_file (str): 新域名文件路径
        output_file (str): 输出文件路径
    """
    start_ts = time.perf_counter()

    if not os.path.exists(old_file):
        print(f"错误: 找不到初始域名文件 {old_file}")
        return False

    if not os.path.exists(new_file):
        print(f"错误: 找不到新域名文件 {new_file}")
        return False

    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    print("正在比较域名列表:")
    print(f"  初始列表: {old_file}")
    print(f"  新列表: {new_file}")
    print(f"  输出文件: {output_file}")

    # 读取旧域名文件，统计总行数并建立集合
    print("正在读取并去重初始域名...")
    old_domains = set()
    old_line_count = 0
    with open(old_file, "r", encoding="utf-8") as old_fp:
        for line in old_fp:
            domain = line.strip()
            if not domain:
                continue
            old_line_count += 1
            old_domains.add(domain)

    print(f"去重前 - 初始域名文件行数: {old_line_count}")
    print(f"去重后 - 初始域名数量: {len(old_domains)}")

    # 扫描新域名文件并即时写出新增域名，避免将大文件全部载入内存
    print("正在扫描新域名文件并筛选新增域名...")
    new_line_count = 0
    overlap_domains = set()
    candidate_new_count = 0
    filtered_candidate_count = 0
    tmp_output = f"{output_file}.tmp"

    try:
        with open(new_file, "r", encoding="utf-8") as new_fp, open(
            tmp_output, "w", encoding="utf-8"
        ) as tmp_fp:
            for line in new_fp:
                domain = line.strip()
                if not domain:
                    continue

                new_line_count += 1
                if domain in old_domains:
                    overlap_domains.add(domain)
                    continue

                candidate_new_count += 1
                if not filter_domain(domain):
                    continue

                filtered_candidate_count += 1
                tmp_fp.write(domain + "\n")
    except Exception as exc:
        print(f"处理新域名文件时出错: {exc}")
        if os.path.exists(tmp_output):
            os.remove(tmp_output)
        return False

    print(f"去重前 - 新域名文件行数: {new_line_count}")
    print(f"与初始列表重叠的域名数量: {len(overlap_domains)}")
    print(f"候选新增域名数量（未过滤、可能包含重复）: {candidate_new_count}")
    print(f"过滤后候选新增域名数量: {filtered_candidate_count}")

    if filtered_candidate_count == 0:
        print("没有发现符合过滤条件的新增域名。")
        with open(output_file, "w", encoding="utf-8") as out_fp:
            out_fp.write("")
        if os.path.exists(tmp_output):
            os.remove(tmp_output)
        return True

    print("正在对筛选结果进行去重与排序...")
    try:
        subprocess.run(["sort", "-u", tmp_output, "-o", output_file], check=True)
        os.remove(tmp_output)
    except (subprocess.CalledProcessError, FileNotFoundError) as exc:
        print(f"排序去重失败: {exc}")
        if os.path.exists(tmp_output):
            os.remove(tmp_output)
        return False

    unique_filtered_count = 0
    preview_domains = []
    with open(output_file, "r", encoding="utf-8") as out_fp:
        for domain in out_fp:
            domain = domain.strip()
            if not domain:
                continue
            unique_filtered_count += 1
            if len(preview_domains) < 20:
                preview_domains.append(domain)

    print(f"去重后新增域名数量: {unique_filtered_count}")
    print(f"新增域名已保存到: {output_file}")

    if preview_domains:
        print("\n前20个新增域名:")
        for i, domain in enumerate(preview_domains, start=1):
            print(f"  {i:2d}. {domain}")
        if unique_filtered_count > len(preview_domains):
            print(f"  ... 还有 {unique_filtered_count - len(preview_domains)} 个域名")

    elapsed = time.perf_counter() - start_ts
    print(f"处理完成，耗时 {elapsed:.2f} 秒")

    return True


def diff_domains():
    try:
        config = load_config()
    except RuntimeError as exc:
        sys.stderr.write("{0}\n".format(str(exc)))
        sys.exit(1)

    tlds = config.get("tlds", [])

    # 默认参数
    OLD_DIR = DIR_OUTPUT_DOMAINS_001
    NEW_DIR = DIR_OUTPUT_DOMAINS_002
    DIFF_DIR = DIR_OUTPUT_DOMAINS_DIFF
    # BASE_DIR = "download"
    
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
        old_file = f"{OLD_DIR}/{tld}.txt"
        new_file = f"{NEW_DIR}/{tld}.txt"
        output_file = f"{DIFF_DIR}/{tld}.txt"
    
        # 执行域名比较
        find_new_domains(old_file, new_file, output_file)

if __name__ == '__main__':
    diff_domains()
