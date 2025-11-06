import time
from app_config.constant import DIR_DOWNLOAD_ZONEFILES, DIR_OUTPUT_DOMAINS_002
from util.util import FILE_OUTPUT_DOMAINS_NEW_ALL


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
    from scripts.extract_first_column import extract_first_column_from_directory
    # 使用较小的批处理大小以减少内存使用
    extract_first_column_from_directory(DIR_DOWNLOAD_ZONEFILES, DIR_OUTPUT_DOMAINS_002, batch_size=2000)
    
    if enable_delay:
        print("等待5秒以释放内存...")
        time.sleep(5)

    print("【5】 ********* diff_domains() ********")
    from scripts.chunked_diff_domain import diff_domains
    diff_domains()
    
    if enable_delay:
        print("等待5秒以释放内存...")
        time.sleep(5)

    print("【6】 ******** merge2all() ********")
    from scripts.merge2all import merge2all
    merge2all(batch_size=2048)
    
    if enable_delay:
        print("等待5秒以释放内存...")
        time.sleep(5)

    print("【7】 ******** save_domains_to_db() ********")
    from scripts.store_domains_db import save_domains_to_db
    # 使用较小的批处理大小以减少内存使用
    save_domains_to_db(FILE_OUTPUT_DOMAINS_NEW_ALL, batch_size=200)
    
    if enable_delay:
        print("等待5秒以释放内存...")
        time.sleep(5)

    print("【8】 ******* find_duplicate() ********")
    from scripts.find_duplicate_domains import find_duplicate
    find_duplicate(1)


def run_task_low_memory():
    """
    低内存模式运行任务
    """
    run_task(enable_delay=True)