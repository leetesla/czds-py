import time

from app_config.constant import DIR_OUTPUT_DOMAINS_002, DIR_DOWNLOAD_ZONEFILES, DIR_OUTPUT_DOMAIN_CHUNKS_NEW

def extract_and_chunk_new_domains():
    enable_delay = True
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
    else:
        print("已生成新的块文件，结束任务。")
        return True


if __name__ == "__main__":
    extract_and_chunk_new_domains()


