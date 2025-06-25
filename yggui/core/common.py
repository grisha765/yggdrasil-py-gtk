import shutil
from pathlib import Path
from importlib.resources import files

class Default:
    ygg_path = shutil.which('yggdrasil')
    yggctl_path = shutil.which('yggdrasilctl')
    config_file = 'config.json'
    config_path = Path(config_file)
    ui_file = files('yggui.ui').joinpath('ui.ui')
    css_file = files('yggui.ui').joinpath('ui.css')
    admin_socket = '/tmp/yggdrasil.sock'
