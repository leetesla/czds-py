#!/bin/bash
SERVICE_NAME="czds.service"

# 使用Python脚本动态生成服务文件
echo "正在生成 systemd 服务文件..."
python3 scripts/generate_systemd_service.py \
    --output-path . \
    --service-name $SERVICE_NAME

# 复制服务文件到systemd目录
sudo cp $SERVICE_NAME /etc/systemd/system/$SERVICE_NAME
sudo systemctl daemon-reload
sudo systemctl enable $SERVICE_NAME
sudo systemctl start $SERVICE_NAME
sudo systemctl status $SERVICE_NAME
sudo journalctl -u $SERVICE_NAME -f