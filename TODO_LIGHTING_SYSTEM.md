# 2D Lighting System Implementation Todo

**Project**: Snatchernauts Framework - Enhanced 2D Lighting Integration  
**Status**: In Progress  
**Last Updated**: 2025-01-10

## Overview

Implementation of a comprehensive 2D lighting system for the RenPy visual novel framework, including JSON-based lighting presets, real-time editing, z-order layering, and seamless integration with existing room/object systems.

## Completed ✅

- **2D Lighting Shaders Foundation** (`game/shaders/shaders_lighting_2d.rpy`)
  - Multi-light support (up to 12 simultaneous lights)
  - Light types: ambient, point, spot, directional, area (rect/ellipse)
  - 2D-specific features: normal mapping, distance attenuation, soft shadows
  - Animation support for dynamic lighting effects

- **Directory Structure** 
  - `json/presets/lights/` - Shipped lighting presets
  - `json/custom/lights/` - User custom lighting presets
  - Migrated legacy `light_*.json` files to new structure

- **Lighting Presets Conversion**
  - Converted legacy presets to new 2D lighting JSON schema v1.0
  - Created comprehensive presets: cyberpunk, neon, daylight, moonlight, etc.
  - Schema supports light arrays, global settings, animations

- **Robust Lighting IO Service** (`game/api/api_lights_io.rpy`)
  - RenPy-compatible JSON loading and validation
  - Comprehensive schema validation with helpful error messages
  - Change detection and atomic writes
  - Normalisation and defaults handling
  - File discovery and preset management

## Pending Tasks 📋

### 1. Create 2D Lighting Runtime Adapter 🎯 **PRIORITY HIGH**

**File**: `game/api/api_lights_runtime.rpy`

**Core Requirements:**
- Map JSON lighting data to 2D shader uniforms
- Manage active scene lights (maximum 12 concurrent)
- Handle light culling and performance optimisation
- Integrate with existing RenPy display system
- Support light animations from JSON configurations
- Z-order aware lighting calculations

**Technical Details:**
```python
# Key functions needed:
- lights_runtime_load_preset(preset_name) 
- lights_runtime_apply_lights(lights_data)
- lights_runtime_update_uniforms()
- lights_runtime_set_light_property(light_id, property, value)
- lights_runtime_animate_lights(delta_time)
- lights_runtime_cull_lights(viewport)
- lights_runtime_calculate_z_order_interactions()
```

**Integration Points:**
- Connect to `shaders_lighting_2d.rpy` shader uniforms
- Use `api_lights_io.rpy` for loading presets
- Integrate with RenPy's transform and displayable system
- Support real-time property updates for editor
- Z-order based light-object interaction calculations

**Performance Considerations:**
- Light distance culling (off-screen lights)
- LOD system for distant lights  
- Batch uniform updates
- Animation interpolation caching
- Z-order sorting optimisation

### 2. Implement Z-Order System for Lighting and Object Layering 🎯 **PRIORITY HIGH**

**Target Files**:
- `game/api/api_room.rpy` (extend object management)
- `game/api/api_lights_runtime.rpy` (z-order lighting calculations)
- Room configuration files (add z-order to objects)

**Z-Order System Requirements:**

**Depth-Based Lighting Interactions:**
```python
# Z-order lighting rules:
- Lights only affect objects on same or higher z-levels
- Background lights (z=0-10) don't illuminate foreground objects (z=40+)
- Proper atmospheric depth and layering
- Support for lighting "passes" by z-level
```

**Object and Light Layering Standards:**
```python
# Recommended z-order conventions:
Z_ORDER_BACKGROUND = 0      # Background elements (walls, floors)
Z_ORDER_BG_LIGHTING = 10    # Background lighting (ambient, distant)
Z_ORDER_MIDGROUND = 20      # Midground objects (furniture, NPCs)
Z_ORDER_MG_LIGHTING = 30    # Midground lighting (lamps, windows)
Z_ORDER_FOREGROUND = 40     # Foreground objects (interactive items)
Z_ORDER_FG_LIGHTING = 50    # Foreground lighting (spotlights, effects)
Z_ORDER_UI_EFFECTS = 60     # UI-level lighting effects
```

**Technical Implementation:**
- Extend room objects and light objects with `z_order` property
- Z-order based shader calculations for realistic depth
- Editor controls for z-order manipulation
- Sorting algorithms for render order
- Z-order aware light culling and optimisation

