#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
分块处理域名差异比较，降低内存使用
通过哈希分块的方式处理大型域名文件
"""

import os
import glob
import hashlib
import tempfile
import shutil
from app_config.config import load_config, get_tlds_from_config
from app_config.constant import DIR_OUTPUT_DOMAINS_001, DIR_OUTPUT_DOMAINS_002, DIR_OUTPUT_DOMAINS_NEW
from scripts.filter import filter_domain, normalize_domain
import sys
import os

from util.util import DIR_OUTPUT_DOMAINS_NEW_TODAY


def hash_domain(domain, num_chunks=100):
    """根据域名计算哈希值，确定其所属的块"""
    hash_val = int(hashlib.md5(domain.encode('utf-8')).hexdigest(), 16)
    return hash_val % num_chunks


def split_file_to_chunks(input_file, output_dir, num_chunks=100, batch_size=1000):
    """将文件按域名哈希值分割成多个块"""
    os.makedirs(output_dir, exist_ok=True)
    
    # 创建临时文件句柄
    chunk_files = {}
    for i in range(num_chunks):
        chunk_files[i] = open(os.path.join(output_dir, f"chunk_{i:03d}.txt"), "w", encoding="utf-8")
    
    # 读取输入文件并分块写入
    with open(input_file, "r", encoding="utf-8") as fp:
        batch_lines = []
        for line in fp:
            batch_lines.append(line)
            
            # 当批次达到指定大小时，处理这一批数据
            if len(batch_lines) >= batch_size:
                _process_batch_lines(batch_lines, chunk_files, num_chunks)
                batch_lines = []  # 清空批次
        
        # 处理剩余的数据
        if batch_lines:
            _process_batch_lines(batch_lines, chunk_files, num_chunks)
    
    # 关闭所有文件
    for f in chunk_files.values():
        f.close()


def _process_batch_lines(lines, chunk_files, num_chunks):
    """处理一批行数据并写入对应的块文件"""
    for line in lines:
        domain = normalize_domain(line)
        if not domain:
            continue
        
        chunk_id = hash_domain(domain, num_chunks)
        chunk_files[chunk_id].write(domain + "\n")


def find_new_domains_chunked(old_file, new_file, output_file, num_chunks=100, batch_size=1000):
    """
    使用分块方式比较两个域名文件，找出新增的域名
    
    Args:
        old_file (str): 旧域名文件路径
        new_file (str): 新域名文件路径
        output_file (str): 输出文件路径
        num_chunks (int): 分块数量
        batch_size (int): 批处理大小
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
        split_file_to_chunks(old_file, old_chunks_dir, num_chunks, batch_size)
        
        print(f"正在分割新域名文件{new_file}...")
        split_file_to_chunks(new_file, new_chunks_dir, num_chunks, batch_size)
        
        print("正在逐块比较域名...")
        with open(output_file, "w", encoding="utf-8") as out_fp:
            # 逐块处理
            for chunk_id in range(num_chunks):
                old_chunk_file = os.path.join(old_chunks_dir, f"chunk_{chunk_id:03d}.txt")
                new_chunk_file = os.path.join(new_chunks_dir, f"chunk_{chunk_id:03d}.txt")
                
                # 如果新块不存在，跳过
                if not os.path.exists(new_chunk_file):
                    continue
                
                # 分批加载旧块到内存
                old_domains = set()
                if os.path.exists(old_chunk_file):
                    with open(old_chunk_file, "r", encoding="utf-8") as old_fp:
                        batch_lines = []
                        for line in old_fp:
                            batch_lines.append(line.strip())
                            
                            # 当批次达到指定大小时，处理这一批数据
                            if len(batch_lines) >= batch_size:
                                for domain in batch_lines:
                                    if domain:
                                        old_domains.add(domain)
                                batch_lines = []  # 清空批次
                        
                        # 处理剩余的数据
                        for domain in batch_lines:
                            if domain:
                                old_domains.add(domain)
                
                # 分批处理新块，找出新增域名
                with open(new_chunk_file, "r", encoding="utf-8") as new_fp:
                    batch_lines = []
                    for line in new_fp:
                        batch_lines.append(line.strip())
                        
                        # 当批次达到指定大小时，处理这一批数据
                        if len(batch_lines) >= batch_size:
                            _process_new_chunk_batch(batch_lines, old_domains, out_fp)
                            batch_lines = []  # 清空批次
                    
                    # 处理剩余的数据
                    _process_new_chunk_batch(batch_lines, old_domains, out_fp)
        
        print(f"新增域名已保存到: {output_file}")
        return True
        
    except Exception as e:
        print(f"处理过程中出现错误: {e}")
        return False
    finally:
        # 清理临时目录
        shutil.rmtree(temp_dir, ignore_errors=True)


