# 低内存环境运行指南

本指南适用于在内存受限的服务器（如2GB RAM）上运行此应用程序。

## 问题描述

在2GB内存的Ubuntu服务器上运行 `uv run main.py` 会导致服务器无响应，这是由于：

1. 大量zone文件下载和解压占用内存
2. 文件合并操作一次性加载大量数据到内存
3. 数据库存储操作处理大量域名数据

## 解决方案

### 方法一：使用低内存模式参数运行

```bash
uv run main.py --low-memory
```

此模式会：
- 分阶段执行任务
- 在各阶段间增加延迟以释放内存
- 使用流式处理减少内存峰值

### 方法二：使用专门的低内存脚本

```bash
uv run scripts/run_low_memory.py
```

### 方法三：配置Systemd服务限制资源使用

1. 使用低内存配置文件：
```bash
sudo cp linux-low-memory.service /etc/systemd/system/czds.service
```

2. 重新加载并启动服务：
```bash
sudo systemctl daemon-reload
sudo systemctl enable czds.service
sudo systemctl start czds.service
```

低内存配置包含以下优化：
- 限制内存使用不超过1GB
- 限制CPU使用率不超过50%
- 使用专门的低内存脚本

### 方法四：手动分阶段运行

您可以手动按顺序运行各个脚本，以更好地控制内存使用：

```bash
# 1. 提取第一列域名
uv run scripts/extract_first_column.py

# 等待一段时间释放内存
sleep 10

# 2. 查找差异域名
uv run scripts/chunked_diff_domain.py

# 等待一段时间释放内存
sleep 10

# 3. 合并所有域名
uv run scripts/merge2all.py

# 等待一段时间释放内存
sleep 10

# 4. 保存域名到数据库
uv run scripts/store_domains_db.py

# 等待一段时间释放内存
sleep 10

# 5. 查找重复域名
uv run scripts/find_duplicate_domains.py
```

## 其他优化建议

1. **限制下载的TLD数量**：
   在 `config.json` 中设置 `"tlds"` 字段，只下载需要的顶级域名，而不是所有域名。

2. **定期清理旧文件**：
   定期删除不需要的旧zone文件和输出文件以释放磁盘空间。

3. **监控系统资源**：
   使用 `htop` 或 `top` 命令监控内存使用情况。

4. **增加交换空间**：
   如果可能，增加系统的交换空间：
   ```bash
   sudo fallocate -l 2G /swapfile
   sudo chmod 600 /swapfile
   sudo mkswap /swapfile
   sudo swapon /swapfile
   ```

## 故障排除

如果服务器仍然无响应：

1. 通过SSH连接到服务器并检查进程：
   ```bash
   ps aux | grep python
   ```

2. 如果需要强制终止进程：
   ```bash
   sudo pkill -f python
   ```

3. 检查系统日志：
   ```bash
   sudo journalctl -u czds.service -f
   ```

4. 检查内存使用情况：
   ```bash
   free -h
   ```