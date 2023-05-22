import time
from math import ceil

from kivy import Logger
from kivy.animation import Animation
from kivy.core.window import Window
from kivy.core.window import WindowBase
from kivy.properties import AliasProperty
from kivy.properties import BooleanProperty
from kivy.properties import BoundedNumericProperty
from kivy.properties import NumericProperty
from kivy.properties import ObjectProperty
from kivy.properties import OptionProperty
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.stacklayout import StackLayout
from kivy.uix.widget import Widget

DO_SPECIAL_ANIM = True
DO_DEFAULT_ANIM = False

HORIZONTAL = True
VERTICAL = False


class AnimTransitions:
    IN_BACK = "in_back"
    IN_BOUNCE = "in_bounce"
    IN_CIRC = "in_circ"
    IN_CUBIC = "in_cubic"
    IN_ELASTIC = "in_elastic"
    IN_EXPO = "in_expo"
    IN_OUT_BACK = "in_out_back"
    IN_OUT_BOUNCE = "in_out_bounce"
    IN_OUT_CIRC = "in_out_circ"
    IN_OUT_CUBIC = "in_out_cubic"
    IN_OUT_ELASTIC = "in_out_elastic"
    IN_OUT_EXPO = "in_out_expo"
    IN_OUT_QUAD = "in_out_quad"
    IN_OUT_QUART = "in_out_quart"
    IN_OUT_QUINT = "in_out_quint"
    IN_OUT_SINE = "in_out_sine"
    IN_QUAD = "in_quad"
    IN_QUART = "in_quart"
    IN_QUINT = "in_quint"
    IN_SINE = "in_sine"
    LINEAR = "linear"
    OUT_BACK = "out_back"
    OUT_BOUNCE = "out_bounce"
    OUT_CIRC = "out_circ"
    OUT_CUBIC = "out_cubic"
    OUT_ELASTIC = "out_elastic"
    OUT_EXPO = "out_expo"
    OUT_QUAD = "out_quad"
    OUT_QUART = "out_quart"
    OUT_QUINT = "out_quint"
    OUT_SINE = "out_sine"


anim_transitions = [
    value
    for key, value in vars(AnimTransitions).items()
    if not key.startswith("__")
]


class ExpandableMixinError(Exception):
    pass


