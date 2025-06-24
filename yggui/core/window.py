import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Adw, Gdk, Gio  # type: ignore

from yggui.func.ygg import switch_switched
from yggui.func.config import create_config
from yggui.func.peers import load_config
from yggui.func.private_key import load_private_key

from yggui.core.common import Default


class MyApp(Adw.Application):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.connect("activate", self.on_activate)

        self.GBox = Gtk.Box
        self.GEntry = Gtk.Entry
        self.GCheckButton = Gtk.CheckButton
        self.GOrientation = Gtk.Orientation

        self.process = None
        self.peers = []
        self.current_private_key = ""
        self.default_private_key = ""

        css_provider = Gtk.CssProvider()
        css_provider.load_from_file(Gio.File.new_for_path(Default.css_file))
        Gtk.StyleContext.add_provider_for_display(
            Gdk.Display.get_default(),
            css_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION,
        )

    def on_activate(self, _app):
        builder = Gtk.Builder()
        builder.add_from_file(Default.ui_file)

        self.win = builder.get_object("main_window")
        self.win.set_application(self)
        self.win.present()

        self.main_box = builder.get_object("main")
        self.settings_box = builder.get_object("settings")
        self.stack = builder.get_object("stack")
        self.peers_box = builder.get_object("peers_box")
        self.private_key_entry = builder.get_object("private_key_entry")
        self.edit_private_key_button = builder.get_object("edit_private_key_button")
        self.reset_private_key_button = builder.get_object("reset_private_key_button")

        self.label = builder.get_object("switch_label")
        self.switch = builder.get_object("switch1")
        self.switch.set_active(False)

        if Default.ygg_path is None:
            self.switch.set_sensitive(False)
            self.label.set_label("Yggdrasil not found")
        else:
            create_config()
            self.switch.connect(
                "state-set",
                lambda sw, state: switch_switched(self, sw, state),
            )

        load_config(self)
        load_private_key(self)

        builder.get_object("main_button").connect("clicked", self.switch_to_main)
        builder.get_object("settings_button").connect(
            "clicked",
            self.switch_to_settings,
        )

        self.stack.set_visible_child(self.main_box)

    def switch_to_main(self, _button):
        self.stack.set_visible_child(self.main_box)

    def switch_to_settings(self, _button):
        self.stack.set_visible_child(self.settings_box)


if __name__ == "__main__":
    raise RuntimeError("This module should be run only via main.py")