**API Functions:**
```python
# New z-order management functions:
- obj_set_z_order(obj_id, z_order)
- obj_get_z_order(obj_id) 
- light_set_z_order(light_id, z_order)
- light_get_z_order(light_id)
- room_sort_by_z_order()  # Sort all objects by z-order
- lights_get_affecting_objects(light_id)  # Get objects in light's z-range
```

**YAML Schema Extension:**
```yaml
# Room configuration with z-order:
room1_config:
  objects:
    desk:
      x: 400, y: 300
      z_order: 20  # Midground object
    lamp:
      x: 450, y: 200  
      z_order: 30  # Midground lighting
  lighting:
    lights:
      - id: "ambient_bg"
        type: "ambient"
        z_order: 10  # Background lighting
      - id: "desk_lamp" 
        type: "point"
        z_order: 30  # Midground lighting
        affects_z_range: [20, 40]  # Which z-levels this light affects
```

### 3. Build Lighting Presets Browser UI 🎯 **PRIORITY MEDIUM**

**File**: `game/ui/ui_lights_browser.rpy`

**Requirements:**
- Browse `json/presets/lights/` and `json/custom/lights/`
- File selector with thumbnails/previews
- Apply/load functionality with immediate preview
- Integration with existing UI system styling
- Z-order preview for complex lighting setups

**UI Components:**
```renpy
# Screens needed:
screen lights_browser_main()      # Main browser interface
screen lights_preset_card()       # Individual preset cards
screen lights_preview_panel()     # Real-time preview with z-order
screen lights_browser_toolbar()   # Load/save/delete actions
screen lights_z_order_view()      # Z-order layer visualization
```

**Features:**
- Grid/list view toggle
- Search and filtering by light type/tags/z-order
- Preview system showing light arrangement and layering
- Quick apply with undo/redo support
- Import/export for sharing presets
- Z-order layer toggle for complex scene understanding

### 4. Integrate Comprehensive Lighting Editor into Object/Scene Editor 🎯 **PRIORITY HIGH**

**Target Files**: 
- `game/ui/ui_screens_room.rpy` (main room editor)
- Related UI files for room editing workflow

**Editor Mode Requirements:**
- **Hotkey Access**: Ctrl+F8 to toggle object/scene editor (if available, check for conflicts with existing shortcuts)
- **Animations & Shaders**: Must be ENABLED during editing for real-time preview
- **Game Logic**: Must be DISABLED to prevent interference with editing
- **Description Windows**: Must be DISABLED (no object descriptions during editing)
- **Interaction Menus**: Must be DISABLED (no interaction popups during editing)
- **Object Highlighting**: Game objects must be visually highlighted when "edit game objects" mode is selected
- **Editor State Isolation**: Editing mode should not trigger normal game interactions

**Advanced Editing Features:**

**Spatial Controls:**
- **Position (X, Y)**: Drag-and-drop light positioning with snap-to-grid
- **Size/Radius**: Interactive resizing handles for light coverage
- **Rotation**: Rotation gizmos for directional/spot lights  
- **Z-order**: Layer management with visual z-order indicators

**Visual Interface:**
- Light gizmos/indicators overlaid on room view
- Different gizmo styles per light type (circle for point, cone for spot)
- Real-time preview of lighting effects during editing
- Visual feedback for light coverage areas and z-order interactions
- Z-order layer view toggle (show/hide objects by z-level)
- **Game object highlighting** when in "edit game objects" mode (outline, glow, or overlay)
- **Editor-specific visual feedback** distinct from normal game UI

**Editor State Management:**
```python
# Editor mode control functions needed:
- toggle_object_scene_editor() -> main toggle function for Ctrl+F8
- editor_enter_mode() -> disable game logic, enable shaders/animations
- editor_exit_mode() -> restore normal game state
- editor_disable_game_interactions() -> block descriptions/menus
- editor_enable_object_highlighting(enabled=True)
- editor_force_shader_preview(enabled=True) 
- editor_suppress_game_logic(enabled=True)
```

**Hotkey Integration:**
```python
# Hotkey binding implementation:
- Check existing F8 (shader editor) and ensure Ctrl+F8 doesn't conflict
- Integrate with existing keymap system in RenPy
- Provide alternative access method if Ctrl+F8 is unavailable
- Consider context-sensitive hotkey availability (only in room scenes)
```

**Property Panels:**
```renpy
# UI sections needed:
- Light Selection Panel (list of scene lights with z-order)
- Transform Properties (position, rotation, scale, z-order)
- Light Properties (intensity, color, radius, falloff)
- Z-Order Settings (z-level, affected z-range)
- Animation Settings (type, speed, parameters)  
- Advanced Settings (layer, tags, enabled state)
```

