#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
处理域名文件，找出出现多次的域名（比较时忽略"-"）

功能说明:
1. 移除常见顶级域名后缀（.org., .com., .net., 等）
2. 在比较域名时忽略连字符 "-"
3. 找出标准化后相同的域名组
4. 生成包含可点击链接的HTML文件

使用方法:
python3 find_duplicate_domains.py [输入文件] [文本输出文件] [HTML输出文件]

如果没有提供参数，则使用默认路径:
输入文件: /Users/chrise/app/util-script/domains/251021-org-domains-no-digits.txt
文本输出文件: /Users/chrise/app/util-script/domains/duplicate_domains.txt
HTML输出文件: /Users/chrise/app/util-script/domains/duplicate_domains.html
"""

import os
import sys
from collections import defaultdict

from app_config.constant import FILE_OUTPUT_DOMAINS_DIFF_ALL, FILE_OUTPUT_DOMAINS_DUPLICATE, \
    HTML_OUTPUT_DOMAINS_DUPLICATE


def normalize_domain(domain):
    """
    标准化域名，移除常见顶级域名后缀并移除所有"-"
    
    Args:
        domain (str): 原始域名
        
    Returns:
        str: 标准化后的域名
    """
    # 移除常见的顶级域名后缀
    common_suffixes = ['.org.', '.com.', '.net.', '.edu.', '.gov.', '.mil.', '.int.', '.online.']
    for suffix in common_suffixes:
        if domain.endswith(suffix):
            domain = domain[:-len(suffix)]  # 移除后缀
            break
    
    # 移除所有的 "-"
    normalized = domain.replace('-', '')
    
    return normalized

def generate_html_output(duplicates, html_output_file):
    """
    生成HTML格式的输出文件，包含可点击的域名链接
    
    Args:
        duplicates (dict): 重复域名字典 {标准化域名: [原始域名列表]}
        html_output_file (str): HTML输出文件路径
    """
    try:
        with open(html_output_file, 'w', encoding='utf-8') as outfile:
            outfile.write('<!DOCTYPE html>\n')
            outfile.write('<html lang="zh-CN">\n')
            outfile.write('<head>\n')
            outfile.write('    <meta charset="UTF-8">\n')
            outfile.write('    <meta name="viewport" content="width=device-width, initial-scale=1.0">\n')
            outfile.write('    <title>重复域名列表</title>\n')
            outfile.write('    <style>\n')
            outfile.write('        body { font-family: Arial, sans-serif; margin: 20px; }\n')
            outfile.write('        h1 { color: #333; }\n')
            outfile.write('        .domain-group { margin-bottom: 20px; padding: 10px; border: 1px solid #ddd; border-radius: 5px; }\n')
            outfile.write('        .normalized-domain { font-weight: bold; color: #0066cc; font-size: 1.2em; }\n')
            outfile.write('        .original-domains { margin-top: 5px; }\n')
            outfile.write('        .original-domain { margin-right: 10px; }\n')
            outfile.write('        a { text-decoration: none; color: #0066cc; }\n')
            outfile.write('        a:hover { text-decoration: underline; }\n')
            outfile.write('    </style>\n')
            outfile.write('</head>\n')
            outfile.write('<body>\n')
            outfile.write(f'    <h1>重复域名列表 (共{len(duplicates)}组)</h1>\n')
            outfile.write('    <p>点击域名可直接访问（需要网络连接）</p>\n')
            
            for normalized, originals in sorted(duplicates.items()):
                outfile.write('    <div class="domain-group">\n')
                outfile.write(f'        <div class="normalized-domain">标准化域名: {normalized}</div>\n')
                outfile.write('        <div class="original-domains">原始域名: \n')
                
                for original in originals:
                    # 移除末尾的点号以生成有效的URL
                    clean_domain = original.rstrip('.')
                    outfile.write(f'            <span class="original-domain"><a href="http://{clean_domain}" target="_blank">{clean_domain}</a></span>\n')
                
                outfile.write('        </div>\n')
                outfile.write('    </div>\n')
            
            outfile.write('</body>\n')
            outfile.write('</html>\n')
        
        print(f"HTML结果已保存到: {html_output_file}")
        
    except Exception as e:
        print(f"生成HTML文件时出错: {e}")

def find_duplicate_domains(input_file, output_file, html_output_file=None):
    """
    读取域名文件，找出出现多次的域名（比较时忽略"-"）
    
    Args:
        input_file (str): 输入文件路径
        output_file (str): 输出文件路径
        html_output_file (str): HTML输出文件路径（可选）
    """
    # 检查输入文件是否存在
    if not os.path.exists(input_file):
        print(f"错误: 输入文件 {input_file} 不存在")
        return False
    
    # 存储标准化域名及其原始形式
    domain_map = defaultdict(list)
    
    # 统计信息
    total_domains = 0
    
    try:
        with open(input_file, 'r', encoding='utf-8') as infile:
            for line in infile:
                # 去除行首行尾空白字符
                domain = line.strip()
                
                # 跳过空行
                if not domain:
                    continue
                
                total_domains += 1
                
                # 标准化域名（移除.org.后缀并移除"-"）
                normalized = normalize_domain(domain)
                
                # 将原始域名添加到对应的标准域名列表中
                domain_map[normalized].append(domain)
        
        # 找出出现多次的域名
        duplicates = {norm: originals for norm, originals in domain_map.items() if len(originals) > 1}
        
        # 写入输出文件
        with open(output_file, 'w', encoding='utf-8') as outfile:
            outfile.write("# 出现多次的域名（比较时忽略\"-\"）\n")
            outfile.write("# 格式: 标准化域名 -> 原始域名列表\n\n")
            
            for normalized, originals in sorted(duplicates.items()):
                outfile.write(f"{normalized} -> {', '.join(originals)}\n")
        
        # 如果指定了HTML输出文件，则生成HTML格式的文件
        if html_output_file:
            generate_html_output(duplicates, html_output_file)
        
        # 输出统计信息
        print(f"处理完成!")
        print(f"总域名数: {total_domains}")
        print(f"不同标准化域名数: {len(domain_map)}")
        print(f"重复域名组数: {len(duplicates)}")
        print(f"结果已保存到: {output_file}")
        
        # 如果有重复域名，在控制台也显示一部分
        if duplicates:
            print("\n前10个重复域名组:")
            count = 0
            for normalized, originals in sorted(duplicates.items()):
                if count >= 10:
                    break
                print(f"  {normalized} -> {', '.join(originals)}")
                count += 1
        
        return True
        
    except Exception as e:
        print(f"处理文件时出错: {e}")
        return False

def find_duplicate():
    # 默认文件路径
    default_input = FILE_OUTPUT_DOMAINS_DIFF_ALL
    default_output = FILE_OUTPUT_DOMAINS_DUPLICATE
    default_html_output = HTML_OUTPUT_DOMAINS_DUPLICATE
    
    # 获取命令行参数
    if len(sys.argv) >= 3:
        input_file = sys.argv[1]
        output_file = sys.argv[2]
        html_output_file = sys.argv[3] if len(sys.argv) > 3 else default_html_output
    else:
        input_file = default_input
        output_file = default_output
        html_output_file = default_html_output
        print("使用默认文件路径:")
        print(f"  输入文件: {input_file}")
        print(f"  文本输出文件: {output_file}")
        print(f"  HTML输出文件: {html_output_file}")
        print()
    
    # 执行查找重复域名
    find_duplicate_domains(input_file, output_file, html_output_file)

if __name__ == '__main__':
    find_duplicate()