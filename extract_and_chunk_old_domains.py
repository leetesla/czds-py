import time
import os
import sys
import glob

from app_config.constant import DIR_OUTPUT_DOMAINS_001, DIR_DOWNLOAD_001, DIR_OUTPUT_DOMAIN_CHUNKS_OLD
from scripts.chunked_diff_domain import chunk_directory_domains
from scripts.extract_first_column import extract_first_column_from_directory
from util.util import clear_files_with_extension


def check_txt_in_dir(dir_check):
    # 检查 dir_check 目录中的 .txt 文件
    print(f"检查目录 {dir_check} 中的 .txt 文件...")

    # 确保目录存在
    if not os.path.exists(dir_check):
        print(f"目录 {dir_check} 不存在")
        return False

    # 查找 .txt 文件
    txt_files = glob.glob(os.path.join(dir_check, "*.txt"))

    if not txt_files:
        print(f"目录 {dir_check} 中没有 .txt 文件，程序退出。")
        return False

    # 列出前 10 个 .txt 文件
    print(f"目录 {dir_check} 中的前 10 个 .txt 文件：")
    for i, file in enumerate(txt_files[:10]):
        print(f"{i + 1}. {os.path.basename(file)}")

    return True

def extract_and_chunk_old_domains():
    enable_delay = True
    print("【5】 ********* extract_old_domains() ********")
    check_download_001 = check_txt_in_dir(DIR_DOWNLOAD_001)

    if check_download_001:
        print(f"{DIR_DOWNLOAD_001}存在.txt文件，清空{DIR_OUTPUT_DOMAINS_001}")
        clear_files_with_extension(DIR_OUTPUT_DOMAINS_001, '.txt')

        old_domains_ready = extract_first_column_from_directory(
            DIR_DOWNLOAD_001,
            DIR_OUTPUT_DOMAINS_001,
            batch_size=2000,
        )

        if enable_delay:
            print("等待5秒以释放内存...")
            time.sleep(5)
    else:
        print(f"{DIR_DOWNLOAD_001}不存在.txt文件，查看{DIR_OUTPUT_DOMAINS_001}")

    print("【7】 ********* chunk_old_domain_files() ********")
    check_domains_001 = check_txt_in_dir(DIR_OUTPUT_DOMAINS_001)

    if check_domains_001:
        print(f"{DIR_OUTPUT_DOMAINS_001}存在.txt文件，清空{DIR_OUTPUT_DOMAIN_CHUNKS_OLD}")
        clear_files_with_extension(DIR_OUTPUT_DOMAIN_CHUNKS_OLD, '.txt')
        old_chunks_ready = chunk_directory_domains(
            DIR_OUTPUT_DOMAINS_001,
            DIR_OUTPUT_DOMAIN_CHUNKS_OLD,
            num_chunks=128,
            batch_size=2000,
        )
        return old_chunks_ready
    else:
        print(f"{DIR_OUTPUT_DOMAINS_001}不存在.txt文件，检查{DIR_OUTPUT_DOMAIN_CHUNKS_OLD}")


    check_chunks_old = check_txt_in_dir(DIR_OUTPUT_DOMAIN_CHUNKS_OLD)
    if check_chunks_old:
        print(f"{DIR_OUTPUT_DOMAIN_CHUNKS_OLD}不存在.txt文件")
        return True

    else:
        print(f"{DIR_OUTPUT_DOMAIN_CHUNKS_OLD}不存在.txt文件")
        return False


if __name__ == "__main__":
    extract_and_chunk_old_domains()


