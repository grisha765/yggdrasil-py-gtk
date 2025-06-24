import json
import re
import subprocess
import time
from threading import Thread

from gi.repository import GLib  # type: ignore

from yggui.core.common import Default


def print_output(process):
    for line in process.stdout:
        print(line.decode("utf-8").strip())


def _get_self_info():
    try:
        yggctl = Default.yggctl_path
        if yggctl is None:
            return "Yggdrasilctl not found", "Yggdrasilctl not found"
        command: list[str] = [
                yggctl,
                "-json",
                f"-endpoint=unix://{Default.admin_socket}",
                "getSelf"
            ]
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=True
        )
        data = json.loads(result.stdout)
        return data.get("address"), data.get("subnet")
    except Exception:
        return None, None


def _poll_for_addresses(app):
    deadline = time.time() + 15
    while time.time() < deadline and app.process is not None:
        addr, subnet = _get_self_info()
        if addr and subnet:
            GLib.idle_add(app._set_ip_labels, addr, subnet)
            return
        time.sleep(1)

    GLib.idle_add(app._set_ip_labels, "-", "-")


def start_yggdrasil():
    command = [
        Default.ygg_path,
        "-useconffile",
        Default.config_path.resolve(),
    ]
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output_thread = Thread(target=print_output, args=(process,), daemon=True)
    output_thread.start()
    return process


def stop_yggdrasil(process):
    subprocess.run(["kill", "-s", "SIGINT", str(process.pid)], check=False)
    process.wait()


def extract_ips(output):
    ipv6_regex = r"([0-9a-fA-F:]+(?::[0-9a-fA-F]+)*\b)"
    return re.findall(ipv6_regex, output)


def switch_switched(app, _switch, state: bool):
    if state and app.process is None:
        app.process = start_yggdrasil()
        app.label.set_label("Disable Yggdrasil")
        print("Yggdrasil started. Waiting for address…")
        app._set_ip_labels("-", "-")
        Thread(target=_poll_for_addresses, args=(app,), daemon=True).start()

    elif not state and app.process is not None:
        stop_yggdrasil(app.process)
        print("Yggdrasil stopped.")
        app.label.set_label("Enable Yggdrasil")
        app.process = None
        app._set_ip_labels("-", "-")

    print(f"The switch has been switched {'on' if state else 'off'}")


if __name__ == "__main__":
    raise RuntimeError("This module should be run only via main.py")
