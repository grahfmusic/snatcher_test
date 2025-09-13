# Snatchernauts Framework

[![version](https://img.shields.io/badge/version-0.5.5-blue)](CHANGELOG.md)
[![license: MIT](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![GitHub mirror](https://img.shields.io/badge/github-mirror-blue?logo=github)](https://github.com/grahfmusic/snatchernauts_framework)
[![gitlab pipeline](https://gitlab.com/grahfmusic/snatchernauts_framework/badges/main/pipeline.svg)](https://gitlab.com/grahfmusic/snatchernauts_framework/-/pipelines)

Create exploration‑driven visual novels that feel tactile and cinematic. Snatchernauts turns static scenes into interactive rooms with pixel‑accurate hotspots, context‑aware action menus, clean event‑based logic, and professional visual effects — all on top of Ren’Py.

## Inspiration
- Inspired by Kojima’s Snatcher and Policenauts — investigation‑forward rooms, micro‑discoveries that reward attention, and cinematic presentation without getting in your way.

## Why Snatchernauts (vs. Vanilla Ren’Py)
- Exploration built‑in: Pixel‑accurate hotspots, contextual menus, keyboard/gamepad navigation — no bespoke screens or glue needed.
- Clean separation: Predictable room/object hooks keep behavior out of UI layouts; your story code stays readable and testable.
- Simple to scale: Start fast with the Simple API, then opt into deeper modules as systems grow.
- Cinematic polish: CRT, grading, grain, vignette, letterbox — tuned with friendly wrappers and dev hotkeys.
- Ship confidently: Clear project layout, lint/run scripts, comprehensive docs, and production workflows.

## Core Features
- Pixel‑perfect interaction: Clicks respect transparency; no clunky rectangles.
- Context‑aware actions: Per‑object menus adapt to story state and inventory.
- Event‑driven logic: Global and per‑room hooks for enter, hover, and interactions.
- Simple API: Define rooms/objects/logic in minutes with concise helpers.
- Cinematic FX: CRT, colour grading (with vignette), film grain (with animation), letterbox; live tuning support via F8 editor.
- Multi‑input: Mouse + keyboard + gamepad navigation out of the box.
- Production tools: Scripts for lint/run/sync, CI‑friendly structure.
- Docs that scale: API references, examples, troubleshooting, build guides.

## Quick Start
- Install Ren’Py 8.4.x and set your SDK path:
```bash
export RENPY_SDK=~/renpy-8.4.1-sdk
```
- Run the project:
```bash
scripts/run-game.sh
```
- Useful variants:
```bash
scripts/run-game.sh --lint
scripts/run-game.sh --debug
"$RENPY_SDK"/renpy.sh . --compile
```

## 5‑Minute Example (Simple API)
```renpy
init python:
    from game.api.simple_api import simple_room, character, item, door, simple_room_logic, go_to_room
    from game.api.simple_fx import grade, letterbox_on, vignette
    from game.api.interactions_api import obj_act_set

    # Define a room with inline interactions
    simple_room(
        "lobby",
        background="rooms/lobby/sprites/bg.png",
        character("reception", "rooms/lobby/sprites/reception.png", 820, 340,
                  interactions=[["Talk", "talk"], ["Ask for Key", "ask_key"]])["reception"],
        item("poster", "rooms/lobby/sprites/poster.png", 120, 320,
             description="A faded concert poster.", interactions=[["Examine", "examine"]])["poster"],
        door("hall_door", "rooms/lobby/sprites/door.png", 1040, 360,
             interactions=[["Enter Hall", "enter"]])["hall_door"],
    )

    # Lightweight room logic
    def _enter(room_id):
        letterbox_on(); grade("neo_noir")

    def _hover(room_id, obj):
        if obj == "poster":
            vignette(d_strength=0.02)

    def _interact(room_id, obj, action):
        if obj == "reception" and action == "ask_key":
            obj_act_set("reception", [{"label": "Talk", "action": "talk"}])
            return False
        if obj == "hall_door" and action == "enter":
            go_to_room("hall")
            return True  # consume default behavior
        return False

    simple_room_logic("lobby", on_enter=_enter, on_hover=_hover, on_interact=_interact)
```

## Effects & Hotkeys

Preset directories
- Shipped presets: game/json/presets/shaders/ (filtered by filename prefix)
- User presets: game/json/custom/shaders/
- CRT: control via wrappers and the F8 Shader Editor (no global hotkeys).
- Grading/Lighting/Grain: preset cycling and live tuning helpers.
- Vignette/Letterbox: cinematic control with simple on/off and param deltas.

## Architecture
- `game/api/`: Public helpers
  - Room: room/object management, navigation, audio helpers
  - Interactions: action defaults, per‑object overrides, menu flow
  - Display: background and object visibility/properties
  - UI: hotspots, focus masks, button configs
  - Simple API: fast room/object/logic helpers + FX wrappers
- `game/core/`: Options, logging, room config utilities
- `game/ui/`: Screens and UI composition
- `game/overlays/`: Info, debug, letterbox overlays
- `game/shaders/`: CRT, colour grading (with vignette), film grain, lighting; setup and hotkeys
- `game/editor/`: F8 shader editor with tabbed interface

## Production & Tooling
```bash
scripts/run-game.sh --help
```
- Lint and compile before commits; use the launcher for builds and distribution.
- Optional repo utilities for auto‑syncing README/wiki and pushing to mirrors.

## Documentation
- Getting Started: `Doc/02-Getting-Started.md`
- Simple API Overview: `Doc/Simple-API-Overview.md`
- Room Logic Examples: `Doc/Room-Logic-Examples.md`
- APIs: `Doc/10-API-Room.md` • `Doc/11-API-Interactions.md` • `Doc/12-API-Display.md` • `Doc/13-API-UI.md`
- Effects & Shaders: `Doc/07-Effects-and-Shaders.md`
- Troubleshooting: `Doc/15-Troubleshooting.md`
- Style Guide (docs): `Doc/STYLE_GUIDE.md`

## License
- MIT — free for personal and commercial projects.

## Get Started
- Clone, set `RENPY_SDK`, run `scripts/run-game.sh`, and build your first interactive room.

