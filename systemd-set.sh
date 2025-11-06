#!/bin/bash
SERVICE_NAME="czds.service"

sudo cp linux.service /etc/systemd/system/$SERVICE_NAME
sudo systemctl daemon-reload
sudo systemctl enable $SERVICE_NAME
sudo systemctl start $SERVICE_NAME
sudo systemctl status $SERVICE_NAME
sudo journalctl -u $SERVICE_NAME -f