import os
import pathlib
import tomllib

base_dir = pathlib.Path(__file__).resolve().parent
hook_env_path = base_dir / "hook_env.toml"

with hook_env_path.open("rb") as f:
    config = tomllib.load(f)

os.environ["HTERM_VERSION"] = config["env"]["version"]
os.environ["HTERM_PACK_TIME"] = config["env"]["pack_time"]
