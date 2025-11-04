#!/bin/bash

INPUT_FILE="/Users/chrise/app/czds-py/download/com.txt"
NUM_PARTS=2
PREFIX="com.txt-part-"

# 检查输入文件是否存在
if [[ ! -f "$INPUT_FILE" ]]; then
    echo "Error: File $INPUT_FILE not found!"
    exit 1
fi

# 获取文件总行数
TOTAL_LINES=$(wc -l < "$INPUT_FILE")
echo "Total lines in file: $TOTAL_LINES"

# 计算每部分的行数
LINES_PER_PART=$(( (TOTAL_LINES + NUM_PARTS - 1) / NUM_PARTS ))
echo "Lines per part: $LINES_PER_PART"

# 创建临时目录来存储分块文件
TEMP_DIR="temp_split"
mkdir -p "$TEMP_DIR"

# 分割文件
split -l "$LINES_PER_PART" "$INPUT_FILE" "$TEMP_DIR/$PREFIX"

# 压缩分割后的文件
counter=1
for file in "$TEMP_DIR"/*; do
    if [[ -f "$file" ]]; then
        # 生成输出文件名
        OUTPUT_FILE="${PREFIX}${counter}.gz"
        
        # 压缩文件
        gzip -c "$file" > "$OUTPUT_FILE"
        
        echo "Created and compressed: $OUTPUT_FILE"
        counter=$((counter + 1))
    fi
done

# 清理临时目录
rm -rf "$TEMP_DIR"

echo "---"
echo "Splitting and compression complete. Check your current directory for files like ${PREFIX}1.txt.gz, ${PREFIX}2.txt.gz, etc."