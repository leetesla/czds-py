#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
筛选不含数字的域名并保存到新文件

使用方法:
python3 filter_domains_no_digits.py [输入文件] [输出文件]

如果没有提供参数，则使用默认路径:
输入文件: /Users/chrise/app/util-script/domains/251021-org-new-domains.txt
输出文件: /Users/chrise/app/util-script/domains/251021-org-domains-without-digits.txt
"""

import os
import re
import sys

def filter_domains_without_digits(input_file, output_file):
    """
    读取域名文件，筛选出不含数字的域名并保存到新文件
    
    Args:
        input_file (str): 输入文件路径
        output_file (str): 输出文件路径
    """
    # 检查输入文件是否存在
    if not os.path.exists(input_file):
        print(f"错误: 输入文件 {input_file} 不存在")
        return False
    
    # 用于匹配数字的正则表达式
    digit_pattern = re.compile(r'\d')
    
    # 统计信息
    total_domains = 0
    domains_without_digits = 0
    
    try:
        with open(input_file, 'r', encoding='utf-8') as infile, \
             open(output_file, 'w', encoding='utf-8') as outfile:
            
            for line in infile:
                # 去除行首行尾空白字符
                domain = line.strip()
                
                # 跳过空行
                if not domain:
                    continue
                
                total_domains += 1
                
                # 检查域名是否包含数字
                if not digit_pattern.search(domain):
                    # 不含数字，写入输出文件
                    outfile.write(domain + '\n')
                    domains_without_digits += 1
        
        print(f"处理完成!")
        print(f"总域名数: {total_domains}")
        print(f"不含数字的域名数: {domains_without_digits}")
        print(f"包含数字的域名数: {total_domains - domains_without_digits}")
        print(f"结果已保存到: {output_file}")
        return True
        
    except Exception as e:
        print(f"处理文件时出错: {e}")
        return False

def main():
    # 默认文件路径
    default_input = '/Users/chrise/app/util-script/domains/251021-org-new-domains.txt'
    default_output = '/Users/chrise/app/util-script/domains/251021-org-domains-no-digits.txt'
    
    # 获取命令行参数
    if len(sys.argv) == 3:
        input_file = sys.argv[1]
        output_file = sys.argv[2]
    else:
        input_file = default_input
        output_file = default_output
        print("使用默认文件路径:")
        print(f"  输入文件: {input_file}")
        print(f"  输出文件: {output_file}")
        print()
    
    # 执行筛选
    filter_domains_without_digits(input_file, output_file)

if __name__ == '__main__':
    main()