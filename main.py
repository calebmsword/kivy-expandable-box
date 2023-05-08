from kivy.animation import Animation
from kivy.app import App
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.modules import inspector
from kivy.properties import AliasProperty
from kivy.properties import BooleanProperty
from kivy.properties import BoundedNumericProperty
from kivy.properties import NumericProperty
from kivy.properties import ObjectProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.widget import Widget


class ExpandableMixin(Widget):
    _expand_animation = ObjectProperty(None, allownone=True)
    expand_animation_done_callback = ObjectProperty(None, allownone=True)

    def _get_expanding(self, *_args):
        return self._expand_animation is not None

    expanding = AliasProperty(_get_expanding, bind=["_expand_animation"])

    def on__expand_animation(self, _instance, expand_animation):
        if expand_animation is not None:

            def done_animating(*_args):
                self._expand_animation = None
                if self.expand_animation_done_callback is not None:
                    self.expand_animation_done_callback()

            expand_animation.bind(
                on_stop=done_animating,
                on_complete=done_animating
            )
            expand_animation.start(self)

    def start_expand_animation(self, animation: Animation):
        self._expand_animation = animation

    min_width_hint = BoundedNumericProperty(None, min=0, allownone=True)
    full_width_hint = BoundedNumericProperty(None, min=0, allownone=True)
    min_height_hint = BoundedNumericProperty(None, min=0, allownone=True)
    full_height_hint = BoundedNumericProperty(None, min=0, allownone=True)
    min_width = NumericProperty(100)
    full_width = NumericProperty(200)
    min_height = NumericProperty(100)
    full_height = NumericProperty(200)
    allow_expand_horizontal = BooleanProperty(False)
    allow_expand_vertical = BooleanProperty(False)
    start_expanded_horizontal = BooleanProperty(None)
    start_expanded_vertical = BooleanProperty(None)
    _expanded_horizontal = BooleanProperty()
    _expanded_vertical = BooleanProperty()
    expand_animation_timeout = NumericProperty(0.25)
    expand_animation_horizontal_timeout = NumericProperty(None)
    expand_animation_vertical_timeout = NumericProperty(None)

    def _get_expanded_horizontal(self, *_args):
        return self._expanded_horizontal
    expanded_horizontal = AliasProperty(
        _get_expanded_horizontal,
        bind=["_expanded_horizontal"]
    )

    def _get_expanded_vertical(self, *_args):
        return self._expanded_vertical
    expanded_vertical = AliasProperty(
        _get_expanded_vertical,
        bind=["_expanded_vertical"]
    )

    def _get_retracted_horizontal(self, *_args):
        return not self._expanded_horizontal
    retracted_horizontal = AliasProperty(
        _get_retracted_horizontal,
        bind=["expanded_horizontal"]
    )

    def _get_retracted_vertical(self, *_args):
        return not self._expanded_vertical
    retracted_vertical = AliasProperty(
        _get_retracted_vertical,
        bind=["expanded_vertical"]
    )

    def _get_fully_expanded_horizontal(self, *_args):
        if self.full_width_hint is not None:
            return self.size_hint_x == self.full_width_hint
        else:
            return self.width == self.full_width
    fully_expanded_horizontal = AliasProperty(
        _get_fully_expanded_horizontal, bind=[
            "size_hint_x",
            "width",
            "full_height_hint",
            "full_height",
            "expanded_horizontal"
        ]
    )

    def _get_fully_retracted_horizontal(self, *_args):
        if self.min_width_hint is not None:
            return self.size_hint_x == self.min_width_hint
        else:
            return self.width == self.min_width
    fully_retracted_horizontal = AliasProperty(
        _get_fully_retracted_horizontal, bind=[
            "size_hint_x",
            "width",
            "min_width_hint",
            "min_width",
            "expanded_horizontal"
        ]
    )

    def _get_fully_expanded_vertical(self, *_args):
        if self.full_height_hint is not None:
            return self.size_hint_y == self.full_height_hint
        else:
            return self.height == self.full_height
    fully_expanded_vertical = AliasProperty(
        _get_fully_expanded_vertical, bind=[
            "size_hint_y",
            "height",
            "full_height_hint",
            "full_height",
            "expanded_vertical"
        ]
    )

    def _get_fully_retracted_vertical(self, *_args):
        if self.min_height_hint is not None:
            return self.size_hint_y == self.min_height_hint
        else:
            return self.height == self.min_height
    fully_retracted_vertical = AliasProperty(
        _get_fully_retracted_vertical, bind=[
            "size_hint_y",
            "height",
            "min_height_hint",
            "min_height",
            "expanded_vertical"
        ]
    )

    def __init__(self, **kwargs):
        super(ExpandableMixin, self).__init__(**kwargs)

        self.expand_animation_done_callback = self._update_width_and_height

        self.bind(min_width_hint=self._update_width)
        self.bind(full_width_hint=self._update_width)
        self.bind(min_width=self._update_width)
        self.bind(full_width=self._update_width)
        self.bind(expanded_horizontal=self._update_width)

        self.bind(min_height_hint=self._update_height)
        self.bind(full_height_hint=self._update_height)
        self.bind(min_height=self._update_height)
        self.bind(full_height=self._update_height)
        self.bind(expanded_vertical=self._update_height)

    def _update_width_and_height(self, *_args):
        self._update_width()
        self._update_height()

    def toggle_expand_horizontal(self, *_args):
        if self.allow_expand_horizontal:
            if self._expanded_horizontal:
                if self.min_width_hint is not None:
                    self._animate_width_hint(self.min_width_hint)
                else:
                    self._animate_width(self.min_width)
            else:
                if self.full_width_hint is not None:
                    self._animate_width_hint(self.full_width_hint)
                else:
                    self._animate_width(self.full_width)
            self._expanded_horizontal = not self._expanded_horizontal

    def toggle_expand_vertical(self, *_args):
        if self.allow_expand_vertical:
            if self._expanded_vertical:
                if self.min_height_hint is not None:
                    self._animate_height_hint(self.min_height_hint)
                else:
                    self._animate_height(self.min_height)
            else:
                if self.full_height_hint is not None:
                    self._animate_height_hint(self.full_height_hint)
                else:
                    self._animate_height(self.full_height)

            self._expanded_vertical = not self._expanded_vertical

    def _update_width(self, *_args):
        if self.allow_expand_horizontal:
            if not self.expanding:
                if not self._expanded_horizontal:
                    if self.min_width_hint is not None:
                        self.size_hint_x = self.min_width_hint
                    else:
                        self.size_hint_x = None
                        self.width = self.min_width
                else:
                    if self.full_width_hint is not None:
                        self.size_hint_x = self.full_width_hint
                    else:
                        self.size_hint_x = None
                        self.width = self.full_width

    def _update_height(self, *_args):
        if self.allow_expand_vertical:
            if not self.expanding:
                if not self._expanded_vertical:
                    if self.min_height_hint is not None:
                        self.size_hint_y = self.min_height_hint
                    else:
                        self.size_hint_y = None
                        self.height = self.min_height
                else:
                    if self.full_height_hint is not None:
                        self.size_hint_y = self.full_height_hint
                    else:
                        self.size_hint_y = None
                        self.height = self.full_height

    def expand_horizontal(self, *_args):
        if not self._expanded_horizontal:
            self.toggle_expand_horizontal()

    def retract_horizontal(self, *_args):
        if not self.retracted_horizontal:
            self.toggle_expand_horizontal()

    def expand_vertical(self, *_args):
        if not self._expanded_vertical:
            self.toggle_expand_vertical()

    def retract_vertical(self, *_args):
        if not self.retracted_vertical:
            self.toggle_expand_vertical()

    def force_expand_horizontal(self, *_args):
        Animation.cancel_all(self, "size_hint_x")
        Animation.cancel_all(self, "width")
        if self.full_width_hint is not None:
            self.size_hint_x = self.full_width_hint
        else:
            self.width = self.full_width
        self._expanded_horizontal = True

    def force_retract_horizontal(self, *_args):
        Animation.cancel_all(self, "size_hint_x")
        Animation.cancel_all(self, "width")
        if self.min_width_hint is not None:
            self.size_hint_x = self.min_width_hint
        else:
            self.width = self.min_width
        self._expanded_horizontal = False

    def force_expand_vertical(self, *_args):
        Animation.cancel_all(self, "size_hint_y")
        Animation.cancel_all(self, "height")
        if self.full_height_hint is not None:
            self.size_hint_y = self.full_height_hint
        else:
            self.height = self.full_height
        self._expanded_vertical = True

    def force_retract_vertical(self, *_args):
        Animation.cancel_all(self, "size_hint_y")
        Animation.cancel_all(self, "height")
        if self.min_height_hint is not None:
            self.size_hint_y = self.min_height_hint
        else:
            self.height = self.min_height
        self._expanded_vertical = False

    def force_toggle_vertical(self, *_args):
        if self._expanded_vertical:
            self.force_retract_vertical()
        else:
            self.force_expand_vertical()

    def force_toggle_horizontal(self, *_args):
        if self._expanded_horizontal:
            self.force_retract_horizontal()
        else:
            self.force_expand_horizontal()

    def _resolve_size_hint_x(self, *_args):
        if self.size_hint_x is None:
            num_siblings = len(self.parent.children) - 1
            if num_siblings == 0:
                self.size_hint_x = self.width / self.parent.width
            else:
                summ = 0.
                fixed_widths = 0.
                for child in self.parent.children:
                    if child.size_hint_x is not None:
                        summ += child.size_hint_x
                    else:
                        fixed_widths += child.width
                allotted_width = min(0, self.parent.width - fixed_widths)
                if allotted_width == 0.:
                    self.size_hint_x = 0
                else:
                    # size_hint_x / summ = width / allotted_width
                    self.size_hint_x = summ * self.width / allotted_width

    def _animate_width_hint(self, new_width_hint, *_args):
        if new_width_hint in [self.min_width_hint, self.full_width_hint]:
            self._resolve_size_hint_x()
            Animation.cancel_all(self, 'width')

            if self.expand_animation_horizontal_timeout is not None:
                timeout = self.expand_animation_horizontal_timeout
            else:
                timeout = self.expand_animation_timeout

            if self.size_hint_x != new_width_hint:
                self.start_expand_animation(Animation(
                    size_hint_x=new_width_hint,
                    d=timeout
                ))
        else:
            raise ValueError(
                f"Attempted to set invalid size_hint_x: {new_width_hint}" +
                f"; value must be either {self.min_width_hint} or " +
                f"{self.full_width_hint}"
            )

    def _resolve_size_hint_y(self, *_args):
        if self.size_hint_y is None:
            num_siblings = len(self.parent.children) - 1
            if num_siblings == 0:
                self.size_hint_y = self.height / self.parent.height
            else:
                summ = 0.
                fixed_heights = 0.
                for child in self.parent.children:
                    if child.size_hint_y is not None:
                        summ += child.size_hint_y
                    else:
                        fixed_heights += child.height
                allotted_height = min(0, self.parent.height - fixed_heights)
                if allotted_height == 0.:
                    self.size_hint_y = 0
                else:
                    # size_hint_y / summ = height / allotted_height
                    self.size_hint_y = summ * self.height / allotted_height

    def _animate_height_hint(self, new_height_hint, *_args):
        if new_height_hint in [self.min_height_hint, self.full_height_hint]:
            self._resolve_size_hint_y()
            Animation.cancel_all(self, 'height')

            if self.expand_animation_vertical_timeout is not None:
                timeout = self.expand_animation_vertical_timeout
            else:
                timeout = self.expand_animation_timeout

            if self.size_hint_y != new_height_hint:
                self.start_expand_animation(Animation(
                    size_hint_y=new_height_hint,
                    d=timeout
                ))
        else:
            raise ValueError(
                f"Attempted to set invalid size_hint_y: {new_height_hint}" +
                f"; value must be {self.min_height_hint} or " +
                f"{self.full_height_hint}"
            )

    def _animate_width(self, new_width, *_args):
        if new_width in [self.min_width, self.full_width]:
            Animation.cancel_all(self, 'size_hint_x')
            self.size_hint_x = None

            if self.expand_animation_horizontal_timeout is not None:
                timeout = self.expand_animation_horizontal_timeout
            else:
                timeout = self.expand_animation_timeout

            self.start_expand_animation(Animation(
                width=new_width,
                d=timeout
            ))
        else:
            raise ValueError(
                f"Attempted to set invalid width: {new_width}" +
                f"; value must be {self.min_width} or {self.full_width}"
            )

    def _animate_height(self, new_height, *_args):
        if new_height in [self.min_height, self.full_height]:
            Animation.cancel_all(self, 'size_hint_y')
            self.size_hint_y = None

            if self.expand_animation_vertical_timeout is not None:
                timeout = self.expand_animation_vertical_timeout
            else:
                timeout = self.expand_animation_timeout

            self.start_expand_animation(Animation(
                height=new_height,
                d=timeout
            ))
        else:
            raise ValueError(
                f"Attempted to set invalid height: {new_height}" +
                f"; value must be {self.min_wheight} or {self.full_height}"
            )

    _expanded_horizontal_initialized = BooleanProperty(False)

    def on_start_expanded_horizontal(self, _instance, start_expanded_horizontal):
        if not self._expanded_horizontal_initialized:
            if start_expanded_horizontal is not None:
                Animation.cancel_all(self, 'size_hint_x')
                Animation.cancel_all(self, 'width')
                if start_expanded_horizontal:
                    if self.full_width_hint is not None:
                        self.size_hint_x = self.full_width_hint
                    else:
                        self.width = self.full_width
                else:
                    if self.min_width_hint is not None:
                        self.size_hint_x = self.min_width_hint
                    else:
                        self.width = self.min_width
                self._expanded_horizontal = start_expanded_horizontal

    _expanded_vertical_initialized = BooleanProperty(False)

    def on_start_expanded_vertical(self, _instance, start_expanded_vertical):
        if not self._expanded_vertical_initialized:
            if start_expanded_vertical is not None:
                Animation.cancel_all(self, 'size_hint_y')
                Animation.cancel_all(self, 'height')
                if start_expanded_vertical:
                    if self.full_height_hint is not None:
                        self.size_hint_y = self.full_height_hint
                    else:
                        self.height = self.full_height
                else:
                    if self.min_height_hint is not None:
                        self.size_hint_y = self.min_height_hint
                    else:
                        self.height = self.min_height
                self._expanded_vertical = start_expanded_vertical


