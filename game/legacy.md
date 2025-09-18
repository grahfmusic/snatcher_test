# Legacy (Docs Only)

The legacy `.rpy` code files have been removed. This document remains to point to the modern equivalents:

- Main exploration screen: `room_exploration` (see `game/ui/ui_screens_room.rpy`).
- Room system core: `game/core/core_room_system.rpy`.
- Exploration glue: `game/core/core_room_exploration.rpy`.
- Public APIs: `game/api/`.

Update any old references like `explore_room` or `room_exploration_shaders` to the current screen and APIs.
