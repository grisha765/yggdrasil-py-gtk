import json
from gi.repository import Gtk, Adw  # type: ignore

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
    # CHANGED
    add_btn = getattr(app, "add_peer_btn", None)
    # CHANGED
    if add_btn is None:
        # CHANGED
        add_btn = app.peers_box.get_parent().get_last_child()
        # CHANGED
        app.add_peer_btn = add_btn
    # CHANGED
    add_btn.connect("clicked", lambda _b: _open_add_peer_dialog(app))


def _rebuild_peers_box(app):
    child = app.peers_box.get_first_child()
    while child:
        nxt = child.get_next_sibling()
        app.peers_box.remove(child)
        child = nxt

    for peer in app.peers:
        row = Adw.ActionRow()
        row.set_title(peer)

        trash_btn = Gtk.Button()
        trash_btn.set_icon_name("user-trash-symbolic")
        trash_btn.add_css_class("destructive-action")
        row.add_suffix(trash_btn)

        trash_btn.connect("clicked", lambda _b, p=peer: _remove_peer(app, p))
        app.peers_box.append(row)

    # (The in‑list “Add peer” row has been removed)

    count = len(app.peers)
    if count == 0:
        app.peers_card.set_subtitle("No peers configured")
    else:
        plural = "s" if count != 1 else ""
        app.peers_card.set_subtitle(f"{count} peer node{plural}")


def _open_add_peer_dialog(app):
    dialog = Adw.Dialog.new()
    dialog.set_title("Add Peer")

    content = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
    dialog.set_child(content)

    domain_row = Adw.EntryRow()
    domain_row.set_title("Domain")
    content.append(domain_row)

    proto_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
    proto_label = Gtk.Label(label="Protocol:")
    proto_box.append(proto_label)
    cb_tcp = Gtk.CheckButton(label="tcp")
    cb_tls = Gtk.CheckButton(label="tls")
    cb_quic = Gtk.CheckButton(label="quic")
    proto_box.append(cb_tcp)
    proto_box.append(cb_tls)
    proto_box.append(cb_quic)
    content.append(proto_box)

    sni_row = Adw.EntryRow()
    sni_row.set_title("SNI")
    sni_row.set_visible(False)
    content.append(sni_row)

    def _proto_toggled(btn):
        if btn.get_active():
            for b in (cb_tcp, cb_tls, cb_quic):
                if b is not btn:
                    b.set_active(False)
        sni_row.set_visible(cb_tls.get_active())

    for b in (cb_tcp, cb_tls, cb_quic):
        b.connect("toggled", _proto_toggled)

    cb_tcp.set_active(True)

    action_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
    cancel_btn = Gtk.Button(label="Cancel")
    add_btn = Gtk.Button(label="Add")
    add_btn.add_css_class("suggested-action")
    action_box.append(cancel_btn)
    action_box.append(add_btn)
    content.append(action_box)

    cancel_btn.connect("clicked", lambda _b: dialog.close())

    def _commit(_b):
        domain = domain_row.get_text().strip()
        if not domain:
            return
        protocol = ("tls" if cb_tls.get_active()
                    else "quic" if cb_quic.get_active()
                    else "tcp")
        peer = f"{protocol}://{domain}"
        sni = sni_row.get_text().strip()
        if protocol == "tls" and sni:
            peer += f"?sni={sni}"
        if peer not in app.peers:
            app.peers.append(peer)
            _save_peers_to_disk(app)
            _rebuild_peers_box(app)
        dialog.close()

    add_btn.connect("clicked", _commit)

    dialog.present(app.win)


def _remove_peer(app, peer):
    if peer in app.peers:
        app.peers.remove(peer)
        _save_peers_to_disk(app)
        _rebuild_peers_box(app)


if __name__ == "__main__":
    raise RuntimeError("This module should be run only via main.py")

