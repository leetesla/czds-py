import os
import glob
from datetime import datetime

from app_config.constant import DIR_OUTPUT_DOMAINS_NEW, DIR_OUTPUT_DOMAINS_RESULTS


def get_date_string():
    """
    获取当前日期字符串，格式为 YYYY-MM-DD

    Returns:
        str: 格式为 YYYY-MM-DD 的日期字符串
    """
    return datetime.now().strftime('%Y-%m-%d')


def clear_files_with_extension(directory, extension):
    """
    清除目录下指定后缀的文件

    Args:
        directory (str): 目录路径
        extension (str): 文件后缀，例如 '.txt' 或 'txt'

    Returns:
        int: 删除的文件数量
    """
    # 确保后缀以点开头
    if not extension.startswith('.'):
        extension = '.' + extension
    
    # 构造搜索模式
    pattern = os.path.join(directory, '*' + extension)
    
    # 查找匹配的文件
    files_to_delete = glob.glob(pattern)
    
    # 删除文件并计数
    deleted_count = 0
    for file_path in files_to_delete:
        try:
            os.remove(file_path)
            deleted_count += 1
        except OSError as e:
            print(f"无法删除文件 {file_path}: {e}")
    
    return deleted_count


def mv_domain_chunks_new2old(source_dir, destination_dir, extension ='.txt'):
    """
    将源目录下指定后缀的文件移动到目标目录

    Args:
        source_dir (str): 源目录路径
        destination_dir (str): 目标目录路径
        extension (str): 文件后缀，例如 '.txt' 或 'txt'

    Returns:
        int: 移动的文件数量
    """
    # 确保后缀以点开头
    if not extension.startswith('.'):
        extension = '.' + extension
    
    # 确保目标目录存在
    os.makedirs(destination_dir, exist_ok=True)
    
    # 构造搜索模式
    pattern = os.path.join(source_dir, '*' + extension)
    
    # 查找匹配的文件
    files_to_move = glob.glob(pattern)
    
    # 移动文件并计数
    moved_count = 0
    for file_path in files_to_move:
        try:
            # 获取文件名
            filename = os.path.basename(file_path)
            # 构造目标路径
            destination_path = os.path.join(destination_dir, filename)
            # 移动文件
            os.rename(file_path, destination_path)
            moved_count += 1
        except OSError as e:
            print(f"无法移动文件 {file_path} 到 {destination_dir}: {e}")
    
    return moved_count


DIR_OUTPUT_DOMAINS_NEW_TODAY = os.path.join(DIR_OUTPUT_DOMAINS_NEW, get_date_string())
DIR_OUTPUT_RESULTS_TODAY = os.path.join(DIR_OUTPUT_DOMAINS_RESULTS, get_date_string())

FILE_OUTPUT_DOMAINS_NEW_ALL = os.path.join(DIR_OUTPUT_RESULTS_TODAY, 'all.txt')
FILE_OUTPUT_DOMAINS_DUPLICATE = os.path.join(DIR_OUTPUT_RESULTS_TODAY, 'domains-duplicate.txt')
HTML_OUTPUT_DOMAINS_DUPLICATE = os.path.join(DIR_OUTPUT_RESULTS_TODAY, 'domains-duplicate.html')

# 添加数据库文件路径
DB_FILE = os.path.join('output', 'domains.db')