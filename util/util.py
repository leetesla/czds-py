import os
from datetime import datetime

from app_config.constant import DIR_OUTPUT_DOMAINS_NEW, DIR_OUTPUT_DOMAINS_RESULTS


def get_date_string():
    """
    获取当前日期字符串，格式为 YYYY-MM-DD

    Returns:
        str: 格式为 YYYY-MM-DD 的日期字符串
    """
    return datetime.now().strftime('%Y-%m-%d')


DIR_OUTPUT_DOMAINS_NEW_TODAY = os.path.join(DIR_OUTPUT_DOMAINS_NEW, get_date_string())
DIR_OUTPUT_RESULTS_TODAY = os.path.join(DIR_OUTPUT_DOMAINS_RESULTS, get_date_string())

FILE_OUTPUT_DOMAINS_NEW_ALL = os.path.join(DIR_OUTPUT_RESULTS_TODAY, 'all.txt')
FILE_OUTPUT_DOMAINS_DUPLICATE = os.path.join(DIR_OUTPUT_RESULTS_TODAY, 'domains-duplicate.txt')
HTML_OUTPUT_DOMAINS_DUPLICATE = os.path.join(DIR_OUTPUT_RESULTS_TODAY, 'domains-duplicate.html')

# 添加数据库文件路径
DB_FILE = os.path.join('output', 'domains.db')