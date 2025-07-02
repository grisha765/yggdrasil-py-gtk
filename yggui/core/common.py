import shutil, os, subprocess, re
from pathlib import Path
from importlib.resources import files

def which_in_flatpak(cmd: str) -> str | None:
    result = subprocess.run(
        ["flatpak-spawn", "--host", "command", "-v", cmd],
        capture_output=True,
        text=True,
        check=False
    )
    if result.returncode == 0:
        return result.stdout.strip()
    return None

def xdg_config(app_name: str) -> Path:
    default_base = Path.home() / ".config"
    base = Path(os.environ.get("XDG_CONFIG_HOME", default_base)).expanduser()
    cfg_dir = base / app_name
    cfg_dir.mkdir(parents=True, exist_ok=True)
    return cfg_dir


class Regexp:
    domain_re = re.compile(
        r"""^(
            (?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}(?::\d{1,5})?
            |
            (?:\d{1,3}\.){3}\d{1,3}:\d{1,5}
        )$""",
        re.X,
    )
    sni_re = re.compile(r"^(?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}$")


class Runtime:
    is_flatpak = Path('/.flatpak-info').is_file()
    is_appimage = os.getenv("APPIMAGE") is not None
    runtime_dir = Path(os.environ.get('XDG_RUNTIME_DIR', '/tmp')) / 'yggui'
    runtime_dir.mkdir(parents=True, exist_ok=True)
    admin_socket = str(runtime_dir / 'yggdrasil.sock')
    config_path = xdg_config('yggui') / 'config.json'


class Binary:
    ygg_path = shutil.which('yggdrasil')
    yggctl_path = shutil.which('yggdrasilctl')
    yggctl_path_stack = yggctl_path
    yggstack_path = shutil.which('yggstack')
    pkexec_path = shutil.which('pkexec')
    if Runtime.is_flatpak or Runtime.is_appimage:
        if Runtime.is_flatpak:
            pkexec_path = which_in_flatpak('pkexec')
        if ygg_path:
            dst = Runtime.runtime_dir / 'yggdrasil'
            shutil.copy2(ygg_path, dst)
            ygg_path = str(dst)
        if yggctl_path:
            dst = Runtime.runtime_dir / 'yggdrasilctl'
            shutil.copy2(yggctl_path, dst)
            yggctl_path = str(dst)


class Gui:
    ui_file = files('yggui.ui').joinpath('ui.ui')
    ui_main_file = files('yggui.ui').joinpath('main.ui')
    ui_settings_file = files('yggui.ui').joinpath('settings.ui')
    peer_ui_file = files('yggui.ui').joinpath('peer_dialog.ui')
    css_file = files('yggui.ui').joinpath('ui.css')
