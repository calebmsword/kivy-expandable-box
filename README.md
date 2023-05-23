# kivy-expandable-box
A robust mixin for creating expandable widgets in Kivy.

In Python:
```python
s1 = "Expand me!"
s2 = "Retract me!"
class ExpandableButton(Button, ExpandableMixin):
    def on_expand_state_x(self, instance, in_expand_state_x):
        self.text = s2 if self.expand_state_x else s1
    
    def on_release(self, *_args):
        self.toggle_x()
 
 
 expandable_button = ExpandableButton(
     min_x=100,
     max_x=500,
     allow_resize_x=True
 )
```

In kvlang:
```kvlang
#: set s1 "Expand me!"
#: set s2 "Retract me!"
<ExpandableButton@Button+ExpandableMixin>:
    text: s2 if self.expand_state_x else s1
    on_release: self.toggle_x()

ExpandableButton:
    min_x: 100
    max_x: 500
    allow_resize_x: True
```

Widgets which inherit the ExpandableMixin receive a rich API for accessing and manipulating the state of the widget.

<details>
 
<summary>The following in kvlang</summary>

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

```
</details>

Widgets can be expanded horizontally or vertically.

```kvlang

<ExpandableButton@Button+ExpandableMixin>:
 
 BoxLayout:
     BoxLayout:
         ExpandableButton:
             text: "Expandable"
             min_x: 100
             max_x: 300
             on_release: self.toggle_x()
     BoxLayout:
          ExpandableButton:
             text: "Expandable"
             min_y_hint: 0.5
             max_y_hint: 1.0
             on_release: self.toggle_y()
     BoxLayout:
          ExpandableButton:
             text: "Expandable"
             min_x: 100
             max_x_hint: 1
             min_y_hint: 0.1
             max_y: 300
             on_release:
                 self.toggle_x()
                 self.toggle_y()
 
```
 
When we say that this Widget is a mixin, we mean that it is not meant to be instantiated directly (although it can be) and instead is meant to be inherited by other Widgets.

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
   - [ ] For `_resolve_size_hint_x` and `_resolve_size_hint_y`, check the instance of the containing Widget and perform the appropriate logic to resolve `size_hint_x` or `size_hint_y`.
   - [ ] Perform extensive manual tests to ensure that you've implemented the size_hint resolvers propertly.
      - [ ] Window
      - [ ] FloatLayout
      - [ ] RelativeLayout
      - [ ] AnchorLayout
      - [ ] StackLayout
      - [ ] BoxLayout
      - [ ] GridLayout (COMPLICATED!)
    - [ ] Refactor resolver to handle size_hint_max_x and size_hint_max_y
      - [ ] Investigate how size_hint_max_x and size_hint_max_y affect every hint listener
        - [ ] Window
        - [ ] FloatLayout
        - [ ] RelativeLayout
        - [ ] AnchorLayout
        - [ ] StackLayout
        - [ ] BoxLayout
        - [ ] GridLayout (COMPLICATED!)
