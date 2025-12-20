import sys
import pathlib
import tomllib
import tomli_w

CONFIG_DIR_NAME = 'profiles'
CONFIG_SUFFIX = '.toml'


class Config:
    """ 配置文件管理 """
    def __init__(self, name: str):
        # 可执行文件路径（兼容 PyInstaller）
        exec_path = pathlib.Path(sys.argv[0]) if getattr(sys, 'frozen', False) else pathlib.Path(__file__)

        # 基准目录
        base_dir = exec_path.resolve().parent

        # 配置文件目录
        config_dir = base_dir / CONFIG_DIR_NAME
        config_dir.mkdir(parents=True, exist_ok=True)

        # 配置文件路径
        self.file_path = config_dir / f'{name}{CONFIG_SUFFIX}'

        # 确保文件存在
        self.file_path.touch(exist_ok=True)

    def load(self):
        with self.file_path.open('rb') as f:
            return tomllib.load(f)

    def dump(self, data):
        with self.file_path.open('wb') as f:
            tomli_w.dump(data, f, multiline_strings=True)


if __name__ == '__main__':
    cfg = Config('test')
    data = {
        'project': {
            'name': 'hterm',
            'version': 'v0.1.1',
        },
        'other': {
            'number': 10.2,
            'bool': True,
            'list': ['apple', 'banana'],
            'dict': {'key1': 1, 'key2': 2},
            'str': 'hello\nworld'
        },
    }
    cfg.dump(data)
    print(cfg.load())