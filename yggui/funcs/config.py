import subprocess, json

from yggui.core.common import Runtime, Binary


def ensure_admin_socket_is_set() -> None:
    try:
        with open(Runtime.config_path, "r+", encoding="utf-8") as handle:
            cfg = json.load(handle)
            if cfg.get("AdminListen") == f'unix://{Runtime.admin_socket}':
                return

            cfg["AdminListen"] = f'unix://{Runtime.admin_socket}'
            handle.seek(0)
            json.dump(cfg, handle, indent=2)
            handle.truncate()
    except Exception:
        pass


def create_config():
    if not Runtime.config_path.exists():
        print(f"The {str(Runtime.config_path)} file was not found. Create it...")
        with open(str(Runtime.config_path), "w") as f:
            cmd = [Binary.ygg_path, "-genconf", "-json"]
            subprocess.run(cmd, stdout=f, check=True)
    ensure_admin_socket_is_set()


if __name__ == "__main__":
    raise RuntimeError("This module should be run only via main.py")
