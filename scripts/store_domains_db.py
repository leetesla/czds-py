#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
将域名数据存储到SQLite数据库，并定期清理旧数据
"""

import os
import sqlite3
from datetime import datetime, timedelta

# 从util模块导入数据库文件路径
from util import FILE_OUTPUT_DOMAINS_NEW_ALL, DB_FILE


def init_database():
    """初始化数据库表"""
    # 确保output目录存在
    output_dir = os.path.dirname(DB_FILE)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
    
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # 创建域名表，使用自增ID和日期组合确保唯一性
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS domains (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            domain TEXT NOT NULL,
            created_date DATE NOT NULL,
            UNIQUE(domain, created_date)
        )
    ''')
    
    # 创建索引提高查询效率
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_domain ON domains(domain)
    ''')
    
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_created_date ON domains(created_date)
    ''')
    
    conn.commit()
    conn.close()


def store_domains_to_db(domains_file):
    """
    将域名存储到数据库
    
    Args:
        domains_file (str): 包含域名的文件路径
    """
    if not os.path.exists(domains_file):
        print(f"文件 {domains_file} 不存在")
        return
    
    # 初始化数据库
    init_database()
    
    # 获取今天的日期
    today = datetime.now().date()
    
    # 确保输出目录存在
    output_dir = os.path.dirname(domains_file)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
    
    # 连接数据库
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # 读取域名文件并插入数据库
    inserted_count = 0
    duplicate_count = 0
    
    with open(domains_file, 'r', encoding='utf-8') as f:
        for line in f:
            domain = line.strip()
            if domain:  # 忽略空行
                try:
                    cursor.execute(
                        'INSERT INTO domains (domain, created_date) VALUES (?, ?)',
                        (domain, today)
                    )
                    inserted_count += 1
                except sqlite3.IntegrityError:
                    # 域名在当天已经存在
                    duplicate_count += 1
    
    conn.commit()
    conn.close()
    
    print(f"成功插入 {inserted_count} 条记录到数据库")
    if duplicate_count > 0:
        print(f"发现 {duplicate_count} 条重复记录")


def delete_old_data(days=7):
    """
    删除指定天数前的数据
    
    Args:
        days (int): 保留数据的天数，默认为7天
    """
    # 检查数据库文件是否存在
    if not os.path.exists(DB_FILE):
        print("数据库文件不存在")
        return
    
    # 计算删除数据的截止日期
    cutoff_date = datetime.now().date() - timedelta(days=days)
    
    # 连接数据库
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # 删除旧数据
    cursor.execute(
        'DELETE FROM domains WHERE created_date < ?',
        (cutoff_date,)
    )
    
    deleted_count = cursor.rowcount
    
    conn.commit()
    conn.close()
    
    print(f"成功删除 {deleted_count} 条 {days} 天前的记录")


def get_domains_count_by_date():
    """获取按日期分组的域名数量统计"""
    if not os.path.exists(DB_FILE):
        print("数据库文件不存在")
        return []
    
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT created_date, COUNT(*) 
        FROM domains 
        GROUP BY created_date 
        ORDER BY created_date DESC
    ''')
    
    results = cursor.fetchall()
    conn.close()
    
    return results


def save_domains(domains_file=FILE_OUTPUT_DOMAINS_NEW_ALL):
    """主函数"""
    print("开始将域名数据存储到数据库...")
    
    # 存储域名到数据库
    store_domains_to_db(domains_file)
    
    # 删除7天前的数据
    print("开始清理7天前的数据...")
    delete_old_data(7)
    
    # 显示统计数据
    print("\n域名数据统计:")
    stats = get_domains_count_by_date()
    for date, count in stats:
        print(f"  {date}: {count} 个域名")


if __name__ == '__main__':
    save_domains()