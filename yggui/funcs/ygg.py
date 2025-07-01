import time
from threading import Thread

from gi.repository import GLib, Gtk  # type: ignore

from yggui.funcs.peers import (
    update_peer_status,
    clear_peer_status
)
from yggui.exec.toggle import (
    start_ygg,
    stop_ygg
)
from yggui.exec.get_info import get_self_info


def show_error_dialog(app, message: str) -> None:
    dialog = Gtk.MessageDialog(
        transient_for=app.win,
        modal=True,
        buttons=Gtk.ButtonsType.OK,
        message_type=Gtk.MessageType.ERROR,
        text="Error while running Yggdrasil",
        secondary_text=message,
    )
    dialog.connect("response", lambda d, _r: d.destroy())
    dialog.show()


def on_process_error(app, message: str) -> bool:
    show_error_dialog(app, message)

    if app.switch.get_active():
        app.switch.set_active(False)

    app.switch_row.set_subtitle("Stopped")
    app.ygg_pid = None
    app._set_ip_labels("-", "-")
    app._expand_ipv6_card(False)
    return False


def poll_for_addresses(app, use_socks) -> None:
    deadline = time.time() + 15
    while time.time() < deadline and (
        app.ygg_pid is not None or app.socks_pid is not None
    ):
        addr, subnet = get_self_info(use_socks)
        if addr and subnet:
            GLib.idle_add(app._set_ip_labels, addr, subnet)
            GLib.idle_add(update_peer_status, app)
            return
        time.sleep(1)

    GLib.idle_add(app._set_ip_labels, "-", "-")
    GLib.idle_add(update_peer_status, app)


def switch_switched(app, _switch, state: bool) -> None:
    use_socks = getattr(app, "socks_config", {}).get("enabled", False)
    if state and app.ygg_pid is None and app.socks_pid is None:
        try:
            pid = start_ygg(use_socks, app.socks_config)
            if use_socks:
                app.socks_pid = pid
            else:
                app.ygg_pid = pid
        except Exception as exc:
            GLib.idle_add(
                on_process_error,
                app,
                f"Failed to start {'Yggstack' if use_socks else 'Yggdrasil'}: {exc}",
            )
            return

        app.switch_row.set_subtitle("Running")
        app._set_ip_labels("-", "-")
        app._expand_ipv6_card(True)

        Thread(target=poll_for_addresses, args=(app, use_socks), daemon=True).start()

    elif not state and (app.ygg_pid is not None or app.socks_pid is not None):
        pid = None
        if app.ygg_pid is not None:
            pid = app.ygg_pid
            app.ygg_pid = None
        elif app.socks_pid is not None:
            pid = app.socks_pid
            app.socks_pid = None
        if pid:
            stop_ygg(use_socks, pid)
        app.switch_row.set_subtitle("Stopped")
        app._set_ip_labels("-", "-")
        app._expand_ipv6_card(False)
        clear_peer_status(app)

    print(f"The switch has been switched {'on' if state else 'off'}")


if __name__ == "__main__":
    raise RuntimeError("This module should be run only via main.py")

