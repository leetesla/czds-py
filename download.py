from do_download import download
from scripts.unzip_zone_files import unzip_zone_files


def download_new_zone_files():
    print("【1】 ******* download() ********")
    download()

    print("【2】 ******* unzip_zone_files() ********")
    unzip_zone_files("download")

if __name__ == "__main__":
    download_new_zone_files()