import gi, json
gi.require_version("Gtk", "4.0")
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw # type: ignore

from yggui.func.ygg import switch_switched
from yggui.func.config import create_config

from yggui.core.common import Default

from yggui.func.peers import add_peer, save_config, load_config

class MyApp(Adw.Application):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.connect('activate', self.on_activate)
        self.process = None

        self.GBox = Gtk.Box
        self.GEntry = Gtk.Entry
        self.GCheckButton = Gtk.CheckButton
        self.GOrientation = Gtk.Orientation
        self.peers = []

    def on_activate(self, app):
        builder = Gtk.Builder()
        builder.add_from_file('yggui/ui/ui.ui')

        self.win = builder.get_object('main_window')
        self.win.set_application(self)
        self.win.present()


        self.main_box = builder.get_object('main')

        self.label = builder.get_object('switch_label')

        self.switch = builder.get_object('switch1')
        self.switch.set_active(False)
        if Default.ygg_path is None:
            self.switch.set_sensitive(False)
            self.label.set_label('Yggdrasil not found')
        else:
            create_config()
            self.switch.connect('state-set', lambda switch, state: switch_switched(self, switch, state))


        self.settings_box = builder.get_object('settings')

        self.save_settings_button = builder.get_object('save_settings_button')
        self.save_settings_button.connect('clicked', lambda button: save_config(self, button))

        self.peers_box = builder.get_object('peers_box')

        load_config(self)

        self.add_peer_button = builder.get_object('add_peer_button')
        self.add_peer_button.connect('clicked', lambda button: add_peer(self, button))


        self.stack = builder.get_object('stack')
        self.stack.set_visible_child(self.main_box)

        main_button = builder.get_object('main_button')
        main_button.connect('clicked', self.switch_to_main)

        settings_button = builder.get_object('settings_button')
        settings_button.connect('clicked', self.switch_to_settings)


    def switch_to_main(self, button):
        self.add_peer_button.set_visible(False)
        self.stack.set_visible_child(self.main_box)

    def switch_to_settings(self, button):
        self.add_peer_button.set_visible(True)
        self.stack.set_visible_child(self.settings_box)

if __name__ == "__main__":
    raise RuntimeError("This module should be run only via main.py")
