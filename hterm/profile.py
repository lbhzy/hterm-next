import os
import sys
import toml


class Profile:
    """ 配置文件管理 """
    def __init__(self, name: str):
        exec_file = sys.argv[0] if getattr(sys, 'frozen', False) else __file__
        base_dir = os.path.dirname(exec_file)
        config_dir = os.path.join(base_dir, 'profiles')
        self.file_path = os.path.join(config_dir, f'{name}.toml')

        if not os.path.exists(config_dir):
            os.makedirs(config_dir)
        if not os.path.isfile(self.file_path):
            with open(self.file_path, 'w') as f:
                pass

    def load(self):
        with open(self.file_path, 'r', encoding='utf-8') as f:
            data = toml.load(f)
        return data

    def dump(self, data):
        with open(self.file_path, 'w', encoding='utf-8') as f:
            toml.dump(data, f)


if __name__ == '__main__':
    cfg = Profile('test')
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
        },
    }
    cfg.dump(data)
    print(cfg.load())