# Snatchernauts Framework

**RenPy Visual Novel Framework for Interactive Adventures**

## Project Context

**Type**: RenPy Game Framework  
**Language**: Python/RenPy Script  
**Version**: 0.5.4
**Status**: Production-ready framework for visual novels and point-and-click adventures

## Environment Setup

```bash
# Required environment variable
export RENPY_SDK=~/renpy-8.4.1-sdk

# Optional development automation
export AUTO_SYNC_README=1
export AUTO_SYNC_WIKI=1
```

**CRITICAL**: The `RENPY_SDK` environment variable must be set to `~/renpy-8.4.1-sdk` for all development work. This SDK version is required for compatibility with the framework's Ren'Py architecture and features.

## Key Commands

### Development
```bash
# Linux/macOS: Launch game with debug and linting
./scripts/run-game.sh --lint --debug

# Linux/macOS: Normal development launch
./scripts/run-game.sh

# Linux/macOS: Code quality check
./scripts/lint.sh
```

Windows equivalents:
- PowerShell: `powershell -ExecutionPolicy Bypass -File scripts\run-game.ps1 --lint` (or `--debug`, `--compile`)
- CMD: `scripts\run-game.cmd --lint` (or `--debug`, `--compile`)

Note: If the dev machine is Windows, prefer the PowerShell/CMD scripts instead of the Bash script.

### Build & Deploy
```bash
# Multi-repository push
./scripts/push-both.sh

# Documentation synchronisation
./scripts/sync-doc.sh

# Make targets
make lint
make push-both
make doc-sync
```

## Architecture Overview

### Shared Preset Discovery
- Centralised API at `game/api/api_presets.rpy`
- Shader preset categories discovered from `json/presets/shaders/` and `json/custom/shaders/` using filename prefixes:
  - `crt_`, `grain_`, `grade_`
  - Note: Legacy `light_` shader presets are no longer supported
- Lighting presets discovered from `json/presets/lights/` and `json/custom/lights/`
- Helper shows notifications when presets are applied via `presets_notify_applied(kind, name, category=None)`

### Core Directories
- `game/` - Ren'Py game source
  - `api/` - Public API helpers (room_api, ui_api, interactions_api, etc.)
  - `core/` - Core engine (config, logging, rooms, utilities)
  - `ui/` - Interface screens and components
  - `overlays/` - Debug/info/letterbox overlays
  - `shaders/` - Visual effects (CRT, film grain, grading with vignette, lighting)
  - `logic/` - Game logic hooks and global handlers
  - `rooms/` - Room-specific logic and assets
    - `room{n}/scripts/{room}_logic.rpy` - Room-specific interactions
    - `room{n}/sprites/` - Room assets
  - `editor/` - Full-screen Shader Editor (F8) implementation
  - `json/presets/shaders/` - Shipped shader presets (filename prefixes: `crt_`, `grain_`, `grade_`) - **v2.1 format**
  - `json/presets/lights/` - Lighting presets - **v1.0 unified format**
  - `json/custom/shaders/` - User shader presets saved by the editor - **v2.1 format**
  - `legacy/` - Reference code (keep intact)
  - `libs/` - External libraries
  - `tl/` - Translations
- `scripts/` - Development automation tools
- `Doc/` - Documentation (replaces `Wiki/`)

### Key Framework Features
- **Room-based exploration** with pixel-perfect interactions
- **Professional visual effects** (CRT shaders, dynamic lighting)
- **Multi-input support** (mouse, keyboard, gamepad)
- **Modular architecture** with clean API separation
- **Development tools** with automated linting and debugging

### Room Logic Pattern (Ren'Py Style)
Room-specific interactions use Ren'Py labels and minimal Python delegation:
```
game/rooms/{room_id}/scripts/{room_id}_logic.rpy
```

#### State Variables
```renpy
# Use Ren'Py default for persistent state
default room1_visited = False
default room1_first_visit = True
default room1_items_collected = []

# Character definitions
define narrator = Character(None, what_italic=True)
define npc_char = Character("NPC Name", color="#4a90e2")
```

