import shutil
from pathlib import Path

class Default:
    ygg_path = shutil.which('yggdrasil')
    config_file = 'config.json'
    config_path = Path(config_file)
    ui_file = 'yggui/ui/ui.ui'
    css_file = 'yggui/ui/ui.css'
