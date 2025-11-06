#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
处理指定目录下所有.txt文件，只保留每行第一列的域名

使用方法:
python3 extract_first_column.py [输入目录] [输出目录]

如果没有提供参数，则使用默认路径:
输入目录: download/diff
输出目录: output/first_column
"""

import os
import sys
import glob

from app_config.constant import DIR_DOWNLOAD_001, DIR_OUTPUT_DOMAINS_001
from scripts.filter import normalize_domain, filter_domain

def extract_first_column_from_directory(input_dir, output_dir, batch_size=5000):
    """
    处理目录下所有.txt文件，只保留每行第一列的域名，并避免重复
    
    Args:
        input_dir (str): 输入目录路径
        output_dir (str): 输出目录路径
        batch_size (int): 批处理大小，用于控制内存使用
    """
    # 检查输入目录是否存在
    if not os.path.exists(input_dir):
        print(f"错误: 输入目录 {input_dir} 不存在")
        return False
    
    # 确保输出目录存在
    os.makedirs(output_dir, exist_ok=True)
    
    # 查找所有.txt文件
    txt_files = glob.glob(os.path.join(input_dir, "*.txt"))
    
    if not txt_files:
        print(f"在目录 {input_dir} 中没有找到.txt文件")
        return False
    
    print(f"找到 {len(txt_files)} 个.txt文件")
    
    # 按文件处理，减少内存占用
    processed_files = 0
    for txt_file in txt_files:
        print(f"正在处理文件: {txt_file}")
        
        # 获取输出文件路径
        filename = os.path.basename(txt_file)
        output_file = os.path.join(output_dir, filename)
        
        # 处理当前文件
        if _process_file_with_grouping(txt_file, output_file, batch_size):
            processed_files += 1
    
    print(f"\n处理完成! 成功处理 {processed_files}/{len(txt_files)} 个文件")
    print(f"输出目录: {output_dir}")
    
    return True


def _process_file_with_grouping(input_file, output_file, batch_size=5000):
    """
    按组处理单个文件，减少内存使用
    
    Args:
        input_file (str): 输入文件路径
        output_file (str): 输出文件路径
        batch_size (int): 批处理大小
        
    Returns:
        bool: 是否处理成功
    """
    try:
        # 统计信息
        total_lines = 0
        total_processed = 0
        total_duplicates = 0
        total_numeric_start = 0
        total_dash_start = 0
        
        # 使用字典存储每个组的域名，按首字母分组以减少内存峰值
        groups = {}
        
        # 初始化26个字母组 + 数字组 + 其他组
        for i in range(26):
            groups[chr(ord('a') + i)] = []
        groups['digit'] = []
        groups['other'] = []
        
        print("  正在读取和分组域名...")
        
        # 第一步：读取文件并将域名按首字母分组
        with open(input_file, 'r', encoding='utf-8') as infile:
            batch_lines = []
            
            for line in infile:
                line = line.strip()
                if not line:
                    continue
                
                total_lines += 1
                batch_lines.append(line)
                
                # 批量处理以提高效率
                if len(batch_lines) >= batch_size:
                    _group_lines(batch_lines, groups)
                    batch_lines = []
            
            # 处理剩余行
            if batch_lines:
                _group_lines(batch_lines, groups)
        
        print(f"  总共读取 {total_lines} 行数据")
        
        # 第二步：对每个组进行去重并写入输出文件
        print("  正在去重并生成输出...")
        
        with open(output_file, 'w', encoding='utf-8') as outfile:
            # 处理每个组
            for group_key, domains in groups.items():
                if domains:  # 只处理非空组
                    # 对组内域名去重
                    seen = set()
                    unique_domains = []
                    
                    for domain in domains:
                        if domain not in seen:
                            seen.add(domain)
                            unique_domains.append(domain)
                            
                            # 统计特殊域名
                            if domain and domain[0].isdigit():
                                total_numeric_start += 1
                            elif domain and domain[0] == '-':
                                total_dash_start += 1
                        else:
                            total_duplicates += 1
                    
                    # 写入去重后的域名
                    for domain in unique_domains:
                        outfile.write(domain + '\n')
                    
                    total_processed += len(unique_domains)
                    
                    # 清理组数据以释放内存
                    groups[group_key] = []
        
        print(f"  处理后域名数: {total_processed}")
        print(f"  重复域名数: {total_duplicates}")
        print(f"  以数字开头: {total_numeric_start}")
        print(f"  以连字符开头: {total_dash_start}")
        print(f"  已生成文件: {output_file}")
        
        return True
        
    except Exception as e:
        print(f"处理文件 {input_file} 时出错: {e}")
        return False


def _group_lines(lines, groups):
    """
    将行数据按域名首字母分类到不同组
    
    Args:
        lines (list): 行数据列表
        groups (dict): 分组字典
    """
    for line in lines:
        columns = line.split()
        if columns:
            first_column = columns[0]
            first_column = normalize_domain(first_column)
            
            # 只处理符合过滤条件的域名
            if filter_domain(first_column):
                # 根据首字母确定组
                if first_column:
                    first_char = first_column[0].lower()
                    if first_char.isalpha():
                        group_key = first_char
                    elif first_char.isdigit():
                        group_key = 'digit'
                    else:
                        group_key = 'other'
                    
                    # 添加到对应组
                    if group_key in groups:
                        groups[group_key].append(first_column)


def extract_first_column_from_file_batched(input_file, output_file, batch_size=10000):
    """
    分批提取单个文件中每行的第一列作为域名，以降低内存使用
    
    Args:
        input_file (str): 输入文件路径
        output_file (str): 输出文件路径
        batch_size (int): 批处理大小
        
    Returns:
        dict: 包含处理统计信息的字典
    """
    # 确保输出目录存在
    output_dir = os.path.dirname(output_file)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
    
    # 统计信息
    total_lines = 0
    processed_lines = 0
    duplicate_count = 0
    numeric_start_count = 0  # 以数字开头的域名数量
    dash_start_count = 0     # 以连字符开头的域名数量
    
    try:
        with open(input_file, 'r', encoding='utf-8') as infile, \
             open(output_file, 'w', encoding='utf-8') as outfile:
            
            # 使用集合进行文件内去重
            seen_in_file = set()
            
            # 分批处理，避免大量域名存储在内存中
            batch_lines = []
            
            for line in infile:
                # 去除行首行尾空白字符
                line = line.strip()
                
                # 跳过空行
                if not line:
                    continue
                
                total_lines += 1
                batch_lines.append(line)
                
                # 当批次达到指定大小时，处理这一批数据
                if len(batch_lines) >= batch_size:
                    batch_result = _process_batch(batch_lines, seen_in_file)
                    _write_batch(outfile, batch_result['domains'], batch_result['stats'])
                    
                    # 更新统计信息
                    processed_lines += batch_result['stats']['processed_lines']
                    duplicate_count += batch_result['stats']['duplicate_count']
                    numeric_start_count += batch_result['stats']['numeric_start_count']
                    dash_start_count += batch_result['stats']['dash_start_count']
                    
                    # 清空批次数据以释放内存
                    batch_lines = []
                    # 定期清理seen_in_file以避免内存过大
                    if len(seen_in_file) > 50000:
                        seen_in_file.clear()
            
            # 处理剩余的数据
            if batch_lines:
                batch_result = _process_batch(batch_lines, seen_in_file)
                _write_batch(outfile, batch_result['domains'], batch_result['stats'])
                
                # 更新统计信息
                processed_lines += batch_result['stats']['processed_lines']
                duplicate_count += batch_result['stats']['duplicate_count']
                numeric_start_count += batch_result['stats']['numeric_start_count']
                dash_start_count += batch_result['stats']['dash_start_count']
        
        print(f"已处理文件: {input_file}")
        print(f"  总行数: {total_lines}")
        print(f"  处理行数: {processed_lines}")
        print(f"  重复域名数: {duplicate_count}")
        print(f"  以数字开头的域名数: {numeric_start_count}")
        print(f"  以连字符开头的域名数: {dash_start_count}")
        return {
            'processed_lines': processed_lines,
            'duplicate_count': duplicate_count,
            'numeric_start_count': numeric_start_count,
            'dash_start_count': dash_start_count
        }
        
    except Exception as e:
        print(f"处理文件 {input_file} 时出错: {e}")
        return None


def _process_batch(lines, seen_in_file):
    """
    处理一批行数据
    
    Args:
        lines (list): 行数据列表
        seen_in_file (set): 文件内已见过的域名集合
        
    Returns:
        dict: 包含处理结果和统计信息的字典
    """
    domains = []
    stats = {
        'processed_lines': 0,
        'duplicate_count': 0,
        'numeric_start_count': 0,
        'dash_start_count': 0
    }
    
    for line in lines:
        # 提取第一列（以空格、制表符等分隔符分割）
        # 假设第一列就是第一个字段
        columns = line.split()
        if columns:
            first_column = columns[0]
            first_column = normalize_domain(first_column)
            
            # 检查域名是否符合过滤条件且未重复
            if filter_domain(first_column) and first_column not in seen_in_file:
                seen_in_file.add(first_column)
                domains.append(first_column)
                stats['processed_lines'] += 1
                
                # 检查是否以数字开头
                if first_column and first_column[0].isdigit():
                    stats['numeric_start_count'] += 1
                # 检查是否以连字符开头
                elif first_column and first_column[0] == '-':
                    stats['dash_start_count'] += 1
            elif first_column in seen_in_file:
                stats['duplicate_count'] += 1
    
    return {
        'domains': domains,
        'stats': stats
    }


def _write_batch(outfile, domains, stats):
    """
    将一批域名写入输出文件
    
    Args:
        outfile (file): 输出文件对象
        domains (list): 域名列表
        stats (dict): 统计信息
    """
    for domain in domains:
        outfile.write(domain + '\n')


def main():
    # 默认目录路径
    default_input_dir = DIR_DOWNLOAD_001
    default_output_dir = DIR_OUTPUT_DOMAINS_001
    
    # 获取命令行参数
    if len(sys.argv) >= 3:
        input_dir = sys.argv[1]
        output_dir = sys.argv[2]
    else:
        input_dir = default_input_dir
        output_dir = default_output_dir
        print("使用默认目录路径:")
        print(f"  输入目录: {input_dir}")
        print(f"  输出目录: {output_dir}")
        print()
    
    # 执行处理
    extract_first_column_from_directory(input_dir, output_dir)


if __name__ == '__main__':
    main()