def _process_new_chunk_batch(lines, old_domains, out_fp):
    """处理新块的一批数据，找出新增域名"""
    for domain in lines:
        if not domain:
            continue
        
        # 如果域名不在旧块中，则为新增
        if domain not in old_domains:
            # 应用过滤规则
            if filter_domain(domain):
                out_fp.write(domain + "\n")


def chunk_directory_domains(input_dir, chunk_dir, num_chunks=100, batch_size=2000):
    """
    遍历目录中的TLD文件，抽取第一列域名，按哈希分块，并对每个块去重
    """
    _prepare_chunk_dir(chunk_dir)

    if not os.path.exists(input_dir):
        print(f"目录 {input_dir} 不存在，已清空 {chunk_dir}")
        return False

    txt_files = sorted(glob.glob(os.path.join(input_dir, "*.txt")))
    if not txt_files:
        print(f"目录 {input_dir} 中没有找到 .txt 文件，已清空 {chunk_dir}")
        return False

    print(f"在 {input_dir} 中找到 {len(txt_files)} 个 TLD 文件，开始分块...")
    chunk_files = _open_chunk_files(chunk_dir, num_chunks)
    total_domains = 0

    try:
        for txt_file in txt_files:
            print(f"  正在处理 {txt_file}")
            total_domains += _process_tld_file_for_chunking(txt_file, chunk_files, num_chunks, batch_size)
    finally:
        for fp in chunk_files.values():
            fp.close()

    print(f"共写入 {total_domains} 个域名，开始对块文件去重...")
    _deduplicate_chunk_files(chunk_dir)
    return True


def diff_chunk_directories_to_file(new_chunk_dir, old_chunk_dir, output_file, num_chunks=100):
    """
    比较新旧块文件，找出新增域名并写入输出文件
    """
    output_dir = os.path.dirname(output_file)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
    total_new_domains = 0

    with open(output_file, "w", encoding="utf-8") as out_fp:
        for chunk_id in range(num_chunks):
            chunk_name = f"chunk_{chunk_id:03d}.txt"
            new_chunk_file = os.path.join(new_chunk_dir, chunk_name)
            if not os.path.exists(new_chunk_file):
                continue

            old_chunk_file = os.path.join(old_chunk_dir, chunk_name)
            old_domains = _load_domains_to_set(old_chunk_file)
            new_domains = _write_new_domains_from_chunk(new_chunk_file, old_domains, out_fp)
            total_new_domains += new_domains
            print(f"  {chunk_name} 新增 {new_domains} 个域名")

    print(f"新增域名总数: {total_new_domains}")
    return total_new_domains


def _prepare_chunk_dir(chunk_dir):
    """删除并重新创建块目录，确保没有旧数据"""
    if os.path.exists(chunk_dir):
        shutil.rmtree(chunk_dir)
    os.makedirs(chunk_dir, exist_ok=True)


