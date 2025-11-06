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


def extract_first_column_from_file(input_file, output_file):
    """
    提取单个文件中每行的第一列作为域名，并避免重复
    
    Args:
        input_file (str): 输入文件路径
        output_file (str): 输出文件路径
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
    
    # 使用集合来跟踪已经见过的域名，避免重复
    seen_domains = set()
    
    try:
        with open(input_file, 'r', encoding='utf-8') as infile, \
             open(output_file, 'w', encoding='utf-8') as outfile:
            
            for line in infile:
                # 去除行首行尾空白字符
                line = line.strip()
                
                # 跳过空行
                if not line:
                    continue
                
                total_lines += 1
                
                # 提取第一列（以空格、制表符等分隔符分割）
                # 假设第一列就是第一个字段
                columns = line.split()
                if columns:
                    first_column = columns[0]
                    first_column = normalize_domain(first_column)
                    
                    # 检查域名是否符合过滤条件且未重复
                    if filter_domain(first_column) and first_column not in seen_domains:
                        seen_domains.add(first_column)
                        outfile.write(first_column + '\n')
                        processed_lines += 1
                        
                        # 检查是否以数字开头
                        if first_column and first_column[0].isdigit():
                            numeric_start_count += 1
                        # 检查是否以连字符开头
                        elif first_column and first_column[0] == '-':
                            dash_start_count += 1
                    elif first_column in seen_domains:
                        duplicate_count += 1
        
        print(f"已处理文件: {input_file}")
        print(f"  总行数: {total_lines}")
        print(f"  处理行数: {processed_lines}")
        print(f"  重复域名数: {duplicate_count}")
        print(f"  以数字开头的域名数: {numeric_start_count}")
        print(f"  以连字符开头的域名数: {dash_start_count}")
        return True
        
    except Exception as e:
        print(f"处理文件 {input_file} 时出错: {e}")
        return False


def extract_first_column_from_directory(input_dir, output_dir):
    """
    处理目录下所有.txt文件，只保留每行第一列的域名，并避免重复
    
    Args:
        input_dir (str): 输入目录路径
        output_dir (str): 输出目录路径
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
    
    # 全局集合来跟踪所有已经见过的域名，避免跨文件重复
    seen_domains = set()
    
    # 全局统计信息
    total_numeric_start = 0
    total_dash_start = 0
    
    # 处理每个文件
    processed_files = 0
    for txt_file in txt_files:
        # 获取文件名（不含路径）
        filename = os.path.basename(txt_file)
        # 生成输出文件路径
        output_file = os.path.join(output_dir, filename)
        
        # 处理文件
        result = extract_first_column_from_file_global_dedup(txt_file, output_file, seen_domains)
        if result:
            processed_files += 1
            # 更新全局统计信息
            total_numeric_start += result.get('numeric_start_count', 0)
            total_dash_start += result.get('dash_start_count', 0)
    
    print(f"\n处理完成! 成功处理 {processed_files}/{len(txt_files)} 个文件")
    print(f"输出目录: {output_dir}")
    print(f"总共以数字开头的域名数: {total_numeric_start}")
    print(f"总共以连字符开头的域名数: {total_dash_start}")
    
    return True


def extract_first_column_from_file_global_dedup(input_file, output_file, seen_domains):
    """
    提取单个文件中每行的第一列作为域名，并避免全局重复
    
    Args:
        input_file (str): 输入文件路径
        output_file (str): 输出文件路径
        seen_domains (set): 全局已见域名集合
        
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
            
            for line in infile:
                # 去除行首行尾空白字符
                line = line.strip()
                
                # 跳过空行
                if not line:
                    continue
                
                total_lines += 1
                
                # 提取第一列（以空格、制表符等分隔符分割）
                # 假设第一列就是第一个字段
                columns = line.split()
                if columns:
                    first_column = columns[0]
                    first_column = normalize_domain(first_column)
                    
                    # 检查域名是否符合过滤条件且未重复
                    if filter_domain(first_column) and first_column not in seen_domains:
                        seen_domains.add(first_column)
                        outfile.write(first_column + '\n')
                        processed_lines += 1
                        
                        # 检查是否以数字开头
                        if first_column and first_column[0].isdigit():
                            numeric_start_count += 1
                        # 检查是否以连字符开头
                        elif first_column and first_column[0] == '-':
                            dash_start_count += 1
                    elif first_column in seen_domains:
                        duplicate_count += 1
        
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