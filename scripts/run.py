import time
from app_config.constant import (
    DIR_DOWNLOAD_001,
    DIR_DOWNLOAD_ZONEFILES,
    DIR_OUTPUT_DOMAINS_001,
    DIR_OUTPUT_DOMAINS_002,
    DIR_OUTPUT_DOMAIN_CHUNKS_NEW,
    DIR_OUTPUT_DOMAIN_CHUNKS_OLD,
)
from scripts.unzip_zone_files import unzip_zone_files
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

    print("【4】 ********* extract_new_domains() ********")
    from scripts.extract_first_column import extract_first_column_from_directory

    new_domains_ready = extract_first_column_from_directory(
        DIR_DOWNLOAD_ZONEFILES,
        DIR_OUTPUT_DOMAINS_002,
        batch_size=2000,
    )
    if not new_domains_ready:
        print("未能生成新的域名文件，结束任务。")
        return False
    
    if enable_delay:
        print("等待5秒以释放内存...")
        time.sleep(5)

    print("【5】 ********* extract_old_domains() ********")
    old_domains_ready = extract_first_column_from_directory(
        DIR_DOWNLOAD_001,
        DIR_OUTPUT_DOMAINS_001,
        batch_size=2000,
    )
    if not old_domains_ready:
        print("旧的 TLD 文件不存在或为空，将视所有域名为新增。")

    if enable_delay:
        print("等待5秒以释放内存...")
        time.sleep(5)

    print("【6】 ********* chunk_new_domain_files() ********")
    from scripts.chunked_diff_domain import chunk_directory_domains, diff_chunk_directories_to_file

    new_chunks_ready = chunk_directory_domains(
        DIR_OUTPUT_DOMAINS_002,
        DIR_OUTPUT_DOMAIN_CHUNKS_NEW,
        num_chunks=128,
        batch_size=2000,
    )
    if not new_chunks_ready:
        print("未能生成新的块文件，结束任务。")
        return False
    
    if enable_delay:
        print("等待5秒以释放内存...")
        time.sleep(5)

    print("【7】 ********* chunk_old_domain_files() ********")
    old_chunks_ready = chunk_directory_domains(
        DIR_OUTPUT_DOMAINS_001,
        DIR_OUTPUT_DOMAIN_CHUNKS_OLD,
        num_chunks=128,
        batch_size=2000,
    )
    if not old_chunks_ready:
        print("旧域名块不存在，将视所有域名为新增。")

    if enable_delay:
        print("等待5秒以释放内存...")
        time.sleep(5)

    print("【8】 ********* diff_chunk_directories() ********")
    diff_chunk_directories_to_file(
        DIR_OUTPUT_DOMAIN_CHUNKS_NEW,
        DIR_OUTPUT_DOMAIN_CHUNKS_OLD,
        FILE_OUTPUT_DOMAINS_NEW_ALL,
        num_chunks=128,
    )
    
    if enable_delay:
        print("等待5秒以释放内存...")
        time.sleep(5)

    print("【9】 ******** save_domains_to_db() ********")
    from scripts.store_domains_db import save_domains_to_db
    # 使用较小的批处理大小以减少内存使用
    save_domains_to_db(FILE_OUTPUT_DOMAINS_NEW_ALL, batch_size=200)
    
    if enable_delay:
        print("等待5秒以释放内存...")
        time.sleep(5)

    print("【10】 ******* find_duplicate() ********")
    from scripts.find_duplicate_domains import find_duplicate
    find_duplicate(1)
    return True


def run_task_low_memory():
    """
    低内存模式运行任务
    """
    return run_task(enable_delay=True)
