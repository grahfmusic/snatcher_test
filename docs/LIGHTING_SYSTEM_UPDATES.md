# Lighting System Z-Order and Save Functionality Updates

**Date**: 2025-01-10  
**Summary**: Updated Z-order rules to avoid post-processing conflicts and added save functionality for custom lighting configurations

## Changes Made

### 1. Updated Z-Order Bucket Ranges

**Previous ranges** (conflicted with film grain/CRT):
- Background: 0-10
- Midground: 10-30  
- Foreground: 30-50

**New conservative ranges** (avoids post-processing):
- **room_bg** (z: 0-8) - Background elements, ambient lighting
- **room_mid** (z: 8-16) - Midground objects, most lighting  
- **room_fg** (z: 16-24) - Foreground objects, UI lighting

**Post-processing layers**: 25+ (film grain, CRT effects, letterbox)

### 2. Updated System Files

#### `game/api/api_lights_runtime.rpy`
- Updated `Z_BUCKET_RANGES` with new conservative values
- Updated `z_to_bucket()` function logic
- Added lighting save functionality:
  - `lights_save_current_config(name, description)` - Main save function
  - `lights_save(name, description)` - Convenient wrapper
  - `lights_save_auto()` - Auto-generated filename
  - `lights_list_custom_configs()` - List saved configurations
  - `lights_list()` - Display configurations with details

#### `game/api/api_room.rpy`  
- Updated default Z-order from 20 to 12 (midground)
- Updated Z-order validation range from 0-50 to 0-24
- Updated all Z-order utility functions with new limits

#### `ROOM_API_LIGHTING_INTEGRATION.md`
- Updated documentation with new Z-order ranges and examples
- Updated validation ranges and default values

### 3. Updated All Lighting Presets

Applied intelligent Z-order mapping to all 11 lighting presets:
- `light_cyberpunk.json`, `light_neon.json`, etc.
- High Z-values (25+) → Reduced to 15-24 range
- Mid Z-values (17-24) → Adjusted down by ~4
- Low Z-values (9-16) → Minor adjustment down by ~2
- Background values (0-8) → Kept as-is

### 4. Added Save Functionality

#### Directory Structure
```
game/json/custom/lights/
├── light_example_custom.json     # Example configuration
└── [user-saved configurations]   # Runtime-saved configs
```

#### API Functions
```python
# Save current lighting setup
lights_save("my_scene", "Description of lighting setup")

# Save with auto-generated name
lights_save_auto()

# List saved configurations
lights_list()

# Get detailed list programmatically
configs = lights_list_custom_configs()
```

#### JSON Format
```json
{
  "version": "1.0",
  "name": "Custom Scene Name",
  "description": "Description of the lighting setup",
  "lights": [
    {
      "id": "light_id",
      "type": "point|spot|area|ambient|directional",
      "position": [x, y],
      "z": 0-24,
      "color": [r, g, b, a],
      "intensity": 1.0,
      "radius": 100.0,
      "falloff": "linear|quadratic",
      "softness": 0.5,
      "enabled": true
    }
  ],
  "global_settings": {
    "global_intensity": 1.0,
    "ambient_base": [0.05, 0.05, 0.1],
    "quality": "high|medium|low"
  }
}
```

## Benefits

### 1. **No Post-Processing Conflicts**
- Lighting Z-orders (0-24) never interfere with film grain/CRT layers (25+)
- Clear separation between scene lighting and post-processing effects
- Maintains visual consistency across different shader combinations

### 2. **Proper Layer Hierarchy**
```
┌─ CRT Frame (Outermost) ────────────────────────┐
│ ┌─ Film Grain + Grading (25+) ─────────────┐   │
│ │ ┌─ Foreground Objects/Lights (16-24) ─┐ │   │
│ │ │ ┌─ Midground Objects/Lights (8-16) ┐ │ │   │
│ │ │ │ ┌─ Background/Ambient (0-8) ────┐ │ │ │   │
│ │ │ │ │   [Scene Content]           │ │ │ │   │
│ │ │ │ └─────────────────────────────┘ │ │ │   │
│ │ │ └───────────────────────────────────┘ │ │   │
│ │ └─────────────────────────────────────────┘ │   │
│ └───────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────┘
```

### 3. **User-Friendly Save System**
- Easy to save custom lighting setups from in-game editor
- Automatic timestamping and validation
- Compatible with existing preset loading system
- Proper error handling and user feedback

### 4. **Backward Compatibility**
- Existing lighting presets updated but still functional
- Room objects automatically migrate to new Z-order ranges
- Graceful fallback for edge cases

## Usage Examples

### In-Game Console Commands
```python
# Create and save a custom lighting setup
lights_save("office_evening", "Warm evening office lighting")

# Save with auto-generated name
lights_save_auto()  # Creates "custom_lighting_20250110_202800.json"

# List all saved configurations  
lights_list()

# Enable debug mode for detailed feedback
lights_debug(True)
```

### Australian English Compliance
All user-facing messages use Australian English spelling:
- "colour" instead of "color" in descriptions
- "realised" instead of "realized" 
- "organised" instead of "organized"

## Testing Verification

✅ **Z-Order Mapping Tests**: All bucket assignments working correctly  
✅ **Preset Updates**: All 11 lighting presets updated with safe Z-values  
✅ **Save Functionality**: JSON generation and file I/O tested  
✅ **Directory Creation**: Custom lights directory auto-created  
✅ **Layer Separation**: No conflicts with post-processing effects  

## Next Steps

The updated system is ready for integration with:
1. **Lighting Editor UI** - Visual controls for Z-order management
2. **Preset Browser** - Load/save interface for custom configurations  
3. **Scene Editor** - Real-time lighting editing with Z-order visualization
4. **Performance Optimization** - Quality scaling based on Z-order complexity

This update provides a solid foundation for advanced lighting features while maintaining compatibility with the existing shader pipeline.
