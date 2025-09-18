# Room-Based Directory Structure Guide

## Overview

The project now uses a comprehensive room-based directory structure that organizes all assets, logic, and scripts per room. This provides better organization, easier maintenance, and cleaner separation of concerns.

## Directory Structure

```
rooms/
├── room1/
│   ├── sprites/           # Room1-specific sprite images
│   ├── video/             # Room1-specific video files
│   ├── audio/
│   │   ├── music/         # Background music for room1
│   │   ├── sfx/           # Sound effects for room1
│   │   └── speech/        # Voice/speech audio for room1
│   └── scripts/
│       ├── room1_config.rpy    # Object definitions, animations, audio setup
│       ├── room1_logic.rpy     # Interaction logic and behavior
│       └── detective_scenes.rpy # Room1-specific dialogue scenes
├── room2/
│   ├── sprites/
│   ├── video/
│   ├── audio/
│   │   ├── music/
│   │   ├── sfx/
│   │   └── speech/
│   └── scripts/
│       ├── room2_config.rpy    # Template provided
│       └── room2_logic.rpy     # Template provided
└── room3/
    ├── sprites/
    ├── video/
    ├── audio/
    │   ├── music/
    │   ├── sfx/
    │   └── speech/
    └── scripts/
        ├── room3_config.rpy    # Template provided
        └── room3_logic.rpy     # Template provided
```

## File Purposes

### Configuration Files (`roomX_config.rpy`)

These files handle:
- **Asset path definitions** - Define paths to sprites, audio, video
- **Object definitions** - All objects in the room with their properties
- **Sprite animations** - Transform animations for room objects
- **Audio configuration** - Music tracks, sound effects, speech files
- **Environmental effects** - Lighting, atmosphere, weather settings
- **Initialization functions** - Setup code for objects, audio, effects

### Logic Files (`roomX_logic.rpy`)

These files handle:
- **Room-specific interactions** - Custom behavior for objects in that room
- **State tracking** - Variables specific to room progress/state
- **Event handling** - Response to player actions in the room
- **Room enter/exit logic** - Setup/teardown when entering/leaving room

### Dialogue/Scene Files

These files handle:
- **Character dialogue** - Conversation scenes specific to room characters
- **Cutscenes** - Room-specific story sequences
- **Narrative content** - Room-specific storytelling elements

## Using the System

### Creating a New Room

1. **Create directory structure:**
   ```bash
   mkdir -p rooms/room4/{sprites,video,audio/{music,sfx,speech},scripts}
   ```

2. **Copy and customize templates:**
   - Copy `room2_config.rpy` template
   - Copy `room2_logic.rpy` template
   - Customize for your new room

3. **Add assets:**
   - Place sprite images in `sprites/`
   - Place audio files in appropriate `audio/` subdirectories
   - Place video files in `video/`

### Room Configuration Example

```python
# Define room4 objects
define ROOM4_OBJECTS = {
    "mysterious_door": merge_configs({
        "x": 400, "y": 300,
        "scale_percent": 100,
        "width": 150, "height": 200,
        "image": ROOM4_SPRITES_PATH + "door.png",
        "description": "An ornate door with strange markings.",
        "object_type": "door",
        "idle_animation": "door_glow",
        "interaction_sounds": {
            "open": ROOM4_SFX_PATH + "door_creak.ogg"
        }
    },
    create_desaturation_config(DESATURATION_PRESETS["neon_intense"]),
    create_animation_config({"hover_scale_boost": 1.05}))
}
```

### Animation System

Define custom animations for each room:

```python
# Room-specific animations
transform door_glow():
    linear 2.0 matrixcolor BrightnessMatrix(0.1)
    linear 2.0 matrixcolor BrightnessMatrix(-0.1)
    repeat

transform character_walk():
    linear 3.0 xoffset 50
    linear 3.0 xoffset -50
    repeat
```

### Audio System

Each room gets its own audio channels:

```python
def setup_room4_audio():
    renpy.music.register_channel("room4_ambient", "sfx", True)
    renpy.music.register_channel("room4_effects", "sfx", False)
    renpy.music.register_channel("room4_speech", "voice", False)
```

### Logic System

Handle room-specific interactions:

```python
class Room4Logic:
    def on_object_interact(self, room_id, obj_name, action_id):
        if obj_name == 'mysterious_door' and action_id == 'open':
            if store.player_has_key:
                narrate("The door creaks open...")
                return True
            else:
                narrate("The door is locked tight.")
                return True
        return False
```

## Asset Organization Best Practices

### Sprites
- Use descriptive filenames: `detective_idle.png`, `detective_talking.png`
- Keep sprite sheets in room-specific directories
- Use consistent naming conventions across rooms

### Audio
- **Music**: Long-form background tracks (`room1_ambient.ogg`)
- **SFX**: Short sound effects (`paper_rustle.wav`, `footsteps.ogg`)
- **Speech**: Voice acting files (`detective_intro.ogg`)

### Video
- Cutscene videos specific to the room
- Environmental background videos (rain, fire, etc.)
- Transition sequences

## Integration with Main System

The room-based system integrates seamlessly with the existing framework:

1. **Room definitions** are automatically combined from all `roomX_config.rpy` files
2. **Logic handlers** are automatically registered with the main logic system
3. **Asset paths** are consistently organized and easily maintainable
4. **Animations and effects** are room-specific but use the same underlying system

## Migration from Old System

The old system still works as a fallback:
- If room-specific configs aren't found, fallback definitions are used
- Existing room1 logic was moved to `rooms/room1/scripts/`
- Main `room_config.rpy` now acts as a coordinator rather than containing all definitions

## Benefits

### Organization
- **Clear separation** of room-specific content
- **Easy to find** assets and scripts for each room
- **Scalable** - easy to add new rooms without cluttering

### Maintainability
- **Modular** - work on one room without affecting others
- **Team-friendly** - different developers can work on different rooms
- **Version control** - easier to track changes per room

### Performance
- **Lazy loading** - only load assets when needed
- **Room-specific channels** - better audio management
- **Modular initialization** - faster startup times

### Development Workflow
- **Template-based** - easy to create new rooms from templates
- **Consistent structure** - same layout for every room
- **Asset management** - clear organization of all room content

## Advanced Features

### Dynamic Loading
Rooms can be loaded/unloaded dynamically to manage memory:

```python
def preload_room_assets(room_id):
    """Preload assets for smoother transitions"""
    room_config = ROOM_DEFINITIONS[room_id]
    # Preload sprites, audio, etc.

def cleanup_room_assets(room_id):
    """Clean up unused assets when leaving room"""
    # Free memory, stop audio channels, etc.
```

### Cross-Room State
State can be shared between rooms while keeping room-specific logic separate:

```python
# Global state
default investigation_progress = 0
default evidence_collected = []

# Room-specific state  
default room1_detective_trust = 0
default room2_puzzle_solved = False
```

This new structure provides a solid foundation for building complex, multi-room games with excellent organization and maintainability.
