# Snatchernauts Framework — Agent Guide (AGENTS.md)

This file provides repository‑specific guidance for AI coding agents working within this project. Its scope applies to the entire repository.

Note: The core game code is stored under the `game/` directory.

## Project Structure & Module Organization
- `game/`: Ren'Py source. Key modules: `api/` (public helpers like `room_api.rpy`, `ui_api.rpy`), `core/` (config, logging, rooms), `ui/` (screens and layouts), `overlays/` (debug/info/letterbox), `shaders/` (CRT, bloom, grading), `editor/` (F8 Shader Editor), `json/` (presets and user custom presets), `rooms/` (room assets + scripts), `logic/` (game hooks).
- `scripts/`: developer tooling (`run-game.sh`, `lint.sh`, sync scripts, git hooks).
- `Doc/`: in-repo docs (replaces `Wiki/`).
- `Makefile`: shortcuts for linting and wiki sync.

## Build, Test, and Development Commands
- Run locally (Linux/macOS): `scripts/run-game.sh` (flags: `--lint`, `--debug`, `--compile`).
- Run locally (Windows): use `scripts\run-game.ps1` (PowerShell) or `scripts\run-game.cmd` (CMD) with the same flags. Example: `powershell -ExecutionPolicy Bypass -File scripts\run-game.ps1 --lint`.
- Direct Ren'Py (Linux/macOS): `$RENPY_SDK/renpy.sh .` (set `RENPY_SDK` to your Ren'Py 8.4.x SDK path).
- Direct Ren'Py (Windows): `"%RENPY_SDK%\renpy.exe" .` (set `RENPY_SDK` to your Ren'Py 8.4.x SDK path).
- Lint: `scripts/run-game.sh --lint` or `make lint` (runs `renpy.sh . lint`). On Windows, use `scripts\run-game.ps1 --lint` or `scripts\run-game.cmd --lint`.
- Build distributions: Ren'Py Launcher → Build & Distribute (GUI-driven).
- Docs: `make doc-sync` (push `Doc/` to wikis), `make doc-dry` to preview.

## Coding Style & Naming Conventions
- Indentation: 4 spaces for Ren'Py/Python blocks; no tabs.
- Python/Ren'Py: `snake_case` functions/vars, `UPPER_CASE` constants.
- Files: lowercase with underscores; screens prefixed clearly (e.g., `screens_room.rpy`).
- IDs: room/object IDs lowercase (e.g., `room1`, `computer_terminal`).
- Separation: game logic in `game/logic/` and public calls in `game/api/`; keep UI concerns in `game/ui/`.
- Comments: keep functions and non-trivial logic blocks accompanied by short, readable comments (or docstrings) that explain intent or tricky behaviour without stating the obvious.

## Testing Guidelines
- Static checks: `scripts/run-game.sh --lint` before commits and PRs.
- CI gates: GitHub workflow validates project structure and compiles Python blocks inside `.rpy` files—fix all reported errors.
- Manual pass: run the game and verify interaction menu, overlays (`i` info, `l` letterbox), and shader toggles on a sample room.

## Commit & Pull Request Guidelines
- Commits: short, imperative subject using Conventional Commit-style scopes where helpful (e.g., `feat(ui): add context menu`, `fix(core): clamp scale`).
- PRs: include summary, rationale, test steps, linked issues, and screenshots/GIFs for UI/visual changes. Ensure lint passes and CI is green.
- Scope changes: API edits in `game/api/` should note downstream impacts; update `Doc/` when changing public behavior.

## Security & Configuration Tips
- Never commit SDKs or secrets. Set `RENPY_SDK` in your shell profile (e.g., `export RENPY_SDK=~/renpy-8.4.1-sdk`).
- Keep heavy assets organized under `game/` (images/audio) and remove unused files to keep builds lean.

## Keybindings & Assets Consistency
- Keys: keep docs and bindings aligned. Current defaults: shader help/menu (`h`/`s`), shader reset (`r`), letterbox (`l`), info overlay (`i`), Shader Editor (`F8`).
- Audio SFX: verify referenced files exist under `game/audio/ui/` (e.g., use `select.wav` for confirm unless a `confirm.wav` asset is added).
- Room editor: prefer editing room configs under `game/rooms/<id>/scripts/*_config.rpy`. If using “Save to File”, ensure it targets the correct config file for your room.