class ExpandableMixin(Widget):
    allow_resize_x = BooleanProperty(False)
    allow_resize_y = BooleanProperty(False)
    start_expanded_x = BooleanProperty(None)
    start_expanded_y = BooleanProperty(None)

    min_x_hint = BoundedNumericProperty(None, min=0, allownone=True)
    max_x_hint = BoundedNumericProperty(None, min=0, allownone=True)
    min_y_hint = BoundedNumericProperty(None, min=0, allownone=True)
    max_y_hint = BoundedNumericProperty(None, min=0, allownone=True)
    min_x = NumericProperty(None)
    max_x = NumericProperty(None)
    min_y = NumericProperty(None)
    max_y = NumericProperty(None)

    duration_resize = NumericProperty(0.25)
    duration_resize_x = NumericProperty(None, allownone=True)
    duration_resize_y = NumericProperty(None, allownone=True)
    duration_expand_x = NumericProperty(None, allownone=True)
    duration_expand_y = NumericProperty(None, allownone=True)
    duration_retract_x = NumericProperty(None, allownone=True)
    duration_retract_y = NumericProperty(None, allownone=True)

    fixed_duration_x = BooleanProperty(False)
    fixed_duration_y = BooleanProperty(False)

    transition_resize = OptionProperty(
        AnimTransitions.LINEAR,
        options=anim_transitions
    )

    transition_resize_x = OptionProperty(
        None,
        options=anim_transitions,
        allownone=True
    )

    transition_resize_y = OptionProperty(
        None,
        options=anim_transitions,
        allownone=True
    )

    transition_expand_x = OptionProperty(
        None,
        options=anim_transitions,
        allownone=True
    )

    transition_expand_y = OptionProperty(
        None,
        options=anim_transitions,
        allownone=True
    )

    transition_retract_x = OptionProperty(
        None,
        options=anim_transitions,
        allownone=True
    )

    transition_retract_y = OptionProperty(
        None,
        options=anim_transitions,
        allownone=True
    )

    _resize_animation = ObjectProperty(None, allownone=True)

    _timestamp_horizontal = NumericProperty(None, allownone=True)
    """Used for determining how much an animation has progressed."""

    _timestamp_vertical = NumericProperty(None, allownone=True)
    """Used for determining how much an animation has progressed."""

    _prev_duration_horizontal = NumericProperty(None, allownone=True)
    _prev_duration_vertical = NumericProperty(None, allownone=True)
    _percent_expanded_horizontal = NumericProperty(None, allownone=True)
    _percent_expanded_vertical = NumericProperty(None, allownone=True)

    _expanded_horizontal = BooleanProperty()
    _expanded_vertical = BooleanProperty()
    _initialized = BooleanProperty(False)

    def _get_resizing(self, *_args):
        return self._resize_animation is not None

    resizing = AliasProperty(_get_resizing, bind=["_resize_animation"])

    def _get_expand_state_hor(self, *_args):
        return self._expanded_horizontal

    expand_state_x = AliasProperty(_get_expand_state_hor, bind=[
        "_expanded_horizontal"
    ])

    def _get_expand_state_vert(self, *_args):
        return self._expanded_vertical

    expand_state_y = AliasProperty(_get_expand_state_vert, bind=[
        "_expanded_vertical"
    ])

    def _get_retract_state_hor(self, *_args):
        return not self._expanded_horizontal

    retract_state_x = AliasProperty(_get_retract_state_hor, bind=[
        "expand_state_x"
    ])

    def _get_retract_state_vert(self, *_args):
        return not self._expanded_vertical

    retract_state_y = AliasProperty(_get_retract_state_vert, bind=[
        "expand_state_y"
    ])

    def _get_fully_expanded_hor(self, *_args):
        if self.max_x_hint is not None:
            return self.size_hint_x == self.max_x_hint
        else:
            return self.width == self.max_x

    expanded_x = AliasProperty(_get_fully_expanded_hor, bind=[
        "size_hint_x",
        "width",
        "max_y_hint",
        "max_y",
        "expand_state_x"
    ])

    def _get_fully_retracted_hor(self, *_args):
        if self.min_x_hint is not None:
            return self.size_hint_x == self.min_x_hint
        else:
            return self.width == self.min_x

    retracted_x = AliasProperty(_get_fully_retracted_hor, bind=[
        "size_hint_x",
        "width",
        "min_x_hint",
        "min_x",
        "expand_state_x"
    ])

    def _get_fully_expanded_vert(self, *_args):
        if self.max_y_hint is not None:
            return self.size_hint_y == self.max_y_hint
        else:
            return self.height == self.max_y

    expanded_y = AliasProperty(_get_fully_expanded_vert, bind=[
        "size_hint_y",
        "height",
        "max_y_hint",
        "max_y",
        "expand_state_y"
    ])

    def _get_fully_retracted_vert(self, *_args):
        if self.min_y_hint is not None:
            return self.size_hint_y == self.min_y_hint
        else:
            return self.height == self.min_y

    retracted_y = AliasProperty(_get_fully_retracted_vert, bind=[
        "size_hint_y",
        "height",
        "min_y_hint",
        "min_y",
        "expand_state_y"
    ])

    def _get_expanding_horizontal(self, *_args):
        return self.expand_state_x and self.resizing

    expanding_x = AliasProperty(_get_expanding_horizontal, bind=[
        "expand_state_x",
        "resizing"
    ])

    def _get_expanding_vertical(self, *_args):
        return self.expand_state_y and self.resizing

    expanding_y = AliasProperty(_get_expanding_vertical, bind=[
        "expand_state_y",
        "resizing"
    ])

    def _get_retracting_horizontal(self, *_args):
        return self.retract_state_x and self.resizing

    retracting_x = AliasProperty(_get_retracting_horizontal, bind=[
        "retract_state_x",
        "resizing"
    ])

    def _get_retracting_vertical(self, *_args):
        return self.retract_state_y and self.resizing

    retracting_y = AliasProperty(_get_retracting_vertical, bind=[
        "retract_state_y",
        "resizing"
    ])

    custom_size_hint_resolver = ObjectProperty(None)
    custom_size_hint_animation = ObjectProperty(None)

    def __init__(self, **kwargs):
        attributes = [
            "allow_resize_x",
            "allow_resize_y",
            "custom_size_hint_animation",
            "custom_size_hint_resolver",
            "duration_expand_x",
            "duration_expand_y",
            "duration_resize",
            "duration_resize_x",
            "duration_resize_y",
            "duration_retract_x",
            "duration_retract_y",
            "expanding_x",
            "expanding_y",
            "fixed_duration_x",
            "fixed_duration_y",
            "max_y",
            "max_y_hint",
            "max_x",
            "max_x_hint",
            "expanded_x",
            "expanded_y",
            "retracted_x",
            "retracted_y",
            "expand_state_x",
            "expand_state_y",
            "retract_state_x",
            "retract_state_y",
            "min_y",
            "min_y_hint",
            "min_x",
            "min_x_hint",
            "resizing",
            "retracting_y",
            "start_expanded_x",
            "start_expanded_y"
        ]
        for attr in attributes:
            value = kwargs.pop(attr, None)
            if value is not None:
                setattr(self, attr, value)

        self.bind(min_x_hint=self._update_width)
        self.bind(max_x_hint=self._update_width)
        self.bind(min_x=self._update_width)
        self.bind(max_x=self._update_width)
        self.bind(expand_state_x=self._update_width)

        self.bind(min_y_hint=self._update_height)
        self.bind(max_y_hint=self._update_height)
        self.bind(min_x=self._update_height)
        self.bind(max_y=self._update_height)
        self.bind(expand_state_y=self._update_height)

        self.bind(expanded_x=self._clear_anim_data_horizontal)
        self.bind(expanded_y=self._clear_anim_data_vertical)
        self.bind(retracted_x=self._clear_anim_data_horizontal)
        self.bind(retracted_y=self._clear_anim_data_vertical)

        self.bind(on_kv_post=self._after_initialization)

        super(ExpandableMixin, self).__init__(**kwargs)

    def start_resize_animation(self, animation: Animation, anim_type: bool):
        if anim_type is HORIZONTAL:
            def on_start(*_args):
                self._timestamp_horizontal = time.perf_counter()

            def on_complete(*_args):
                self._timestamp_horizontal = None
                self._resize_animation = None
                self._update_width_and_height()
        else:
            def on_start(*_args):
                self._timestamp_vertical = time.perf_counter()

            def on_complete(*_args):
                self._timestamp_vertical = None
                self._resize_animation = None
                self._update_width_and_height()

        animation.bind(on_start=on_start, on_complete=on_complete)
        self._resize_animation = animation
        animation.start(self)

    def toggle_x(self, *_args):
        if not self.allow_resize_x:
            return

        if self._expanded_horizontal:
            if self.min_x_hint is not None:
                self._animate_width_hint(self.min_x_hint)
            elif self.min_x is not None:
                self._animate_width(self.min_x)
            else:
                raise ExpandableMixinError(
                    "allow_resize_x is True yet there is no min_x or min_x_hint"
                )
        else:
            if self.max_x_hint is not None:
                self._animate_width_hint(self.max_x_hint)
            elif self.max_x is not None:
                self._animate_width(self.max_x)
            else:
                raise ExpandableMixinError(
                    "allow_resize_x is True yet there is no max_x or max_x_hint"
                )
        self._expanded_horizontal = not self._expanded_horizontal

    def toggle_y(self, *_args):
        if not self.allow_resize_y:
            return

        if self._expanded_vertical:
            if self.min_y_hint is not None:
                self._animate_height_hint(self.min_y_hint)
            elif self.min_y is not None:
                self._animate_height(self.min_y)
            else:
                raise ExpandableMixinError(
                    "allow_resize_y is True yet there is no min_y or min_y_hint"
                )
        else:
            if self.max_y_hint is not None:
                self._animate_height_hint(self.max_y_hint)
            elif self.max_y is not None:
                self._animate_height(self.max_y)
            else:
                raise ExpandableMixinError(
                    "allow_resize_y is True yet there is no max_y or max_y_hint"
                )

        self._expanded_vertical = not self._expanded_vertical

    def expand_x(self, *_args):
        if not self._expanded_horizontal:
            self.toggle_x()

    def retract_x(self, *_args):
        if not self.retract_state_x:
            self.toggle_x()

    def expand_y(self, *_args):
        if not self._expanded_vertical:
            self.toggle_y()

    def retract_y(self, *_args):
        if not self.retract_state_y:
            self.toggle_y()

    def instant_expand_x(self, *_args):
        if not self.allow_resize_x:
            return

        Animation.cancel_all(self, "size_hint_x")
        Animation.cancel_all(self, "width")
        if self.max_x_hint is not None:
            self.size_hint_x = self.max_x_hint
        elif self.max_x is not None:
            self.width = self.max_x
        else:
            raise ExpandableMixinError(
                "allow_resize_x is True yet there is no max_x or max_x_hint"
            )
        self._expanded_horizontal = True

    def instant_retract_x(self, *_args):
        if not self.allow_resize_x:
            return

        Animation.cancel_all(self, "size_hint_x")
        Animation.cancel_all(self, "width")
        if self.min_x_hint is not None:
            self.size_hint_x = self.min_x_hint
        elif self.min_x is not None:
            self.width = self.min_x
        else:
            raise ExpandableMixinError(
                "allow_resize_x is True yet there is no min_x or min_x_hint"
            )
        self._expanded_horizontal = False

    def instant_expand_y(self, *_args):
        if not self.allow_resize_y:
            return

        Animation.cancel_all(self, "size_hint_y")
        Animation.cancel_all(self, "height")
        if self.max_y_hint is not None:
            self.size_hint_y = self.max_y_hint
        elif self.max_y is not None:
            self.height = self.max_y
        else:
            raise ExpandableMixinError(
                "allow_resize_y is True yet there is no max_y or max_y_hint"
            )
        self._expanded_vertical = True

    def instant_retract_y(self, *_args):
        if not self.allow_resize_y:
            return

        Animation.cancel_all(self, "size_hint_y")
        Animation.cancel_all(self, "height")
        if self.min_y_hint is not None:
            self.size_hint_y = self.min_y_hint
        elif self.min_y is not None:
            self.height = self.min_y
        else:
            raise ExpandableMixinError(
                "allow_resize_y is True yet there is no min_y or min_y_hint"
            )
        self._expanded_vertical = False

    def instant_toggle_x(self, *_args):
        if not self.allow_resize_x:
            return

        if self._expanded_horizontal:
            self.instant_retract_x()
        else:
            self.instant_expand_x()

    def instant_toggle_y(self, *_args):
        if not self.allow_resize_y:
            return

        if self._expanded_vertical:
            self.instant_retract_y()
        else:
            self.instant_expand_y()

    def _update_width(self, *_args):
        if not self._initialized:
            return

        if not self.allow_resize_x:
            return

        if self.resizing:
            return

        if not self._expanded_horizontal:
            if self.min_x_hint is not None:
                self.size_hint_x = self.min_x_hint
            elif self.min_x is not None:
                self.size_hint_x = None
                self.width = self.min_x
            else:
                raise ExpandableMixinError(
                    "allow_resize_x is True yet there is no min_x or min_x_hint"
                )
        else:
            if self.max_x_hint is not None:
                self.size_hint_x = self.max_x_hint
            elif self.max_x is not None:
                self.size_hint_x = None
                self.width = self.max_x
            else:
                raise ExpandableMixinError(
                    "allow_resize_x is True yet there is no max_x or max_x_hint"
                )

    def _update_height(self, *_args):
        if not self._initialized:
            return

        if not self.allow_resize_y:
            return

        if self.resizing:
            return

        if not self._expanded_vertical:
            if self.min_y_hint is not None:
                self.size_hint_y = self.min_y_hint
            elif self.min_y is not None:
                self.size_hint_y = None
                self.height = self.min_y
            else:
                raise ExpandableMixinError(
                    "allow_resize_y is True yet there is no min_y or min_y_hint"
                )
        else:
            if self.max_y_hint is not None:
                self.size_hint_y = self.max_y_hint
            elif self.max_y is not None:
                self.size_hint_y = None
                self.height = self.max_y
            else:
                raise ExpandableMixinError(
                    "allow_resize_y is True yet there is no max_y or max_y_hint"
                )

    def _update_width_and_height(self, *_args):
        self._update_width()
        self._update_height()

    def _after_initialization(self, *_args):
        """This method determines whether the widget should start expanded or
        retracted. If the user doesn't pick one, then it starts retracted by
        default.

        This method is meant to be bound to the "kv_post" event. Note that the
        "kv_post" event is fired after instantiating the class in Python or
        after the kvlang Builder has finished parsing the rules for that
        instance."""

        if self._initialized:
            return

        has_min_x = self.min_x is not None or self.min_x_hint is not None
        has_max_x = self.max_x is not None or self.max_x_hint is not None
        has_min_y = self.min_y is not None or self.min_y_hint is not None
        has_max_y = self.max_y is not None or self.max_y_hint is not None

        if has_min_x and has_max_x:
            self.allow_resize_x = True
        if has_min_y and has_max_y:
            self.allow_resize_y = True

        if self.allow_resize_x:
            if not has_min_x:
                raise ExpandableMixinError(
                    "allow_resize_x is True yet there is no min_x or min_x_hint"
                )

            if not has_max_x:
                raise ExpandableMixinError(
                    "allow_resize_x is True yet there is no max_x or max_x_hint"
                )

            if self.start_expanded_x:
                if self.max_x_hint is not None:
                    self.size_hint_x = self.max_x_hint
                else:
                    self.width = self.max_x
                self._expanded_horizontal = True
            else:
                if self.min_x_hint is not None:
                    self.size_hint_x = self.min_x_hint
                elif self.min_x is not None:
                    self.width = self.min_x
                self._expanded_horizontal = False

        if self.allow_resize_y:
            if not has_min_y:
                raise ExpandableMixinError(
                    "allow_resize_y is True yet there is no min_y or min_y_hint"
                )

            if not has_max_y:
                raise ExpandableMixinError(
                    "allow_resize_y is True yet there is no max_y or max_y_hint"
                )

            if self.start_expanded_y:
                if self.max_y_hint is not None:
                    self.size_hint_y = self.max_y_hint
                else:
                    self.height = self.max_y
                self._expanded_vertical = True
            else:
                if self.min_y_hint is not None:
                    self.size_hint_y = self.min_y_hint
                else:
                    self.height = self.min_y
                self._expanded_vertical = False

        self._initialized = True
        self._update_width_and_height()

    def _clear_anim_data_horizontal(self, _instance, finished_animating):
        if finished_animating:
            self._percent_expanded_horizontal = None
            self._prev_duration_horizontal = None

    def _clear_anim_data_vertical(self, _instance, finished_animating):
        if finished_animating:
            self._percent_expanded_vertical = None
            self._prev_duration_vertical = None

    def _resolve_parent(self, *_args):
        if self.parent is not None:
            return

        def find_self(event_dispatcher):
            for child in event_dispatcher.children:
                if self is child:
                    self.parent = event_dispatcher
                    return
                find_self(child)

        find_self(Window)

    def _handle_child_of_stack_layout(self, *_args):
        """
        Returns a dictionary containing information about the StackLayout
        containing this widget. Should only be called if self is actually a
        child of a StackLayout.

        If the StackLayout orientation begins with "tb" or "bt", then the
        returned dictionary will contain two keys: "cols" and "col_of_self".
        "col" maps to another dictionary which maps (0-indexed) column numbers
        (integers) to a list of widgets; i.e., col[0] is the list of children of
        StackLayout in the first column populated by the StackLayout.
        "col_of_self" is the zero-indexed column number containing self.

        If the StackLayout orientation begins with "rl" or "lr", then the
        returned dictionary contains the keys "rows" and "row_of_self". "rows"
        maps integers to lists of widgets, i.e. row[2] is the children of the
        StackLayout located in the third row populated by that StackLayout.
        "row_of_self" is an integer representing the row containing self.

        :return: Dictionary containing information about what columns/rows the
        children of StackLayout are mapped to.
        """
        parent = self.parent
        if not isinstance(parent, StackLayout):
            Logger.warning(
                "Ran handle_child_of_stack_layout when self not in StackLayout!"
            )
            return {}

        prefix = parent.orientation[:2]
        padding_hor = parent.padding[0] + parent.padding[2]
        padding_vert = parent.padding[1] + parent.padding[3]
        if prefix is "tb" or prefix is "bt":
            cols = {0: []}
            col_of_self = None
            current = 0
            spacing = parent.spacing[1]
            for child in reversed(parent.children):
                # should only happen on first pass
                if len(cols[current]) == 0:
                    cols[current].append(child)
                    continue

                # calculate height of column if child were added to it
                spacing_vert = spacing * len(cols[current])
                allotted_height = parent.height - padding_vert - spacing_vert
                total_height = 0
                for widget in cols[current] + [child]:
                    if widget.size_hint_y is None:
                        total_height += widget.height
                    else:
                        total_height += widget.size_hint_y / allotted_height

                if total_height <= allotted_height:
                    # place child in current column
                    cols[current].append(child)
                    if child is self:
                        col_of_self = current
                else:
                    # add child to next column, unless current has nothing
                    if len(cols[current]) == 0:
                        cols[current].append(child)
                        if child is self:
                            col_of_self = current
                    else:
                        cols[current + 1] = [child]
                        if child is self:
                            col_of_self = current + 1
                    current += 1

            return {
                "col_of_self": col_of_self,
                "cols": cols
            }
        else:
            rows = {0: []}
            row_of_self = None
            current = 0
            spacing = parent.spacing[0]
            for child in reversed(parent.children):
                # should only happen on first pass
                if len(rows[current]) == 0:
                    rows[current].append(child)
                    continue

                # calculate width of row if child were added to it
                spacing_hor = spacing * len(rows[current])
                total_width = 0
                allotted_width = parent.width - padding_hor - spacing_hor
                for widget in rows[current] + [child]:
                    if widget.size_hint_x is None:
                        total_width += widget.width
                    else:
                        total_width += widget.size_hint_x / allotted_width

                if total_width <= allotted_width:
                    # place child in current row
                    rows[current].append(child)
                    if child is self:
                        row_of_self = current
                else:
                    # add child to next row, unless current has nothing
                    if len(rows[current]) == 0:
                        rows[current].append(child)
                        if child is self:
                            row_of_self = current
                    else:
                        rows[current + 1] = [child]
                        if child is self:
                            row_of_self = current + 1
                    current += 1
            return {
                "row_of_self": row_of_self,
                "rows": rows
            }

    def _handle_child_of_grid_layout(self, *_args):
        """Returns a dictionary containing the children in each row and column
        of the grid. For example, call the dictionary "result". Then
        result["cols"] is itself a dictionary where result["cols"][0] is a list
        of all widgets in the 0th column of the GridLayout. NOTE THAT THE ORDER
        OF WIDGETS IN THE LIST IS ARBITRARY. Analogously, result["rows"][3] is
        an arbitrarily-ordered list of widgets in the fourth row of the
        GridLayout.

        If the parent of this widget is not a GridLayout, then result["rows"]
        and result["cols"] are empty dictionaries.

        There are also keys "row_of_self" and "col_of_self" that return the row
        and column number containing this widget."""
        parent = self.parent
        _row = "rows"
        _col = "cols"
        result = {_row: {}, _col: {}}
        if not isinstance(parent, GridLayout):
            Logger.warning(
                "Ran handle_child_of_grid_layout when self not in GridLayout!"
            )
            return result

        prefix = parent.orientation[:2]
        orientation = parent.orientation

        rows = parent.rows
        cols = parent.cols
        num_children = len(parent.children)
        if rows is None and cols is None:
            return result
        elif rows is None:
            rows = ceil(num_children / cols)
        elif cols is None:
            cols = ceil(num_children / rows)
        elif rows * cols != num_children:
            if prefix is "tb" or prefix is "bt":
                cols = ceil(num_children / rows)
            else:
                rows = ceil(num_children / cols)

        result[_row][0] = result[_row][rows - 1] = []
        result[_col][0] = result[_col][cols - 1] = []

        def add_child(_child, _row_num, _col_num):
            result[_row][_row_num].append(_child)
            result[_col][_col_num].append(_child)
            if child is self:
                result["row_of_self"] = _row_num
                result["col_of_self"] = _col_num

        if orientation is "lr-tb":
            row_num = col_num = 0
            for child in reversed(parent.children):
                add_child(child, row_num, col_num)
                col_num += 1
                if col_num == cols:
                    row_num += 1
                    col_num = 0
        elif orientation is "lr-bt":
            row_num = rows - 1
            col_num = 0
            for child in reversed(parent.children):
                add_child(child, row_num, col_num)
                col_num += 1
                if col_num == cols:
                    row_num -= 1
                    col_num = 0
        elif orientation is "rl-tb":
            row_num = 0
            col_num = cols - 1
            for child in reversed(parent.children):
                add_child(child, row_num, col_num)
                col_num -= 1
                if col_num < 0:
                    row_num += 1
                    col_num = cols - 1
        elif orientation is "rl-bt":
            row_num = rows - 1
            col_num = cols - 1
            for child in reversed(parent.children):
                add_child(child, row_num, col_num)
                col_num -= 1
                if col_num < 0:
                    row_num -= 1
                    col_num = cols - 1
        elif orientation is "tb-lr":
            row_num = col_num = 0
            for child in reversed(parent.children):
                add_child(child, row_num, col_num)
                row_num += 1
                if row_num == rows:
                    row_num = 0
                    col_num += 1
        elif orientation is "tb-rl":
            row_num = 0
            col_num = cols - 1
            for child in reversed(parent.children):
                add_child(child, row_num, col_num)
                row_num += 1
                if row_num == rows:
                    row_num = 0
                    col_num -= 1
        elif orientation is "bt-lr":
            row_num = rows - 1
            col_num = 0
            for child in reversed(parent.children):
                add_child(child, row_num, col_num)
                row_num -= 1
                if row_num < 0:
                    row_num = rows - 1
                    col_num += 1
        elif orientation is "bt-rl":
            row_num = rows - 1
            col_num = cols - 1
            for child in reversed(parent.children):
                add_child(child, row_num, col_num)
                row_num -= 1
                if row_num < 0:
                    row_num = rows - 1
                    col_num -= 1

        return result

    def _resolve_size_hint_x(self, *_args):
        """
        If the size_hint_x is currently None, we cannot animate on size_hint.
        Thus, find what value of size_hint_x would lead to the current width,
        if possible.

        This is much more nuanced than it sounds.

        First of all, we may be the child of a widget that does not honor size
        hints at all. In that case, just return the default value of
        size_hint_x. Also log a warning to the user.

        If our parent does honor size hints, then we need to understand how that
        parent handles size hints. Different Layouts have different approaches
        to interpreting size hints. We need to account for every possibility.

        This method has not been tested with a RecycleBoxLayout or a
        RecycleGridLayout. However, the logic used in this method for BoxLayouts
        and GridLayouts will be used for RecycleBoxLayouts and
        RecycleGridLayouts, respectively.

        If you have your own widgets which listen to the size_hints of their
        children, or you have a subclass of one of the default Layout classes
        which overrides the do_layout logic, then you can add custom behavior to
        properly resolve for that widget by assigning a callback to the
        custom_size_hint_resolver attribute. The custom_size_hint_resolver
        callback will be given the argument "x" or "y" corresponding to the type
        of size_hint being resolved. If the callback returns any non-None value,
        then the default behavior of this method will be ignored.

        :return: By default, this method returns a boolean. It returns True if
        self is child of a GridLayout with at least one of the attributes
        "rows" or "cols" set to a non-None value. False otherwise. But if the
        user assigns a callback to custom_size_hint_resolver, this method will
        return the response of self.custom_size_hint_resolver if the return
        value is not None; if self.custom_size_hint_resolver returns None, then
        the default behavior of this method is performed.
        """
        if self.size_hint_x is not None:
            return DO_DEFAULT_ANIM

        if self.custom_size_hint_resolver is not None:
            custom_result = self.custom_size_hint_resolver(self, "x")
            if custom_result is not None:
                return custom_result

        self._resolve_parent()
        parent = self.parent
        padding_hor = parent.padding[0] + parent.padding[2]

        if parent is None:
            Logger.warning("Widget is detached from widget tree!")
            self.size_hint_x = 1
            return DO_DEFAULT_ANIM

        if (
                isinstance(parent, WindowBase) or
                isinstance(parent, FloatLayout) or
                isinstance(parent, RelativeLayout)
        ):
            """Please see corresponding docstring in _resolve_size_hint_y."""
            self.size_hint_x = self.width / parent.width
            return DO_DEFAULT_ANIM

        if isinstance(parent, AnchorLayout):
            """Please see corresponding docstring in _resolve_size_hint_y."""
            allotted_width = parent.width - padding_hor
            if allotted_width <= 0:
                self.size_hint_x = 1
            else:
                self.size_hint_x = self.width / allotted_width
            return DO_DEFAULT_ANIM

        if isinstance(parent, BoxLayout):
            """Please see corresponding docstring in _resolve_size_hint_y."""
            num_siblings = len(parent.children) - 1
            if parent.orientation is "vertical":
                allotted_width = parent.width - padding_hor
                self.size_hint_x = self.width / allotted_width
            else:
                sum_fixed_widths = 0.
                sum_hint_x = 0.
                for child in parent.children:
                    if child.size_hint_x is None:
                        sum_fixed_widths += child.width
                    else:
                        sum_hint_x += child.size_hint_x
                if sum_hint_x == 0:
                    return DO_SPECIAL_ANIM
                spacing_hor = (len(parent.children) - 1) * parent.spacing
                allotted_width = (
                        parent.width - padding_hor -
                        spacing_hor - sum_fixed_widths
                )
                allotted_width = max(0, allotted_width)
                if allotted_width == 0:
                    self.size_hint_x = 1
                else:
                    self.size_hint_x = sum_hint_x * self.width / allotted_width
            return DO_DEFAULT_ANIM

        if isinstance(parent, StackLayout):
            """Please see corresponding docstring in _resolve_size_hint_y."""
            result = self._handle_child_of_stack_layout()
            if "rows" in result:
                row_of_self = result["rows_of_self"]
                rows = result["rows"]
                spacing_hor = (len(rows[row_of_self]) - 1) * parent.spacing[0]
                allotted_width = parent.width - padding_hor - spacing_hor
            else:
                allotted_width = parent.width - padding_hor
            self.size_hint_y = self.height / allotted_width
            return DO_DEFAULT_ANIM

        if isinstance(parent, GridLayout):
            """Please see corresponding docstring in _resolve_size_hint_y."""
            if parent.rows is None and parent.cols is None:
                self.size_hint_y = 1
                return DO_DEFAULT_ANIM
            else:
                return DO_SPECIAL_ANIM

        Logger.warning(
            "Assigned size_hint, but parent does not listen to size_hint!"
        )
        self.size_hint_y = True
        return DO_DEFAULT_ANIM

    def _get_expand_anim_hor_duration(self, *_args):
        if self.duration_expand_x:
            return self.duration_expand_x
        elif self.duration_resize_x:
            return self.duration_resize_x
        else:
            return self.duration_resize

    def _get_retract_anim_hor_duration(self, *_args):
        if self.duration_retract_x:
            return self.duration_retract_x
        elif self.duration_resize_x:
            return self.duration_resize_x
        else:
            return self.duration_resize

    def _get_horizontal_animation_duration(self):
        was_expanding = will_retract = self._expanded_horizontal
        if will_retract:
            duration = self._get_retract_anim_hor_duration()
        else:
            duration = self._get_expand_anim_hor_duration()

        if self.fixed_duration_x:
            return duration

        # if we are starting an animation in the middle of an expansion or
        # retraction
        if self._timestamp_horizontal is not None:

            # how much of the expansion/retraction was achieved?
            if will_retract:
                total_duration = self._get_expand_anim_hor_duration()
            else:
                total_duration = self._get_retract_anim_hor_duration()
            time_passed = time.perf_counter() - self._timestamp_horizontal
            percent = min(1, time_passed / total_duration)

            # initialize percent expanded if necessary
            if self._percent_expanded_horizontal is None:
                if was_expanding:
                    self._percent_expanded_horizontal = percent
                else:
                    self._percent_expanded_horizontal = 1 - percent
            else:
                if was_expanding:
                    self._percent_expanded_horizontal += percent
                else:
                    self._percent_expanded_horizontal -= percent

            if will_retract:
                duration = self._percent_expanded_horizontal * duration
            else:
                duration = (1 - self._percent_expanded_horizontal) * duration
            self._prev_duration_horizontal = duration

        return duration

    def _get_horizontal_animation_transition(self):
        will_expand = not self._expanded_horizontal
        if will_expand:
            if self.transition_expand_x:
                return self.transition_expand_x
            elif self.transition_resize_x:
                return self.transition_resize_x
            else:
                return self.transition_resize
        else:
            if self.transition_retract_x:
                return self.transition_retract_x
            elif self.transition_resize_x:
                return self.transition_resize_x
            else:
                return self.transition_resize

    def _animate_width_hint_special_case(self, x_hint, transition, duration):
        if not self.allow_resize_x:
            return

        if self.custom_size_hint_animation is not None:
            result = self.custom_size_hint_animation(
                self,
                "x",
                x_hint,
                transition,
                duration
            )
            if result is not None:
                return

        parent = self.parent

        if isinstance(parent, BoxLayout):
            Animation.cancel_all(self, "width")
            Animation.cancel_all(self, "size_hint_x")
            self.size_hint_x = None

            sum_widths = 0.
            for child in parent.children:
                if child.size_hint_x is None and child is not self:
                    sum_widths += child.width

            padding_hor = parent.padding[0] + parent.padding[2]
            spacing_hor = parent.spacing * (len(parent.children) - 1)
            padding_and_spacing = padding_hor + spacing_hor
            full_width = parent.width - padding_and_spacing - sum_widths
            full_width = max(0, full_width)

            anim = Animation(width=full_width, t=transition, d=duration)
            self.start_resize_animation(anim, HORIZONTAL)

        if isinstance(parent, GridLayout):
            result = self._handle_child_of_grid_layout()

            col_of_self = result["col_of_self"]

            if parent.col_force_default:
                if col_of_self in parent.cols_minimum:
                    full_width = parent.cols_minimum[col_of_self]
                else:
                    full_width = parent.col_default_width

                anim = Animation(width=full_width, t=transition, d=duration)
                self.start_resize_animation(anim, HORIZONTAL)
                return

            # we will override this attribute, but we will need to set it back
            # to this value after we're done
            temp = parent.cols_minimum

            # calculate the width of the slot for each column. This requires
            # calculating the minimum width for each column AND the fraction of
            # allotted width provided up to each column

            # mins[n] is the minimum width of column n
            mins = {}
            # max_size_hints[n] is the largest size_hint_x found in column n
            max_size_hints = {}

            col_default_width = parent.col_default_width

            cols = result["cols"]
            num_cols = len(cols.keys())

            # loop through every child in column. Determine the minimum width of
            # the column, as well as the largest size_hint_x in that column.
            for col_num in cols.keys():

                minimum_from_dict = None
                if col_num in parent.cols_minimum:
                    minimum_from_dict = parent.cols_minimum[col_num]

                minimum_from_children = None
                max_size_hint = None
                for child in cols[col_num]:
                    if child.size_hint_x is None:
                        # find a value for minimum_from_children
                        if minimum_from_children is None:
                            minimum_from_children = child.width
                        else:
                            minimum_from_children = max(
                                minimum_from_children,
                                child.width
                            )
                    else:
                        # find the largest size_hint_x in the column
                        if max_size_hint is None:
                            max_size_hint = child.size_hint_x
                        else:
                            max_size_hint = max(
                                max_size_hint,
                                child.size_hint_x
                            )

                min_width = col_default_width

                if minimum_from_dict is not None:
                    min_width = max(min_width, minimum_from_dict)

                if minimum_from_children is not None:
                    min_width = max(min_width, minimum_from_children)

                # the minimum width for col_num is...
                mins[col_num] = min_width
                # the maximum size_hint for col_num is...
                if max_size_hint is not None:
                    max_size_hints[col_num] = max_size_hint

            spacing = (num_cols - 1) * parent.spacing[0]
            padding = parent.padding[0] + parent.padding[2]
            allotted_width = parent.width - spacing - padding
            allotted_width -= sum(mins.values())

            # create a cols_minimum dictionary that represents the widths of
            # each column currently. Then make another one that represents the
            # widths of each column after expandable widget gets a new size hint
            widths_before = {}
            widths_after = {}
            dicts = [widths_before, widths_after]
            for dictionary in dicts:
                sum_size_hint = sum(max_size_hints.values())
                for column in cols.keys():
                    width = mins[column]

                    if sum_size_hint > 0:
                        ratio = max_size_hints[column] / sum_size_hint
                        width += ratio * allotted_width

                    dictionary[column] = width
                max_size_hints[col_of_self] = x_hint

            # set col_force_default to True
            parent.col_force_default = True
            parent.cols_minimum = widths_before

            # bind parent.rows_minimum to parent._trigger_layout
            parent.bind(cols_minimum=parent._trigger_layout)  # noqa

            # create animations
            anim1 = Animation(
                cols_minimum=widths_after,
                t=transition,
                d=duration
            )
            anim2 = Animation(
                width=widths_after[col_of_self],
                t=transition,
                d=duration
            )

            # unbind parent._trigger_layout, set parent.cols_minimum back to its
            # original value
            def on_complete(*_args):
                parent.unbind(cols_minimum=parent._trigger_layout)  # noqa
                parent.cols_minimum = temp
            anim1.bind(on_complete=on_complete)

            # animate self and cols_minimum to new value
            self.start_resize_animation(anim2, HORIZONTAL)
            anim1.start(parent)

    def _animate_width_hint(self, x_hint, *_args):
        if not self.allow_resize_x:
            return

        if x_hint not in [self.min_x_hint, self.max_x_hint]:
            raise ExpandableMixinError(
                f"Attempted to set invalid size_hint_x: {x_hint}; value must be"
                f" either {self.min_x_hint} or {self.max_x_hint}"
            )

        Animation.cancel_all(self, "size_hint_x")
        Animation.cancel_all(self, "width")

        transition = self._get_horizontal_animation_transition()
        duration = self._get_horizontal_animation_duration()

        use_special_animation = self._resolve_size_hint_x()

        if use_special_animation:
            self._animate_width_hint_special_case(
                x_hint,
                transition,
                duration
            )
            return

        if self.size_hint_x != x_hint:
            self.start_resize_animation(Animation(
                size_hint_x=x_hint,
                t=transition,
                d=duration
            ), HORIZONTAL)

    def _resolve_size_hint_y(self, *_args):
        """
        If the size_hint_y is currently None, we cannot animate on size_hint.
        Thus, find what value of size_hint_y would lead to the current height,
        if possible, and set this widget's size_hint_y to that value.

        This is much more nuanced than it sounds.

        First of all, we may be the child of a widget that does not honor size
        hints at all. In that case, just return the default value of
        size_hint_y. Also log a warning to the user.

        If our parent does honor size hints, then we need to understand how that
        parent handles size hints. Different Layouts have different approaches
        to interpreting size hints. Great effort has been expended to account
        for every edge case.

        Some widgets will "snap" to a height after being assigned a size_hint_y,
        meaning a smooth animation will not be possible. In that case, this
        method will return True. When this method returns True, a special method
        is called during the animation process in the internals of this widget.
        It performs dark magic under-the-hood to ensure a smooth animation.

        This method has not been tested with a RecycleBoxLayout or a
        RecycleGridLayout. However, the logic used in this method for BoxLayouts
        and GridLayouts will be used for RecycleBoxLayouts and
        RecycleGridLayouts, respectively.

        If you have your own widgets which listen to the size_hints of their
        children, or you have a subclass of one of the default Layout classes
        which overrides the do_layout logic, then you can add custom behavior to
        properly resolve for that widget by assigning a callback to the
        custom_size_hint_resolver attribute.

        :return: By default, this method returns a boolean. It returns True if
        we need a special behavior to perform a smooth animation. This method
        returns False otherwise. But if the user assigns a callback to
        custom_size_hint_resolver, this method will return the response of
        self.custom_size_hint_resolver if the return value is not None.
        """
        if self.custom_size_hint_resolver is not None:
            custom_result = self.custom_size_hint_resolver(self, "y")
            if custom_result is not None:
                return custom_result

        self._resolve_parent()
        parent = self.parent
        padding_vert = parent.padding[1] + parent.padding[3]

        if parent is None:
            Logger.warning("Widget is detached from widget tree!")
            self.size_hint_y = 1
            return DO_DEFAULT_ANIM

        if (
                isinstance(parent, WindowBase) or
                isinstance(parent, FloatLayout) or
                isinstance(parent, RelativeLayout)
        ):
            """Window, FloatLayout, RelativeLayout:
            The size_hint represents a percentage of the size of the containing
            Layout. For example, size_hint_y=0.5 would make the child widget
            have half the height of the containing Layout."""
            self.size_hint_y = self.height / parent.height
            return DO_DEFAULT_ANIM

        if isinstance(parent, AnchorLayout):
            """ AnchorLayout:
            The size_hint_y is the percentage of the allotted height awarded to
            the widget. The allotted height is the AnchorLayout height minus the
            height of the vertical padding (padding-top and padding-bottom, i.e.
            padding[1] and padding[3]). Every child has the same allotted
            height."""
            allotted_height = parent.height - padding_vert
            if allotted_height <= 0:
                self.size_hint_y = 1
            else:
                self.size_hint_y = self.height / allotted_height
            return DO_DEFAULT_ANIM

        if isinstance(parent, BoxLayout):
            """BoxLayout:
            If orientation is "horizontal":
                size_hint_y is the percent height of the allotted height, which 
                is the BoxLayout height minus the vertical padding.
            If orientation is "vertical":
                The allotted height is the height of the BoxLayout minus the
                height of every widget with a size_hint of None, the spacing
                between each child ((len(children) - 1) * spacing), and the
                vertical and horizontal padding. Every child with a non-None
                size_hint_y gets some ratio of the allotted height. This ratio 
                is that widget's size_hint_y over the sum of every non-None 
                size_hint_y."""
            num_siblings = len(parent.children) - 1
            if parent.orientation is "horizontal":
                allotted_height = parent.height - padding_vert
                self.size_hint_y = self.height / allotted_height
            else:
                sum_fixed_heights = 0.
                sum_hint_y = 0.
                for child in parent.children:
                    if child.size_hint_y is None:
                        sum_fixed_heights += child.height
                    else:
                        sum_hint_y += child.size_hint_y
                if sum_hint_y == 0:
                    """If we are the only child of a vertically-oriented 
                    BoxLayout, any size_hint_y will cause us to fill the entire 
                    allotted space. Resolving the size_hint_y does not allow, 
                    then, for a smooth animation, hence we return True to 
                    perform dark magic."""
                    return DO_SPECIAL_ANIM
                spacing_vert = (len(parent.children) - 1) * parent.spacing
                allotted_height = (
                        parent.height - padding_vert -
                        spacing_vert - sum_fixed_heights
                )
                allotted_height = max(0, allotted_height)
                if allotted_height == 0:
                    self.size_hint_y = 1
                else:
                    height = self.height
                    self.size_hint_y = sum_hint_y * height / allotted_height
            return DO_DEFAULT_ANIM

        if isinstance(parent, StackLayout):
            """StackLayout:
            The size_hint_y is a percentage of allotted height awarded to the
            widget. However, how allotted height is calculated depends on
            orientation:
            If the orientation starts with "tb" or "bt":
                Allotted height can be different for each column. For column n,
                allotted height is GridLayout height minus vertical padding
                minus (vertical spacing * ((# of rows in column n) - 1)).

                Converting height to size_hint_y, therefore, requires knowing
                the number of rows in that column. The most straightforward way
                to calculate this is to iterate over the children list of the
                StackLayout and determine the rows in each column ourselves. The
                tricky part is that a StackLayout will add a widget to a row if
                it can. But adding a new widget reduces the height of all
                previous widgets in that row that have size_hint_y's since
                adding an extra widget adds more vertical spacing and therefore
                reduces the allotted height for that column.
            If the orientation starts with "rl" or "lr":
                The allotted height doesn't care about the spacing between rows.
                It is just GridLayout height minus vertical padding."""
            result = self._handle_child_of_stack_layout()
            if "rows" in result:
                allotted_height = parent.height - padding_vert
            else:
                col_of_self = result["cols_of_self"]
                cols = result["cols"]
                spacing_vert = (len(cols[col_of_self]) - 1) * parent.spacing[1]
                allotted_height = parent.height - padding_vert - spacing_vert
            self.size_hint_y = self.height / allotted_height
            return DO_DEFAULT_ANIM

        if isinstance(parent, GridLayout):
            """GridLayout:
            If rows is None and cols is None:
                The Layout does not manage the position and size of any child.
                Whatever is assigned to pos and size of the child is that
                child's pos and size. size_hint_y has no effect.
            If row_force_default is True:
                The height of the widget is the height of its slot if it has a
                non-None size_hint_y (the slot height of row n is given by
                rows_minimum[n], or by row_height_default if n is not in the
                dictionary). If the size_hint_y is None, the widget's height is
                whatever value is assigned to the height attribute.
            If row_force_default is False:
                A non-None size_hint_y means that the widget height will be
                exactly that of the slot. A None size_hint_y means that the
                height of the widget will be whatever is assigned to the height
                attribute of the widget.
                So, how is the slot height calculated? The slot height is the
                sum of the minimum height for that row and some fraction of the
                allotted height for rows.

                Minimum height:
                    Look for any widgets in row n with a None size_hint_y, and
                    find the maximum height of all widgets in that row with a
                    None size_hint_y.

                    Then, for row n, look for the value of n mapped by
                    rows_minimum. If n is even a key in the dictionary, that is.

                    Then look at the value of row_default_height.

                    Whatever is largest of these values is the minimum height
                    for that row.
                Allotted height:
                    The allotted height is the height of the GridLayout minus
                    the minimum height of each row, minus the vertical padding,
                    minus the vertical spacing (spacing[1] * (len(children)-1)).

                    If the allotted height is negative, just make it zero.

                    Then, for each row n, calculate the maximum non-None
                    size_hint_y for every widget in that row.

                    Sum the maximum size_hint_y in each row for every row that
                    has at least one widget with a non-None size_hint_y.

                    Each row with a maximum non-None size_hint_y gets an
                    additional max_size_hint_y/sum_size_hint_y * allotted_height
                    added to its minimum height. That is the height of every
                    slot in that row.

                    If the allotted height is zero or there are no children with
                    a non-None size_hint_y, then the minimum height for the row
                    is the slot height for the row.
            We return True from this method if we need special logic to animate
            from a non-None to a None size_hint_y in a smooth manner. This case
            will happen for most cases that we are in a GridLayout widget, since
            a child of a GridLayout will instantaneously "snap" to fill its slot
            once we set the size_hint_y to some value."""
            if parent.rows is None and parent.cols is None:
                self.size_hint_y = 1
                return DO_DEFAULT_ANIM
            else:
                return DO_SPECIAL_ANIM

        Logger.warning(
            "Assigned size_hint, but parent does not listen to size_hint!"
        )
        self.size_hint_y = True
        return DO_DEFAULT_ANIM

    def _get_expand_anim_vert_duration(self, *_args):
        if self.duration_expand_y:
            return self.duration_expand_y
        elif self.duration_resize_y:
            return self.duration_resize_y
        else:
            return self.duration_resize

    def _get_retract_anim_vert_duration(self, *_args):
        if self.duration_retract_y:
            return self.duration_retract_y
        elif self.duration_resize_y:
            return self.duration_resize_y
        else:
            return self.duration_resize

    def _get_vertical_animation_duration(self):
        was_expanding = will_retract = self._expanded_vertical
        if will_retract:
            duration = self._get_retract_anim_vert_duration()
        else:
            duration = self._get_expand_anim_vert_duration()

        if self.fixed_duration_y:
            return duration

        # if we are starting an animation in the middle of an expansion or
        # retraction
        if self._timestamp_vertical is not None:

            # how much of the expansion/retraction was achieved?
            if will_retract:
                total_duration = self._get_expand_anim_vert_duration()
            else:
                total_duration = self._get_retract_anim_vert_duration()
            time_passed = time.perf_counter() - self._timestamp_vertical
            percent = min(1, time_passed / total_duration)

            # initialize percent expanded if necessary
            if self._percent_expanded_vertical is None:
                if will_retract:
                    self._percent_expanded_vertical = percent
                else:
                    self._percent_expanded_vertical = 1 - percent
            else:
                if was_expanding:
                    self._percent_expanded_vertical += percent
                else:
                    self._percent_expanded_vertical -= percent

            if will_retract:
                duration = self._percent_expanded_vertical * duration
            else:
                duration = (1 - self._percent_expanded_vertical) * duration
            self._prev_duration_vertical = duration

        return duration

    def _get_vertical_animation_transition(self):
        will_expand = not self._expanded_vertical
        if will_expand:
            if self.transition_expand_y:
                return self.transition_expand_y
            elif self.transition_resize_y:
                return self.transition_resize_y
            else:
                return self.transition_resize
        else:
            if self.transition_retract_y:
                return self.transition_retract_y
            elif self.transition_resize_y:
                return self.transition_resize_y
            else:
                return self.transition_resize

    def _animate_height_hint_special_case(self, y_hint, transition, duration):
        """
        Notice that we have an issue for a child of a GridLayout if we
        animate from a min_x to a max_x_hint (or a max_x to a
        min_x_hint). As soon as we add a size_hint, the widget will
        instantaneously fill its slot, ruining what is supposed to be a
        smooth animation. Therefore, if we are animating a GridLayout that
        is "switching" from a None size_hint_y to a non-None size_hint_y,
        we have to cheat.

        Save the current rows_minimum of the GridLayout to some temporary
        variable and then make a new rows_minimum that maps each row to its
        current slot height. Then set force_row_default to True.

        Calculate what the new height of each row will be after we set the
        widget size_hint_y. Make a second rows_minimum dict and animate to it.
        Note that GridLayouts don't, by default, bind their layout logic to the
        rows_minimum property (this is likely a bug that should be fixed, make
        an MR to the kivy source code), so bind rows_minimum to the private
        method _trigger_layout.

        Once this animation is complete, set the size_hint_y to
        min/max_y_hint. Also unbind _trigger_layout.
        """
        if not self.allow_resize_y:
            return

        if self.custom_size_hint_animation is not None:
            result = self.custom_size_hint_animation(
                self,
                "y",
                y_hint,
                transition,
                duration
            )
            if result is not None:
                return

        if isinstance(self.parent, BoxLayout):
            Animation.cancel_all(self, "height")
            self.size_hint_y = None

            sum_heights = 0.
            for child in self.parent.children:
                if child.size_hint_y is None and child is not self:
                    sum_heights += child.height

            padding_vert = self.parent.padding[1] + self.parent.padding[3]
            spacing_vert = self.parent.spacing * (len(self.parent.children) - 1)
            padding_and_spacing = padding_vert + spacing_vert
            height = self.parent.height - padding_and_spacing - sum_heights
            height = max(0, height)

            duration = self._get_vertical_animation_duration()
            transition = self._get_vertical_animation_transition()
            anim = Animation(height=height, t=transition, d=duration)
            self.start_resize_animation(anim, VERTICAL)

    def _animate_height_hint(self, y_hint, *_args):
        if not self.allow_resize_y:
            return

        if y_hint not in [self.min_y_hint, self.max_y_hint]:
            raise ExpandableMixinError(
                f"Attempted to set invalid size_hint_y: {y_hint}; value must be"
                + f"{self.min_y_hint} or {self.max_y_hint}"
            )

        Animation.cancel_all(self, "height")
        Animation.cancel_all(self, "size_hint_y")

        transition = self._get_vertical_animation_transition()
        duration = self._get_vertical_animation_duration()

        use_special_animation = self._resolve_size_hint_y()
        if use_special_animation:
            self._animate_height_hint_special_case(
                y_hint,
                transition,
                duration
            )
            return

        if self.size_hint_y != y_hint:
            self.start_resize_animation(Animation(
                size_hint_y=y_hint,
                t=transition,
                d=duration
            ), VERTICAL)

    def _animate_width(self, new_width, *_args):
        if not self.allow_resize_x:
            return

        if new_width not in [self.min_x, self.max_x]:
            raise ExpandableMixinError(
                f"Attempted to set invalid width: {new_width}" +
                f"; value must be {self.min_x} or {self.max_x}"
            )

        Animation.cancel_all(self, "size_hint_x")
        Animation.cancel_all(self, "width")
        self.size_hint_x = None

        transition = self._get_horizontal_animation_transition()
        duration = self._get_horizontal_animation_duration()

        self.start_resize_animation(Animation(
            width=new_width,
            t=transition,
            d=duration
        ), HORIZONTAL)

    def _animate_height(self, new_height, *_args):
        if not self.allow_resize_y:
            return

        if new_height not in [self.min_y, self.max_y]:
            raise ExpandableMixinError(
                f"Attempted to set invalid height: {new_height}" +
                f"; value must be {self.min_y} or {self.max_y}"
            )

        Animation.cancel_all(self, "size_hint_y")
        Animation.cancel_all(self, "height")
        self.size_hint_y = None

        transition = self._get_vertical_animation_transition()
        duration = self._get_vertical_animation_duration()

        self.start_resize_animation(Animation(
            height=new_height,
            t=transition,
            d=duration
        ), VERTICAL)
