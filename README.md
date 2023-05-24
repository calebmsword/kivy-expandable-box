# kivy-expandable-box
A robust mixin for creating expandable widgets in Kivy.

When we say that this Widget is a mixin, we mean that it is not meant to be instantiated directly. Instead it should be inherited by other widgets. You can make any Kivy widget or custom widget expandable simply by having the class inherit this mixin!

In Python:
```python
class ExpandableButton(Button, ExpandableMixin):
    def on_expand_state_x(self, instance, expand_state_x):
        self.text = "Retract me!" if expand_state_x else "Expand me!"
    
    def on_release(self, *_args):
        self.toggle_x()
 
 
 expandable_button = ExpandableButton(
     min_x=100,
     max_x=500
 )
```

In kvlang:
```kvlang
<ExpandableButton@Button+ExpandableMixin>:
    text: "Retract me!" if self.expand_state_x else "Expand me!"
    on_release: self.toggle_x()

ExpandableButton:
    min_x: 100
    max_x: 500
```

The ExpandableMixin gives any widget the ability to expand or retract vertically or horizontally.

<details>
    
<summary>Example</summary>

```kvlang
#: set BLUE  0, 0, 1, 1
#: set WHITE 1, 1, 1, 1
<ExpandableLabel@Label+ExpandableMixin>:
    bg_color: TRANSPARENT
    canvas.before:
        Color:
            rgba: TRANSPARENT if self.bg_color is None else self.bg_color
        Rectangle:
            pos: self.pos
            size: self.size

BoxLayout:
    ExpandableLabel:
        id: label
        min_x: 100
        max_x: 300
        min_y: 100
        max_y: 300
        bg_color: BLUE
        color: WHITE
        text: "Resizable"
    BoxLayout:
        orientation: "vertical"
        Button:
            text: "toggle_x()"
            on_release: label.toggle_x()
        Button:
            text: "toggle_y()"
            on_release: label.toggle_y()
```

</details>

The user can use size hints to set the min width/height and max width/height.

<details>

<summary> Example </summary>

```kvlang
BoxLayout:
    BoxLayout:
        orientation: "vertical"
        BoxLayout:
            ExpandableButton:
                text: "size hints for min and max"
                min_x_hint: 0.5
                max_x_hint: 1.0
        BoxLayout:
            ExpandableButton:
                text: "min is width but max is size hint"
                min_x: 200
                max_x_hint: 1
        BoxLayout:
            ExpandableButton:
                text: "min is size hint but max is width"
                min_x_hint: 0.3
                max_x: 400
        
```

</details>

Widgets which inherit the ExpandableMixin receive a rich API for accessing and manipulating the state of the widget.

<details>
 
<summary>Example</summary>

```kvlang
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
                text: "expand_state_x: {0}".format(expandable.expand_state_x)
            ColoredLabel:
                bg_color: LIGHT_GREY
                color: BLACK
                text: "expanding_x: {0}".format(expandable.expanding_x)
            ColoredLabel:
                bg_color: GREY
                color: BLACK
                text: "expanded_x: {0}".format(expandable.expanded_x)
            ColoredLabel:
                bg_color: LIGHT_GREY
                color: BLACK
                text: "retract_state_x: {0}".format(expandable.retract_state_x)
            ColoredLabel:
                bg_color: GREY
                color: BLACK
                text: "retracting_x: {0}".format(expandable.retracting_x)
            ColoredLabel:
                bg_color: LIGHT_GREY
                color: BLACK
                text: "retracted_x: {0}".format(expandable.retracted_x)
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

```
</details>

The user has many options for configuring properties of the animation which represents a transition from expanded to retracted or vice versa.

<details>

<summary>Example</summary>

```kvlang
#: import t kivy.animation.AnimationTransition

<ExpandableButton@Button+ExpandableMixin>:
    

BoxLayout:
    orientation: "vertical"
    ExpandableButton:
        min_x_hint: 0.5
        max_x_hint: 1.0
        on_release: self.toggle_x()
        duration_expand_x: 0.5
        duration_retract_x: 0.1
        transition_expand_x: t.out_back  # must be one of the attributes of AnimationTransition static class from kivy.animation module
        transition_retract_x: "linear"  # but you can also use a string instead of kivy.animation.AnimationTransition.linear
    ExpandableButton:
        min_x_hint: 0.5
        max_x_hint: 1.0
        min_y: 100
        max_y: 200
        on_release:
            self.toggle_x()
            self.toggle_y()
        duration_resize: 1
        duration_resize_x: 0.5  # takes priority over duration_resize for horizontal animation
        duration_expand_y: 0.1  # takes priority over duration_resize for vertical expansion
        transition_resize: "linear"
        transition_resize_x: "out_bounce"  # takes priority over transition_resize for horizontal animation
        transition_retract_y: "linear"  # takes priority over transition resize for vertical retraction
```

</details>

TO-DO:
 - [ ] Fix `resolve_size_hint_x` and `resolve_size_hint_y`.
   - [x] Take notes on how each Layout type (aside from RecycleViewBoxLayout and RecycleViewGridLayout) manage size_hints.
     - [x] Window
     - [x] FloatLayout
     - [x] RelativeLayout
     - [x] AnchorLayout
     - [x] StackLayout
     - [x] BoxLayout
     - [x] GridLayout (COMPLICATED!)
     - [x] Take special notes on `GridLayout` because it is particularly complex.
   - [x] For `_resolve_size_hint_x` and `_resolve_size_hint_y`, check the instance of the containing Widget and perform the appropriate logic to resolve `size_hint_x` or `size_hint_y`.
   - [ ] Perform extensive manual tests to ensure that you've implemented the size_hint resolvers propertly.
      - [ ] Window
      - [ ] FloatLayout
      - [ ] RelativeLayout
      - [ ] AnchorLayout
      - [ ] StackLayout
      - [ ] BoxLayout
      - [ ] GridLayout (COMPLICATED!)
    - [ ] Refactor resolvers to handle size_hint_max_x and size_hint_max_y
      - [ ] Investigate how size_hint_max_x and size_hint_max_y affect every hint listener
        - [ ] Window
        - [ ] FloatLayout
        - [ ] RelativeLayout
        - [ ] AnchorLayout
        - [ ] StackLayout
        - [ ] BoxLayout
        - [ ] GridLayout (COMPLICATED!)