**Multi-Light Management:**
- Light selection system (click to select, multi-select support)
- Copy/paste light properties including z-order
- Duplicate lights with offset positioning and z-order
- Group operations (enable/disable multiple lights)
- Z-order based grouping and layer management

**Z-Order Visual Tools:**
- Layer visibility toggles (show/hide by z-order range)
- Z-order timeline/stack view
- Visual indicators for light-object interactions
- Color-coded z-order levels in editor

### 5. Integrate Lighting Data with Existing Room YAML Save System 🎯 **PRIORITY HIGH**

**Target Files**:
- `game/api/api_room.rpy` (extend save/load functions)
- Room config files (e.g., `rooms/room1/scripts/room1_config.rpy`)

**Integration Points:**

**Room Save Functions:**
```python
# Extend existing functions:
- room_save() -> include lighting data and z-order
- room_update_file() -> persist light objects with z-order to YAML  
- room_load() -> restore lighting configurations and z-order
- room_reset() -> restore default lighting and object layering
```

**YAML Schema Extension:**
```yaml
# Example room configuration with lighting and z-order:
room1_config:
  objects:
    # existing room objects with z-order...
    computer:
      x: 500, y: 400
      z_order: 20
    desk_lamp:
      x: 520, y: 350
      z_order: 25
  lighting:
    preset: "cyberpunk_office"  # Optional preset reference
    lights:
      - id: "ambient_lighting"
        type: "ambient"
        z_order: 5
        color: [0.1, 0.1, 0.2]
        intensity: 0.8
      - id: "desk_light"
        type: "point"
        position: [520, 350]
        z_order: 30
        affects_z_range: [20, 40]  # Affects midground objects
        intensity: 2.5
        radius: 150
        color: [1.0, 0.9, 0.7]
    global_settings:
      global_intensity: 1.0
      ambient_base: [0.05, 0.05, 0.1]
      z_order_enabled: true
```

**Backward Compatibility:**
- Existing rooms without lighting or z-order data continue to work
- Default z-order assignment for objects without z-order specified
- Migration path for rooms with legacy lighting setups
- Graceful fallback when z-order system is disabled

### 6. Add Lighting Object Persistence and State Management 🎯 **PRIORITY HIGH**

**Integration with Room Object System:**

**Store Extensions:**
```python
# Extend existing room object stores:
store.room_objects -> include light objects with z-order
store.room_lights -> dedicated lighting state (optional)
store.selected_light -> currently selected light for editing
store.z_order_enabled -> toggle for z-order system
```

**Object Management API:**
```python
# New functions mirroring existing object APIs:
- light_move(light_id, x, y)
- light_scale(light_id, radius_scale) 
- light_rotate(light_id, angle)
- light_set_z_order(light_id, z_order)
- light_show(light_id) / light_hide(light_id)
- light_props(light_id) -> get properties including z-order
- light_set_prop(light_id, property, value)
```

**Z-Order Object Management:**
```python
# Z-order specific functions:
- obj_move_to_front(obj_id) -> highest z-order
- obj_move_to_back(obj_id) -> lowest z-order  
- obj_move_up(obj_id) -> increase z-order by 1
- obj_move_down(obj_id) -> decrease z-order by 1
- get_objects_by_z_order() -> sorted list
- get_z_order_range() -> min/max z-order values
```

**Persistent State:**
- Light object changes including z-order saved with `room_save()`
- Integration with existing `persistent.room_overrides` system
- Support for per-room lighting and z-order customisation
- Maintain light and z-order state across game sessions

### 7. Implement Comprehensive Error Handling 🎯 **PRIORITY MEDIUM**

**Error Types and Handling:**

**JSON Loading Errors:**
- Malformed JSON syntax -> show line/column info
- Invalid light type -> suggest valid types
- Missing required fields -> highlight missing properties
- Out-of-range values -> show valid ranges with current value
- Invalid z-order values -> suggest valid z-order ranges

**Runtime Errors:**
- Light limit exceeded (>12) -> graceful degradation with z-order priority
- Shader compilation failures -> fallback to simple lighting
- Missing preset files -> show available alternatives
- Invalid light references -> remove broken lights with notification
- Z-order conflicts -> automatic z-order resolution

**User-Friendly Feedback:**
```renpy
# Error notification system:
- Toast notifications for minor issues
- Modal dialogs for critical errors  
- Inline validation in property panels
- Status indicators in lights browser
- Z-order conflict warnings in editor
```

