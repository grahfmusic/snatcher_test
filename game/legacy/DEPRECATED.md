# DEPRECATED - Legacy Code (Removed)

## Status
Legacy `.rpy` code in this directory has been removed. This folder now contains documentation only to aid migration.

## Migration Guide
Use the modern modules instead:
- `core/core_room_system.rpy` — Room system core
- `core/core_room_exploration.rpy` — Room exploration logic and screens
- `api/api_room.rpy` — Public room API

Main exploration screen name: `room_exploration` (replaces any earlier `room_exploration_shaders`).

If your code still references legacy labels (e.g., `explore_room`), update call sites to use the current screen and APIs.
