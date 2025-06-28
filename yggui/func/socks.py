import json
import subprocess
import signal
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


def _save_param(key: str, value):
    cfg = _read_config()
    cfg[key] = value
    _write_config(cfg)


def _update_visibility(app, enabled: bool):
    app.socks_listen_row.set_visible(enabled)
    app.socks_dns_ip_row.set_visible(enabled)
    app.socks_dns_port_row.set_visible(enabled)


def load_socks_config(app):
    cfg = _read_config()
    enabled = cfg.get("yggstack-enable", False)
    listen = cfg.get("yggstack-listen", "127.0.0.1:1080")
    dns_ip = cfg.get("yggstack-dns-ip", "")
    dns_port = cfg.get("yggstack-dns-port", "53")
    if Default.yggstack_path is None:
        enabled = False
        app.socks_switch.set_sensitive(False)
        app.socks_card.set_sensitive(False)
        app.socks_card.set_subtitle("Yggstack not found")
    app.socks_config = {
        "enabled": enabled,
        "listen": listen,
        "dns_ip": dns_ip,
        "dns_port": dns_port,
    }
    app.socks_switch.set_active(enabled)
    app.socks_card.set_subtitle("Enabled" if enabled else "Disabled")
    app.socks_listen_row.set_text(listen)
    app.socks_dns_ip_row.set_text(dns_ip)
    app.socks_dns_port_row.set_text(dns_port)
    app.socks_card.set_expanded(enabled)
    _update_visibility(app, enabled)


def socks_switch_toggled(app, _switch, state: bool):
    _save_param("yggstack-enable", state)
    app.socks_card.set_subtitle("Enabled" if state else "Disabled")
    app.socks_card.set_expanded(state)
    _update_visibility(app, state)
    app.socks_config["enabled"] = state


def listen_changed(app, _row, _pspec):
    value = app.socks_listen_row.get_text().strip()
    if value:
        _save_param("yggstack-listen", value)
        app.socks_config["listen"] = value


def ip_changed(app, _row, _pspec):
    value = app.socks_dns_ip_row.get_text().strip()
    _save_param("yggstack-dns-ip", value)
    app.socks_config["dns_ip"] = value


def port_changed(app, _row, _pspec):
    value = app.socks_dns_port_row.get_text().strip() or "53"
    _save_param("yggstack-dns-port", value)
    app.socks_config["dns_port"] = value


def start_yggstack(listen: str, dns_ip: str, dns_port: str) -> subprocess.Popen[str]:
    cmd = [
        Default.yggstack_path or "yggstack",
        "-useconffile",
        str(Default.config_path.resolve()),
    ]
    if listen:
        cmd.extend(["-socks", listen])
    if dns_ip:
        if ":" in dns_ip and not dns_ip.startswith("["):
            nameserver = f"[{dns_ip}]:{dns_port}"
        else:
            nameserver = f"{dns_ip}:{dns_port}"
        cmd.extend(["-nameserver", nameserver])
    return subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )


def stop_yggstack(proc: subprocess.Popen[str]) -> None:
    if proc.poll() is None:
        try:
            proc.send_signal(signal.SIGINT)
            proc.wait(timeout=5)
        except Exception:
            proc.kill()


if __name__ == "__main__":
    raise RuntimeError("This module should be run only via main.py")

