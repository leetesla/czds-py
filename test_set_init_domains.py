from app_config.constant import DIR_OUTPUT_DOMAIN_CHUNKS_NEW, DIR_OUTPUT_DOMAIN_CHUNKS_OLD
from scripts.prepare import set_init_domains

if __name__ == "__main__":
    print("【1】 ******* set_init_domains() ********")
    set_init_domains(DIR_OUTPUT_DOMAIN_CHUNKS_NEW, DIR_OUTPUT_DOMAIN_CHUNKS_OLD)