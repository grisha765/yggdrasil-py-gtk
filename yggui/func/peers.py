import json
from gi.repository import Gtk, Adw  # type: ignore
from urllib.parse import urlparse, parse_qs

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

    for peer in sorted(app.peers):
        parsed = urlparse(peer)
        proto = parsed.scheme
        host = parsed.hostname or parsed.netloc.split("?", 1)[0]
        port = f":{parsed.port}" if parsed.port else ""
        title = f"{host}{port}"

        row = Adw.ActionRow()
        row.set_title(title)
        row.add_css_class("compact")

        subtitle_parts = [proto.upper()]
        if proto == "tls":
            sni = parse_qs(parsed.query).get("sni", [None])[0]
            if sni:
                subtitle_parts.append(f"SNI: {sni}")
        row.set_subtitle(" • ".join(subtitle_parts))
        row.set_activatable(False)

        icon_map = {
            "tcp": "network-wired-symbolic",
            "tls": "security-high-symbolic",
            "quic": "network-transmit-receive-symbolic",
        }
        icon_name = icon_map.get(proto, "network-server-symbolic")
        icon = Gtk.Image.new_from_icon_name(icon_name)
        row.add_prefix(icon)

        trash_btn = Gtk.Button()
        trash_btn.set_icon_name("user-trash-symbolic")
        trash_btn.add_css_class("destructive-action")
        trash_btn.add_css_class("flat")
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
    builder = Gtk.Builder.new_from_file(str(Default.peer_ui_file))

    dialog: Adw.AlertDialog = builder.get_object("add_peer_dialog")
    domain_row: Adw.EntryRow = builder.get_object("domain_row")
    proto_row: Adw.ComboRow = builder.get_object("proto_row")
    sni_row: Adw.EntryRow = builder.get_object("sni_row")

    def _update_sni_row(_row=None, _pspec=None):
        sni_row.set_visible(proto_row.get_selected() == 1)
        _validate()

    proto_row.connect("notify::selected", _update_sni_row)

    def _validate(_row=None, _pspec=None):
        domain = domain_row.get_text().strip()
        sni    = sni_row.get_text().strip()
        proto  = ["tcp", "tls", "quic"][proto_row.get_selected()]

        domain_has_text = bool(domain)
        domain_valid    = bool(Default.domain_re.fullmatch(domain))

        if domain_has_text and not domain_valid:
            domain_row.add_css_class("error")
            domain_row.set_tooltip_text(
                "Format: example.com:1234 or 1.2.3.4:1234"
            )
        else:
            domain_row.remove_css_class("error")
            domain_row.set_tooltip_text(None)

        sni_valid = True
        if proto == "tls":
            sni_has_text = bool(sni)
            sni_valid = (not sni_has_text) or bool(Default.sni_re.fullmatch(sni))

            if sni_has_text and not sni_valid:
                sni_row.add_css_class("error")
                sni_row.set_tooltip_text("Only the domain name, e.g. example.com")
            else:
                sni_row.remove_css_class("error")
                sni_row.set_tooltip_text(None)
        else:
            sni_row.remove_css_class("error")
            sni_row.set_tooltip_text(None)

        dialog.set_response_enabled("add", domain_valid and sni_valid)

    domain_row.connect("notify::text", _validate)
    sni_row.connect("notify::text",    _validate)

    _update_sni_row()

    def _commit():
        domain = domain_row.get_text().strip()
        if not domain:
            return

        proto = ["tcp", "tls", "quic"][proto_row.get_selected()]
        peer  = f"{proto}://{domain}"

        sni = sni_row.get_text().strip()
        if proto == "tls" and sni:
            peer += f"?sni={sni}"

        if peer not in app.peers:
            app.peers.append(peer)
            _save_peers_to_disk(app)
            _rebuild_peers_box(app)

    dialog.connect("response", lambda _d, resp: resp == "add" and _commit())
    dialog.present(app.win)

def _remove_peer(app, peer):
    if peer in app.peers:
        app.peers.remove(peer)
        _save_peers_to_disk(app)
        _rebuild_peers_box(app)


if __name__ == "__main__":
    raise RuntimeError("This module should be run only via main.py")

