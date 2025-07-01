import subprocess, json

from yggui.core.common import Default


def ensure_admin_socket_is_set() -> None:
    try:
        with open(Default.config_path, "r+", encoding="utf-8") as handle:
            cfg = json.load(handle)
            if cfg.get("AdminListen") == f'unix://{Default.admin_socket}':
                return

            cfg["AdminListen"] = f'unix://{Default.admin_socket}'
            handle.seek(0)
            json.dump(cfg, handle, indent=2)
            handle.truncate()
    except Exception:
        pass


def create_config():
    if not Default.config_path.exists():
        print(f"The {str(Default.config_path)} file was not found. Create it...")
        with open(str(Default.config_path), "w") as f:
            cmd = [Default.ygg_path, "-genconf", "-json"]
            subprocess.run(cmd, stdout=f, check=True)
    ensure_admin_socket_is_set()


if __name__ == "__main__":
    raise RuntimeError("This module should be run only via main.py")