**Recovery Mechanisms:**
- Automatic fallback to "light_off" preset
- Malformed light object removal with user confirmation
- Preset validation before applying to scene
- Backup/restore system for lighting configurations
- Z-order auto-correction for conflicts

### 8. Create Lighting System Documentation and Testing 🎯 **PRIORITY LOW**

**Documentation Requirements:**

**JSON Schema Documentation:**
```markdown
# Files to create:
- docs/lighting/schema-reference.md
- docs/lighting/preset-creation-guide.md  
- docs/lighting/integration-examples.md
- docs/lighting/migration-from-legacy.md
- docs/lighting/z-order-system-guide.md
- docs/lighting/performance-optimization.md
```

**Usage Examples:**
- Step-by-step lighting setup tutorials
- Z-order layering best practices
- Common lighting scenarios (interior, exterior, dramatic, etc.)
- Performance best practices
- Troubleshooting guide for z-order issues

**Test Presets:**
```json
# Create comprehensive test cases:
- test_all_light_types.json (showcase each light type)
- test_z_order_layering.json (complex z-order scenarios)
- test_performance_stress.json (12 animated lights with z-order)
- test_edge_cases.json (boundary values, unusual configurations)
- test_backwards_compatibility.json (legacy format support)
```

**Migration Tools:**
- Script to convert old `light_*.json` files to new schema
- Z-order assignment tool for existing rooms
- Validation tool for existing presets
- Batch conversion utilities

### 9. Add Performance Optimisation and Quality Levels 🎯 **PRIORITY LOW**

**Performance Features:**

**Z-Order Aware Culling System:**
```python
# Implementation areas:
- Distance-based culling (lights too far from viewport)
- Frustum culling (lights outside camera view)
- Z-order culling (lights that don't affect visible objects)
- Contribution culling (lights with minimal impact)  
- Occlusion culling (lights blocked by opaque objects)
```

**Quality Levels:**
```python
# Settings for different performance tiers:
quality_levels = {
    "high": {
        "max_lights": 12, 
        "shadows": True, 
        "animations": True,
        "z_order_precision": "full"
    },
    "medium": {
        "max_lights": 8, 
        "shadows": True, 
        "animations": False,
        "z_order_precision": "simplified" 
    }, 
    "low": {
        "max_lights": 4, 
        "shadows": False, 
        "animations": False,
        "z_order_precision": "disabled"
    }
}
```

**Performance Monitoring:**
- Frame time tracking for lighting system
- Light count warnings when approaching limits
- Z-order calculation performance metrics
- Automatic quality adjustment based on performance
- Performance metrics in debug overlay

**Optimisation Strategies:**
- Z-order aware light LOD (level of detail) system
- Shader variant compilation for different light counts and z-order modes
- Uniform buffer optimisation for light data
- Animation interpolation caching
- Z-order sorting cache for static scenes

## Implementation Priority Order 📊

1. **Z-Order System** (Foundation for proper lighting layering)
2. **Runtime Adapter** (Core functionality with z-order support)
3. **Room YAML Integration** (Persistence with z-order data)  
4. **Object State Management** (Editor foundation with z-order)
5. **Comprehensive Editor UI** (User interface with z-order tools)
6. **Presets Browser** (User experience)
7. **Error Handling** (Polish and reliability)
8. **Documentation and Testing** (Maintenance)
9. **Performance Optimisation** (Enhancement)

## Architecture Notes 📝

**Key Design Principles:**
- **RenPy Compatibility**: All code must work within RenPy's restricted Python environment
- **Z-Order First**: All lighting calculations must respect depth layering
- **Backward Compatibility**: Existing rooms and saves must continue working
- **Performance First**: Lighting system should not impact frame rate significantly
- **User Experience**: Editing should be intuitive with clear z-order visualization

**Z-Order System Design:**
- Z-order values are integers (0-100 typical range)
- Lower z-order = background, higher z-order = foreground
- Lights affect objects at same or higher z-order levels
- Editor provides visual z-order management tools
- Performance optimized z-order calculations

**Integration Strategy:**
- Treat lights as first-class objects alongside room sprites
- Leverage existing room object management infrastructure
- Maintain consistency with existing UI/UX patterns
- Support both preset-based and custom lighting workflows
- Z-order system integrates seamlessly with existing object management

**Quality Assurance:**
- Test with various light configurations and room layouts
- Validate z-order interactions in complex scenes
- Validate performance across different hardware tiers
- Ensure graceful degradation when limits are exceeded
- Comprehensive error handling with helpful user feedback

---

*This document serves as the master tracking file for 2D lighting system implementation with z-order support. Update as tasks are completed and new requirements discovered.*
