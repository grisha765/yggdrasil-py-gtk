import json
import time
from threading import Thread

from gi.repository import GLib, Gtk  # type: ignore

from yggui.core.common import Default
from yggui.func.pkexec_shell import PkexecShell
from yggui.func.socks import (
    start_yggstack,
    stop_yggstack
)


def _show_error_dialog(app, message: str) -> None:
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


def _on_process_error(app, message: str) -> bool:
    _show_error_dialog(app, message)

    if app.switch.get_active():
        app.switch.set_active(False)

    app.switch_row.set_subtitle("Stopped")
    app.ygg_pid = None
    app._set_ip_labels("-", "-")
    app._expand_ipv6_card(False)
    return False


def _get_self_info() -> tuple[str | None, str | None]:
    cmd = (
        f"{Default.yggctl_path} -json "
        f"-endpoint=unix://{Default.admin_socket} getSelf"
    )
    try:
        output = PkexecShell.run_capture(cmd)
        data = json.loads(output)
        return data.get("address"), data.get("subnet")
    except Exception:
        return None, None


def _poll_for_addresses(app) -> None:
    deadline = time.time() + 15
    while time.time() < deadline and app.ygg_pid is not None:
        addr, subnet = _get_self_info()
        if addr and subnet:
            GLib.idle_add(app._set_ip_labels, addr, subnet)
            return
        time.sleep(1)

    GLib.idle_add(app._set_ip_labels, "-", "-")


def start_yggdrasil() -> int:
    cmd = (
        f"{Default.ygg_path} "
        f"-useconffile {Default.config_path.resolve()}"
    )
    return PkexecShell.run_background(cmd)


def stop_yggdrasil(pid: int) -> None:
    PkexecShell.run(f"/usr/bin/kill -s SIGINT {pid}")


def switch_switched(app, _switch, state: bool) -> None:
    use_stack = getattr(app, "socks_config", {}).get("enabled", False)
    if state and app.ygg_pid is None:
        try:
            if use_stack:
                proc = start_yggstack(
                    app.socks_config.get("listen", "127.0.0.1:1080"),
                    app.socks_config.get("dns_ip", ""),
                    app.socks_config.get("dns_port", "53"),
                )
                app.socks_proc = proc
                app.ygg_pid = proc.pid
            else:
                app.ygg_pid = start_yggdrasil()
        except Exception as exc:
            GLib.idle_add(
                _on_process_error,
                app,
                f"Failed to start {'Yggstack' if use_stack else 'Yggdrasil'}: {exc}",
            )
            return

        app.switch_row.set_subtitle("Running")
        app._set_ip_labels("-", "-")
        app._expand_ipv6_card(True)

        Thread(target=_poll_for_addresses, args=(app,), daemon=True).start()

    elif not state and app.ygg_pid is not None:
        use_stack = getattr(app, "socks_config", {}).get("enabled", False)
        if use_stack and getattr(app, "socks_proc", None) is not None:
            stop_yggstack(app.socks_proc)
            app.socks_proc = None
        else:
            stop_yggdrasil(app.ygg_pid)
        app.switch_row.set_subtitle("Stopped")
        app.ygg_pid = None
        app._set_ip_labels("-", "-")
        app._expand_ipv6_card(False)

    print(f"The switch has been switched {'on' if state else 'off'}")


if __name__ == "__main__":
    raise RuntimeError("This module should be run only via main.py")

