# pylint: disable=wrong-import-position

import kivy
kivy.require("2.0.0")

from kivy import Config  # noqa: E402
Config.read("config.ini")

from kivy.app import App  # noqa: E402
from kivy.core.window import Window  # noqa: E402
from kivy.modules import inspector  # noqa: E402


class ExpandableBoxApp(App):

    def on_start(self):
        inspector.create_inspector(Window, self.root)

    def on_stop(self):
        inspector.stop(Window, self.root)


if __name__ == '__main__':
    ExpandableBoxApp().run()
