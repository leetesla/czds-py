#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
将域名数据存储到SQLite数据库，并定期清理旧数据
"""

import os
import sqlite3
from datetime import datetime, timedelta

from util.util import DB_FILE, FILE_OUTPUT_DOMAINS_NEW_ALL


def _deduplicate_domain_records(cursor):
    """
    清理domains表中的重复域名记录，只保留最新的一条
    """
    cursor.execute('''
        SELECT 1
        FROM domains
        GROUP BY domain
        HAVING COUNT(*) > 1
        LIMIT 1
    ''')
    if cursor.fetchone() is None:
        return 0
    
    cursor.execute('''
        DELETE FROM domains AS older
        WHERE EXISTS (
            SELECT 1
            FROM domains AS newer
            WHERE newer.domain = older.domain
              AND (
                  newer.created_date > older.created_date
                  OR (newer.created_date = older.created_date AND newer.id > older.id)
              )
        )
    ''')
    return cursor.rowcount


def init_database():
    """初始化数据库表"""
    # 确保output目录存在
    output_dir = os.path.dirname(DB_FILE)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
    
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # 创建域名表，使用域名确保唯一性
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS domains (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            domain TEXT NOT NULL UNIQUE,
            created_date DATE NOT NULL
        )
    ''')
    
    removed_rows = _deduplicate_domain_records(cursor)
    if removed_rows:
        print(f"清理了 {removed_rows} 条重复域名记录，确保域名唯一")
    
    # 创建唯一索引确保域名不重复
    cursor.execute('''
        CREATE UNIQUE INDEX IF NOT EXISTS idx_domains_domain_unique ON domains(domain)
    ''')
    
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_created_date ON domains(created_date)
    ''')
    
    conn.commit()
    conn.close()


def store_domains_to_db(domains_file, batch_size=1000):
    """
    将域名存储到数据库
    
    Args:
        domains_file (str): 包含域名的文件路径
        batch_size (int): 批处理大小，控制内存使用
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
    
    insert_sql = 'INSERT OR IGNORE INTO domains (domain, created_date) VALUES (?, ?)'
    update_sql = 'UPDATE domains SET created_date = ? WHERE domain = ?'
    
    def flush_batch(batch_items):
        """将批次数据写入数据库并更新重复数据的日期"""
        nonlocal inserted_count, duplicate_count
        if not batch_items:
            return
        
        cursor.executemany(insert_sql, batch_items)
        inserted = cursor.rowcount if cursor.rowcount is not None and cursor.rowcount >= 0 else 0
        duplicates = len(batch_items) - inserted
        if duplicates < 0:
            duplicates = 0
        
        update_params = [(created_date, domain) for domain, created_date in batch_items]
        cursor.executemany(update_sql, update_params)
        
        conn.commit()
        
        inserted_count += inserted
        duplicate_count += duplicates
    
    # 读取域名文件并插入数据库（分批处理以节省内存）
    inserted_count = 0
    duplicate_count = 0
    batch = []
    
    with open(domains_file, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            domain = line.strip()
            if domain:  # 忽略空行
                batch.append((domain, today))
                
                # 当批次达到指定大小时，执行插入操作
                if len(batch) >= batch_size:
                    try:
                        flush_batch(batch)
                        batch = []  # 清空批次
                        
                        # 每处理一定数量的行后打印进度
                        if line_num % (batch_size * 10) == 0:
                            print(f"已处理 {line_num} 行...")
                    except sqlite3.Error as e:
                        print(f"数据库插入错误 (行 {line_num}): {e}")
                        batch = []  # 清空批次
    
    # 处理剩余的记录
    if batch:
        try:
            flush_batch(batch)
        except sqlite3.Error as e:
            print(f"数据库插入错误: {e}")
    
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


def save_domains_to_db(domains_file=FILE_OUTPUT_DOMAINS_NEW_ALL, batch_size=1000):
    """主函数"""
    print("开始将域名数据存储到数据库...")
    
    # 存储域名到数据库
    store_domains_to_db(domains_file, batch_size)
    
    # 删除7天前的数据
    print("开始清理7天前的数据...")
    delete_old_data(7)
    
    # 显示统计数据
    print("\n域名数据统计:")
    stats = get_domains_count_by_date()
    for date, count in stats:
        print(f"  {date}: {count} 个域名")


if __name__ == '__main__':
    save_domains_to_db()
