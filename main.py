from download import download
from scripts.fast_diff_domain import diff_domains
from scripts.find_duplicate_domains import find_duplicate
from scripts.merge2all import merge2all
from scripts.unzip_zone_files import unzip_zone_files

if __name__ == "__main__":
    # download()
    unzip_zone_files("download")
    # diff_domains()
    # merge2all()
    # find_duplicate()
