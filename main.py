from app_config.constant import DIR_DOWNLOAD_ZONEFILES, DIR_OUTPUT_DOMAINS_002
from download import download
from scripts.chunked_diff_domain import diff_domains
from scripts.extract_first_column import extract_first_column_from_directory
# from scripts.fast_diff_domain import diff_domains
from scripts.find_duplicate_domains import find_duplicate
from scripts.merge2all import merge2all
from scripts.prepare import set_init_domains
from scripts.store_domains_db import save_domains
from scripts.unzip_zone_files import unzip_zone_files

if __name__ == "__main__":
    print("【1】 ******* set_init_domains() ********")
    # set_init_domains()

    print("【2】 ******* download() ********")
    # download()

    print("【3】 ******* unzip_zone_files() ********")
    # unzip_zone_files("download")

    print("【4】 ********* extract_first_column_from_directory() ********")
    extract_first_column_from_directory(DIR_DOWNLOAD_ZONEFILES, DIR_OUTPUT_DOMAINS_002)

    print("【5】 ********* diff_domains() ********")
    diff_domains()

    print("【6】 ******** merge2all() ********")
    merge2all()

    print("【6】 ******** merge2all() ********")
    save_domains()

    print("【7】 ******* find_duplicate() ********")
    find_duplicate()
