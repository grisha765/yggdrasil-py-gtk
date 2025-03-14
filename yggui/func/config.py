import subprocess

from yggui.core.common import Default

def create_config():
    if not Default.config_path.exists():
        print(f"The {Default.config_file} file was not found. Create it...")
        with open(str(Default.config_path), "w") as f:
            cmd = [Default.ygg_path, "-genconf", "-json"]
            subprocess.run(cmd, stdout=f, check=True)

if __name__ == "__main__":
    raise RuntimeError("This module should be run only via main.py")
