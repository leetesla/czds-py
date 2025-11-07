#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
定时任务调度器
支持添加每日执行的定时任务

使用方法:
1. 直接运行脚本启动默认任务（每天凌晨2点执行）:
   python scripts/schedule_daily_task.py

2. 修改 sample_daily_task 函数以实现您需要的每日任务

3. 修改 main 函数中的调度器参数来设置自定义执行时间:
   scheduler = DailyTaskScheduler(sample_daily_task, hour=9, minute=0)  # 每天早上9点执行

4. 按 Ctrl+C 可以优雅地停止定时任务调度器

日志:
脚本会生成日志文件 daily_task.log，记录任务执行情况
"""

import time
import logging
from datetime import datetime, timedelta
import threading

from app_config.constant import DIR_OUTPUT_DOMAIN_CHUNKS_NEW, DIR_OUTPUT_DOMAIN_CHUNKS_OLD
from scripts.prepare import set_init_domains
from scripts.run import run_task, run_task_low_memory

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('daily_task.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


def daily_task():
    """
    示例任务函数 - 每天执行的任务
    您可以在这里添加实际需要执行的代码
    
    示例任务可以是：
    - 数据备份
    - 文件清理
    - API数据同步
    - 报表生成
    - 等等...
    """
    logger.info("开始执行每日任务...")
    
    # 在这里添加您的实际任务逻辑
    # 例如：数据处理、文件操作、API调用等
    print(f"每日任务执行时间: {datetime.now()}")
    
    # 任务执行
    # time.sleep(2)
    # 移动前一天的 domain chunks new作为 今天的 domain chunks old
    set_init_domains(DIR_OUTPUT_DOMAIN_CHUNKS_NEW, DIR_OUTPUT_DOMAIN_CHUNKS_OLD)
    run_task_low_memory()

    
    logger.info("每日任务执行完成")


class DailyTaskScheduler:
    """每日任务调度器"""
    
    def __init__(self, task_function, hour=2, minute=0):
        """
        初始化调度器
        
        Args:
            task_function: 要执行的任务函数
            hour (int): 执行小时 (0-23), 默认凌晨2点
            minute (int): 执行分钟 (0-59), 默认0分
        """
        self.task_function = task_function
        self.hour = hour
        self.minute = minute
        self.running = False
        self.thread = None
    
    def _get_next_run_time(self):
        """计算下次运行时间"""
        now = datetime.now()
        next_run = now.replace(hour=self.hour, minute=self.minute, second=0, microsecond=0)
        
        # 如果今天的时间已经过了，设置为明天
        if next_run <= now:
            next_run += timedelta(days=1)
            
        return next_run
    
    def _run_scheduler(self):
        """运行调度器"""
        logger.info("定时任务调度器已启动")
        
        while self.running:
            try:
                next_run = self._get_next_run_time()
                now = datetime.now()
                
                # 计算等待时间
                wait_seconds = (next_run - now).total_seconds()
                
                if wait_seconds > 0:
                    logger.info(f"下次任务执行时间: {next_run}")
                    time.sleep(min(wait_seconds, 60))  # 最多等待60秒，以便能响应停止信号
                
                # 检查是否到了执行时间
                if datetime.now() >= next_run and self.running:
                    self.task_function()
                    
            except Exception as e:
                logger.error(f"调度器运行出错: {e}")
                time.sleep(60)  # 出错后等待1分钟再继续
    
    def start(self):
        """启动调度器"""
        if self.running:
            logger.warning("调度器已在运行中")
            return
            
        self.running = True
        self.thread = threading.Thread(target=self._run_scheduler, daemon=True)
        self.thread.start()
        logger.info(f"已设置每日任务，执行时间: {self.hour:02d}:{self.minute:02d}")
    
    def stop(self):
        """停止调度器"""
        logger.info("正在停止调度器...")
        self.running = False
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=5)
        logger.info("调度器已停止")


def main():
    """
    主函数
    可以修改这里的参数来自定义任务执行时间
    """
    # 创建调度器实例 (默认凌晨2点执行)
    scheduler = DailyTaskScheduler(daily_task, hour=2, minute=0)
    
    try:
        # 启动调度器
        scheduler.start()
        
        # 保持主线程运行
        print("定时任务调度器已启动，按 Ctrl+C 停止")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("收到中断信号")
    finally:
        # 停止调度器
        scheduler.stop()


if __name__ == "__main__":
    main()