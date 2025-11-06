import os

from app_config.constant import DIR_OUTPUT_DOMAINS_DIFF, FILE_OUTPUT_DOMAINS_DIFF_ALL


def merge2all():
    # 将download/diff文件夹下所有.txt文件合并 输出到 output/all.txt中
    input_dir = DIR_OUTPUT_DOMAINS_DIFF
    output_file = FILE_OUTPUT_DOMAINS_DIFF_ALL

    # 检查输入目录是否存在
    if not os.path.exists(input_dir):
        print(f"目录 {input_dir} 不存在")
        return
    
    # 获取所有.txt文件并按名称排序
    txt_files = sorted([f for f in os.listdir(input_dir) if f.endswith('.txt')])
    
    # 如果没有.txt文件，给出提示并创建空文件
    if not txt_files:
        print(f"目录 {input_dir} 中没有找到.txt文件")
        # 创建一个空的输出文件（会清空已存在的文件）
        with open(output_file, 'w', encoding='utf-8') as outfile:
            pass
        return
    
    # 合并文件（使用'w'模式会自动清空已存在的文件）
    with open(output_file, 'w', encoding='utf-8') as outfile:
        for i, txt_file in enumerate(txt_files):
            file_path = os.path.join(input_dir, txt_file)
            with open(file_path, 'r', encoding='utf-8') as infile:
                content = infile.read()
                outfile.write(content)
                # 在文件之间添加换行符（除了最后一个文件）
                if i < len(txt_files) - 1:
                    outfile.write('\n')
    
    print(f"成功合并 {len(txt_files)} 个文件到 {output_file}")