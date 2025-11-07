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


DIR_OUTPUT_DOMAINS_NEW_TODAY = os.path.join(DIR_OUTPUT_DOMAINS_NEW, get_date_string())
DIR_OUTPUT_RESULTS_TODAY = os.path.join(DIR_OUTPUT_DOMAINS_RESULTS, get_date_string())

FILE_OUTPUT_DOMAINS_NEW_ALL = os.path.join(DIR_OUTPUT_RESULTS_TODAY, 'all.txt')
FILE_OUTPUT_DOMAINS_DUPLICATE = os.path.join(DIR_OUTPUT_RESULTS_TODAY, 'domains-duplicate.txt')
HTML_OUTPUT_DOMAINS_DUPLICATE = os.path.join(DIR_OUTPUT_RESULTS_TODAY, 'domains-duplicate.html')

# 添加数据库文件路径
DB_FILE = os.path.join('output', 'domains.db')