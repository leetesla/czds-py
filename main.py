import sys

# 检查是否启用了低内存模式
if "--lm" in sys.argv:
    from scripts.run import run_task_low_memory
    if __name__ == "__main__":
        run_task_low_memory()
else:
    from scripts.run import run_task
    if __name__ == "__main__":
        run_task()