#### Room Entry Label
```renpy
label room1_enter:
    # Set up atmosphere with effects
    $ suppress_room_fade_once = True
    
    # Apply visual effects using simplified API
    $ crt_params(warp=0.2, scan=0.5, chroma=0.9)
    $ light('car_headlights')
    $ vignette(0.95, 0.14)  # Now uses color_grade system (v2.1)
    $ grade('midnight_chase')
    $ grain('subtle')
    
    # Handle first visit
    if room1_first_visit:
        $ room1_first_visit = False
        narrator "You enter the room for the first time..."
    
    return
```

#### Interaction Labels
```renpy
label room1_examine_object:
    narrator "You examine the object carefully..."
    
    if "clue" not in room1_items_collected:
        $ room1_items_collected.append("clue")
        narrator "You found an important clue!"
    else:
        narrator "Nothing new here."
    
    return

label room1_talk_npc:
    npc_char "Welcome to this room."
    
    menu:
        "Ask about the case":
            npc_char "I've heard strange rumours..."
        "Leave conversation":
            narrator "You step back."
    
    return
```

#### Python Handler (Minimal Delegation)
```python
init -1 python:
    class Room1Logic:
        def on_room_enter(self, room_id):
            # Delegate to Ren'Py label
            renpy.call("room1_enter")
            
        def on_object_interact(self, room_id, obj_name, action_id):
            # Route to appropriate labels
            if obj_name == 'evidence' and action_id == 'examine':
                renpy.call("room1_examine_object")
                return True
            elif obj_name == 'npc' and action_id == 'talk':
                renpy.call_in_new_context("room1_talk_npc")
                return True
            return False
    
    register_room_logic('room1', Room1Logic())
```

## Quick Navigation

**Documentation**: `Doc/01-Overview.md`  
**Getting Started**: `Doc/02-Getting-Started.md`  
**Development Tools**: `DEVELOPMENT_TOOLS.md`  
**Room Creation**: `ROOM_STRUCTURE_GUIDE.md`  
**Agent Guidelines**: `AGENTS.md`

## Debug Controls (In-Game)
- `i` - Toggle info overlay
- `Cmd+Shift+F12` / `Ctrl+Shift+F12` - Cycle debug overlay verbosity
- `1-4` - Scanline presets
- `r` - Reset all shaders
- `l` - Toggle letterbox
- `F8` - Shader editor (CRT, Grain, Colour Grading, Presets/IO)
- `Ctrl+F8` - Lighting editor (2D lighting with real-time animation support)

## Coding Standards

### RenPy Architecture Compliance
**CRITICAL RULE**: All code must strictly adhere to RenPy's architecture, environment, and ruleset:

- **File Structure**: Use `.rpy` files for all game code (NOT `.py` files)
- **Initialization**: Use RenPy's `init` phases (`init -10`, `init -1`, `init 0`, etc.)
- **Module Imports**: Only import modules that RenPy supports (avoid complex Python dependencies)
- **Type Hints**: Avoid Python 3.5+ type hints as RenPy may not support them
- **API Usage**: Use `renpy.loader` for file access, RenPy's persistent system for state
- **Error Handling**: Use `ValueError` instead of `JSONDecodeError` (RenPy compatibility)
- **Code Blocks**: All Python code must be within `init python:` or `python:` blocks
- **Script Structure**: Follow RenPy label/screen/transform patterns, not pure Python classes
- **Asset Loading**: Use RenPy's asset loading system, not direct file system access
- **State Management**: Use RenPy's `default`, `define`, and persistent variables

**Validation**: All code must compile and run within RenPy's restricted Python environment.

### Style Guidelines
- **Indentation**: 4 spaces for RenPy/Python blocks (no tabs)
- **Naming Conventions**:
  - Functions/variables: `snake_case`
  - Constants: `UPPER_CASE`
  - Files: lowercase with underscores
  - Screens: prefixed clearly (e.g., `screens_room.rpy`)
  - Room/object IDs: lowercase (e.g., `room1`, `computer_terminal`)

### File Naming Convention
**MANDATORY RULE**: All files must follow the structure: `{directory_name}_{description_of_function}.ext`

