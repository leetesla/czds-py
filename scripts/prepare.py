import os
import shutil
import glob

from app_config.config import get_tlds_from_config


def set_init_domains():
    # 确保必要的目录存在
    os.makedirs('output/domains-001', exist_ok=True)
    os.makedirs('output/domains-002', exist_ok=True)
    
    # 清理output/domains-001目录下与TLD对应的.txt文件
    clean_txt_files('output/domains-001')
    
    # 将output/domains-002目录下与TLD对应的.txt文件移动到output/domains-001目录下
    move_txt_files('output/domains-002', 'output/domains-001')


def clean_txt_files(directory):
    """清理指定目录下与TLD对应的.txt文件"""
    tlds = get_tlds_from_config()
    if not tlds:
        print("未找到配置的TLD列表")
        return
        
    for tld in tlds:
        # 构造特定TLD的文件名
        file_name = f"{tld}.txt"
        file_path = os.path.join(directory, file_name)
        
        # 检查文件是否存在并删除
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                print(f"已删除文件: {file_path}")
            except Exception as e:
                print(f"删除文件 {file_path} 时出错: {e}")
        else:
            print(f"文件不存在: {file_path}")


def move_txt_files(source_dir, target_dir):
    """将源目录下与TLD对应的.txt文件移动到目标目录"""
    # 确保目标目录存在
    os.makedirs(target_dir, exist_ok=True)
    
    # 获取配置中的TLD列表
    tlds = get_tlds_from_config()
    if not tlds:
        print("未找到配置的TLD列表")
        return
    
    # 只处理与TLD对应的文件
    for tld in tlds:
        file_name = f"{tld}.txt"
        source_path = os.path.join(source_dir, file_name)
        
        # 检查源文件是否存在
        if os.path.exists(source_path):
            try:
                # 构建目标路径
                target_path = os.path.join(target_dir, file_name)
                # 移动文件
                shutil.move(source_path, target_path)
                print(f"已移动文件: {source_path} -> {target_path}")
            except Exception as e:
                print(f"移动文件 {source_path} 时出错: {e}")
        else:
            print(f"源文件不存在: {source_path}")