# Baseline Capture Matrix
## Editor Multi-Light Z-Order Feature Development

**Date**: 2025-01-10  
**Purpose**: Document current state before implementing Multi-Light Z-Order enhancements  
**Feature Branch**: `feature/editor-multi-light-zorder`

## Capture Scenarios

### 1. Editor UI States
| Scenario ID | Description | File Pattern | Notes |
|-------------|-------------|--------------|-------|
| UI-01 | Main menu / splash screen | `baseline_ui-main_view-00.png` | Clean state before entering game |
| UI-02 | F8 Shader Editor - closed | `baseline_ui-f8closed_view-00.png` | Normal gameplay view |
| UI-03 | F8 Shader Editor - open | `baseline_ui-f8open_view-00.png` | Current shader editor interface |
| UI-04 | F8 Shader Editor - presets tab | `baseline_ui-f8presets_view-00.png` | Current preset selection UI |
| UI-05 | F8 Shader Editor - lighting tab | `baseline_ui-f8lighting_view-00.png` | Current dynamic lighting controls |
| UI-06 | In-game editor (if exists) | `baseline_ui-editor_view-00.png` | Any existing scene editing tools |

### 2. Scene Rendering States
| Scenario ID | Description | File Pattern | Notes |
|-------------|-------------|--------------|-------|
| SCENE-01 | Room1 - no effects | `baseline_scene-01_lights-00_view-00.png` | Clean baseline |
| SCENE-02 | Room1 - single light | `baseline_scene-01_lights-01_view-00.png` | One dynamic light active |
| SCENE-03 | Room1 - multiple lights | `baseline_scene-01_lights-02_view-00.png` | Multiple lights if supported |
| SCENE-04 | Room1 - CRT shader only | `baseline_scene-01_shader-crt_view-00.png` | CRT without lighting |
| SCENE-05 | Room1 - CRT + lighting | `baseline_scene-01_shader-crt_lights-01_view-00.png` | Combined effects |
| SCENE-06 | Room1 - layered objects | `baseline_scene-01_layers-mixed_view-00.png` | Objects at different depths |

### 3. Shader Preset Application
| Scenario ID | Description | File Pattern | Notes |
|-------------|-------------|--------------|-------|
| PRESET-01 | Apply shipped CRT preset | `baseline_preset-crt_shipped_view-00.png` | From `json/presets/shaders/` |
| PRESET-02 | Apply custom grade preset | `baseline_preset-grade_custom_view-00.png` | From `json/custom/shaders/` |
| PRESET-03 | Apply light_ shader preset | `baseline_preset-light_shader_view-00.png` | Current shader-based lighting |
| PRESET-04 | Preset notification message | `baseline_preset-notification_view-00.png` | On-screen confirmation |

### 4. Animation and Effects
| Scenario ID | Description | File Pattern | Notes |
|-------------|-------------|--------------|-------|
| ANIM-01 | Static lighting | `baseline_anim-static_view-00.mp4` | No animation |
| ANIM-02 | Animated lighting | `baseline_anim-dynamic_view-00.mp4` | If lighting animation exists |
| ANIM-03 | Shader transitions | `baseline_anim-transitions_view-00.mp4` | Applying/removing effects |

## Directory Structure
```
docs/baseline/editor-multi-light-zorder/20250110/
├── capture-matrix.md (this file)
├── screenshots/
│   ├── baseline_ui-*.png
│   ├── baseline_scene-*.png
│   └── baseline_preset-*.png
└── videos/
    └── baseline_anim-*.mp4
```

## File Naming Convention
- **Format**: `baseline_<type>-<id>_<descriptor>_view-<angle>.ext`
- **Type**: ui, scene, preset, anim
- **ID**: Unique identifier within type (01, 02, main, f8open, etc.)
- **Descriptor**: Additional context (lights-01, shader-crt, etc.)
- **Angle**: Camera/view angle (00 for standard, 01+ for alternates)
- **Extension**: png for screenshots, mp4 for videos

## Target Areas for Capture

### Current Limitations to Document
- **Z-Order**: How objects currently layer (if at all)
- **Lighting**: Current dynamic lighting capabilities and controls
- **F8 Integration**: Which lighting controls are in F8 vs elsewhere
- **File Structure**: Where presets are stored (`json/presets/shaders/`, `json/custom/shaders/`)
- **Editor State**: What editing capabilities currently exist

### Key Features to Validate
- Shader preset detection from both shipped and custom directories
- Light_ shader presets vs dynamic lighting distinction
- Current lighting animation (if any)
- Object layering and depth rendering

## Quality Standards
- **Screenshots**: PNG format, full resolution
- **Videos**: MP4, 10-20 seconds, reasonable compression
- **Coverage**: Each scenario captured at least once
- **Consistency**: Same scene setup across related captures
- **Documentation**: Each file referenced in baseline.md with purpose

## Notes for Manual Capture
1. Launch via `.\scripts\run-game.ps1` (no flags for normal run)
2. Navigate to Room1 or primary test scene
3. Use Ren'Py screenshot key 'S' if available, or Win+Shift+S
4. For videos, use Win+G (Windows Game Bar) or preferred recorder
5. Test both shipped and custom preset directories
6. Document any errors or limitations encountered
