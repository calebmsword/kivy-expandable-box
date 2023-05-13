from kivy import Logger
from kivy.animation import Animation
from kivy.core.window import Window
from kivy.properties import AliasProperty
from kivy.properties import BooleanProperty
from kivy.properties import BoundedNumericProperty
from kivy.properties import NumericProperty
from kivy.properties import ObjectProperty
from kivy.uix.widget import Widget


class ExpandableMixin(Widget):

    allow_expand_horizontal = BooleanProperty(False)
    allow_expand_vertical = BooleanProperty(False)
    start_expanded_horizontal = BooleanProperty(None)
    start_expanded_vertical = BooleanProperty(None)

    min_width_hint = BoundedNumericProperty(None, min=0, allownone=True)
    full_width_hint = BoundedNumericProperty(None, min=0, allownone=True)
    min_height_hint = BoundedNumericProperty(None, min=0, allownone=True)
    full_height_hint = BoundedNumericProperty(None, min=0, allownone=True)
    min_width = NumericProperty(100)
    full_width = NumericProperty(200)
    min_height = NumericProperty(100)
    full_height = NumericProperty(200)

    expand_animation_timeout = NumericProperty(0.25)
    expand_animation_horizontal_timeout = NumericProperty(None)
    expand_animation_vertical_timeout = NumericProperty(None)

    _expand_animation = ObjectProperty(None, allownone=True)
    _expanded_horizontal = BooleanProperty()
    _expanded_vertical = BooleanProperty()
    _expanded_horizontal_initialized = BooleanProperty(False)
    _expanded_vertical_initialized = BooleanProperty(False)

    def _get_expanding(self, *_args):
        return self._expand_animation is not None
    expanding = AliasProperty(_get_expanding, bind=["_expand_animation"])

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

        self._update_width_and_height()

    def on_start_expanded_horizontal(self, _instance, start_expanded):
        if not self._expanded_horizontal_initialized:
            if start_expanded is not None:
                Animation.cancel_all(self, 'size_hint_x')
                Animation.cancel_all(self, 'width')
                if start_expanded:
                    if self.full_width_hint is not None:
                        self.size_hint_x = self.full_width_hint
                    else:
                        self.width = self.full_width
                else:
                    if self.min_width_hint is not None:
                        self.size_hint_x = self.min_width_hint
                    else:
                        self.width = self.min_width
                self._expanded_horizontal = start_expanded
                self._expanded_horizontal_initialized = True

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
                self._expanded_vertical_initialized = True

    def on__expand_animation(self, _instance, expand_animation):
        if expand_animation is not None:

            def done_animating(*_args):
                self._expand_animation = None
                self._update_width_and_height()

            expand_animation.bind(
                on_stop=done_animating,
                on_complete=done_animating
            )
            expand_animation.start(self)

    def start_expand_animation(self, animation: Animation):
        self._expand_animation = animation

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
            # so that any future change to self.start_expanded_horizontal
            # doesn't cause sudden expansion/retraction after initialization
            # (note that on_start_expanded_horizontal executes before this
            #  method)
            if not self._expanded_horizontal_initialized:
                self._expanded_horizontal_initialized = True

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
            # so that any future change to self.start_expanded_vertical
            # doesn't cause sudden expansion/retraction after initialization
            # (note that on_start_expanded_vertical executes before this
            #  method)
            if not self._expanded_vertical_initialized:
                self._expanded_vertical_initialized = True

    def _update_width_and_height(self, *_args):
        self._update_width()
        self._update_height()

    def _resolve_parent(self, *_args):
        if self.parent is not None:
            return

        def find_self(widget):
            for child in widget.children:
                if self is child:
                    self.parent = widget
                    return
                find_self(child)
        find_self(Window)

    def _resolve_size_hint_x(self, *_args):
        """
        If size_hint_x is None, then animating size_hint_x will return an error.
        Hence, we need to take the current width and convert it to the
        corresponding size_hint_x.
        """
        if self.size_hint_x is not None:
            return
        self._resolve_parent()
        if self.parent is None:
            Logger.critical("Widget is detached from Widget tree!")
            self.size_hint_x = 1
            return
        if self.parent is Window:
            # Window size_hint is always relative to window size even if the
            # Window has multiple children
            self.size_hint_x = self.width / Window.width
            return
        num_siblings = len(self.parent.children) - 1
        if num_siblings == 0:
            # If a Layout has only one child, then size_hint_x represents the
            # percent width of the parent
            self.size_hint_x = self.width / self.parent.width
            return
        # If a Layout has multiple children, then size_hint_x is a relative
        # value. Sum the (non-None) size_hint_x's of all children. The width of
        # a child is the ratio of its size_hint_x to the sum total of all
        # size_hint_x's multiplied by the parent width.
        # If a child has a size_hint_x of None, then total width is subtracted
        # from the width of the containing Layout. All the children with
        # non-None size_hint_x's have widths proportional to the remaining
        # width.
        summ = 0.
        fixed_widths = 0.
        min_size_hint = None
        for child in self.parent.children:
            if child.size_hint_x is not None:
                if min_size_hint is None:
                    min_size_hint = child.size_hint_x
                else:
                    min_size_hint = min(
                        min_size_hint,
                        child.size_hint_x
                    )
                summ += child.size_hint_x
            else:
                fixed_widths += child.width
        allotted_width = min(0, self.parent.width - fixed_widths)
        if min_size_hint is None:
            # No children have a size_hint_x, so any non-None value of
            # size_hint_x will cause our Widget to take all allotted
            # width
            self.size_hint_x = 1
        elif allotted_width == 0.:
            # size_hint_x = 0 is actually equivalent to size_hint_x = 1
            # (???) so instead make it small enough to round any value
            # down to 0 pixels
            self.size_hint_x = 0.000001 * min_size_hint
        else:
            # by definition,
            #   size_hint_x / summ = width / allotted_width
            self.size_hint_x = summ * self.width / allotted_width

    def _animate_width_hint(self, new_width_hint, *_args):
        if self.allow_expand_horizontal:
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
        """
        If size_hint_y is None, then animating size_hint_y will return an error.
        Hence, we need to take the current height and convert it to the
        corresponding size_hint_y.
        """
        if self.size_hint_y is None:
            if self.parent is None:
                self.size_hint_y = 1
                return
            num_siblings = len(self.parent.children) - 1
            if num_siblings == 0:
                # If a Layout has only one child, then size_hint_y represents
                # the percent height of the parent
                self.size_hint_y = self.height / self.parent.height
            else:
                # If a Layout has multiple children, then size_hint_y is a
                # relative value. Sum the (non-None) size_hint_y's of all
                # children. The height of a child is the ratio of its
                # size_hint_y to the sum total of all size_hint_y's.
                # If a child has a size_hint_y of None, then its total height is
                # subtracted from the height of the containing Layout. All the
                # children with non-None size_hint_y's have heights proportional
                # to the remaining height.
                summ = 0.
                fixed_heights = 0.
                min_size_hint = None
                for child in self.parent.children:
                    if child.size_hint_y is not None:
                        if min_size_hint is None:
                            min_size_hint = child.size_hint_y
                        else:
                            min_size_hint = min(
                                min_size_hint,
                                child.size_hint_y
                            )
                        summ += child.size_hint_y
                    else:
                        fixed_heights += child.height
                allotted_height = min(0, self.parent.height - fixed_heights)
                if min_size_hint is None:
                    # No children have a size_hint_y, so any non-None value of
                    # size_hint_y will cause our Widget to take all allotted
                    # height
                    self.size_hint_x = 1
                elif allotted_height == 0.:
                    # size_hint_y = 0 is actually equivalent to size_hint_y = 1
                    # (???) so instead make it small enough to round any value
                    # down to 0 pixels
                    self.size_hint_y = 0.000001 * min_size_hint
                else:
                    # by definition,
                    #   size_hint_y / summ = height / allotted_height
                    self.size_hint_y = summ * self.height / allotted_height

    def _animate_height_hint(self, new_height_hint, *_args):
        if self.allow_expand_vertical:
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
        if self.allow_expand_horizontal:
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
        if self.allow_expand_vertical:
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
                    f"; value must be {self.min_height} or {self.full_height}"
                )
