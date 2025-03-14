import gi
gi.require_version("Gtk", "4.0")
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw # type: ignore

from yggui.func.ygg import switch_switched
from yggui.func.config import ygg_path_check, save_config, load_config_params

class MyApp(Adw.Application):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.connect('activate', self.on_activate)
        self.process = None
        self.ygg_path, self.config_ygg_path, self.config_ygg_path_check = load_config_params()

    def on_activate(self, app):
        builder = Gtk.Builder()
        builder.add_from_file('yggui/ui/ui.ui')

        self.win = builder.get_object('main_window')
        self.win.set_application(self)
        self.win.present()

        self.main_box = builder.get_object('main')
        self.settings_box = builder.get_object('settings')

        self.save_settings_button = builder.get_object('save_settings_button')
        self.save_settings_button.connect('clicked', lambda button: save_config(self, button))

        main_button = builder.get_object('main_button')
        main_button.connect('clicked', self.switch_to_main)

        settings_button = builder.get_object('settings_button')
        settings_button.connect('clicked', self.switch_to_settings)

        self.ygg_path_check = builder.get_object('ygg_path_check')
        self.ygg_path_check.set_active(self.config_ygg_path_check)
        self.ygg_path_check.connect('toggled', lambda button: ygg_path_check(self, button))

        self.ygg_path_input = builder.get_object('ygg_path_input')
        self.ygg_path_input.set_text(self.config_ygg_path)
        self.ygg_path_input.set_sensitive(self.ygg_path_check.get_active())

        self.label = builder.get_object('switch_label')

        self.switch = builder.get_object('switch1')
        self.switch.set_active(False)
        self.switch.connect('state-set', lambda switch, state: switch_switched(self, switch, state))

        self.stack = builder.get_object('stack')
        self.stack.set_visible_child(self.main_box)

    def switch_to_main(self, button):
        self.stack.set_visible_child(self.main_box)

    def switch_to_settings(self, button):
        self.stack.set_visible_child(self.settings_box)

if __name__ == "__main__":
    raise RuntimeError("This module should be run only via main.py")
