from download import download
from scripts.fast_diff_domain import diff_domains
from scripts.find_duplicate_domains import find_duplicate
from scripts.merge2all import merge2all

if __name__ == "__main__":
    download()
    diff_domains()
    merge2all()
    find_duplicate()
