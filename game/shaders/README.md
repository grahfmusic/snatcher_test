# Snatchernauts Framework - Shader System (Simplified)

## Overview

The shader system has been cleaned up and simplified to focus on only the most essential visual effects. This improves performance, reduces complexity, and maintains the core visual identity of the game.

## What Remains (Core Effects)

### 1. CRT Shader (`crt_shader.rpy`)
- **Purpose**: Authentic retro CRT monitor effects
- **Features**: 
  - Screen warp/curvature
  - Animated scanlines 
  - Chroma aberration (color bleeding)
  - Horizontal vignette
  - Live parameter tuning
- **Controls**: `C` key, `A` key, `1-4` keys, `[],` `-=`, `0`
- **Performance**: ~2-3ms overhead when enabled

### 2. Color Grading (professional presets)
- **Purpose**: Cinematic looks and mood
- **Files**: `shaders_cinematic_presets.rpy`, `shaders_complete_grading.rpy`
- **Usage**: Apply presets from the Shader Editor (F8) or via preset IO
- **Performance**: Minimal; applied as overlay

### 3. Letterbox Shader (`letterbox_shader.rpy`)
- **Purpose**: Cinematic letterbox bars for dialogue and cutscenes
- **Features**:
  - Smooth height and alpha animations
  - Configurable bar color and opacity
  - Automatic activation during dialogue
  - Manual toggle support
- **Controls**: `L` key, automatic during dialogue
- **Performance**: Negligible overhead

### 4. Breathing Warp (Python, not GLSL)
- Purpose: Per-object chest/shoulder/head breathing implemented as a Python DynamicDisplayable (no custom shader), with a tuner UI.
- Files: `ui/chest_warp.rpy`, `shaders/breathing_tuner_ui.rpy`, `api/breathing_api.rpy`.
- Behavior: Any object with `breath_enabled: True` animates using its own saved parameters. Tuner edits affect only the selected object.
- Keys: F6 debug bands, F7 toggle tuner, TAB switches target; `[` `]` cycle profiles.

## What Was Removed

The following complex shader effects have been removed to improve performance and reduce maintenance overhead:

### Atmospheric Effects (Removed)
- **Vintage/Sepia Shader**: Color grading and aging effects
- **Lighting Shader**: Dynamic lighting (candlelight, streetlight, moonlight)
- **Rain/Weather Shader**: Particle effects and storm atmospheres

### Investigation Effects (Removed)
- **Depth of Field Shader**: Focus effects (center/left/right/close)
- **Edge Detection Shader**: Evidence highlighting and danger visualization
- **Mystery Reveal Shader**: Progressive unveiling effects
- **Flashlight Shader**: Investigative lighting with beam types

### Complex Systems (Removed)
- **Color Grading Shader**: Scene mood adjustment (cool/warm/noir)
- **Detective Atmospheric Shaders**: Crime scene, warehouse ambiance
- Composite preset stacks and alternate shader layer screens

## Why This Simplification?

### Performance Benefits
- **Reduced GPU Load**: From 15+ complex shaders to 3 essential ones
- **Memory Efficiency**: Less shader compilation and caching
- **Smoother Gameplay**: Consistent 60+ FPS on integrated graphics
- **Faster Loading**: Reduced shader initialization time

### Maintenance Benefits  
- **Cleaner Codebase**: Removed ~15 shader files and integration systems
- **Fewer Bugs**: Less complex shader interactions and state management
- **Easier Updates**: Simplified system following proper Ren'Py shader documentation
- **Better Documentation**: Clear, focused guides instead of complex manuals

### Design Benefits
- **Core Identity Preserved**: CRT and bloom effects maintain the retro aesthetic
- **Essential Functionality**: Letterbox for cinematic dialogue scenes
- **Developer Focus**: More time for gameplay features instead of shader tuning
- **User Experience**: Simple, predictable visual effects without overwhelming options

## File Structure (current)

```
game/shaders/
├── shaders_crt.rpy             # Retro CRT monitor simulation  
├── shaders_cinematic_presets.rpy # Cinematic grading presets
├── shaders_complete_grading.rpy  # Grading overlay
├── shaders_film_grain.rpy        # Film grain overlay
├── shaders_letterbox(.rpy, _system.rpy) # Letterbox bars
├── SETUP_GUIDE.md         # Setup and usage documentation
├── HOTKEY_MAPPING.md      # Control keys reference
└── README.md              # This overview file
```

## Integration Points

The simplified shader system integrates with:

### Core Systems
- **Room System**: Object highlight uses desaturation transforms on hover
- **Debug System**: Shader info appears in debug overlay (`I` key)
- **Audio System**: CRT effects can trigger audio feedback
- **UI System**: Letterbox appears above room content but below UI elements

### Preserved Functionality
- **Existing Controls**: CRT controls work as before
- **Letterbox Integration**: Dialogue system continues to trigger letterbox automatically
- **Developer Tools**: Debug overlay shows shader status and performance info

## Usage Examples

### Enable CRT Effect
```renpy
$ store.crt_enabled = True
$ store.crt_warp = 0.2        # Screen curvature
$ store.crt_scan = 0.5        # Scanline intensity  
$ store.crt_chroma = 0.9      # Color separation
```

### Apply Color Grading
Use the Shader Editor (F8) and select a preset; film grain can be toggled and adjusted there as well.

### Control Letterbox
```renpy
# Simple API wrappers
$ letterbox_on()
"This is an important revelation..."
$ letterbox_off()
```

Advanced: to influence animation speed directly, call the compatibility wrappers with a duration:
```renpy
$ show_letterbox(duration=1.5)  # slower ease-in
"..."
$ hide_letterbox(duration=1.5)
```

Or choose a speed directly via the simple API:
```renpy
$ letterbox_on('fast')
"..."
$ letterbox_off('fast')
```

You can also pass an integer 0..4 (0=very_slow → 4=very_fast):
```renpy
$ letterbox_on(0)
"..."
$ letterbox_off(0)
```

## Performance Monitoring

Use the debug overlay (`I` key) to monitor shader performance:
- **FPS Counter**: Shows real-time framerate impact
- **Shader Info**: Displays which effects are currently active
- **Memory Usage**: Tracks shader-related memory consumption

## Future Considerations

If additional shader effects are needed in the future:

1. **Follow Ren'Py Documentation**: Use the official model-based rendering approach
2. **Implement Incrementally**: Add one effect at a time with performance testing
3. **Maintain Simplicity**: Avoid complex preset systems and hotkey combinations
4. **Document Thoroughly**: Clear documentation for each new shader effect

This simplified system provides a solid foundation for the game's visual effects while maintaining excellent performance and code clarity.