def _open_chunk_files(chunk_dir, num_chunks):
    """为每个哈希块创建写入文件句柄"""
    chunk_files = {}
    for chunk_id in range(num_chunks):
        chunk_path = os.path.join(chunk_dir, f"chunk_{chunk_id:03d}.txt")
        chunk_files[chunk_id] = open(chunk_path, "w", encoding="utf-8")
    return chunk_files


def _process_tld_file_for_chunking(file_path, chunk_files, num_chunks, batch_size):
    """读取TLD文件，按批次写入对应块"""
    total = 0
    batch = []

    with open(file_path, "r", encoding="utf-8") as infile:
        for line in infile:
            batch.append(line)
            if len(batch) >= batch_size:
                total += _flush_lines_to_chunks(batch, chunk_files, num_chunks)
                batch = []

        if batch:
            total += _flush_lines_to_chunks(batch, chunk_files, num_chunks)

    return total


def _flush_lines_to_chunks(lines, chunk_files, num_chunks):
    """将一批原始行写入对应块"""
    processed = 0
    for raw_line in lines:
        columns = raw_line.strip().split()
        if not columns:
            continue
        domain = normalize_domain(columns[0])
        if not domain or not filter_domain(domain):
            continue
        chunk_id = hash_domain(domain, num_chunks)
        chunk_files[chunk_id].write(domain + "\n")
        processed += 1
    return processed


def _deduplicate_chunk_files(chunk_dir):
    """对目录内的块文件逐个去重"""
    chunk_files = sorted(glob.glob(os.path.join(chunk_dir, "chunk_*.txt")))
    for chunk_file in chunk_files:
        _deduplicate_chunk_file(chunk_file)


def _deduplicate_chunk_file(chunk_file):
    """读取块文件，去除重复域名"""
    seen = set()
    duplicates = 0
    temp_file = chunk_file + ".tmp"

    with open(chunk_file, "r", encoding="utf-8") as infile, open(temp_file, "w", encoding="utf-8") as outfile:
        for line in infile:
            domain = line.strip()
            if not domain:
                continue
            if domain not in seen:
                seen.add(domain)
                outfile.write(domain + "\n")
            else:
                duplicates += 1

    os.replace(temp_file, chunk_file)
    print(f"  {os.path.basename(chunk_file)} 去重完成, 保留 {len(seen)} 个域名, 去除 {duplicates} 个重复")


def _load_domains_to_set(chunk_file):
    """将块文件中的域名加载为集合"""
    domains = set()
    if not os.path.exists(chunk_file):
        return domains

    with open(chunk_file, "r", encoding="utf-8") as infile:
        for line in infile:
            domain = line.strip()
            if domain:
                domains.add(domain)
    return domains


def _write_new_domains_from_chunk(new_chunk_file, old_domains, out_fp):
    """将不在旧集合中的域名写入输出文件"""
    added = 0
    with open(new_chunk_file, "r", encoding="utf-8") as infile:
        for line in infile:
            domain = line.strip()
            if not domain:
                continue
            if domain not in old_domains:
                out_fp.write(domain + "\n")
                added += 1
    return added


def diff_domains():
    tlds = get_tlds_from_config()
    
    OLD_DIR = DIR_OUTPUT_DOMAINS_001
    NEW_DIR = DIR_OUTPUT_DOMAINS_002
    DIFF_DIR_TODAY = DIR_OUTPUT_DOMAINS_NEW_TODAY

    if not os.path.exists(DIFF_DIR_TODAY):
        print(f"目录 {DIFF_DIR_TODAY} 不存在, 新建中...")
        os.makedirs(DIFF_DIR_TODAY, exist_ok=True)
    
    for tld in tlds:
        old_file = f"{OLD_DIR}/{tld}.txt"
        new_file = f"{NEW_DIR}/{tld}.txt"
        output_file = f"{DIFF_DIR_TODAY}/{tld}.txt"
        
        print(f"正在处理 {tld} 域名...")
        find_new_domains_chunked(old_file, new_file, output_file, num_chunks=50, batch_size=500)


if __name__ == '__main__':
    diff_domains()
