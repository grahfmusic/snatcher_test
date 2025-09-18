# Legacy (Docs Only)

This folder now contains documentation only. The legacy `.rpy` code files have been removed.

Use the modern systems instead:
- Main exploration screen: `room_exploration` (in `game/ui/ui_screens_room.rpy`).
- Room system core: `game/core/core_room_system.rpy`.
- Room exploration glue: `game/core/core_room_exploration.rpy`.
- Public APIs: `game/api/` (e.g., `api_room.rpy`).

Note: If you still have old references like `explore_room` or `room_exploration_shaders` in local branches, update them to `room_exploration` and current APIs.
