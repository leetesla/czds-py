from app_config.constant import DIR_OUTPUT_DOMAINS_001, DIR_DOWNLOAD_001
from scripts.extract_first_column import extract_first_column_from_directory

if __name__ == "__main__":
    # print("******* download() ********")
    # download()

    # print("******* unzip_zone_files() ********")
    # unzip_zone_files("download")

    # print("********* extract_first_column_from_directory() ********")
    extract_first_column_from_directory(DIR_DOWNLOAD_001, DIR_OUTPUT_DOMAINS_001)