class ExpandableLabel(Label, ExpandableMixin):
    pass


class StatefulButton(Button):
    active = BooleanProperty(False)

    def on_release(self, *_args):
        self.active = not self.active


Builder.load_string(f"""
<RootWidget>:
    orientation: "vertical"
    BoxLayout:
        ExpandableLabel:
            canvas.before:
                Color:
                    rgba: 0, 0, 1, 1
                Rectangle:
                    pos: self.pos
                    size: self.size
            id: expandable_hor
            allow_expand_horizontal: True
            start_expanded_horizontal: False
            min_width_hint:  1./3
            full_width_hint: 1
            text: "Expandable"
        StatefulButton:
            id: btn_stateful_hor
            text: "<== Expandable horizontally"
            on_release: expandable_hor.toggle_expand_horizontal()
    BoxLayout:
        BoxLayout:
            ExpandableLabel:
                canvas.before:
                    Color:
                        rgba: 1, 0, 0, 1
                    Rectangle:
                        pos: self.pos
                        size: self.size
                id: expandable_vert
                allow_expand_vertical: True
                start_expanded_vertical: False
                expand_animation_timeout: 1
                min_height_hint:  0.25
                full_height_hint: 0.50
                text: "Expandable"
        BoxLayout:
            orientation: "vertical"
            StatefulButton:
                id: btn_stateful_vert_01
                text: "<== Force " + ("expand" if expandable_vert.retracted_vertical else "retract") + " vertically"
                on_release: expandable_vert.force_expand_vertical() if expandable_vert.retracted_vertical else expandable_vert.force_retract_vertical()
            StatefulButton:
                id: btn_stateful_vert_02
                text: "<== Toggle vertically"
                on_release: expandable_vert.toggle_expand_vertical()
    BoxLayout:
        AnchorLayout:
            anchor_x: "center"
            anchor_y: "center"
            ExpandableLabel:
                id: expandable_both
                allow_expand_horizontal: True
                allow_expand_vertical: True
                start_expanded_horizontal: False
                start_expanded_vertical: False
                
                min_width_hint:   0.25
                full_width_hint:  0.50
                min_height_hint:  0.25
                full_height_hint: 0.50
                               
                # min_width: 150
                # full_width_hint:  1
                # min_height_hint:  0.25
                # full_height: 400
                
                # min_width: 150
                # full_width: 300
                # min_height: 200
                # full_height: 400
                
                expand_animation_timeout: 1
                color: 0, 0, 0, 1
                text: "Expandable"
                canvas.before:
                    Color:
                        rgba: 0, 1, 0, 1
                    Rectangle:
                        pos: self.pos
                        size: self.size
        BoxLayout:
            StatefulButton:
                id: btn_stateful_hor_02
                size_hint_x: 1
                text: "<== Toggle horizontal"
                on_release: expandable_both.toggle_expand_horizontal()
            StatefulButton:
                id: btn_stateful_vert_02
                size_hint_x: 1
                text: "<== Toggle vertical"
                on_release: expandable_both.toggle_expand_vertical()
            GridLayout:
                cols: 2
                size_hint_x: 2
                Button:
                    text: "Force expand vertical"
                    on_release: expandable_both.force_expand_vertical()
                Button:
                    text: "Force retract vertical"
                    on_release: expandable_both.force_retract_vertical()
                Button:
                    text: "Force expand horizontal"
                    on_release: expandable_both.force_expand_horizontal()
                Button:
                    text: "Force retract horizontal"
                    on_release: expandable_both.force_retract_horizontal()
    BoxLayout:
        AnchorLayout:
            anchor_x: "left"
            anchor_y: "bottom"
            ExpandableLabel:
                id: expandable_both_2
                allow_expand_horizontal: True
                allow_expand_vertical: True
                start_expanded_horizontal: True
                start_expanded_vertical: False
                
                # min_width_hint:   0.25
                # full_width_hint:  0.50
                # min_height_hint:  0.25
                # full_height_hint: 0.50
                               
                min_width: 150
                full_width_hint:  1
                min_height_hint:  0.25
                full_height: 400
                
                # min_width: 150
                # full_width: 300
                # min_height: 200
                # full_height: 400
                
                expand_animation_timeout: 0.10
                color: 0, 0, 0, 1
                text: "Expandable"
                canvas.before:
                    Color:
                        rgba: 0, 1, 1, 1
                    Rectangle:
                        pos: self.pos
                        size: self.size
        BoxLayout:
            Button:
                size_hint_x: 1
                text: "Force toggle horizontal"
                on_release: expandable_both_2.force_toggle_horizontal()
            Button:
                size_hint_x: 1
                text: "Force toggle vertical"
                on_release: expandable_both_2.force_toggle_vertical()
            GridLayout:
                cols: 2
                size_hint_x: 2
                Button:
                    text: "Expand vertical"
                    on_release: expandable_both_2.expand_vertical()
                Button:
                    text: "Retract vertical"
                    on_release: expandable_both_2.retract_vertical()
                Button:
                    text: "Expand horizontal"
                    on_release: expandable_both_2.expand_horizontal()
                Button:
                    text: "Retract horizontal"
                    on_release: expandable_both_2.retract_horizontal()
""")


class RootWidget(BoxLayout):
    pass


class ExpandableBoxApp(App):

    def build(self):
        root = RootWidget()
        Window.maximize()

        inspector.create_inspector(Window, root)
        return root


if __name__ == '__main__':
    ExpandableBoxApp().run()
