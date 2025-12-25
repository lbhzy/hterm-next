from PyInstaller.__main__ import run


def pack():
    params = [
        "hterm/main.py",  # 打包目标
        "-y",  # 不询问，直接替换旧成果物
        "-w",  # 不显示控制台
        "--specpath=build",  # 不需要 spec 文件，所以将其生成到 build 下
        "--name=hterm",  # 设置软件名
    ]
    run(params)


if __name__ == "__main__":
    pack()
