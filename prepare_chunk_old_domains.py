import sys

from app_config.constant import DIR_OUTPUT_DOMAIN_CHUNKS_NEW, DIR_OUTPUT_DOMAIN_CHUNKS_OLD
from extract_and_chunk_old_domains import extract_and_chunk_old_domains
from scripts.prepare import set_init_domains

if "--mv" in sys.argv:
    print("【1】 ******* set_init_domains() ********")
    set_init_domains(DIR_OUTPUT_DOMAIN_CHUNKS_NEW, DIR_OUTPUT_DOMAIN_CHUNKS_OLD)
else:
    print("【1】 ******* extract_and_chunk_old_domains() ********")
    extract_and_chunk_old_domains()