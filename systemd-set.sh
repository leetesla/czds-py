#!/bin/bash
sudo cp linux.service /etc/systemd/system/czds.service
sudo systemctl daemon-reload
sudo systemctl enable czds.service
sudo systemctl start czds.service
sudo systemctl status czds.service
sudo journalctl -u czds.service -f