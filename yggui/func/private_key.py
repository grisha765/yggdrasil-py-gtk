import json
import subprocess
from yggui.core.common import Default


def _read_config():
    if Default.config_path.exists():
        try:
            with open(
                Default.config_path,
                "r",
                encoding="utf-8"
            ) as handle:
                return json.load(handle)
        except Exception:
            return {}
    return {}


def _write_config(cfg):
    with open(
        Default.config_path,
        "w",
        encoding="utf-8"
    ) as handle:
        json.dump(cfg, handle, indent=2)


def _regenerate(app):
    try:
        cmd = [
            Default.ygg_path,
            "-genconf",
            "-json"
        ]
        result = subprocess.run(
            cmd,
            capture_output=True,
            check=True,
            text=True,
        )
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

    entry = app.private_key_entry
    entry.set_text(new_key)
    entry.set_editable(False)
    app.edit_private_key_button.set_icon_name("document-edit-symbolic")


def _toggle_edit(app):
    entry = app.private_key_entry
    editing = entry.get_editable()

    if not editing:
        entry.set_editable(True)
        app.edit_private_key_button.set_icon_name("object-select")
        entry.grab_focus()
        return

    new_key = entry.get_text().strip()
    if not new_key:
        return

    cfg = _read_config()
    cfg["PrivateKey"] = new_key
    _write_config(cfg)

    app.current_private_key = new_key
    entry.set_editable(False)
    app.edit_private_key_button.set_icon_name("document-edit-symbolic")


def load_private_key(app):
    cfg = _read_config()
    current_key = cfg.get("PrivateKey", "")

    app.current_private_key = current_key
    app.default_private_key = current_key

    entry = app.private_key_entry
    entry.set_text(current_key)
    entry.set_editable(False)

    edit_btn = app.edit_private_key_button
    regen_btn = app.reset_private_key_button

    edit_btn.connect("clicked", lambda _b: _toggle_edit(app))
    regen_btn.connect("clicked", lambda _b: _regenerate(app))


if __name__ == "__main__":
    raise RuntimeError("This module should be run only via main.py")

