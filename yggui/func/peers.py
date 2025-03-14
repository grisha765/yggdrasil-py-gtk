import json
from yggui.core.common import Default

def add_peer(app, button):
    row = app.GBox(orientation=app.GOrientation.HORIZONTAL)
    entry = app.GEntry()
    checkbox = app.GCheckButton()
    checkbox.set_active(True)
    row.append(entry)
    row.append(checkbox)
    app.peers_box.append(row)
    checkbox.connect("toggled", lambda cb: on_peer_toggled(app, cb, entry))

def on_peer_toggled(app, checkbox, entry):
    text = entry.get_text().strip()
    if checkbox.get_active():
        if text and text not in app.peers:
            app.peers.append(text)
    else:
        if text in app.peers:
            app.peers.remove(text)

def load_config(app):
    if Default.config_path.exists():
        with open(Default.config_path, "r") as f:
            try:
                config = json.load(f)
            except:
                config = {}
        app.peers = config.get("Peers", [])
    else:
        app.peers = []
    refresh_peers_box(app)

def refresh_peers_box(app):
    child = app.peers_box.get_first_child()
    while child:
        next_child = child.get_next_sibling()
        app.peers_box.remove(child)
        child = next_child
    for peer in app.peers:
        row = app.GBox(orientation=app.GOrientation.HORIZONTAL)
        entry = app.GEntry()
        entry.set_text(peer)
        checkbox = app.GCheckButton()
        checkbox.set_active(True)
        row.append(entry)
        row.append(checkbox)
        app.peers_box.append(row)
        checkbox.connect("toggled", lambda cb: on_peer_toggled(app, cb, entry))

def save_config(app, button):
    if Default.config_path.exists():
        with open(Default.config_path, "r") as f:
            try:
                config = json.load(f)
            except:
                config = {}
    else:
        config = {}

    updated_peers = []
    row = app.peers_box.get_first_child()
    while row:
        next_row = row.get_next_sibling()
        entry = None
        checkbox = None

        subchild = row.get_first_child()
        while subchild:
            next_subchild = subchild.get_next_sibling()
            if isinstance(subchild, app.GEntry):
                entry = subchild
            if isinstance(subchild, app.GCheckButton):
                checkbox = subchild
            subchild = next_subchild

        if entry and checkbox:
            text = entry.get_text().strip()
            if checkbox.get_active() and text:
                updated_peers.append(text)

        row = next_row

    app.peers = updated_peers
    config["Peers"] = app.peers

    with open(Default.config_path, "w") as f:
        json.dump(config, f, indent=2)

    load_config(app)

if __name__ == "__main__":
    raise RuntimeError("This module should be run only via main.py")