- Directory name comes first (e.g., `api`, `core`, `ui`, `shaders`)
- Use underscores (`_`) to replace spaces in descriptions
- Description should clearly indicate what the script does
- Examples:
  - `game/api/api_lights_io.rpy` (API for lighting I/O)
  - `game/core/core_room_manager.rpy` (Core room management)
  - `game/ui/ui_context_menu.rpy` (UI context menu implementation)
  - `game/shaders/shaders_lighting_2d.rpy` (2D lighting shaders)
  - `game/logic/logic_interactions.rpy` (Interaction logic)

**Exceptions**: Configuration files, documentation, and assets may use descriptive names without directory prefixes.

### Code Organisation
- Game logic in `game/logic/`
- Public API calls in `game/api/`
- UI concerns in `game/ui/`
- Keep room scripts in `game/rooms/<id>/scripts/` (do NOT place APIs inside rooms)
- Put runnable examples and templates in `Doc/` only (not under `game/`)

## Testing & Quality

### User Testing & Approval Workflow
**CRITICAL REQUIREMENT**: Before making any commits or pushing changes:

1. **Test Each Function**: Thoroughly test every modified or new function
2. **User Confirmation**: Get explicit user approval for each feature/fix
3. **Functional Verification**: Confirm all reported issues are resolved
4. **No Premature Commits**: Do not stage files or make commits until user testing is complete
5. **Interactive Testing**: Walk through functionality with the user step-by-step

**Example Workflow**:
```
1. User reports: "Panel dragging doesn't work"
2. Agent implements fix
3. Agent asks: "Please test panel dragging - can you now drag the properties panel?"
4. User confirms: "Yes, dragging works now"
5. Only then proceed with git add/commit
```

### Linting
```bash
# Run lint checks before commits
./scripts/run-game.sh --lint
# Or via make
make lint
```

### Compilation
```bash
# Compile only (no run)
"$RENPY_SDK"/renpy.sh . --compile
```

### CI Requirements
- GitHub workflow validates project structure
- All Python blocks in `.rpy` files must compile
- Fix all reported errors before PR merge

## Commit & Pull Request Guidelines

### Commit Format
- Short, imperative subject
- Use conventional commit scopes:
  - `feat(ui): add context menu`
  - `fix(core): clamp scale`
  - `docs(wiki): update room guide`

### Pull Request Requirements
- Include summary and rationale
- Provide test steps
- Link related issues
- Add screenshots/GIFs for UI changes
- Note downstream impacts for API changes
- Update `Doc/` when changing public behaviour

## Framework API Conventions

### Simplified API Aliases
When functions are stable, add concise aliases alongside existing long-form APIs:

#### Room/Object Operations
- `obj_move`, `obj_scale`, `obj_show`, `obj_hide`
- `room_load`, `room_save`, `room_reset`, `room_update_file`, `room_export_config`

#### Display Management
- `room_bg`, `bg_default`, `bg_fallback`, `bg_fallback_set`
- `obj_visible`, `obj_props`, `obj_hidden`

#### UI Helpers
- `hotspot`, `hotspots` (respect `focus_mask` for clickable regions)
- `hover`, `unhover`
- `exit_action`, `editor_action`

#### Interactions
- `act_get`, `act_set`, `act_add`, `act_remove`
- `obj_act_set`, `obj_act_clear`, `obj_actions`
- `interact_show`, `interact_hide`, `interact_nav`, `interact_execute`, `interact_do`

#### Events
- `once`, `once_ran`, `once_mark`
- `on_first_enter`, `first_enter_run`, `first_enter_once`, `room_visited`

#### Effects (Shaders & FX)
- `grade`, `light`, `grain` (with animation support), `vignette` (uses color_grade system in v2.1)
- `crt_on`, `crt_off`, `crt_params` (vignette deprecated, use `vignette()` instead)
- `letterbox_on`, `letterbox_off` (with speed control)
- **Shader Presets v2.1**: All JSON presets now use version "2.1" format with vignette settings in colour grade section

### Shader Preset Migration (v2.0 → v2.1)

**Migration Script**: Use `scripts/ensure-grade-vignette.py` to update presets:
```bash
# Check all files (dry run)
python scripts/ensure-grade-vignette.py --all

# Update specific files
python scripts/ensure-grade-vignette.py file1.json file2.json
```

