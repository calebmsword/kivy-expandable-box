# kivy-expandable-box
A mixin for creating robust expandable widgets in Kivy.

TO-DO:
 - Make animation timings dynamic so that, for example, if you interrupt an expansion for a Widget whose `expand_animation_timeout` is 3 seconds in 0.5 seconds, you don't have to wait 3 agonizing seconds for the animation to complete, and instead only wait 2.5 seconds.
 - Refactor variables which use "expanding" when they should use "resizing". 
   - Refactor `expanding` into `resizing`.
   - Refactor `_expand_animation` into `_resize_animation`. Refactor `on__expand_animation` to `on__resize_animation`
   - Create `expanding_horizontal`/`expanding_vertical` and `retracting_horizontal`/`retracting_vertical` as read-only AliasProperties. Refactor logic to use these new variables when appropriate.
 - Guard all `force_xxx` methods based on whether `allow_expand_horizontal`/`allow_expand_vertical` are true. Create an `ignore_allowance` keyword argument which bypasses these guards
   - Also add `ignore_allowance` keyword to `expand_xxx` and `toggle_xxx` methods.
 - Raise an error in `force_xxx` methods and `toggle_xxx` methods if `xxx_hint` and `xxx` are both `None`
 - Allow for users to make the expansion and retraction animation durations different:
   -  create variables:
      -  `duration_expand_horizontal`
      -  `duration_expand_vertical`
      -  `duration_retract_horizontal`
      -  `duration_retract_vertical`
   -  refactor variables:
      - `expand_animation_timeout` → `duration_resize`
      - `expand_animation_timeout_horizontal`  → `duration_resize_horizontal`
      - `expand_animation_timeout_vertical`  → `duration_resize_vertical`
   - Prioritize based on specificity. For example, `duration_expand_horizontal` → `duration_resize_horizontal` → `duration_resize`
 - Make `allow_expand_horizontal` and `allow_expand_vertical` both `True` by default.
