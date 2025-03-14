import json
from pathlib import Path
from core.common import Default

def load_config_file():
    config_file = Path("config.json")
    if not config_file.exists():
        default_config = {
            "ygg_path": {
                "params": {
                    "param": Default.ygg_path,
                    "use_config": False
                }
            }
        }
        with config_file.open("w", encoding="utf-8") as f:
            json.dump(default_config, f, ensure_ascii=False, indent=4)
        return default_config
    with config_file.open("r", encoding="utf-8") as f:
        config = json.load(f)
    return config

def load_config_params():
    config = load_config_file()
    config = config
    config_ygg_path = config["ygg_path"]["params"]["param"]
    config_ygg_path_check = config["ygg_path"]["params"]["use_config"]
    ygg_path = config_ygg_path if config_ygg_path_check else Default.ygg_path
    return ygg_path, config_ygg_path, config_ygg_path_check

def save_config_file(config):
    config_file = Path("config.json")
    with config_file.open("w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=4)

def ygg_path_check(self, button):
    self.ygg_path_input.set_sensitive(self.ygg_path_check.get_active())

def save_config(self, button):
    ygg_path_check = self.ygg_path_check.get_active()
    self.ygg_path = self.ygg_path_input.get_text()
    print(f"Using ygg_path parameter: {self.ygg_path}")
    print(f"Check box ygg_path: {ygg_path_check}")
    config = {
        "ygg_path": {
            "params": {
                "param": self.ygg_path,
                "use_config": ygg_path_check
            }
        }
    }
    save_config_file(config)
    self.ygg_path, self.config_ygg_path, self.config_ygg_path_check = load_config_params()

if __name__ == "__main__":
    raise RuntimeError("This module should be run only via main.py")
