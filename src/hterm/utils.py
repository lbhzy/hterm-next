import importlib.util
import time
from functools import wraps


def run_python_script_string(content):
    """运行 python 脚本字符串中的 main() 函数并返回值"""
    spec = importlib.util.spec_from_loader("script", loader=None)
    script = importlib.util.module_from_spec(spec)
    exec(content, script.__dict__)
    return script.main()


def monitor(func):
    # 初始化上一次调用的时间（闭包变量）
    last_call_time = None

    @wraps(func)
    def wrapper(*args, **kwargs):
        nonlocal last_call_time  # 声明使用外部嵌套作用域变量

        # 1. 计算函数调用间隔
        current_time = time.time()
        interval = (current_time - last_call_time) * 1000 if last_call_time else 0
        last_call_time = current_time

        # 2. 计算函数执行耗时
        start_exec = time.time()
        result = func(*args, **kwargs)  # 执行原函数
        end_exec = time.time()

        duration = (end_exec - start_exec) * 1000

        # 打印统计信息（单位：ms）
        print(f"{func.__name__} interval: {interval:.2f}ms cost: {duration:.2f}ms")

        return result

    return wrapper
