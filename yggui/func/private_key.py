import json
from yggui.core.common import Default

_INACTIVE_KEY_FIELD = "PrivateKeyInactive"


def _read_config():
    """
    Load the whole JSON config or return an empty dict on error.
    """
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


def load_private_key(app):
    cfg = _read_config()

    current_key = cfg.get("PrivateKey", "")
    inactive_key = cfg.get(_INACTIVE_KEY_FIELD)

    if inactive_key is None and current_key:
        cfg[_INACTIVE_KEY_FIELD] = current_key
        _write_config(cfg)
        inactive_key = current_key

    app.default_private_key = inactive_key or ""
    app.current_private_key = current_key

    entry = app.private_key_entry
    entry.set_text(current_key)
    entry.set_editable(False)

    edit_btn = app.edit_private_key_button
    reset_btn = app.reset_private_key_button

    edit_btn.connect("clicked", lambda _b: _toggle_edit(app))
    reset_btn.connect("clicked", lambda _b: _reset(app))
    reset_btn.set_sensitive(current_key != inactive_key)


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
    app.reset_private_key_button.set_sensitive(
        new_key != app.default_private_key
    )


def _reset(app):
    """
    Revert to the factory‑generated PrivateKey.
    """
    default_key = app.default_private_key
    if not default_key:
        return

    entry = app.private_key_entry
    cfg = _read_config()
    cfg["PrivateKey"] = default_key
    _write_config(cfg)

    app.current_private_key = default_key
    entry.set_text(default_key)
    entry.set_editable(False)
    app.edit_private_key_button.set_icon_name("document-edit-symbolic")
    app.reset_private_key_button.set_sensitive(False)

