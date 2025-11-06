from app_config.constant import DIR_OUTPUT_DOMAINS_001, DIR_DOWNLOAD_001, DIR_OUTPUT_DOMAINS_002, DIR_DOWNLOAD_ZONEFILES
from scripts.extract_first_column import extract_first_column_from_directory

if __name__ == "__main__":

    print("********* extract_first_column_from_directory() 001 ********")
    extract_first_column_from_directory(DIR_DOWNLOAD_001, DIR_OUTPUT_DOMAINS_001)

    # print("********* extract_first_column_from_directory() 002 ********")
    # extract_first_column_from_directory(DIR_DOWNLOAD_ZONEFILES, DIR_OUTPUT_DOMAINS_002)