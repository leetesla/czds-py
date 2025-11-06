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
python3 find_duplicate_domains.py [文本输出文件] [HTML输出文件] [最近几天]

如果没有提供参数，则使用默认路径:
文本输出文件: /Users/chrise/app/util-script/domains/duplicate_domains.txt
HTML输出文件: /Users/chrise/app/util-script/domains/duplicate_domains.html
最近几天: 7 (默认读取最近7天的数据)
"""

import os
import sys
import sqlite3
from collections import defaultdict
from datetime import datetime, timedelta
import shutil

from app_config.constant import DUPLICATE_MIN_COUNT, DIR_PUBLIC
from util.util import get_date_string, DB_FILE, FILE_OUTPUT_DOMAINS_DUPLICATE, HTML_OUTPUT_DOMAINS_DUPLICATE


def get_domain_keyword(domain):
    """
    移除常见顶级域名后缀并移除所有"-"
    
    Args:
        domain (str): 原始域名
        
    Returns:
        str: 标准化后的域名 keyword
    """
    # 先判断最后一个是不是"."，如果是，先去掉
    if domain.endswith('.'):
        domain = domain[:-1]
    
    # 重新获取最后一个"."的位置，去掉"."和它后面的后缀
    last_dot_index = domain.rfind('.')
    if last_dot_index != -1:
        domain = domain[:last_dot_index]
    
    # 移除所有的 "-"
    normalized = domain.replace('-', '')

    # print(f"--- normalized: {normalized} ---")
    
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
            outfile.write(f"    <title>{get_date_string()} 重复域名列表</title>\n")
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
            outfile.write(f'    <h1>{get_date_string()} 重复域名列表 (共{len(duplicates)}组)</h1>\n')
            outfile.write('    <p>点击域名可直接访问（需要网络连接）</p>\n')
            
            for normalized, originals in sorted(duplicates.items()):
                outfile.write('    <div class="domain-group">\n')
                outfile.write(f'        <div class="normalized-domain">域名关键词: {normalized}</div>\n')
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

def get_domains_from_db(days=7):
    """
    从数据库获取最近几天的域名数据
    
    Args:
        days (int): 最近几天的数据，默认7天
        
    Returns:
        list: 域名列表
    """
    # 检查数据库文件是否存在
    if not os.path.exists(DB_FILE):
        print(f"错误: 数据库文件 {DB_FILE} 不存在")
        return []
    
    # 计算截止日期
    cutoff_date = datetime.now().date() - timedelta(days=days)
    
    # 连接数据库
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # 查询最近几天的域名数据
    cursor.execute(
        'SELECT domain FROM domains WHERE created_date >= ?',
        (cutoff_date,)
    )
    
    domains = [row[0] for row in cursor.fetchall()]
    
    conn.close()
    
    print(f"从数据库读取了 {len(domains)} 个域名（最近 {days} 天）")
    return domains

def find_duplicate_domains_from_db(output_file, html_output_file=None, days=7):
    """
    从数据库读取域名，找出出现多次的域名（比较时忽略"-"）
    
    Args:
        output_file (str): 输出文件路径
        html_output_file (str): HTML输出文件路径（可选）
        days (int): 读取最近几天的数据，默认7天
    """
    # 从数据库获取域名数据
    domains = get_domains_from_db(days)
    
    if not domains:
        print("没有从数据库读取到任何域名数据")
        return False
    
    # 存储标准化域名及其原始形式
    domain_map = defaultdict(list)
    
    # 统计信息
    total_domains = len(domains)
    
    # 处理每个域名
    for domain in domains:
        # 跳过空行
        if not domain:
            continue
        
        # 标准化域名（移除.org.后缀并移除"-"）
        normalized = get_domain_keyword(domain)
        
        # 将原始域名添加到对应的标准域名列表中
        domain_map[normalized].append(domain)
    
    # 找出出现多次的域名
    duplicates = {norm: originals for norm, originals in domain_map.items() if len(originals) >= DUPLICATE_MIN_COUNT}
    
    # 写入输出文件
    with open(output_file, 'w', encoding='utf-8') as outfile:
        outfile.write("# 出现多次的域名（比较时忽略\"-\"）\n")
        outfile.write("# 格式: 标准化域名 -> 原始域名列表\n\n")
        
        for normalized, originals in sorted(duplicates.items()):
            outfile.write(f"{normalized} -> {', '.join(originals)}\n")
    
    # 如果指定了HTML输出文件，则生成HTML格式的文件
    if html_output_file:
        generate_html_output(duplicates, html_output_file)
        
        # 将html_output_file复制到DIR_PUBLIC目录下，重命名为date_str.html
        date_str = get_date_string()
        public_html_file = os.path.join(DIR_PUBLIC, date_str + '.html')
        try:
            # 确保public目录存在
            os.makedirs(DIR_PUBLIC, exist_ok=True)
            # 复制文件
            shutil.copy2(html_output_file, public_html_file)
            print(f"HTML文件已复制到: {public_html_file}")
        except Exception as e:
            print(f"复制HTML文件到public目录时出错: {e}")
    
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

def find_duplicate(default_days=7):
    # 默认文件路径
    default_output = FILE_OUTPUT_DOMAINS_DUPLICATE
    default_html_output = HTML_OUTPUT_DOMAINS_DUPLICATE
    # default_days = 7
    
    # 获取命令行参数
    if len(sys.argv) >= 2:
        output_file = sys.argv[1]
        html_output_file = sys.argv[2] if len(sys.argv) > 2 else default_html_output
        days = int(sys.argv[3]) if len(sys.argv) > 3 else default_days
    else:
        output_file = default_output
        html_output_file = default_html_output
        days = default_days
        print("使用默认配置:")
        print(f"  文本输出文件: {output_file}")
        print(f"  HTML输出文件: {html_output_file}")
        print(f"  读取最近天数: {days} 天")
        print()
    
    # 执行查找重复域名
    find_duplicate_domains_from_db(output_file, html_output_file, days)
    date_str = get_date_string()

if __name__ == '__main__':
    find_duplicate(1)