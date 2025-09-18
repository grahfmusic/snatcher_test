Public API for the framework.

- room_api.rpy: room/object management, CRT toggles, gamepad.
- display_api.rpy: display helpers and visibility.
- ui_api.rpy: hotspots, hover, button customization.
- interactions_api.rpy: interaction menu routines and handlers.
- simple_api.rpy: ultra-light helpers to define rooms/objects and wire minimal logic.
 - simple_fx.rpy: friendly wrappers for shader presets, CRT, vignette, letterbox, breathing.

Quick start (Simple API)

- Define objects with auto-sizing and inline interactions:
  - `character(id, image, x, y, scale_percent=100, description=..., interactions=[{"label":"Talk","action":"talk"}, ...])`
  - `item(...)`, `door(...)`, `container(...)` are sugar around `simple_object(...)`.
- Define a room in one call and it’s available to `load_room()`/`go_to_room()`:
  - `simple_room("my_room", background="rooms/my_room/sprites/bg.png", obj1["id"], obj2["id"], ...)`
- Optional lightweight logic without a class:
  - `simple_room_logic("my_room", on_enter=fn, on_hover=fn, on_interact=fn)`
- Jump to it: `go_to_room("my_room")`

Short aliases (readability)

- Rooms/objects (room_api):
  - `room_load(id)`, `room_save()`, `room_reset()`, `room_update_file()`, `room_export_config()`
  - `obj_move(id, dx, dy)`, `obj_scale(id, delta)`, `obj_show(id)`, `obj_hide(id)`
- CRT/Vignette:
  - `crt_toggle()`, `crt_params(...)`
  - `vignette(strength=None, width=None, feather=None)` - now routed to Colour Grading
  - **DEPRECATED**: `crt_params(vignette=...)` - use `vignette()` function instead
- Letterbox: `letterbox_on(speed='normal')`, `letterbox_off(speed='normal')`
  - `speed`: one of `'very_slow'|'slow'|'normal'|'fast'|'very_fast'` or an integer `0..4` (0=very_slow → 4=very_fast)
  - Navigation: `nav_list()`, `nav_pad(dir)`, `nav_first()`, `nav_toggle()`

- Display (display_api):
  - `room_bg()`, `bg_default(path)`, `bg_fallback()`, `bg_fallback_set(color)`
  - `obj_visible(obj)`, `obj_props(obj)`, `obj_hidden(obj)`

- UI (ui_api):
  - `hover(id)`, `unhover()`, `hotspot(id, data)`, `hotspots()`
  - `exit_action()`, `ui_exit_cfg(...)`, `ui_add_button(id, cfg)`

- Interactions (interactions_api):
  - Type defaults: `act_get(type)`, `act_set(type, list)`, `act_add(type, label, action)`, `act_remove(type, action)`
  - Per-object: `obj_act_set(id, list)`, `obj_act_clear(id)`, `obj_actions(id)`
  - Menu flow: `interact_show(id)`, `interact_hide()`, `interact_nav(dir)`, `interact_execute()`, `interact_do(id, action)`

- Events (events_api, room_events_api):
  - Global once: `once(key, func=..., label=..., persist=False)`; helpers `once_ran`, `once_mark`
  - Room once: `on_first_enter(room, ...)`, `first_enter_run(room)`, `first_enter_once(room, ...)`, `room_visited(room)`

- Breathing (breathing_api):
  - Targets: `breath_target()`, `breath_next()`
  - Apply/save: `breath_apply(room, obj)`, `breath_save(room, obj)`, `breath_values(room, obj)`
  - Profiles: `breath_profiles(...)`, `breath_profile(...)`, `breath_apply_profile(name, ...)`, `breath_save_profile(name, ...)`, `breath_delete_profile(name, ...)`
  - Toggles/params: `breath_on(obj)`, `breath_off(obj)`, `breath_off_all()`, `breath_set(key, value, obj)`

