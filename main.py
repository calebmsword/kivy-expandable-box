# pylint: disable=wrong-import-position
from functools import partial

import kivy
from kivy.uix.label import Label

kivy.require("2.0.0")

from kivy import Config  # noqa: E402
Config.read("config.ini")

from kivy.app import App  # noqa: E402
from kivy.core.window import Window  # noqa: E402
from kivy.modules import inspector  # noqa: E402
from kivy.uix.button import Button
from expandable import ExpandableMixin
from kivy.lang import Builder


class ExpandableButton(Button, ExpandableMixin):
    pass


root_widget = Builder.load_string(f"""
BoxLayout:
    orientation: "vertical"
""")


def toggle(obj, *_args):
    obj.toggle_expand_horizontal()


expandable_button = ExpandableButton(
    text="hai :3",
    min_width_hint=0.1,
    full_width_hint=1.0,
    allow_expand_horizontal=True,
    # start_expanded_horizontal=False,
)

expandable_button.bind(on_release=partial(toggle, expandable_button))

root_widget.add_widget(expandable_button)


class ExpandableBoxApp(App):

    # def build(self):
    #     return root_widget

    def on_start(self):
        inspector.create_inspector(Window, self.root)

    def on_stop(self):
        inspector.stop(Window, self.root)


if __name__ == '__main__':
    ExpandableBoxApp().run()
