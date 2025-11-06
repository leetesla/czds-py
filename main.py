from app_config.constant import DIR_DOWNLOAD_ZONEFILES, DIR_OUTPUT_DOMAINS_002
from download import download
from scripts.extract_first_column import extract_first_column_from_directory
from scripts.fast_diff_domain import diff_domains
from scripts.find_duplicate_domains import find_duplicate
from scripts.merge2all import merge2all
from scripts.unzip_zone_files import unzip_zone_files

if __name__ == "__main__":
    # print("******* download() ********")
    # download()

    # print("******* unzip_zone_files() ********")
    # unzip_zone_files("download")

    print("********* extract_first_column_from_directory() ********")
    extract_first_column_from_directory(DIR_DOWNLOAD_ZONEFILES, DIR_OUTPUT_DOMAINS_002)

    print("********* diff_domains() ********")
    diff_domains()

    print("******** merge2all() ********")
    merge2all()


    print("******* find_duplicate() ********")
    find_duplicate()