- Lighting (simple_fx dynamic):
  - Presets: `grade(name)`, `light(name)`, `grain(name)`
  - Film grain parameters via room API: `room.grain(intensity=..., size=..., downscale=...)`.
  - Dynamic: `light_add(kind='point'|'spot', x=..., y=..., color='#RRGGBB'|(r,g,b), intensity=1.0, radius=0.5, dir=(1,0), angle=0.5, anim={...}) -> index`
  - Control: `light_set(index, ...)`, `light_remove(index)`, `light_clear()`
  - Animate: `light_anim(index, mode='pulse'|'orbit', speed=..., amount=..., radius=..., center=(x,y), phase=...)`, `light_anim_toggle()`
  - Global: `light_strength(value)`
  - Bloom (global): `bloom_on(threshold=0.75, strength=0.6, radius=2.5)`, `bloom_off()` (or set vars `bloom_enabled/threshold/strength/radius`)

Lighting YAML (v2.1)
- Location: `game/yaml/shaders/preset/light_*.yaml` (shipped) and `game/yaml/shaders/custom/light_*.yaml` (user).
- Top-level keys:
  - `version`: string, e.g. "2.1"
  - `meta`: `{ name, description, group }`
  - `globals` (optional): `{ strength, bloom_threshold, bloom_strength, bloom_radius }`
  - `lights`: list of light entries
- Per-light keys:
  - `type`: `point|spot|directional`
  - `position`: `[px, py]` in pixels (screen space)
  - `radius`: in pixels (converted internally)
  - `color`: `[r,g,b,(a)]` floats 0..1
  - `intensity`: float 0..5
  - `direction`: `[dx,dy]` for spot/directional
  - `angle`: radians (spot cone)
  - `layer`: `back|front|all|bg|objects`
  - `enabled`: bool (default true)
  - `falloff`: `smooth|linear|quadratic|inverse_square|custom`
  - `falloff_exp`: float (used when `falloff: custom`)
  - `bloom_boost`: float (future expansion; global bloom handles threshold/strength)
  - `animation` (optional):
    - `{ mode: 'flicker'|'pulse'|'sweep', ...params }`
      - `flicker`: `{ min, max, speed_hz, seed }`
      - `pulse`: `{ base, amplitude, period_s, phase }`
      - `sweep`: `{ start_angle, end_angle, angular_speed, loop('wrap'|'bounce') }`

Tips
- Use Ctrl+F8 for Lighting Selector (preset browser), F8 → Lighting tab → Open Lighting Editor for full editing.
- Per-light falloff defaults to `smooth` to match legacy behaviour.
- Bloom runs after lighting and before colour grading; enable with `bloom_enabled=True` or in preset `globals`.
- Runtime helpers (`lights_runtime_apply_lights`, `lights_runtime_clear_visual_lighting`) now update shader uniforms immediately via the unified pipeline.

- Presets IO (YAML v2.1+):
  - Files: `game/yaml/shaders/preset/*.yaml` (shipped), `game/yaml/shaders/custom/*.yaml` (user)
  - Filename filtering: `crt_*.yaml`, `grain_*.yaml`, `grade_*.yaml`, `light_*.yaml` appear in respective editor tabs
  - Apply: `preset_load('shaders/preset/noir.yaml')`
  - Save: `preset_save('shaders/custom/my_style.yaml')`
  - **v2.1 Change**: Vignette now saved under `effects.color_grade.*` instead of `effects.crt.*`
  - Automatic migration: Old JSON presets are migrated and saved as YAML when edited

- Room (script-style convenience):
  - `room.set_shader_preset('shaders/preset/noir.yaml')`
  - `room.save_shader_preset('shaders/custom/my_style.yaml')`
- `room.crt(aberration=0.2, enabled=True, animated=False, aberration_mode='pulse', aberration_speed=1.0, glitch=0.05, glitch_speed=1.5)` (vignette moved to colour grading)
  - `room.grain(intensity=0.03, size=1.0, downscale=2.0)` or `room.grain(preset='moderate')`
- `room.color_grade('neon_night')` - now includes vignette controls
- `room.vignette(strength=0.5, width=0.25, feather=1.0)` - sets colour grading vignette
  - `room.lighting(x=320, y=240, preset='street_lamp', strength=1.0, animation='pulse')`
  - `room.bloom(True, threshold=0.75, strength=0.6, radius=2.5)` or `room.bloom(False)`

Keybinds
- F8: Shader Editor (CRT, Grain, Colour Grading, Presets/IO)
- Ctrl+F8: Lighting Selector (browse/apply lighting presets)
  - From there, click “Edit Lights…” to open the Lighting Editor
