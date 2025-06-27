import json
import subprocess

from yggui.core.common import Default
from gi.repository import Gtk, Adw  # type: ignore


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


def _on_text_changed(app, _row, _pspec):
    app.private_key_regen_icon.set_visible(False)
    new_val = app.private_key_row.get_text().strip()
    if not new_val:
        return
    cfg = _read_config()
    cfg["PrivateKey"] = new_val
    _write_config(cfg)
    app.current_private_key = new_val


def _on_entry_activated(app, _row):
    app.win.child_focus(Gtk.DirectionType.TAB_FORWARD)


def _on_focus_leave(app, _controller):
    app.private_key_regen_icon.set_visible(True)


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
    app.private_key_row.set_text(new_key)
    app.private_key_regen_icon.set_visible(True)


def load_private_key(app):
    cfg = _read_config()
    current_key = cfg.get("PrivateKey", "")

    app.current_private_key = current_key
    app.default_private_key = current_key

    app.private_key_row.set_text(current_key)

    app.private_key_row.connect(
        "notify::text",
        lambda r, p: _on_text_changed(app, r, p),
    )

    app.private_key_row.connect(
        "entry-activated",
        lambda r: _on_entry_activated(app, r),
    )

    focus_controller = Gtk.EventControllerFocus.new()
    focus_controller.connect("leave", lambda c: _on_focus_leave(app, c))
    app.private_key_row.add_controller(focus_controller)

    gesture = Gtk.GestureClick.new()
    gesture.connect(
        "released",
        lambda _g, _n, _x, _y: _regenerate(app),
    )
    app.private_key_regen_icon.add_controller(gesture)


if __name__ == "__main__":
    raise RuntimeError("This module should be run only via main.py")
