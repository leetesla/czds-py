import sys

from app_config.constant import DIR_OUTPUT_DOMAIN_CHUNKS_NEW, DIR_OUTPUT_DOMAIN_CHUNKS_OLD
from extract_and_chunk_old_domains import extract_and_chunk_old_domains
from util.util import mv_domain_chunks_new2old

if "--mv" in sys.argv:
    print("【1】 ******* mv_domain_chunks_new2old() ********")
    c = mv_domain_chunks_new2old(DIR_OUTPUT_DOMAIN_CHUNKS_NEW, DIR_OUTPUT_DOMAIN_CHUNKS_OLD)
    print(f"移动了{c}个文件")
else:
    print("【1】 ******* extract_and_chunk_old_domains() ********")
    extract_and_chunk_old_domains()