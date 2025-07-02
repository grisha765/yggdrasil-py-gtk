import signal

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")

from gi.repository import Gtk, Adw, Gdk, Gio  # type: ignore

from yggui.core.common import Gui, Binary
from yggui.funcs.config import create_config
from yggui.funcs.peers import load_config
from yggui.exec.pkexec_shell import PkexecShell
from yggui.exec.shell import Shell
from yggui.funcs.private_key import load_private_key
from yggui.funcs.ygg import switch_switched
from yggui.funcs.socks import (
    load_socks_config,
    socks_switch_toggled,
    listen_changed,
    ip_changed,
    port_changed,
)
from yggui.exec.toggle import stop_ygg


class MyApp(Adw.Application):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.connect("activate", self.on_activate)
        self.connect("shutdown", self.on_shutdown)
        signal.signal(signal.SIGINT, lambda _sig, _frm: self._on_sigint())

        self.GBox = Gtk.Box
        self.GEntry = Gtk.Entry
        self.GCheckButton = Gtk.CheckButton
        self.GOrientation = Gtk.Orientation

        self.ygg_pid: int | None = None
        self.socks_pid: int | None = None
        self.socks_config: dict = {}
        self.peers: list[str] = []
        self.current_private_key = ""
        self.default_private_key = ""

        css_provider = Gtk.CssProvider()
        css_provider.load_from_file(Gio.File.new_for_path(str(Gui.css_file)))
        Gtk.StyleContext.add_provider_for_display(
            Gdk.Display.get_default(),
            css_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION,
        )

    def on_activate(self, _app):
        if getattr(self, "win", None) is not None:
            self.win.present()
            return

        builder = Gtk.Builder()

        builder.add_from_file(str(Gui.ui_file))
        builder.add_from_file(str(Gui.ui_main_file))
        builder.add_from_file(str(Gui.ui_settings_file))

        self.win: Adw.ApplicationWindow = builder.get_object("main_window")
        self.win.set_application(self)
        self.win.present()

        self.toast_overlay: Adw.ToastOverlay = builder.get_object("toast_overlay")

        self.stack: Adw.ViewStack = builder.get_object("stack")

        self.main_box = builder.get_object("main")
        self.settings_box = builder.get_object("settings")

        page_main = self.stack.add_titled(self.main_box, "main", "Main")
        page_main.set_icon_name("go-home-symbolic")

        page_settings = self.stack.add_titled(self.settings_box, "settings", "Settings")
        page_settings.set_icon_name("emblem-system-symbolic")

        self.ygg_card: Adw.ExpanderRow = builder.get_object("ygg_card")
        self.ygg_switch: Gtk.Switch = builder.get_object("ygg_switch")

        self.switch = self.ygg_switch
        self.switch_row = self.ygg_card

        self.address_row: Adw.ActionRow = builder.get_object("address_row")
        self.subnet_row: Adw.ActionRow = builder.get_object("subnet_row")

        self.address_copy_icon: Gtk.Image = builder.get_object("address_copy_icon")
        self.subnet_copy_icon: Gtk.Image = builder.get_object("subnet_copy_icon")

        self.ygg_switch.set_active(False)
        self._set_ip_labels("-", "-")
        self._expand_ipv6_card(False)

        self.peers_box: Gtk.Box = builder.get_object("peers_box")
        self.add_peer_btn: Gtk.Button = builder.get_object("add_peer_btn")

        self.private_key_row: Adw.EntryRow = builder.get_object("private_key_row")
        self.private_key_regen_icon: Gtk.Button = builder.get_object(
            "private_key_regen_icon"
        )

        self.peers_group: Adw.PreferencesGroup = builder.get_object("peers_group")

        self.socks_card: Adw.ExpanderRow = builder.get_object("socks_card")
        self.socks_switch: Gtk.Switch = builder.get_object("socks_switch")
        self.socks_listen_row: Adw.EntryRow = builder.get_object("socks_listen_row")
        self.socks_dns_ip_row: Adw.EntryRow = builder.get_object("socks_dns_ip_row")
        self.socks_dns_port_row: Adw.EntryRow = builder.get_object(
            "socks_dns_port_row"
        )

        self._make_row_clickable(self.address_row, lambda: self.address_row.get_subtitle())
        self._make_row_clickable(self.subnet_row, lambda: self.subnet_row.get_subtitle())

        if Binary.pkexec_path is None:
            self.ygg_switch.set_sensitive(False)
            self.ygg_card.set_sensitive(False)
            self.ygg_card.set_subtitle("Polkit not found")

        if Binary.ygg_path is None:
            self.ygg_switch.set_sensitive(False)
            self.ygg_card.set_sensitive(False)
            self.ygg_card.set_subtitle("Yggdrasil not found")
        else:
            create_config()
            self.ygg_switch.connect(
                "notify::active",
                lambda sw, _pspec: switch_switched(self, sw, sw.get_active()),
            )
            self.ygg_card.connect("notify::expanded", self._card_expanded)
            if Binary.yggstack_path is None:
                self.socks_switch.set_sensitive(False)
                self.socks_card.set_sensitive(False)
                self.socks_card.set_subtitle("Yggstack not found")
            else:
                self.socks_switch.connect(
                    "notify::active",
                    lambda sw, _pspec: socks_switch_toggled(self, sw, sw.get_active()),
                )
                self.socks_card.connect("notify::expanded", self._socks_card_expanded)
                self.socks_listen_row.connect(
                    "notify::text", lambda r, _pspec: listen_changed(self, r, _pspec)
                )
                self.socks_dns_ip_row.connect(
                    "notify::text", lambda r, _pspec: ip_changed(self, r, _pspec)
                )
                self.socks_dns_port_row.connect(
                    "notify::text", lambda r, _pspec: port_changed(self, r, _pspec)
                )
                load_socks_config(self)

        load_config(self)
        load_private_key(self)


        self.stack.set_visible_child(self.main_box)

    def on_shutdown(self, _app):
        runner = PkexecShell if self.ygg_pid else Shell
        pid = self.ygg_pid or self.socks_pid
        use_socks = pid is self.socks_pid
        self.ygg_pid = self.socks_pid = None
        if pid:
            stop_ygg(use_socks, pid)
        runner.stop()

    def _on_sigint(self):
        pid = self.ygg_pid or self.socks_pid
        use_socks = pid is self.socks_pid
        self.ygg_pid = self.socks_pid = None
        if pid:
            stop_ygg(use_socks, pid)
        self.quit()

    def _make_row_clickable(self, widget: Gtk.Widget, get_text):
        gesture = Gtk.GestureClick.new()
        gesture.connect(
            "released", lambda _g, _n, _x, _y: self._copy_to_clipboard(get_text())
        )
        widget.add_controller(gesture)

    def _set_ip_labels(self, address: str, subnet: str) -> None:
        self.address_row.set_subtitle(address)
        self.subnet_row.set_subtitle(subnet)

    def _expand_ipv6_card(self, expanded: bool) -> None:
        self.ygg_card.set_expanded(expanded)
        state = "Running" if expanded else "Stopped"
        self.ygg_card.set_subtitle(state)

    def _card_expanded(self, _row, _pspec) -> None:
        expanded = self.ygg_card.get_expanded()
        if self.ygg_switch.get_active() != expanded:
            self.ygg_switch.set_active(expanded)

    def _socks_card_expanded(self, _row, _pspec) -> None:
        expanded = self.socks_card.get_expanded()
        if self.socks_switch.get_active() != expanded:
            self.socks_switch.set_active(expanded)

    def _copy_to_clipboard(self, text: str) -> None:
        if not text or text == "-":
            return
        clipboard = self.win.get_clipboard()
        clipboard.set(text)
        toast = Adw.Toast.new("Copied to clipboard")
        self.toast_overlay.add_toast(toast)


if __name__ == "__main__":
    raise RuntimeError("This module should be run only via main.py")

