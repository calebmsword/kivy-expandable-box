# kivy-expandable-box
A mixin for creating robust expandable widgets in Kivy.

TO-DO:
 - [ ] Make animation timings dynamic so that, for example, if you interrupt an expansion for a Widget whose `expand_animation_timeout` is 3 seconds in 0.5 seconds, you don't have to wait 3 agonizing seconds for the animation to complete, and instead only wait 2.5 seconds.
 - [ ] Refactor variables which use "expanding" when they should use "resizing". 
   - [ ] Refactor `expanding` into `resizing`.
   - [ ] Refactor `_expand_animation` into `_resize_animation`.
   - [ ] Refactor `on__expand_animation` to `on__resize_animation`
   - [ ] Create `expanding_horizontal`/`expanding_vertical` and `retracting_horizontal`/`retracting_vertical` as read-only AliasProperties.
   - [ ] Refactor logic to use these new variables when appropriate.
 - [ ] Guard all `force_xxx` methods based on whether `allow_expand_horizontal`/`allow_expand_vertical` are true.
 - [ ] Allow for users to make the expansion and retraction animation durations different:
   -  [ ] create variables:
      - [ ] `duration_expand_horizontal`
      - [ ] `duration_expand_vertical`
      - [ ] `duration_retract_horizontal`
      - [ ] `duration_retract_vertical`
   -  [ ] refactor variables:
      - [ ] `expand_animation_timeout` → `duration_resize`
      - [ ] `expand_animation_timeout_horizontal`  → `duration_resize_horizontal`
      - [ ] `expand_animation_timeout_vertical`  → `duration_resize_vertical`
   - [ ] Prioritize based on specificity. For example, `duration_expand_horizontal` → `duration_resize_horizontal` → `duration_resize`
 - [ ] Create fields that allow users to add custom transition parameters to each animation (expand hor, expand ver, retract hor, retract ver) with levels of specificity equivalent to animation durations.
 - [ ] Fix `resolve_size_hint_x` and `resolve_size_hint_y`.
   - [ ] Take notes on how each Layout type (aside from RecycleViewBoxLayout and RecycleViewGridLayout) manage size_hints.
     - [ ] Window
     - [ ] FloatLayout
     - [ ] RelativeLayout
     - [ ] AnchorLayout
     - [ ] StackLayout
     - [ ] BoxLayout
     - [ ] GridLayout (COMPLICATED!)
   - [ ] Take special notes on `GridLayout` because it is particularly complex.
   - [ ] For `_resolve_size_hint_x` and `_resolve_size_hint_y`, check the instance of the containing Widget and perform the appropriate logic to resolve `size_hint_x` or `size_hint_y`.
