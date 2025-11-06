#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
分块处理域名差异比较，降低内存使用
通过哈希分块的方式处理大型域名文件
"""

import os
import hashlib
import tempfile
import shutil
from app_config.config import load_config, get_tlds_from_config
from app_config.constant import DIR_OUTPUT_DOMAINS_001, DIR_OUTPUT_DOMAINS_002, DIR_OUTPUT_DOMAINS_NEW
from scripts.filter import filter_domain, normalize_domain


def hash_domain(domain, num_chunks=100):
    """根据域名计算哈希值，确定其所属的块"""
    hash_val = int(hashlib.md5(domain.encode('utf-8')).hexdigest(), 16)
    return hash_val % num_chunks


def split_file_to_chunks(input_file, output_dir, num_chunks=100):
    """将文件按域名哈希值分割成多个块"""
    os.makedirs(output_dir, exist_ok=True)
    
    # 创建临时文件句柄
    chunk_files = {}
    for i in range(num_chunks):
        chunk_files[i] = open(os.path.join(output_dir, f"chunk_{i:03d}.txt"), "w", encoding="utf-8")
    
    # 读取输入文件并分块写入
    with open(input_file, "r", encoding="utf-8") as fp:
        for line in fp:
            domain = normalize_domain(line)
            if not domain:
                continue
            
            chunk_id = hash_domain(domain, num_chunks)
            chunk_files[chunk_id].write(domain + "\n")
    
    # 关闭所有文件
    for f in chunk_files.values():
        f.close()


def find_new_domains_chunked(old_file, new_file, output_file, num_chunks=100):
    """
    使用分块方式比较两个域名文件，找出新增的域名
    
    Args:
        old_file (str): 旧域名文件路径
        new_file (str): 新域名文件路径
        output_file (str): 输出文件路径
        num_chunks (int): 分块数量
    """
    if not os.path.exists(old_file):
        print(f"错误: 找不到初始域名文件 {old_file}")
        return False

    if not os.path.exists(new_file):
        print(f"错误: 找不到新域名文件 {new_file}")
        return False

    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    # 创建临时目录存放分块文件
    temp_dir = tempfile.mkdtemp()
    old_chunks_dir = os.path.join(temp_dir, "old_chunks")
    new_chunks_dir = os.path.join(temp_dir, "new_chunks")
    
    try:
        print(f"正在分割旧域名文件{old_file}...")
        split_file_to_chunks(old_file, old_chunks_dir, num_chunks)
        
        print(f"正在分割新域名文件{new_file}...")
        split_file_to_chunks(new_file, new_chunks_dir, num_chunks)
        
        print("正在逐块比较域名...")
        with open(output_file, "w", encoding="utf-8") as out_fp:
            # 逐块处理
            for chunk_id in range(num_chunks):
                old_chunk_file = os.path.join(old_chunks_dir, f"chunk_{chunk_id:03d}.txt")
                new_chunk_file = os.path.join(new_chunks_dir, f"chunk_{chunk_id:03d}.txt")
                
                # 如果新块不存在，跳过
                if not os.path.exists(new_chunk_file):
                    continue
                
                # 加载旧块到内存
                old_domains = set()
                if os.path.exists(old_chunk_file):
                    with open(old_chunk_file, "r", encoding="utf-8") as old_fp:
                        for line in old_fp:
                            domain = line.strip()
                            if domain:
                                old_domains.add(domain)
                
                # 处理新块，找出新增域名
                with open(new_chunk_file, "r", encoding="utf-8") as new_fp:
                    for line in new_fp:
                        domain = line.strip()
                        if not domain:
                            continue
                        
                        # 如果域名不在旧块中，则为新增
                        if domain not in old_domains:
                            # 应用过滤规则
                            if filter_domain(domain):
                                out_fp.write(domain + "\n")
        
        print(f"新增域名已保存到: {output_file}")
        return True
        
    except Exception as e:
        print(f"处理过程中出现错误: {e}")
        return False
    finally:
        # 清理临时目录
        shutil.rmtree(temp_dir, ignore_errors=True)


def diff_domains():
    tlds = get_tlds_from_config()
    
    OLD_DIR = DIR_OUTPUT_DOMAINS_001
    NEW_DIR = DIR_OUTPUT_DOMAINS_002
    DIFF_DIR = DIR_OUTPUT_DOMAINS_NEW
    
    for tld in tlds:
        old_file = f"{OLD_DIR}/{tld}.txt"
        new_file = f"{NEW_DIR}/{tld}.txt"
        output_file = f"{DIFF_DIR}/{tld}.txt"
        
        print(f"正在处理 {tld} 域名...")
        find_new_domains_chunked(old_file, new_file, output_file)


if __name__ == '__main__':
    diff_domains()