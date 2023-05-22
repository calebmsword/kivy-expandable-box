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


# class ExpandableButton(Button, ExpandableMixin):
#     pass
#
#
# root_widget = Builder.load_string(f"""
# BoxLayout:
#     orientation: "vertical"
# """)
#
#
# def toggle(obj, *_args):
#     obj.toggle_x()
#
#
# expandable_button = ExpandableButton(
#     text="hai :3",
#     min_x_hint=0.3,
#     max_x_hint=1.0,
#     # allow_resize_x=True,
#     start_expanded_x=True,
# )
#
# expandable_button.bind(on_release=partial(toggle, expandable_button))
#
# root_widget.add_widget(expandable_button)
#
# root_widget = Builder.load_string(f"""
# <ExpandableButton@Button+ExpandableMixin>:
#
# BoxLayout:
#     ExpandableButton:
#         text: "Expandable"
#         min_width: 100
#         max_width: 300
#         min_height: 100
#         max_height: 300
#         allow_expand_horizontal: True
#         allow_expand_vertical: True
#         on_release:
#             self.toggle_x()
#             self.toggle_y()
# """)


root_widget = Builder.load_string(f"""
#: set WHITE 1, 1, 1, 1
#: set GREY 0.77, 0.77, 0.77, 1
#: set LIGHT_GREY 0.88, 0.88, 0.88, 1
#: set BLACK 0, 0, 0, 1
#: set BLUE  0, 0, 1, 1
#: set TRANSPARENT 0, 0, 0, 0

<ColoredLabel@Label>:
    bg_color: TRANSPARENT
    canvas.before:
        Color:
            rgba: TRANSPARENT if self.bg_color is None else self.bg_color
        Rectangle:
            pos: self.pos
            size: self.size


<ExpandableLabel@ColoredLabel+ExpandableMixin>:


BoxLayout:
    BoxLayout:
        ExpandableLabel:
            id: expandable
            text: "Expandable"
            bg_color: BLUE
            color: WHITE
            min_x: 100
            max_x_hint: 1
            duration_resize: 3
    BoxLayout:
        orientation: "vertical"
        GridLayout:
            cols: 3
            ColoredLabel:
                bg_color: GREY
                color: BLACK
                text: "expand_state_x: {{0}}".format(expandable.expand_state_x)
            ColoredLabel:
                bg_color: LIGHT_GREY
                color: BLACK
                text: "expanding_x: {{0}}".format(expandable.expanding_x)
            ColoredLabel:
                bg_color: GREY
                color: BLACK
                text: "expanded_x: {{0}}".format(expandable.expanded_x)
            ColoredLabel:
                bg_color: LIGHT_GREY
                color: BLACK
                text: "retract_state_x: {{0}}".format(expandable.retract_state_x)
            ColoredLabel:
                bg_color: GREY
                color: BLACK
                text: "retracting_x: {{0}}".format(expandable.retracting_x)
            ColoredLabel:
                bg_color: LIGHT_GREY
                color: BLACK
                text: "retracted_x: {{0}}".format(expandable.retracted_x)
        BoxLayout:
            Button:
                text: "toggle_x()"
                on_release: expandable.toggle_x()
        GridLayout:
            cols: 2
            Button:
                text: "expand_x()"
                on_release: expandable.expand_x()
            Button:
                text: "retract_x()"
                on_release: expandable.retract_x()
            Button:
                text: "instant_expand_x()"
                on_release: expandable.instant_expand_x()
            Button:
                text: "instant_retract_x()"
                on_release: expandable.instant_retract_x()

""")


class ExpandableBoxApp(App):

    # def build(self):
    #     return root_widget

    def on_start(self):
        inspector.create_inspector(Window, self.root)

    def on_stop(self):
        inspector.stop(Window, self.root)


if __name__ == '__main__':
    ExpandableBoxApp().run()
