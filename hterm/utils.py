import importlib.util


def run_python_script_string(content):
    """运行 python 脚本字符串中的 main() 函数并返回值"""
    spec = importlib.util.spec_from_loader("script", loader=None)
    script = importlib.util.module_from_spec(spec)
    exec(content, script.__dict__)
    return script.main()
