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


def extract_first_column_from_file(input_file, output_file):
    """
    提取单个文件中每行的第一列作为域名
    
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
                    outfile.write(first_column + '\n')
                    processed_lines += 1
        
        print(f"已处理文件: {input_file}")
        print(f"  总行数: {total_lines}")
        print(f"  处理行数: {processed_lines}")
        return True
        
    except Exception as e:
        print(f"处理文件 {input_file} 时出错: {e}")
        return False


def extract_first_column_from_directory(input_dir, output_dir):
    """
    处理目录下所有.txt文件，只保留每行第一列的域名
    
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
    
    # 处理每个文件
    processed_files = 0
    for txt_file in txt_files:
        # 获取文件名（不含路径）
        filename = os.path.basename(txt_file)
        # 生成输出文件路径
        output_file = os.path.join(output_dir, filename)
        
        # 处理文件
        if extract_first_column_from_file(txt_file, output_file):
            processed_files += 1
    
    print(f"\n处理完成! 成功处理 {processed_files}/{len(txt_files)} 个文件")
    print(f"输出目录: {output_dir}")
    
    return True


def main():
    # 默认目录路径
    default_input_dir = os.path.join('download', '001')
    default_output_dir = os.path.join('output', 'domains-001')
    
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