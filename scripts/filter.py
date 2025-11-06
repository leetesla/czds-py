def normalize_domain(domain):
    """
    将域名标准化：去除首尾空白、移除尾部的点号并转换为小写
    """
    if not domain:
        return ""
    normalized = domain.strip().rstrip(".")
    return normalized.lower()

def filter_domain(domain):
    """
    过滤域名：排除点号数量超过2个的域名，以及含有双连字符的域名，以及含有数字超过2个的域名

    Args:
        domain (str): 域名

    Returns:
        bool: True表示保留该域名，False表示过滤掉
    """
    domain = normalize_domain(domain)
    if not domain:
        return False

    # 计算点号数量
    dot_count = domain.count('.')

    # 检查是否含有双连字符
    has_double_dash = '--' in domain

    # 计算数字数量
    digit_count = sum(1 for char in domain if char.isdigit())
    # 保留点号数量不超过2个且不含有双连字符且数字数量<2个的域名
    return dot_count == 1 and not has_double_dash and digit_count <= 1