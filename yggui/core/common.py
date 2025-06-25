import shutil, os
from pathlib import Path
from importlib.resources import files

def xdg_config(app_name: str) -> Path:
    default_base = Path.home() / ".config"
    base = Path(os.environ.get("XDG_CONFIG_HOME", default_base)).expanduser()
    cfg_dir = base / app_name
    cfg_dir.mkdir(parents=True, exist_ok=True)
    return cfg_dir

class Default:
    ygg_path = shutil.which('yggdrasil')
    yggctl_path = shutil.which('yggdrasilctl')
    config_path = xdg_config('yggui') / 'config.json'
    ui_file = files('yggui.ui').joinpath('ui.ui')
    css_file = files('yggui.ui').joinpath('ui.css')
    admin_socket = '/tmp/yggdrasil.sock'

