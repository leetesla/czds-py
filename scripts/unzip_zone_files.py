import os
import gzip
import shutil


def unzip_zone_files(working_directory="."):
    """
    解压 download/zonefiles 目录下所有 .gz 文件，解压后不保留 .gz 文件
    
    Args:
        working_directory (str): 工作目录路径，默认为当前目录
    """
    # 构建 zonefiles 目录路径
    zonefiles_dir = os.path.join(working_directory, "zonefiles")
    
    # 检查目录是否存在
    if not os.path.exists(zonefiles_dir):
        print(f"目录 {zonefiles_dir} 不存在")
        return
    
    # 遍历目录中的所有 .gz 文件
    for filename in os.listdir(zonefiles_dir):
        if filename.endswith(".gz"):
            gz_file_path = os.path.join(zonefiles_dir, filename)
            # 去掉 .gz 后缀得到解压后的文件名
            unzipped_filename = filename[:-3]  # 移除 .gz 后缀
            unzipped_file_path = os.path.join(zonefiles_dir, unzipped_filename)
            
            # 解压文件
            with gzip.open(gz_file_path, 'rb') as gz_file:
                with open(unzipped_file_path, 'wb') as unzipped_file:
                    shutil.copyfileobj(gz_file, unzipped_file)
            
            # 删除原始的 .gz 文件
            os.remove(gz_file_path)
            print(f"已解压并删除文件: {filename}")