**Key Changes**:
- Version updated from `"2.0"` to `"2.1"`
- Vignette settings moved from `crt` to `color_grade` section:
  ```json
  {
    "version": "2.1",
    "effects": {
      "color_grade": {
        "vignette_strength": 0.25,
        "vignette_width": 0.8,
        "vignette_feather": 0.2
      }
    }
  }
  ```
- All `grade_*` and `grain_*` presets now include vignette settings
- CRT sections no longer contain vignette parameters

#### Breathing System
- `breath_apply_profile`, `breath_save_profile`, `breath_delete_profile`
- Settings stored in `ROOM_BREATHING_SETTINGS`

#### Audio Management
- Rooms manage audio directly via standard Ren'Py `play music` / `stop music` commands in room logic handlers
- Legacy `play_room_audio` flow removed to avoid conflicts

## Room Development Best Practices

### Configuration
- Define objects in `<room>_config.rpy` using `merge_configs(...)` and builders
- Prefer declaring `"interactions": [{"label":..., "action":...}, ...]` inline per object
- Use `box_position` values: `auto`, `right+40`, `left+25`
- Keep assets in `rooms/<id>/sprites/` with room-local constants
- Room registration: `ROOM_DEFINITIONS_<ID>` maps background and objects to room ID

### Logic Implementation
- Register handlers with `register_room_logic('<id>', Handler())`
- Use concise FX helpers: `crt_params`, `grade`, `light`, `grain`, `vignette`
- One-time flows: `once(...)` (global), `first_enter_once(room_id, ...)` (per-room)
- Visibility: use `obj_hide`/`obj_show` (avoid ad-hoc flags)
- Clear UI screens when needed: `interact_hide()`
- Use `renpy.call_in_new_context(...)` for invoking labels from interaction flows

## Housekeeping

### Artifact Cleanup
```bash
# Remove compiled caches (*.rpyc, cache/, saves/)
# Preview changes
bash scripts/git-clean-artifacts.sh --dry-run

# Apply cleanup
bash scripts/git-clean-artifacts.sh
```