## Housekeeping
- Don’t commit compiled caches (`*.rpyc`, `cache/`, `saves/`). One-time cleanup script:
  - Preview: `bash scripts/git-clean-artifacts.sh --dry-run`
  - Apply: `bash scripts/git-clean-artifacts.sh` then commit and push

## Shader Editor Overhaul (F8)

The legacy in‑game editor and older shader system are deprecated and scheduled for removal. A new, focused Shader Editor replaces them.

### Entry & File Locations
- Open editor: `F8` (full‑screen overlay)
- Editor code: `game/editor/`
- Shipped presets: `game/json/presets/shaders/` (filtered by filename prefix: crt_, grain_, grade_, light_)
- User presets: `game/json/custom/shaders/`

### Editor UI
- Full‑screen overlay toggled with `F8`.
- Tabbed layout: CRT, Film Grain, Colour Grading, Lighting, Animation, Presets/IO.
- Professional controls: sliders, dropdowns, tooltips, reset buttons, colour pickers.
- Preset management: load shipped presets with filename filtering; save custom presets by name to user folder.
- Film Grain: Manual controls for intensity, size factor, downscale (animation controls removed).
- Colour Grading: Includes vignette controls (strength, width, feather) moved from CRT tab.

### Shader Stack (top = last pass)
1. Scene content
2. Lighting (position + preset + animation)
3. Colour grading (includes vignette controls)
4. Film grain (with animation and manual controls)
5. CRT (aberration, scanlines - vignette moved to colour grading)

### Preset Families
- CRT: ~5 presets (vignette/aberration styles)
- Film Grain: ~10 presets (patterns and intensities)
- Colour Grading: ~30 stylised looks
- Lighting: ~30 presets (directional/spot/ambient) + 5 animations (pulse, flicker, sweep, orbit, breathe)

### Room API (Ren'Py‑style)
Keep calls simple and readable from script blocks. Example calls (map to simple FX helpers internally):

```
$ room.set_shader_preset("presets/shaders/noir.json")
$ room.crt(aberration=0.2, vignette=0.5)
$ room.grain(intensity=0.3, size="fine")
$ room.color_grade("NeoTokyo")
$ room.lighting(x=320, y=240, preset="Streetlamp", animation="flicker")
$ room.save_shader_preset("custom/shaders/my_custom.json")
```

Simple aliases continue to be supported for readability in logic:
`grade(name)`, `light(name)`, `grain(name)`, `crt_params(...)`, `vignette(...)`.

### JSON Preset Structure (simplified)
``` json
{
  "version": "2.1",
  "effects": {
    "crt": { "preset": "NeoCRT", "aberration": 0.2 },
    "grain": { "preset": "Fine", "intensity": 0.3, "size": 1.0, "downscale": 2.0, "anim_mode": "none" },
    "color_grade": { "preset": "NeoTokyo", "vignette_strength": 0.5, "vignette_width": 0.25, "vignette_feather": 1.0 },
    "lighting": { "preset": "Streetlamp", "x": 320, "y": 240, "animation": "flicker" }
  }
}
```

### Migration Notes
- Remove legacy editor/shader code under `game/editor/` and related bindings once the new editor is in place.
- Keep debug/info overlays and keybind docs aligned (`h`/`s` help/menu, `r` reset, `l` letterbox, `i` info, `F8` editor).

## Framework Simplification Policy (For Codex Agent)

When a new function/feature in the framework is confirmed stable, add a Simple API and document it thoroughly.

- Add concise aliases alongside existing long-form APIs (do not remove existing names).
- Keep room scripts in `game/rooms/<id>/scripts/`—do not place APIs inside `rooms/`.
- Put runnable examples and templates in `Doc/` only (not under `game/`).
- Update `game/api/README.md` with the new aliases and a quick usage section.

Short alias families to keep consistent:
- Rooms/Objects: `obj_move/obj_scale/obj_show/obj_hide`, `room_load/room_save/room_reset/room_update_file/room_export_config`.
- Display: `room_bg/bg_default/bg_fallback/bg_fallback_set`, `obj_visible/obj_props/obj_hidden`.
  - UI: `hotspot/hotspots`, `hover/unhover`, `exit_action`, `ui_exit_cfg`, `ui_add_button`.
- Interactions: `act_get/act_set/act_add/act_remove`, `obj_act_set/obj_act_clear/obj_actions`, `interact_show/interact_hide/interact_nav/interact_execute/interact_do`.
- Events: `once/once_ran/once_mark`, `on_first_enter/first_enter_run/first_enter_once/room_visited`.
- Breathing: `breath_*` helpers for targets, profiles, params, enable/disable.
- FX: `grade/light/grain`, `crt_on/crt_off/crt_params`, `vignette`, `letterbox_on/letterbox_off`.

