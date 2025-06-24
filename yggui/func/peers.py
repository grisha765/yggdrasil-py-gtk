import json
from gi.repository import Gtk  # type: ignore

from yggui.core.common import Default


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


def _save_peers_to_disk(app):
    cfg = _read_config()
    cfg["Peers"] = app.peers
    _write_config(cfg)


def load_config(app):
    cfg = _read_config()
    app.peers = cfg.get("Peers", [])
    _rebuild_peers_box(app)


def _rebuild_peers_box(app):
    child = app.peers_box.get_first_child()
    while child:
        nxt = child.get_next_sibling()
        app.peers_box.remove(child)
        child = nxt

    for peer in app.peers:
        row = app.GBox(orientation=app.GOrientation.HORIZONTAL, spacing=12)
        row.set_hexpand(True)

        label = Gtk.Label(label=peer)
        label.set_xalign(0)
        label.set_hexpand(True)
        label.set_margin_start(6)

        minus = Gtk.Button(label="–")
        minus.set_margin_end(6)

        row.append(label)
        row.append(minus)

        minus.connect("clicked", lambda _btn, p=peer: _remove_peer(app, p))
        app.peers_box.append(row)

    add_row = app.GBox(orientation=app.GOrientation.HORIZONTAL, spacing=12)
    add_row.set_hexpand(True)

    entry = app.GEntry()
    entry.set_hexpand(True)
    entry.set_margin_start(6)

    plus = Gtk.Button(label="+")
    plus.set_margin_end(6)

    add_row.append(entry)
    add_row.append(plus)

    plus.connect("clicked", lambda _btn: _add_peer(app, entry))
    app.peers_box.append(add_row)


def _add_peer(app, entry):
    text = entry.get_text().strip()
    if not text or text in app.peers:
        return
    app.peers.append(text)
    _save_peers_to_disk(app)
    _rebuild_peers_box(app)


def _remove_peer(app, peer):
    if peer in app.peers:
        app.peers.remove(peer)
        _save_peers_to_disk(app)
        _rebuild_peers_box(app)


if __name__ == "__main__":
    raise RuntimeError("This module should be run only via main.py")