### Important Notes
- Never commit SDKs or secrets
- Remove `.rpyc` when deleting `.rpy` files (Ren'Py loads stale caches)
- Keep heavy assets organised under `game/`
- Update `game/api/README.md` when adding new APIs
- Verify referenced SFX files exist under `game/audio/ui/`

## Lighting System

### Lighting Preset Format (v1.0)

**Unified JSON Structure**: All lighting presets now follow a consistent format with direct light object definitions:

```json
{
  "version": "1.0",
  "name": "Preset Name",
  "description": "Detailed description of the lighting effect",
  "lights": [
    {
      "id": "unique_light_id",
      "type": "point|spot|area|ambient",
      "enabled": true,
      "position": [0.0, 0.0],  // Normalised coordinates (0.0-1.0)
      "z": 25,                 // Z-order for layering
      "color": [1.0, 1.0, 1.0, 1.0],  // RGBA colour
      "intensity": 1.0,
      "radius": 200.0,
      "falloff": "quadratic|linear",
      "softness": 0.5,
      // Additional properties for spot lights
      "angle": 0.8,
      "direction": [0.0, 1.0],
      // Animation properties (optional)
      "animate": {
        "type": "pulse|flicker|strobe|colour_cycle|orbit",
        "speed": 1.0,
        "intensity_variation": 0.2,
        "randomness": 0.1  // For flicker type only
      }
    }
  ],
  "global_settings": {
    "global_intensity": 1.0,
    "ambient_base": [0.1, 0.1, 0.1]
  }
}
```

### Available Lighting Presets

**Standardised Presets** (all using v1.0 format with animation support):
- `light_candle.json` - Gentle candle flicker with warm orange glow (animated: flicker)
- `light_cyberpunk.json` - Electric blue and magenta neon accents
- `light_dawn.json` - Cool dawn lighting with soft blues and warm highlights
- `light_disco.json` - Colourful disco lighting with rotating red, blue, and green beams
- `light_film_noir.json` - Classic noir with dramatic shadows and venetian blind effects
- `light_firelight.json` - Warm flickering fire for cozy indoor scenes (animated: flicker)
- `light_fluorescent.json` - Harsh fluorescent office lighting with cool tones
- `light_moonlight.json` - Cool moonlight with silver highlights and deep shadows
- `light_neon.json` - Bright electric neon glow with vivid colours
- `light_neon_cyberpunk.json` - Multi-colour neon with pulse animation (animated: pulse)
- `light_off.json` - Neutral baseline lighting (no effects)
- `light_spotlight.json` - Dramatic spotlight with focused beam and rim lighting
- `light_storm.json` - Lightning flashes with storm clouds
- `light_streetlamp.json` - Urban cold blue-white light with sharp shadows
- `light_sunset.json` - Warm golden hour with rich oranges and reds
- `light_underglow.json` - Cool blue underglow effect from below
- `light_window_day.json` - Natural daylight streaming through windows

### Animation System

**Real-time Light Animations**: The lighting system supports 5 animation types with 60fps real-time updates:

1. **Pulse** - Smooth sine wave intensity variation for breathing effects
2. **Flicker** - Random intensity variation with smoothing for realistic candle/fire effects
3. **Strobe** - Fast on/off intensity changes for dramatic lighting
4. **Colour Cycle** - Intensity pulsing (extensible for future colour transitions)
5. **Orbit** - Circular movement with intensity variation for dynamic effects

**Animation Properties**:
- `type`: Animation style (pulse, flicker, strobe, colour_cycle, orbit)
- `speed`: Animation playback speed multiplier (0.1-5.0x)
- `intensity_variation`: How much the intensity varies (0.0-1.0)
- `randomness`: Randomness factor for flicker type (0.0-1.0)

**Runtime System**:
- Delta-time based calculations for consistent speed across framerates
- Automatic callback system using `renpy.timeout()` at ~60fps
- Performance optimised - only animates lights marked as `animated`
- Base intensity preservation for accurate animation calculations

### Lighting Editor Integration

**Coordinate System**: Presets use normalised coordinates (0.0-1.0) that are automatically converted to screen pixel coordinates by the lighting editor.

**Loading Process**:
1. Editor reads JSON from `game/json/presets/lights/`
2. Converts normalised `position` arrays to `x`, `y` screen coordinates
3. Maps `type` field to `kind` for Light class compatibility
4. Handles `direction` vectors for spot lights
5. Processes animation properties for real-time effects
6. Applies lights via `lights_runtime_apply_lights()`

**Editor Controls**:
- **Ctrl+F8** - Open/close lighting editor with preset browser
- **P** - Toggle preset browser panel
- **F12** - Toggle help panel
- **R** - Open properties panel for selected light
- Draggable panels with 40px drag handles
- Grid snapping with configurable grid size
- Real-time light manipulation with proper z-order layering
- Full animation controls: enable/disable, type cycling, speed, intensity variation
- Live animation preview while editing

### Migration from v2.1 Reference Format

**Completed Migration**: All lighting presets have been converted from the old reference-based format:
```json
// OLD v2.1 format (deprecated)
{
  "effects": {
    "lighting": {
      "preset": "preset_name",
      "x": 640, "y": 288,
      "strength": 1.5
    }
  }
}
```

To the new v1.0 direct light objects format with explicit light definitions, proper z-ordering, and normalised coordinates for cross-resolution compatibility.

## Debug Workflow

### Self-Debug Commands
```bash
# Lint only
bash scripts/run-game.sh --lint

# Compile check
"$RENPY_SDK"/renpy.sh . --compile

# Debug run (requires local Ren'Py SDK)
bash scripts/run-game.sh --debug
```

### Error Triage
Check logs in order:
1. `errors.txt`
2. `traceback.txt`
3. `log.txt`

### Useful One-Liners
```bash
# Quick structure map
rg -n "^\s*(label|screen|transform|init|define|default)\b" game

# Find TODOs
rg -n "TODO|FIXME|XXX"

# Find migration targets
rg -n "show_letterbox|hide_letterbox" game

# Find compiled caches
rg --files --hidden -g '!**/.git/**' | rg '\.(rpyc|rpymc)$'
```