Room script guidance:
- Prefer declaring `interactions` inline in object configs (e.g., in `ROOM1_OBJECTS`).
- Use concise helpers in logic: `crt_params`, `grade`, `light`, `grain`, `vignette`, `once`, `first_enter_once`, `breath_apply_profile`, `obj_hide`.

Artifact hygiene:
- After deleting `.rpy` files, also remove corresponding `.rpyc` so Ren'Py won’t load stale caches.
- Use `scripts/git-clean-artifacts.sh` regularly.

## Self‑Debug Workflow (For Codex Agent)

Goal: autonomously lint, build, and triage issues without relying on pasted tracebacks.

- Preferred commands
  - Lint: `bash scripts/run-game.sh --lint`
  - Compile only: `"$RENPY_SDK"/renpy.sh . --compile`
  - Run (debug): `bash scripts/run-game.sh --debug` (requires local Ren’Py SDK)

- SDK handling
  - Check `RENPY_SDK` env. If absent/unavailable, run lint only; ask user to set `RENPY_SDK` or adjust path in shell profile.
  - Validate `"$RENPY_SDK"/renpy.sh` exists before attempting run/compile.

- Triage artifacts after lint/run
  - Read error logs if present (in order):
    - `errors.txt`, `traceback.txt`, `log.txt`
  - Summarize errors with file:line and brief context.
  - Open and patch referenced files; prefer surgical changes with minimal scope.

- Loop & verify
  - After applying patches, re‑run lint (and compile if possible).
  - Repeat until lint is clean or remaining errors require user input.

- Non‑interactive defaults
  - If sandbox cannot run the SDK, default to static lint and code audit (ripgrep for anti‑patterns).
  - Offer next steps clearly: which command to run locally and what results to paste only if necessary.

- Useful one‑liners (agent may invoke):
  - `rg -n "^\s*(label|screen|transform|init|define|default)\b" game` — quick structure map
  - `rg -n "TODO|FIXME|XXX"` — find outstanding tasks
  - `rg -n "show_letterbox|hide_letterbox" game` — migration targets for `letterbox_on/off`
  - `rg --files --hidden -g '!**/.git/**' | rg '\\.(rpyc|rpymc)$'` — compiled caches

## Agent Audit Playbook

This section captures conventions observed in the current codebase and how the agent should operate when making changes.

- Source Map & Allowed Changes
  - `game/api/`: Public helpers. OK to add/extend functions. Prefer additive short aliases next to existing long names. Update `game/api/README.md`.
  - `game/core/`: Engine glue (builders, utils, rooms). OK for surgical fixes. Don’t redesign; keep compatibility (e.g., `merge_configs`, `create_*` stay).
  - `game/ui/`: Screens and UI. OK to refactor call sites to new aliases for readability. Preserve look and feel; keep bindings and zorders stable.
  - `game/overlays/`: Debug/info/letterbox overlays. OK to use new helpers (e.g., `letterbox_on/off`). Keep debug screens above letterbox.
  - `game/shaders/`: Shader transforms and hotkeys. Do NOT mutate shader state directly at call sites; use `grade/light/grain` wrappers. Maintain keybinds.
  - `game/logic/`: Global hooks and handler registration. OK to wire new global behaviors via hooks; keep hooks optional.
  - `game/rooms/<id>/scripts/`: Room config + room logic. Do NOT create new APIs here. Prefer inline `interactions` in config; keep logic to story/state.
  - `game/legacy/`, `game/libs/`, `game/tl/`: Keep intact; don’t remove or reformat. Legacy is reference; libs/tl loaded by Ren’Py.

- Room Configuration Guidelines
  - Define objects in `<room>_config.rpy` under `ROOM<id>_OBJECTS` using `merge_configs(...)` and builders from `core/config_builders.rpy`.
  - Prefer declaring `"interactions": [{"label":..., "action":...}, ...]` inline per object so UI can read menus without logic code.
  - Use `box_position` values like `auto`, `right+40`, `left+25` as needed; compute placement with `calculate_box_position`.
  - Keep assets in `rooms/<id>/sprites/` and reference with room-local constants.
  - Room registration: `ROOM_DEFINITIONS_<ID>` should map background and `objects` to the room ID.

