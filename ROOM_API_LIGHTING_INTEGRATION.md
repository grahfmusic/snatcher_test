# Room API Lighting Integration

## Overview

This document outlines the comprehensive extensions made to the room API system to support the new 2D lighting system with z-order layering in the Snatchernauts RenPy framework.

## Core Features Implemented

### 1. Z-Order Support for Room Objects

All room objects now include z-order properties for proper layering:

```python
# Z-order properties added to every room object
{
    "z": 12,                    # Z-order value (0-24, default 12)
    "light_affectable": True,   # Whether object can be affected by lighting
    "layer": "room_mid"        # Derived lighting layer bucket
}
```

**Key Functions:**
- `ensure_object_z_properties(obj_data, obj_name)` - Ensures objects have z-order properties
- `place_object_on_lighting_layer(obj_name, obj_data)` - Places objects on correct lighting layers
- `set_object_z_order(obj_name, new_z)` - Updates object z-order with layer refresh
- `move_object_to_front(obj_name)` / `move_object_to_back(obj_name)` - Layer movement utilities

### 2. Z-Order Layer Buckets

Objects are automatically sorted into lighting layer buckets:
- **room_bg** (z: 0-8) - Background layer (ambient lighting, walls, floors)
- **room_mid** (z: 8-16) - Middle layer (objects, furniture, most lighting)
- **room_fg** (z: 16-24) - Foreground layer (UI elements, foreground lighting)

### 3. Enhanced Room Save/Load with Lighting Persistence

**Save Function Extensions:**
- Saves z-order and lighting properties for all objects
- Persists active lighting configuration and quality settings
- Stores lights as serializable dictionaries

**Load Function Extensions:**
- Ensures all objects have z-order properties on load
- Applies persistent lighting configurations automatically
- Restores lighting state using `room_apply_lighting_from_data()`

### 4. YAML Configuration Support

**Export to YAML:**
```python
export_room_to_yaml(room_id, output_path=None)
```
- Exports complete room configuration including lighting
- Includes metadata and timestamp information
- Preserves z-order and lighting properties

**Import from YAML:**
```python
import_room_from_yaml(yaml_path, room_id=None)
```
- Imports room configuration with lighting data
- Applies lighting immediately if importing current room
- Stores lighting in persistent overrides for future loads

**Batch Operations:**
```python
export_all_rooms_to_yaml(base_dir=None)
```
- Exports all room definitions to YAML files
- Creates organized directory structure
- Reports success/failure statistics

### 5. Lighting Data Integration

**Persistence Structure:**
```yaml
lighting:
  quality: "high"
  lights:
    - type: "point"
      position: [400, 300]
      z: 15
      color: [1.0, 0.8, 0.6]
      intensity: 1.2
      falloff: 0.8
      # ... additional light properties
```

**Runtime Integration:**
- `room_apply_lighting_from_data(lighting_data)` - Applies saved lighting
- Automatic light serialization/deserialization
- Quality level persistence and restoration

## API Reference

### Z-Order Management Functions

```python
# Get/set z-order
get_object_z_order(obj_name) -> int
set_object_z_order(obj_name, new_z) -> bool

# Layer movement
move_object_up_layer(obj_name) -> bool
move_object_down_layer(obj_name) -> bool
move_object_to_front(obj_name) -> bool
move_object_to_back(obj_name) -> bool

# Query functions
get_objects_by_z_order(room_id=None) -> list
get_objects_in_z_range(min_z, max_z, room_id=None) -> list
```

### Lighting Integration Functions

```python
# Apply lighting data
room_apply_lighting_from_data(lighting_data) -> bool

# YAML operations
export_room_to_yaml(room_id, output_path=None) -> str|bool
import_room_from_yaml(yaml_path, room_id=None) -> str|bool
export_all_rooms_to_yaml(base_dir=None) -> dict|bool
```

### Migration Functions

```python
# Ensure backward compatibility
migrate_room_objects_z_order() -> int
```

## Directory Structure

```
game/rooms/
├── <room_id>/
│   ├── config/
│   │   └── <room_id>_config.yaml     # Room configuration with lighting
│   └── scripts/
│       └── <room_id>_config.rpy      # Original RenPy definitions
└── rooms_export/                     # Batch export directory
    ├── room1_config.yaml
    ├── room2_config.yaml
    └── ...
```

## Integration with Lighting System

The room API extensions seamlessly integrate with the lighting system:

1. **Layer Management**: Objects are automatically placed on correct lighting layers based on z-order
2. **Light Culling**: Lights are culled based on z-order compatibility with room objects
3. **Persistence**: Lighting configurations are saved and restored with room state
4. **Quality Scaling**: Lighting quality settings persist across room loads

## Usage Examples

### Basic Z-Order Management
```python
# Move object to specific z-layer
set_object_z_order("desk", 18)  # Places on foreground layer

# Move object to front/back
move_object_to_front("character")
move_object_to_back("background_item")
```

### YAML Configuration Workflow
```python
# Export current room with lighting
export_room_to_yaml("office_room")

# Import room configuration
import_room_from_yaml("game/rooms/office_room/config/office_room_config.yaml")

# Batch export all rooms
results = export_all_rooms_to_yaml()
print(f"Exported {len(results['exported'])} rooms")
```

### Lighting State Management
```python
# Save room with current lighting
save_room_changes()  # Now includes lighting data

# Load room (lighting restored automatically)
load_room("office_room")
```

## Error Handling

The system includes comprehensive error handling:
- Graceful fallback when lighting system unavailable
- Validation of z-order ranges (0-24)
- File I/O error handling for YAML operations
- Backward compatibility for objects without z-order properties

## Performance Considerations

- Z-order updates trigger layer placement refresh
- YAML operations use change detection to avoid unnecessary writes
- Lighting data serialization optimized for RenPy compatibility
- Migration functions run only when needed

## Conclusion

These room API extensions provide a robust foundation for the 2D lighting system while maintaining full backward compatibility with existing room configurations. The integration supports both runtime manipulation and persistent storage of complex lighting setups with proper z-order layering.
