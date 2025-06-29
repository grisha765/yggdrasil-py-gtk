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
    is_flatpak = Path('/.flatpak-info').is_file()
    runtime_dir = Path(os.environ.get('XDG_RUNTIME_DIR', '/tmp')) / 'yggui'
    runtime_dir.mkdir(parents=True, exist_ok=True)
    ygg_path = shutil.which('yggdrasil')
    yggctl_path = shutil.which('yggdrasilctl')
    yggctl_path_stack = yggctl_path
    yggstack_path = shutil.which('yggstack')
    if is_flatpak:
        if ygg_path:
            dst = runtime_dir / 'yggdrasil'
            shutil.copy2(ygg_path, dst)
            ygg_path = str(dst)
        if yggctl_path:
            dst = runtime_dir / 'yggdrasilctl'
            shutil.copy2(yggctl_path, dst)
            yggctl_path = str(dst)
    config_path = xdg_config('yggui') / 'config.json'
    pkexec_path = '/usr/bin/pkexec'
    ui_file = files('yggui.ui').joinpath('ui.ui')
    css_file = files('yggui.ui').joinpath('ui.css')
    admin_socket = str(runtime_dir / 'yggdrasil.sock')
    if ygg_path is None:
        raise FileNotFoundError(
            "The 'yggdrasil' executable was not found in your PATH. "
            "Please install Yggdrasil or adjust your PATH environment "
            "variable accordingly."
        )

    if yggctl_path is None:
        raise FileNotFoundError(
            "The 'yggdrasilctl' executable was not found in your PATH. "
            "Please install Yggdrasil or adjust your PATH environment "
            "variable accordingly."
        )