- Room Logic Guidelines
  - Register a handler with `register_room_logic('<id>', Handler())`. Implement only needed hooks.
  - Use concise helpers for FX: `crt_params`, `grade`, `light`, `grain`, `vignette`, and `letterbox_on/off`.
  - One-time flows: use `once(...)` for global and `first_enter_once(room_id, ...)` for per-room.
  - Interactions: logic only overrides menus when story state requires it via `obj_act_set`. Otherwise keep `interactions` in config.
  - Use `obj_hide/obj_show` for visibility changes; avoid ad-hoc flags.
  - Dialogue: clear UI screens as needed (e.g., `interact_hide()`) and use `renpy.call_in_new_context(...)` when invoking labels from interaction flows.

- Interactions & UI
  - Type defaults live in `INTERACTION_ACTIONS`. Per-object actions override type defaults via `obj_act_set` or inline `interactions`.
  - Use `interact_show/interact_hide/interact_nav/interact_execute` for menus. Keep letterbox overlay and interaction zorders intact.
  - Hotspots: use `hotspot(...)`, `hotspots()`; respect `focus_mask` for precise clickable regions.
  - Main exploration screen: `room_exploration` (current main screen).
  - Interaction Menu System: `interaction_menu` screen is registered in `config.overlay_screens` for automatic display when `interaction_menu_active = True`.
  - Description Persistence: Object descriptions remain visible during interaction menus by excluding only `editor_open` from visibility conditions, not `interaction_menu_active`.

- Shader & FX
  - Do not set `shader_states` directly at call sites. Use `grade('preset')`, `light('preset')`, `grain('preset')` for readability and UI notifications.
  - CRT: use `crt_on/off`, `crt_params(...)`, `vignette(...)`. Keep `restart_interaction` calls minimal and contained (helpers already refresh).
  - Letterbox: prefer `letterbox_on()/letterbox_off()` wrappers; leave timing to the shader system.
  - Letterbox speed: `letterbox_on/off(speed)` accepts `'very_slow'|'slow'|'normal'|'fast'|'very_fast'` or `0..4`.

- Breathing System
  - Store per-room/object settings in `ROOM_BREATHING_SETTINGS`. Use `breath_*` helpers to apply, change, and save.
  - Profiles: `breath_apply_profile/breath_save_profile/breath_delete_profile`. Don’t change file emit format.
  - Tuner/UI: rely on `get_tuner_target_object()`; cycle with `breath_next()`.

- Audio
  - Prefer `room_play_audio(room_id)` and `room_fade_audio(duration)` rather than raw channel manipulation.
  - Rooms can specify `music` and `ambient_channel` in their definitions.

- Sizing Utilities
  - Use `get_original_size_by_path(...)` and `calc_size(...)` from `core/room_utils.rpy` when computing dimensions or masks.

- Logging & Messaging
  - Lightweight user-facing: `show_hint(...)`, `narrate(...)`.
  - Avoid assuming `common_logging` is loaded (it may be disabled). Wrap debug logs in try/except.

- Keybinds & Overlays
  - Keep documented inputs consistent (`r` reset, `l` letterbox, `i` info, `F8` editor). Update Doc if modified.

- Docs & Examples
  - Add or update `game/api/README.md` when new aliases are added.
  - Put implementation examples in `Doc/` (e.g., `Doc/simple_room_example.md`). Never under `game/` unless part of runtime.

- Lint & Hygiene
  - Run `scripts/run-game.sh --lint` after changes touching `.rpy` files.
  - Remove `.rpyc` when deleting `.rpy` so Ren'Py doesn't load stale caches.
  - Use `scripts/git-clean-artifacts.sh` to keep repo clean.

## Interaction System Troubleshooting

### Common Issues and Fixes

**Interaction menus not appearing when clicking objects:**
- Ensure `interaction_menu` screen is added to `config.overlay_screens`
- Check that `show_interaction_menu()` properly sets `interaction_menu_active = True`
- Verify `interaction_target` is set to the clicked object name
- Confirm object hotspots are properly configured in `object_hotspots()` screen

**Description boxes disappearing during interactions:**
- Remove `not interaction_menu_active` from description visibility conditions
- Keep description logic: `if (not input_locked) and (not editor_open) and current_hover_object:`
- Ensure `current_hover_object` remains set when interaction menu opens

**Menu positioning issues:**
- Use `get_menu_base_position(obj_name)` for automatic positioning
- Account for screen edges and letterbox areas in calculation
- Test with different object positions and screen resolutions
