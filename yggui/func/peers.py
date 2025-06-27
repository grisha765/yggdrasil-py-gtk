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
    add_btn = getattr(app, "add_peer_btn", None)
    if add_btn is None:
        add_btn = app.peers_box.get_parent().get_last_child()
        app.add_peer_btn = add_btn
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

    count = len(app.peers)
    if count == 0:
        app.peers_card.set_subtitle("No peers configured")
    else:
        plural = "s" if count != 1 else ""
        app.peers_card.set_subtitle(f"{count} peer node{plural}")


def _open_add_peer_dialog(app):
    dialog = Adw.AlertDialog.new("Add Peer", None)

    group = Adw.PreferencesGroup()
    dialog.set_extra_child(group)

    domain_row = Adw.EntryRow()
    domain_row.set_title("Domain")
    group.add(domain_row)

    proto_row = Adw.ComboRow()
    proto_row.set_title("Protocol")
    proto_model = Gtk.StringList.new(["tcp", "tls", "quic"])
    proto_row.set_model(proto_model)
    proto_row.set_selected(0)
    group.add(proto_row)

    sni_row = Adw.EntryRow()
    sni_row.set_title("SNI")
    sni_row.set_visible(False)
    group.add(sni_row)

    def _update_sni_row(_row, _pspec):
        sni_row.set_visible(proto_row.get_selected() == 1)
    proto_row.connect("notify::selected", _update_sni_row)

    dialog.add_response("cancel", "Cancel")
    dialog.add_response("add", "Add")
    dialog.set_response_appearance("add", Adw.ResponseAppearance.SUGGESTED)
    dialog.set_default_response("add")

    def _commit():
        domain = domain_row.get_text().strip()
        if not domain:
            return
        protocol = ["tcp", "tls", "quic"][proto_row.get_selected()]
        peer = f"{protocol}://{domain}"
        sni = sni_row.get_text().strip()
        if protocol == "tls" and sni:
            peer += f"?sni={sni}"
        if peer not in app.peers:
            app.peers.append(peer)
            _save_peers_to_disk(app)
            _rebuild_peers_box(app)
        dialog.close()

    def _on_response(_d, response):
        if response == "add":
            _commit()

    dialog.connect("response", _on_response)
    dialog.present(app.win)


def _remove_peer(app, peer):
    if peer in app.peers:
        app.peers.remove(peer)
        _save_peers_to_disk(app)
        _rebuild_peers_box(app)


if __name__ == "__main__":
    raise RuntimeError("This module should be run only via main.py")
