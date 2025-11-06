import os
import shutil
import glob

from app_config.config import get_tlds_from_config


def set_init_domains():
    # 确保必要的目录存在
    os.makedirs('output/domains-001', exist_ok=True)
    os.makedirs('output/domains-002', exist_ok=True)
    
    # 清理output/domains-001目录下以.txt结尾的文件
    clean_txt_files('output/domains-001')
    
    # 将output/domains-002目录下以.txt结尾的文件移动到output/domains-001目录下
    move_txt_files('output/domains-002', 'output/domains-001')


def clean_txt_files(directory):
    """清理指定目录下以.txt结尾的文件"""
    tlds = get_tlds_from_config()
    for tld in tlds:
        pass
    txt_files = glob.glob(os.path.join(directory, '*.txt'))
    for file_path in txt_files:
        try:
            os.remove(file_path)
            print(f"已删除文件: {file_path}")
        except Exception as e:
            print(f"删除文件 {file_path} 时出错: {e}")


def move_txt_files(source_dir, target_dir):
    """将源目录下以.txt结尾的文件移动到目标目录"""
    # 确保目标目录存在
    os.makedirs(target_dir, exist_ok=True)
    
    # 查找源目录下所有.txt文件
    txt_files = glob.glob(os.path.join(source_dir, '*.txt'))
    
    for file_path in txt_files:
        try:
            # 获取文件名
            filename = os.path.basename(file_path)
            # 构建目标路径
            target_path = os.path.join(target_dir, filename)
            # 移动文件
            shutil.move(file_path, target_path)
            print(f"已移动文件: {file_path} -> {target_path}")
        except Exception as e:
            print(f"移动文件 {file_path} 时出错: {e}")