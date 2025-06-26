import json
import subprocess

from yggui.core.common import Default
from gi.repository import Gtk, Adw  # type: ignore


def _truncate_key(key: str, max_len: int = 48) -> str:
    if len(key) <= max_len:
        return key
    return f"{key[:24]}…{key[-24:]}"


def _read_config():
    if Default.config_path.exists():
        try:
            with open(Default.config_path, "r", encoding="utf-8") as handle:
                return json.load(handle)
        except Exception:
            return {}
    return {}


def _write_config(cfg):
    with open(Default.config_path, "w", encoding="utf-8") as handle:
        json.dump(cfg, handle, indent=2)


def _regenerate(app):
    try:
        cmd = [Default.ygg_path, "-genconf", "-json"]
        result = subprocess.run(cmd, capture_output=True, check=True, text=True)
        generated = json.loads(result.stdout)
        new_key = generated.get("PrivateKey", "").strip()
    except Exception:
        return

    if not new_key:
        return

    cfg = _read_config()
    cfg["PrivateKey"] = new_key
    _write_config(cfg)

    app.current_private_key = new_key
    app.private_key_row.set_subtitle(_truncate_key(new_key))


def _open_editor_dialog(app):
    dialog = Adw.AlertDialog()
    dialog.set_heading("Edit Private Key")

    entry = Gtk.Entry()
    entry.set_hexpand(True)
    entry.set_text(app.current_private_key)
    dialog.set_extra_child(entry)

    dialog.add_response("cancel", "Cancel")
    dialog.add_response("regen", "Regenerate")
    dialog.add_response("save", "Save")
    dialog.set_default_response("save")

    def _on_response(dlg, response):
        if response == "cancel":
            return
        if response == "regen":
            _regenerate(app)
            entry.set_text(app.current_private_key)
            return
        if response == "save":
            new_val = entry.get_text().strip()
            if new_val:
                cfg = _read_config()
                cfg["PrivateKey"] = new_val
                _write_config(cfg)
                app.current_private_key = new_val
                app.private_key_row.set_subtitle(_truncate_key(new_val))

    dialog.connect("response", _on_response)
    dialog.present(app.win)


def load_private_key(app):
    cfg = _read_config()
    current_key = cfg.get("PrivateKey", "")

    app.current_private_key = current_key
    app.default_private_key = current_key

    app.private_key_row.set_subtitle(_truncate_key(current_key))
    app.private_key_row.connect("activated", lambda _r: _open_editor_dialog(app))


if __name__ == "__main__":
    raise RuntimeError("This module should be run only via main.py")

