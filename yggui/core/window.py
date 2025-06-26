import gi
import signal

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")

from gi.repository import Gtk, Adw, Gdk, Gio, GLib  # type: ignore

from yggui.func.ygg import switch_switched, stop_yggdrasil
from yggui.func.config import create_config
from yggui.func.peers import load_config
from yggui.func.private_key import load_private_key
from yggui.func.pkexec_shell import PkexecShell
from yggui.core.common import Default


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
        self.peers: list[str] = []
        self.current_private_key = ""
        self.default_private_key = ""

        css_provider = Gtk.CssProvider()
        css_provider.load_from_file(Gio.File.new_for_path(str(Default.css_file)))
        Gtk.StyleContext.add_provider_for_display(
            Gdk.Display.get_default(),
            css_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION,
        )

    def on_activate(self, _app):
        builder = Gtk.Builder()
        builder.add_from_file(str(Default.ui_file))

        self.win: Gtk.ApplicationWindow = builder.get_object("main_window")
        self.win.set_application(self)
        self.win.present()

        GLib.idle_add(lambda: PkexecShell.run("# privilege escalation") or False)

        self.main_box = builder.get_object("main")
        self.settings_box = builder.get_object("settings")
        self.stack: Gtk.Stack = builder.get_object("stack")
        self.main_button: Gtk.Button = builder.get_object("main_button")
        self.settings_button: Gtk.Button = builder.get_object("settings_button")

        self.switch_row: Adw.SwitchRow = builder.get_object("switch_row")
        self.switch: Adw.SwitchRow = self.switch_row

        self.address_row: Adw.ActionRow = builder.get_object("address_row")
        self.subnet_row: Adw.ActionRow = builder.get_object("subnet_row")

        self.switch.set_active(False)
        self._set_ip_labels("-", "-")

        self.peers_box: Gtk.Box = builder.get_object("peers_box")
        self.private_key_entry: Gtk.Entry = builder.get_object("private_key_entry")
        self.edit_private_key_button: Gtk.Button = builder.get_object(
            "edit_private_key_button"
        )
        self.reset_private_key_button: Gtk.Button = builder.get_object(
            "reset_private_key_button"
        )
        self.peers_card: Adw.ExpanderRow = builder.get_object("peers_card")

        if Default.ygg_path is None:
            self.switch.set_sensitive(False)
            self.switch_row.set_subtitle("Yggdrasil not found")
        else:
            create_config()
            self.switch_row.connect(
                "notify::active",
                lambda row, _pspec: switch_switched(self, row, row.get_active()),
            )

        load_config(self)
        load_private_key(self)

        self.main_button.connect("clicked", self.switch_to_main)
        self.settings_button.connect("clicked", self.switch_to_settings)

        self.stack.set_visible_child(self.main_box)
        self._update_nav_buttons(self.main_button)

    def on_shutdown(self, _app):
        if self.ygg_pid is not None:
            stop_yggdrasil(self.ygg_pid)
            self.ygg_pid = None
        PkexecShell.stop()

    def _on_sigint(self):
        if self.ygg_pid is not None:
            stop_yggdrasil(self.ygg_pid)
            self.ygg_pid = None
        self.quit()

    def _set_ip_labels(self, address: str, subnet: str) -> None:
        self.address_row.set_subtitle(address)
        self.subnet_row.set_subtitle(subnet)

    def _update_nav_buttons(self, active_btn: Gtk.Button) -> None:
        for btn in (self.main_button, self.settings_button):
            btn.remove_css_class("suggested-action")
        active_btn.add_css_class("suggested-action")

    def switch_to_main(self, _button):
        self.stack.set_visible_child(self.main_box)
        self._update_nav_buttons(self.main_button)

    def switch_to_settings(self, _button):
        self.stack.set_visible_child(self.settings_box)
        self._update_nav_buttons(self.settings_button)


if __name__ == "__main__":
    raise RuntimeError("This module should be run only via main.py")

