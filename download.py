from do_download import download
from scripts.unzip_zone_files import unzip_zone_files

if __name__ == "__main__":
    print("【2】 ******* download() ********")
    download()

    print("【3】 ******* unzip_zone_files() ********")
    unzip_zone_files("download")