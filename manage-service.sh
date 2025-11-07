#!/bin/bash
SERVICE_NAME="czds.service"

# 显示可用的操作选项
echo "请选择要执行的操作："
echo "1) 生成并复制服务文件到systemd目录"
echo "2) 只生成服务文件（不复制）"
echo ""

# 读取用户输入
read -p "请输入选项编号: " gen_choice

if [ "$gen_choice" = "1" ]; then
    # 使用Python脚本动态生成服务文件
    echo "正在生成 systemd 服务文件..."
    python scripts/generate_systemd_service.py \
        --output-path . \
        --service-name $SERVICE_NAME

    # 复制服务文件到systemd目录
    sudo cp $SERVICE_NAME /etc/systemd/system/$SERVICE_NAME
    echo "sudo cp $SERVICE_NAME /etc/systemd/system/$SERVICE_NAME ..."
    echo "服务文件$SERVICE_NAME 已生成并复制到 /etc/systemd/system/$SERVICE_NAME"
elif [ "$gen_choice" = "2" ]; then
    # 只生成服务文件
    echo "正在生成 systemd 服务文件（不复制）..."
    python scripts/generate_systemd_service.py \
        --output-path . \
        --service-name $SERVICE_NAME
    echo "服务文件$SERVICE_NAME 已生成，位于当前目录"
    echo "你可以手动执行以下命令复制到/etc/systemd/system/目录下："
    echo "sudo cp $SERVICE_NAME /etc/systemd/system/$SERVICE_NAME"
    echo "退出脚本"
    exit 0
else
    echo "无效选项，退出脚本"
    exit 1
fi

echo ""
echo "请选择要执行的操作："
echo "1) 重新加载systemd配置 (sudo systemctl daemon-reload)"
echo "2) 启用服务（开机自启） (sudo systemctl enable $SERVICE_NAME)"
echo "3) 启动服务 (sudo systemctl start $SERVICE_NAME)"
echo "4) 查看服务状态 (sudo systemctl status $SERVICE_NAME)"
echo "5) 实时查看服务日志 (sudo journalctl -u $SERVICE_NAME -f)"
echo "6) 执行所有操作（重新加载、启用、启动、查看状态）"
echo "0) 退出"
echo ""

# 读取用户输入
read -p "请输入选项编号: " choice

case $choice in
    1)
        echo "正在重新加载systemd配置..."
        sudo systemctl daemon-reload
        ;;
    2)
        echo "正在启用服务..."
        sudo systemctl enable $SERVICE_NAME
        ;;
    3)
        echo "正在启动服务..."
        sudo systemctl start $SERVICE_NAME
        ;;
    4)
        echo "正在查看服务状态..."
        sudo systemctl status $SERVICE_NAME
        ;;
    5)
        echo "正在实时查看服务日志..."
        sudo journalctl -u $SERVICE_NAME -f
        ;;
    6)
        echo "正在执行所有操作..."
        sudo systemctl daemon-reload
        sudo systemctl enable $SERVICE_NAME
        sudo systemctl start $SERVICE_NAME
        sudo systemctl status $SERVICE_NAME
        ;;
    0)
        echo "退出脚本"
        exit 0
        ;;
    *)
        echo "无效选项，请重新运行脚本并选择有效选项"
        exit 1
        ;;
esac