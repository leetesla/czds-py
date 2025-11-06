import time
from app_config.constant import DIR_DOWNLOAD_ZONEFILES, DIR_OUTPUT_DOMAINS_002
from scripts.chunked_diff_domain import diff_domains
from scripts.extract_first_column import extract_first_column_from_directory
from scripts.find_duplicate_domains import find_duplicate
from scripts.merge2all import merge2all
from scripts.store_domains_db import save_domains_to_db


def run_task(enable_delay=False):
    """
    运行任务
    
    Args:
        enable_delay (bool): 是否启用延迟以减少内存峰值使用
    """
    print("【1】 ******* set_init_domains() ********")
    # set_init_domains()

    print("【2】 ******* download() ********")
    # download()

    print("【3】 ******* unzip_zone_files() ********")
    # unzip_zone_files("download")

    print("【4】 ********* extract_first_column_from_directory() ********")
    extract_first_column_from_directory(DIR_DOWNLOAD_ZONEFILES, DIR_OUTPUT_DOMAINS_002)
    
    if enable_delay:
        print("等待5秒以释放内存...")
        time.sleep(5)

    print("【5】 ********* diff_domains() ********")
    diff_domains()
    
    if enable_delay:
        print("等待5秒以释放内存...")
        time.sleep(5)

    print("【6】 ******** merge2all() ********")
    merge2all()
    
    if enable_delay:
        print("等待5秒以释放内存...")
        time.sleep(5)

    print("【7】 ******** save_domains_to_db() ********")
    save_domains_to_db()
    
    if enable_delay:
        print("等待5秒以释放内存...")
        time.sleep(5)

    print("【8】 ******* find_duplicate() ********")
    find_duplicate(1)


def run_task_low_memory():
    """
    低内存模式运行任务
    """
    run_task(enable_delay=True)