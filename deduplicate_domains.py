#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
统计文件中的重复域名数量，以及去重前后的域名数量

功能说明:
1. 统计文件中域名的总数量
2. 统计去重后的域名数量
3. 统计重复域名的数量（出现次数大于1的域名）
4. 显示重复率
5. 显示重复域名的示例

使用方法:
python3 deduplicate_domains.py [文件路径]

如果没有提供文件路径，则使用默认路径: output/all.txt
"""

import sys
from collections import Counter

def count_domains(file_path):
    """
    统计文件中的域名数量，包括重复和去重后的数量
    
    Args:
        file_path (str): 域名文件路径
        
    Returns:
        tuple: (总域名数, 去重后域名数, 重复域名数, 域名计数器)
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            # 读取所有行并去除空白字符
            domains = [line.strip() for line in f if line.strip()]
        
        total_count = len(domains)
        unique_domains = set(domains)
        unique_count = len(unique_domains)
        
        # 使用Counter统计每个域名出现的次数
        domain_counter = Counter(domains)
        
        # 找出重复的域名数量（出现次数大于1的域名）
        duplicate_count = sum(1 for count in domain_counter.values() if count > 1)
        
        return total_count, unique_count, duplicate_count, domain_counter
        
    except FileNotFoundError:
        print(f"错误: 文件 '{file_path}' 未找到")
        return None
    except Exception as e:
        print(f"处理文件时出错: {e}")
        return None

def show_help():
    """显示帮助信息"""
    print("域名重复统计工具")
    print("使用方法:")
    print("  python3 deduplicate_domains.py [文件路径]")
    print("")
    print("参数说明:")
    print("  文件路径    要分析的域名文件路径（可选）")
    print("              如果未提供，则默认使用 'output/all.txt'")
    print("")
    print("功能说明:")
    print("  - 统计文件中域名的总数量")
    print("  - 统计去重后的域名数量")
    print("  - 统计重复域名的数量")
    print("  - 显示重复率")
    print("  - 显示重复域名的示例")

def main():
    # 检查是否需要显示帮助信息
    if len(sys.argv) > 1 and sys.argv[1] in ['-h', '--help', 'help']:
        show_help()
        return
    
    # 如果提供了命令行参数，则使用参数作为文件路径，否则使用默认路径
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
    else:
        # 默认文件路径
        file_path = "output/domains-001/org.txt"
        print(f"未提供文件路径，使用默认路径: {file_path}")
    
    result = count_domains(file_path)
    if result:
        total_count, unique_count, duplicate_count, domain_counter = result
        
        print(f"\n文件分析结果: {file_path}")
        print("=" * 50)
        print(f"去重前域名总数: {total_count}")
        print(f"去重后域名总数: {unique_count}")
        print(f"重复域名数量: {duplicate_count}")
        print(f"重复率: {(duplicate_count/total_count)*100:.2f}%" if total_count > 0 else "重复率: 0%")
        
        # 计算去重减少的数量
        reduced_count = total_count - unique_count
        print(f"去重减少数量: {reduced_count}")
        
        # 显示一些重复的域名示例（如果有的话）
        duplicates = {domain: count for domain, count in domain_counter.items() if count > 1}
        if duplicates:
            print(f"\n重复域名详情:")
            print("-" * 30)
            print(f"{'域名':<30} {'出现次数':<10}")
            print("-" * 40)
            # 按出现次数排序，显示前20个
            for domain, count in sorted(duplicates.items(), key=lambda x: x[1], reverse=True)[:20]:
                print(f"{domain:<30} {count:<10}")

if __name__ == "__main__":
    main()