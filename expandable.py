import time
from math import ceil

from kivy import Logger
from kivy.animation import Animation
from kivy.animation import AnimationTransition
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

anim_transitions = [
    key
    for key in vars(AnimationTransition).keys()
    if not key.startswith("__")
] + [
    value
    for key, value in vars(AnimationTransition).items()
    if not key.startswith("__")
]


class ExpandableMixinError(Exception):
    pass


class ExpandableMixin(Widget):
    """A robust mixin for creating widgets that can be in an "expanded" or
    "retracted" state, horizontally and vertically.
    """

    allow_resize_x = BooleanProperty(False)
    """If True, then the widget can resize horizontally. This value is 
    automatically set to True on initialization if the widget has a non-None
    min_x/min_x_hint and a max_x/max_x_hint.
    
    The user can dynamically set this value to False if they want to 
    conditionally "lock" the widget from any horizontal resizing behavior."""

    allow_resize_y = BooleanProperty(False)
    """If True, then the widget can resize vertically. This value is 
    automatically set to True on initialization if the widget has a non-None
    min_y/min_y_hint and a none-None max_y/max_y_hint.

    The user can dynamically set this value to False if they want to 
    conditionally "lock" the widget from any vertical resizing behavior."""

    start_expanded_x = BooleanProperty(None)
    """When True, the widget's expand_state_x is True when after initialization.
    
    This value is set to False during initialization if the user does not assign 
    a value. Hence, by default, widgets start horizontally retracted."""

    start_expanded_y = BooleanProperty(None)
    """When True, the widget's expand_state_y is True when after initialization.

    This value is set to False during initialization if the user does not assign 
    a value. Hence, by default, widgets start vertically retracted."""

    min_x_hint = BoundedNumericProperty(None, min=0, allownone=True)
    """The value of size_hint_x the widget will have when horizontally 
    retracted. The value cannot be negative and can be changed to None, although 
    this will raise an exception if there is no value for min_x.
    
    If the widget has a value for both min_x and min_x_hint, then the value for 
    min_x_hint is ALWAYS prioritized."""

    max_x_hint = BoundedNumericProperty(None, min=0, allownone=True)
    """The value of size_hint_x the widget will have when horizontally 
    expanded. The value cannot be negative and can be changed to None, although 
    this will raise an exception if there is no value for max_x.
    
    If the widget has a value for both max_x and max_x_hint, then the value for 
    max_x_hint is ALWAYS prioritized."""

    min_y_hint = BoundedNumericProperty(None, min=0, allownone=True)
    """The value of size_hint_y the widget will have when vertically 
    retracted. The value cannot be negative and can be changed to None, although 
    this will raise an exception if there is no value for min_y.
    
    If the widget has a value for both min_y and min_y_hint, then the value for 
    min_y_hint is ALWAYS prioritized."""

    max_y_hint = BoundedNumericProperty(None, min=0, allownone=True)
    """The value of size_hint_x the widget will have when vertically 
    expanded. The value cannot be negative and can be changed to None, although 
    this will raise an exception if there is no value for max_y.
    
    If the widget has a value for both max_y and max_y_hint, then the value for 
    max_y_hint is ALWAYS prioritized."""

    min_x = NumericProperty(None)
    """The width the widget will have when horizontally retracted. It can never 
    be assigned a value of None.
    
    If the widget has a value for both min_x and min_x_hint, then the value for 
    min_x_hint is ALWAYS prioritized."""

    max_x = NumericProperty(None)
    """The width the widget will have when horizontally expanded. It can never 
    be assigned a value of None.
    
    If the widget has a value for both max_x and max_x_hint, then the value for 
    max_x_hint is ALWAYS prioritized."""

    min_y = NumericProperty(None)
    """The height the widget will have when vertically retracted. It can never 
    be assigned a value of None.
    
    If the widget has a value for both min_y and min_y_hint, then the value for 
    min_y_hint is ALWAYS prioritized."""

    max_y = NumericProperty(None)
    """The height the widget will have when vertically expanded. It can never 
    be assigned a value of None.
    
    If the widget has a value for both max_y and max_y_hint, then the value for 
    max_y_hint is ALWAYS prioritized."""

    duration_resize = NumericProperty(0.25)
    """The duration of the resize animation in units of seconds. That is, 
    whenever you expand or retract the widget horizontally or vertically without 
    using instant_toggle_x or any similar method, the length of the animation 
    depicting the state change is determined by this value. The default duration 
    is 0.25 seconds. 
    
    This value can be overriden by any duration attribute which has higher 
    specificity. For example, if duration_resize_x is assigned a value, then 
    expanding or retracting the widget horizontally will have an animation 
    duration of the value of duration_resize_x"""

    duration_resize_x = NumericProperty(None, allownone=True)
    """The duration of the horizontal resize animation, in units of seconds. By 
    default, this value is None and it can be set to None during the widget's 
    lifetime.
    
    This value will override the value of duration_resize if it is not None. 
    This value is overriden by duration_expand_x or duration_retract_x if either 
    of those attributes are not None."""

    duration_resize_y = NumericProperty(None, allownone=True)
    """The duration of the vertical resize animation, in units of seconds. By 
    default, this value is None and it can be set to None during the widget's 
    lifetime.

    This value will override the value of duration_resize if it is not None.  
    This value is overriden by duration_expand_y or duration_retract_y if either 
    of those attributes are not None."""

    duration_expand_x = NumericProperty(None, allownone=True)
    """The duration of the horizontal expand animation, in units of seconds. By 
    default, this value is None and it can be set to None during the widget's 
    lifetime.
    
    This value will override the values of duration_resize and duration_resize_x 
    if its value is not None."""

    duration_expand_y = NumericProperty(None, allownone=True)
    """The duration of the vertical expand animation, in units of seconds. By 
    default, this value is None and it can be set to None during the widget's 
    lifetime.

    This value will override the values of duration_resize and duration_resize_y 
    if its value is not None."""

    duration_retract_x = NumericProperty(None, allownone=True)
    """The duration of the horizontal retract animation, in units of seconds. By 
    default, this value is None and it can be set to None during the widget's 
    lifetime.

    This value will override the values of duration_resize and duration_resize_x 
    if its value is not None."""

    duration_retract_y = NumericProperty(None, allownone=True)
    """The duration of the vertical retract animation, in units of seconds. By 
    default, this value is None and it can be set to None during the widget's 
    lifetime.

    This value will override the values of duration_resize and duration_resize_y 
    if its value is not None."""

    fixed_duration_x = BooleanProperty(False)
    """The animation duration is actually dynamic. If duration_resize is 5 and 
    the toggle_x method is called, and then toggle_x is called once again after 
    exactly one second, then by default, the animation will now take 4 seconds. 
    If you want the animation to always take the full 5 seconds, then set this 
    property to True."""

    fixed_duration_y = BooleanProperty(False)
    """The animation duration is actually dynamic. If duration_resize is 5 and 
    the toggle_y method is called, and then toggle_x is called once again after 
    exactly one second, then by default, the animation will now take 4 seconds. 
    If you want the animation to always take the full 5 seconds, then set this 
    property to True."""

    transition_resize = OptionProperty(
        AnimationTransition.linear,
        options=anim_transitions
    )
    """This will determine the transition property applied to the Animation 
    object used to animate any state change of this widget. It must be a string 
    or one of the properties from the AnimationTransition class in the 
    kivy.animation module.
    
    This value can be overridden by any transition attribute of higher 
    specificity."""

    transition_resize_x = OptionProperty(
        None,
        options=anim_transitions,
        allownone=True
    )
    """This will determine the transition property applied to the Animation 
    object used to animate any horizontal state changes of this widget. It must 
    be a string or one of the properties from the AnimationTransition class in 
    the kivy.animation module.

    This value will override transition_resize if its value is not None. This 
    value can be overridden by transition_expand_x or transition_retract_x 
    if either is not None."""

    transition_resize_y = OptionProperty(
        None,
        options=anim_transitions,
        allownone=True
    )
    """This will determine the transition property applied to the Animation 
    object used to animate any vertical state changes of this widget. It must be 
    a string or one of the properties from the AnimationTransition class in the 
    kivy.animation module.

    This value will override transition_resize if its value is not None. This 
    value can be overridden by transition_expand_y or transition_retract_y 
    if either is not None."""

    transition_expand_x = OptionProperty(
        None,
        options=anim_transitions,
        allownone=True
    )
    """This will determine the transition property applied to the Animation 
    object used to animate any horizontal expansion for this widget. It must be 
    a string or one of the properties from the AnimationTransition class in the 
    kivy.animation module.

    This value will override any value assigned to transition_resize or 
    transition_resize_x."""

    transition_expand_y = OptionProperty(
        None,
        options=anim_transitions,
        allownone=True
    )
    """This will determine the transition property applied to the Animation 
    object used to animate any vertical expansion for this widget. It must be a 
    string or one of the properties from the AnimationTransition class in the 
    kivy.animation module.

    This value will override any value assigned to transition_resize or 
    transition_resize_y."""

    transition_retract_x = OptionProperty(
        None,
        options=anim_transitions,
        allownone=True
    )
    """This will determine the transition property applied to the Animation 
    object used to animate any horizontal retraction for this widget. It must be 
    a string or one of the properties from the AnimationTransition class in the 
    kivy.animation module.

    This value will override any value assigned to transition_resize or 
    transition_resize_x."""

    transition_retract_y = OptionProperty(
        None,
        options=anim_transitions,
        allownone=True
    )
    """This will determine the transition property applied to the Animation 
    object used to animate any vertical retraction for this widget. It must be a 
    string or one of the properties from the AnimationTransition class in the 
    kivy.animation module.

    This value will override any value assigned to transition_resize or 
    transition_resize_y."""

    _resize_animation = ObjectProperty(None, allownone=True)
    """Private variable used for determining whether this widget is currently 
    animating something. Stores the Animation object which is performing the 
    current animation, or is None if there is no animation."""

    _timestamp_horizontal = NumericProperty(None, allownone=True)
    """Used for determining how much any horizontal animation has progressed."""

    _timestamp_vertical = NumericProperty(None, allownone=True)
    """Used for determining how much any vertical animation has progressed."""

    _prev_duration_horizontal = NumericProperty(None, allownone=True)
    """Used for the internal algorithm which dynamically assigns animation 
    duration times. This value represents the duration of the previous 
    horizontal animation if it were allowed to execute in full. It is None if no 
    animation was interrupted."""

    _prev_duration_vertical = NumericProperty(None, allownone=True)
    """Used for the internal algorithm which dynamically assigns animation 
    duration times. This value represents the duration of the previous vertical 
    animation if it were allowed to execute in full. It is None if no vertical 
    animation was interrupted."""

    _percent_expanded_horizontal = NumericProperty(None, allownone=True)
    """Used for the internal algorithm which dynamically assigns animation 
    duration times. Is a value between 0 and 1, where 0 means the widget is 
    retracted and 1 mean the widget is expanded (horizontally). 
    
    This value is not continuously updated. It is determined every time the 
    widget calculates the dynamic animation duration and is set to None once 
    all animations are complete."""

    _percent_expanded_vertical = NumericProperty(None, allownone=True)
    """Used for the internal algorithm which dynamically assigns animation 
    duration times. Is a value between 0 and 1, where 0 means the widget is 
    retracted and 1 mean the widget is expanded (vertically). 
    
    This value is not continuously updated. It is determined every time the 
    widget calculates the dynamic animation duration and is set to None once 
    all animations are complete."""

    _expanded_horizontal = BooleanProperty()
    """Used internally. Is True if the widget is expanding or expanded 
    (horizontally). Please  never make assignments to this attribute at 
    runtime."""

    _expanded_vertical = BooleanProperty()
    """Used internally. Is True if the widget is expanding or expanded 
    (vertically). Please never make assignments to this attribute at runtime."""

    _initialized = BooleanProperty(False)
    """Used internally. An internal callback sets this value to True, after the 
    widget constructor is called in Python, or after all of the rules in kvlang 
    are parsed for this instance."""

    def _get_resizing(self, *_args):
        """Return True if the widget is currently animating."""
        return self._resize_animation is not None

    resizing = AliasProperty(_get_resizing, bind=["_resize_animation"])
    """Is True if the widget is currently animating a horizontal/vertical 
    expansion/retraction. This property is read-only."""

    def _get_expand_state_hor(self, *_args):
        """Returns True if the widget is expanded or expanding horizontally."""
        return self._expanded_horizontal

    expand_state_x = AliasProperty(_get_expand_state_hor, bind=[
        "_expanded_horizontal"
    ])
    """Is True if the widget is expanded or expanding horizontally. This 
    property is read-only."""

    def _get_expand_state_vert(self, *_args):
        """Return True if the widget is expanded or expanding vertically."""
        return self._expanded_vertical

    expand_state_y = AliasProperty(_get_expand_state_vert, bind=[
        "_expanded_vertical"
    ])
    """Is True if the widget is expanded or expanding vertically. This property 
    is read-only."""

    def _get_retract_state_hor(self, *_args):
        """Returns True if the widget is retracted or retracting
        horizontally."""
        return not self._expanded_horizontal

    retract_state_x = AliasProperty(_get_retract_state_hor, bind=[
        "expand_state_x"
    ])
    """Is True if the widget is retracted or retracting horizontally. This 
    property is read-only."""

    def _get_retract_state_vert(self, *_args):
        """Returns True if the widget is retracted or retracting vertically.
        This property is read-only."""
        return not self._expanded_vertical

    retract_state_y = AliasProperty(_get_retract_state_vert, bind=[
        "expand_state_y"
    ])
    """Returns True if the widget is retracted or retracted vertically. This 
    property is read-only."""

    def _get_fully_expanded_hor(self, *_args):
        """Returns True if this widget is horizontally expanded."""
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
    """Is True if this widget is horizontally expanded. This property is 
    read-only."""

    def _get_fully_retracted_hor(self, *_args):
        """Returns True if this widget is horizontally retracted."""
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
    """Is True if this widget is horizontally retracted. This property is 
    read-only."""

    def _get_fully_expanded_vert(self, *_args):
        """Returns True if this widget is vertically expanded."""
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
    """Is True if this widget is vertically expanded. This property is 
    read-only."""

    def _get_fully_retracted_vert(self, *_args):
        """Returns True if this widget is vertically retracted."""
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
    """Is True if this widget is vertically retracted."""

    def _get_expanding_horizontal(self, *_args):
        """Returns True if this widget is horizontally expanding."""
        return self.expand_state_x and self.resizing

    expanding_x = AliasProperty(_get_expanding_horizontal, bind=[
        "expand_state_x",
        "resizing"
    ])
    """Is True if this widget is horizontally expanding. This property is 
    read-only."""

    def _get_expanding_vertical(self, *_args):
        """Returns True if this widget is vertically expanding."""
        return self.expand_state_y and self.resizing

    expanding_y = AliasProperty(_get_expanding_vertical, bind=[
        "expand_state_y",
        "resizing"
    ])
    """Is True if this widget is vertically expanding."""

    def _get_retracting_horizontal(self, *_args):
        """Returns True if this widget is horizontally retracting."""
        return self.retract_state_x and self.resizing

    retracting_x = AliasProperty(_get_retracting_horizontal, bind=[
        "retract_state_x",
        "resizing"
    ])
    """Is True if this widget is horizontally retracting. This property is 
    read-only."""

    def _get_retracting_vertical(self, *_args):
        """Returns True if this widget is vertically retracting."""
        return self.retract_state_y and self.resizing

    retracting_y = AliasProperty(_get_retracting_vertical, bind=[
        "retract_state_y",
        "resizing"
    ])
    """Is True if this widget is vertically retracting."""

    custom_size_hint_resolver = ObjectProperty(None)
    """For advanced users.
    
    If you "mix" hinted and not hinted bounds for this widget (i.e., you assign 
    a min_x and a max_x_hint), the widget will animate in the expected manner. 
    However, when the widget is at min_x, it is assigned a specific width and 
    therefore must have a size_hint_x of None. Thus, to animate to max_x_hint, 
    we must resolve for size_hint_x. That is, we must find the size_hint_x which 
    brings the widget the width of min_x.
    
    This process is non-trivial if handled appropriately for every edge case 
    for every kivy Widget which listens to size_hint. However, it is possible 
    that an advanced user has their own custom widgets which listen to the size 
    hints of their children. In that case, the user can provide their own custom 
    resolver by assigning a callback to this attribute. The callback must take a 
    single argument, which is the string "x" or "y". This should represent 
    whether you are resolving size_hint_x or size_hint_y.
    
    The custom callback is ALWAYS called before any logic is performed in this 
    widget's default size hint resolver. In your custom resolver, you must 
    manually check for whether the widget is a child of a custom widget 
    yourself.
    
    If the custom callback returns any value, then the default logic performed 
    in this widget's size hint resolver is ignored.
    
    If your custom widget cannot smoothly animate from a specific width/height 
    to a width/height determined by size hint, then you can "cheat" by also 
    assigning a custom animation to the custom_size_hint_animation attribute.
    This custom_size_hint_animation method will be called if 
    custom_size_hint_resolver returns True."""

    custom_size_hint_animation = ObjectProperty(None)
    """For advanced users. See the discussion in the documentation for the 
    custom_size_hint_resolver attribute.
    
    If your custom widget cannot smoothly animate from a specific width/height 
    to a width/height determined by size hint, then you can "cheat" by also 
    assigning a custom animation to the custom_size_hint_animation attribute.
    This custom_size_hint_animation method will be called if 
    custom_size_hint_resolver (or if the default internal size hint resolver) 
    returns True.
    
    This callback will be performed before any internal animation logic is 
    performed. If this callback returns any non-None value, then the default 
    animation logic will be ignored.
    
    The callback takes four positional parameters:
        x_or_y: str; whether you are animating horizontally/vertically
        hint: float; the size_hint_x/y to animate to
        transition; one of the properties of AnimationTransition from the 
            kivy.animation module, or a string.
        duration: float; the duration of the animation.
                
    You can perform any behavior that you wish in this method. But we HIGHLY 
    recommend that you use this widget's start_resize_animation method when 
    performing any animation, as the widget's properties (i.e., expanded, 
    expand_state, expanding, resizing, etc) will be updated appropriately if you 
    use that method."""

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
            "expand_state_x",
            "expand_state_y",
            "expanded_x",
            "expanded_y",
            "expanding_x",
            "expanding_y",
            "fixed_duration_x",
            "fixed_duration_y",
            "max_x",
            "max_x_hint",
            "max_y",
            "max_y_hint",
            "min_x",
            "min_x_hint",
            "min_y",
            "min_y_hint",
            "resizing",
            "retract_state_x",
            "retract_state_y",
            "retracted_x",
            "retracted_y",
            "retracting_x",
            "retracting_y",
            "start_expanded_x",
            "start_expanded_y",
            "transition_expand_x",
            "transition_expand_y",
            "transition_resize",
            "transition_resize_x",
            "transition_resize_y",
            "transition_retract_x",
            "transition_retract_y"
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
        """This method takes an animation object and performs that animation on
        this widget. The second argument informs the method whether we are
        animating width/size_hint_x or height/size_hint_y. This method then
        binds to various events for the animation so that the relevant
        properties of this widget (resizing, expanding_x, retracted_y, etc.) are
        updated as expected.

        In particular, the internal private method which updates the values of
        width/height/size_hint_x/size_hint_y is executed upon the animation's
        completion, guaranteed that the size_hint and size will be the value
        specified by min_x/max_x/min_y/max_y/min_x_hint/max_x_hint/etc."""
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
        """If horizontal resizing is allowed, then change the horizontal state
        and animate to the new width."""
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
        """If vertical resizing is allowed, then change the vertical state and
        animate to the new height."""
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
        """If horizontal resizing is allowed, then ensure the horizontal state
        is the expand state. If not, animate to the expanded width."""
        if not self._expanded_horizontal:
            self.toggle_x()

    def retract_x(self, *_args):
        """If horizontal resizing is allowed, then ensure the horizontal state
        is in the retract state. If not, animate to the retracted width."""
        if not self.retract_state_x:
            self.toggle_x()

    def expand_y(self, *_args):
        """If vertical resizing is allowed, then ensure the vertical state is in
        the expand state. If not, animate to the expanded width."""
        if not self._expanded_vertical:
            self.toggle_y()

    def retract_y(self, *_args):
        """If vertical resizing is allowed, then ensure the vertical state is in
        the retract state. If not, animate to the retracted width."""
        if not self.retract_state_y:
            self.toggle_y()

    def instant_expand_x(self, *_args):
        """If horizontal resizing is allowed, then immediately expand to the
        expanded width without animating."""
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
        """If horizontal resizing is allowed, then immediately retract to the
        retracted width without animating."""
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
        """If vertical resizing is allowed, then immediately expand to the
        expanded height without animating."""
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
        """If vertical resizing is allowed, then immediately retract to the
        retracted height without animating."""
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
        """If horizontal resizing is allowed, then immediately change the state
        without animating."""

        if not self.allow_resize_x:
            return

        if self._expanded_horizontal:
            self.instant_retract_x()
        else:
            self.instant_expand_x()

    def instant_toggle_y(self, *_args):
        """If vertical resizing is allowed, then immediately change the state
        without animating."""

        if not self.allow_resize_y:
            return

        if self._expanded_vertical:
            self.instant_retract_y()
        else:
            self.instant_expand_y()

    def _update_width(self, *_args):
        """This method assigns the width/size_hint_x to the value reflected by
        the current state. But only if the widget has been "initialized" (i.e.,
        the widget had its constructor called or the kvlang Builder finished
        parsing all the rules for this instance), if horizontal resizing is
        allowed, and only if we aren't currently resizing."""
        if not self._initialized:
            return
        print("hi")
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
        """This method assigns the height/size_hint_y to the value reflected by
        the current state. But only if the widget has been "initialized" (i.e.,
        the widget had its constructor called or the kvlang Builder finished
        parsing all the rules for this instance), if vertical resizing is
        allowed, and only if we aren't currently resizing."""
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
        """A convenience method for calling both _update_width and
        _update_height, in that order."""
        self._update_width()
        self._update_height()

    def _after_initialization(self, *_args):
        """This method determines whether the widget should start expanded or
        retracted. If the user doesn't pick one, then it starts retracted by
        default.

        This method also automatically allows the widget to resize horizontally
        or vertically if the appropriate attributes were given non-None values
        (for example, if the widget has a min_x and a max_height assigned, then
        allow_resize_x will be set to True).

        If the user assigns allow_resize_x/y to True but doesn't assign values
        to the appropriate attributes, an exception is raised.

        The method will then assign a width/height to the expanded/retracted
        value, based on whether the user has assigned a value to
        start_expanded_x/y. If they did not, then the widget starts retracted.

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
        """This clears internal flags used to perform logic for calculating
        dynamic animation durations."""
        if finished_animating:
            self._percent_expanded_horizontal = None
            self._prev_duration_horizontal = None

    def _clear_anim_data_vertical(self, _instance, finished_animating):
        """This clears internal flags used to perform logic for calculating
        dynamic animation durations."""
        if finished_animating:
            self._percent_expanded_vertical = None
            self._prev_duration_vertical = None

    def _resolve_parent(self, *_args):
        """If the parent of this widget is set to None for some ungodly reason,
        this Widget will crawl through the Widget tree to find the parent.

        This method should never be called. It is introduced as an extremely
        cautious security measure, but if its use is necessary, then you have
        something wrong with your app."""
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
        if prefix == "tb" or prefix == "bt":
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
            if prefix == "tb" or prefix == "bt":
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

        if orientation == "lr-tb":
            row_num = col_num = 0
            for child in reversed(parent.children):
                add_child(child, row_num, col_num)
                col_num += 1
                if col_num == cols:
                    row_num += 1
                    col_num = 0
        elif orientation == "lr-bt":
            row_num = rows - 1
            col_num = 0
            for child in reversed(parent.children):
                add_child(child, row_num, col_num)
                col_num += 1
                if col_num == cols:
                    row_num -= 1
                    col_num = 0
        elif orientation == "rl-tb":
            row_num = 0
            col_num = cols - 1
            for child in reversed(parent.children):
                add_child(child, row_num, col_num)
                col_num -= 1
                if col_num < 0:
                    row_num += 1
                    col_num = cols - 1
        elif orientation == "rl-bt":
            row_num = rows - 1
            col_num = cols - 1
            for child in reversed(parent.children):
                add_child(child, row_num, col_num)
                col_num -= 1
                if col_num < 0:
                    row_num -= 1
                    col_num = cols - 1
        elif orientation == "tb-lr":
            row_num = col_num = 0
            for child in reversed(parent.children):
                add_child(child, row_num, col_num)
                row_num += 1
                if row_num == rows:
                    row_num = 0
                    col_num += 1
        elif orientation == "tb-rl":
            row_num = 0
            col_num = cols - 1
            for child in reversed(parent.children):
                add_child(child, row_num, col_num)
                row_num += 1
                if row_num == rows:
                    row_num = 0
                    col_num -= 1
        elif orientation == "bt-lr":
            row_num = rows - 1
            col_num = 0
            for child in reversed(parent.children):
                add_child(child, row_num, col_num)
                row_num -= 1
                if row_num < 0:
                    row_num = rows - 1
                    col_num += 1
        elif orientation == "bt-rl":
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
            if parent.orientation == "vertical":
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
        """Returns the full duration for horizontally expanding. This does not
        account for the eventual logic that may be performed to reduce the
        actual animation time."""
        if self.duration_expand_x:
            return self.duration_expand_x
        elif self.duration_resize_x:
            return self.duration_resize_x
        else:
            return self.duration_resize

    def _get_retract_anim_hor_duration(self, *_args):
        """Returns the full duration for horizontally retracting. This does not
        account for the eventual logic that may be performed to reduce the
        actual animation time."""
        if self.duration_retract_x:
            return self.duration_retract_x
        elif self.duration_resize_x:
            return self.duration_resize_x
        else:
            return self.duration_resize

    def _get_horizontal_animation_duration(self):
        """Calculates the actual horizontal animation duration, based on whether
        we should be expanding or retracting.

        To see the reason this method exists, imagine the user assigns a large
        value for duration_resize (say, 5 seconds). Then, the expandable widget
        calls its toggle_x. It slowly expands/retracts; then suppose, after 1
        second, the widget calls toggle_x again. Well, is has only traveled 1/5
        of the distance it needs to reach the new width, and yet the second
        animation will cover this small distance in 5 seconds, which may feel
        terrible for the user.

        The logic performed here will cause the actual animation time from the
        previous example to only take 1 second.

        If, for whatever reason, the example behavior is actually preferable,
        then assigning fixed_duration_x to True will cause it happen.
        """
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
        """Returns the animation transition for based on whether we will
        horizontally expand or retract."""
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
        """There are some cases where resolving the size_hint_x would cause the
        widget to "snap" into place, making a smooth animation simply
        impossible. This method is called whenever one of these edge cases occur
        to perform a smooth animation before assigning a size_hint to the
        widget.

        The only known edge cases where this can happen occur in BoxLayouts or
        GridLayouts."""
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
            """Please see corresponding docstring in 
            _animate_height_hint_special_case."""
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
            """Please see corresponding docstring in 
            _animate_height_hint_special_case."""
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
        """If we are allowed to resize horizontally, and if the x_hint is one
        of the values min_x_hint or max_x_hint, then we perform the needed
        animation to animate to that value of x_hint. This will call
        self._resolve_size_hint_x if the current size_hint_x is None and
        possibly call self._animate_width_hint_special_case if necessary."""
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
            if parent.orientation == "horizontal":
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
        """Returns the full duration for vertically expanding. This does not
        account for the eventual logic that may be performed to reduce the
        actual animation time."""
        if self.duration_expand_y:
            return self.duration_expand_y
        elif self.duration_resize_y:
            return self.duration_resize_y
        else:
            return self.duration_resize

    def _get_retract_anim_vert_duration(self, *_args):
        """Returns the full duration for vertically retracting. This does not
        account for the eventual logic that may be performed to reduce the
        actual animation time."""
        if self.duration_retract_y:
            return self.duration_retract_y
        elif self.duration_resize_y:
            return self.duration_resize_y
        else:
            return self.duration_resize

    def _get_vertical_animation_duration(self):
        """See the comment in _get_horizontal_animation_duration. The behavior
        of this method is entirely analogous."""
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
        """Returns the animation transition for based on whether we will
        vertically expand or retract."""
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
        """There are some cases where resolving the size_hint_y would cause the
        widget to "snap" into place, making a smooth animation simply
        impossible. This method is called whenever one of these edge cases occur
        to perform a smooth animation before assigning a size_hint to the
        widget.

        The only known edge cases where this can happen occur in BoxLayouts or
        GridLayouts."""
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

        parent = self.parent

        if isinstance(parent, BoxLayout):
            """If orientation is vertical, then the allotted height is divided 
            between all widgets with non-None size_hint_y's. But if we are the 
            only child, then we get all of the allotted height no matter the 
            value of our size_hint_y. Hence, assigning a value to size_hint_y 
            causes widget to "snap" into a particular height, ruining a smooth 
            animation. Hence, we cheat by simply animating the height to the 
            allotted height."""
            self.size_hint_y = None

            sum_heights = 0.
            for child in parent.children:
                if child.size_hint_y is None and child is not self:
                    sum_heights += child.height

            padding_vert = parent.padding[1] + parent.padding[3]
            spacing_vert = parent.spacing * (len(parent.children) - 1)
            padding_and_spacing = padding_vert + spacing_vert
            height = parent.height - padding_and_spacing - sum_heights
            height = max(0, height)

            duration = self._get_vertical_animation_duration()
            transition = self._get_vertical_animation_transition()
            anim = Animation(height=height, t=transition, d=duration)
            self.start_resize_animation(anim, VERTICAL)

        if isinstance(parent, GridLayout):
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
            widget size_hint_y. Make a second rows_minimum dict and animate to 
            it. Note that GridLayouts don't, by default, bind their layout logic 
            to the rows_minimum property (this is likely a bug that should be 
            fixed, make an MR to the kivy source code), so bind rows_minimum to 
            the private method _trigger_layout.

            Once this animation is complete, set the size_hint_y to
            min/max_y_hint. Also unbind _trigger_layout.
            """

            result = self._handle_child_of_grid_layout()

            row_of_self = result["row_of_self"]

            if parent.row_force_default:
                if row_of_self in parent.rows_minimum:
                    full_height = parent.rows_minimum[row_of_self]
                else:
                    full_height = parent.row_default_width

                anim = Animation(width=full_height, t=transition, d=duration)
                self.start_resize_animation(anim, VERTICAL)
                return

            # we will override this attribute, but we will need to set it back
            # to this value after we're done
            temp = parent.rows_minimum

            # calculate the width of the slot for each row. This requires
            # calculating the minimum width for each row AND the fraction of
            # allotted width provided to each row

            # mins[n] is the minimum height of row n
            mins = {}
            # max_size_hints[n] is the largest size_hint_y found in row n
            max_size_hints = {}

            row_default_width = parent.row_default_width

            rows = result["rows"]
            num_rows = len(rows.keys())

            # loop through every child in row. Determine the minimum height of
            # the row, as well as the largest size_hint_y in that row.
            for row_num in rows.keys():

                minimum_from_dict = None
                if row_num in parent.rows_minimum:
                    minimum_from_dict = parent.rows_minimum[row_num]

                minimum_from_children = None
                max_size_hint = None
                for child in rows[row_num]:
                    if child.size_hint_y is None:
                        # find a value for minimum_from_children
                        if minimum_from_children is None:
                            minimum_from_children = child.height
                        else:
                            minimum_from_children = max(
                                minimum_from_children,
                                child.height
                            )
                    else:
                        # find the largest size_hint_y in the row
                        if max_size_hint is None:
                            max_size_hint = child.size_hint_y
                        else:
                            max_size_hint = max(
                                max_size_hint,
                                child.size_hint_y
                            )

                min_height = row_default_width

                if minimum_from_dict is not None:
                    min_height = max(min_height, minimum_from_dict)

                if minimum_from_children is not None:
                    min_height = max(min_height, minimum_from_children)

                # the minimum width for col_num is...
                mins[row_num] = min_height
                # the maximum size_hint for col_num is...
                if max_size_hint is not None:
                    max_size_hints[row_num] = max_size_hint

            spacing = (num_rows - 1) * parent.spacing[1]
            padding = parent.padding[1] + parent.padding[3]
            allotted_height = parent.height - spacing - padding
            allotted_height -= sum(mins.values())

            # create a rows_minimum dictionary that represents the height of
            # each row currently. Then make another one that represents the
            # height of each row after expandable widget gets a new size hint
            heights_before = {}
            heights_after = {}
            dicts = [heights_before, heights_after]
            for dictionary in dicts:
                sum_size_hint = sum(max_size_hints.values())
                for row in rows.keys():
                    height = mins[row]

                    if sum_size_hint > 0:
                        ratio = max_size_hints[row] / sum_size_hint
                        height += ratio * allotted_height

                    dictionary[row] = height
                max_size_hints[row_of_self] = y_hint

            # set row_force_default to True
            parent.row_force_default = True
            parent.rows_minimum = heights_before

            # bind parent.rows_minimum to parent._trigger_layout
            parent.bind(rows_minimum=parent._trigger_layout)  # noqa

            # create animations
            anim1 = Animation(
                rows_minimum=heights_after,
                t=transition,
                d=duration
            )
            anim2 = Animation(
                height=heights_after[row_of_self],
                t=transition,
                d=duration
            )

            # unbind parent._trigger_layout, set parent.cols_minimum back to its
            # original value
            def on_complete(*_args):
                parent.unbind(rows_minimum=parent._trigger_layout)  # noqa
                parent.rows_minimum = temp
            anim1.bind(on_complete=on_complete)

            # animate self and cols_minimum to new value
            self.start_resize_animation(anim2, HORIZONTAL)
            anim1.start(parent)

    def _animate_height_hint(self, y_hint, *_args):
        """If we are allowed to resize vertically, and if the y_hint is one of
        the values min_y_hint or max_y_hint, then we perform the needed
        animation to animate to that value of y_hint. This will call
        self._resolve_size_hint_xy if the current size_hint_y is None and
        possibly call self._animate_height_hint_special_case if necessary."""
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
        """If we are allowed to resize horizontally and the given parameter is
        one of the values min_x or max_x, then animate to that width."""
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
        """If we are allowed to resize vertically and the given parameter is one
        of the values min_y or max_y, then animate to that height."""
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
