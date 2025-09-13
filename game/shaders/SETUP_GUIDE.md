# Simplified Shader System - CRT, Grading, Film Grain, Letterbox

## ✅ Clean Shader System

### 🎯 **Overview** 
This system provides the essential visual effects:
- **CRT Shader**: Authentic CRT monitor effects with scanlines and distortion
- **Color Grading**: Cinematic looks via professional presets
- **Film Grain**: Subtle texture overlay with adjustable intensity/scale
- **Letterbox Shader**: Cinematic letterbox bars for cutscenes

All complex atmospheric and environmental shaders have been removed for performance and simplicity.

### 🔧 **Quick Setup**

The system is automatically initialized when the game loads. No manual setup required!

**Usage:**
- CRT effects are controlled via the Shader Editor (F8) or CRT wrappers (`crt_on()`, `crt_off()`, `crt_params(...)`). No global toggle hotkeys.
- Color grading presets and film grain are applied via the Shader Editor (F8) or preset IO
- Letterbox effects activate during dialogue and cutscenes

### 🎨 **How the Layering Works**

```
┌─ CRT Frame (Outermost) ────────────────────────┐
│ ┌─ Background + Shaders ───────────────────┐   │
│ │ ┌─ Objects + Shaders ───────────────┐   │   │
│ │ │ ┌─ Grading + Film Grain ──────┐   │   │   │
│ │ │ │   [Cinematic Looks]         │   │   │   │
│ │ │ └─────────────────────────────┘   │   │   │
│ │ └───────────────────────────────────┘   │   │
│ └─────────────────────────────────────────┘   │
└───────────────────────────────────────────────┘
```

### 🎯 **Key Features**

#### ✅ **CRT Integration**  
- CRT frame remains the outermost container
- Shaders apply inside the CRT, affecting the "screen content"
- Global CRT toggle hotkeys have been removed; control via editor/wrappers

#### ✅ **Object Consistency**
- Shaders affect **both background AND objects** uniformly
- Investigation modes can override for specific objects (evidence highlighting, etc.)
- Maintains visual coherence

### ⌨️ **Hotkey Controls**

#### **CRT Shader Controls:**
- **Scanline Size**: `1-4` - Adjust scanline thickness

#### **System Controls:**
- **Info Overlay**: `i` - Show/hide info overlay
- **Letterbox Toggle**: `l` - Toggle cinematic letterbox bars

### 🔄 **Usage Examples**

#### **CRT Effects:**
```renpy
# Enable CRT with custom settings
$ store.crt_enabled = True
$ store.crt_warp = 0.2
$ store.crt_scan = 0.5
$ store.crt_chroma = 0.9
```

#### **Letterbox Control (Simple API):**
```renpy
# Show letterbox for dialogue/cutscene
$ letterbox_on()
"Detective Blake looks serious."
$ letterbox_off()
```

You can choose an animation speed: 'very_slow'|'slow'|'normal'|'fast'|'very_fast'
```renpy
$ letterbox_on('fast')
"..."
$ letterbox_off('fast')  # ease-out with the same speed
```

Numeric speeds are also accepted (0..4):
```
# 0=very_slow, 1=slow, 2=normal, 3=fast, 4=very_fast
$ letterbox_on(3)
"..."
$ letterbox_off(3)
```

Advanced: you can also call the compatibility wrappers directly to influence speed by duration if needed:
```renpy
$ show_letterbox(duration=1.5)  # maps to a slower ease-in
"..."
$ hide_letterbox(duration=1.5)
```

#### **Color Grading + Film Grain:**
Use the Shader Editor (F8) to apply presets and adjust film grain.

### 🚀 **Performance Notes**

#### **Optimized for Real-time:**
- Individual effects: ~1-2ms overhead each
- Composite presets: ~3-5ms total
- Automatically limits complex combinations
- Works on integrated graphics

#### **Scalability:**
- Effects automatically reduce on lower-end hardware
- Individual shader cycling allows fine-tuning
- Preset system provides one-click optimization

### 🐛 **Troubleshooting**

#### **If CRT Effects Don't Appear:**
1. Open the Shader Editor (F8) and enable CRT, or call `crt_on()`
2. Check CRT variables: `crt_enabled`, `crt_warp`, `crt_scan`
3. Verify `shaders_crt.rpy` is loaded

#### **If Grading/Grain Don't Appear:**
1. Open the Shader Editor (F8) and apply a preset
2. Ensure film grain is enabled in the editor or via preset

#### **If Letterbox Doesn't Show:**
1. Try `L` key to manually toggle letterbox
2. Check that `letterbox_shader.rpy` is loaded
3. Verify screen has proper zorder for overlay

#### **Performance Issues:**
1. Disable CRT effects via the Shader Editor (F8) or call `crt_off()`
2. Check graphics settings in your game
3. Monitor performance with debug overlay (`i` key)

### 📁 **File Structure**

```
game/shaders/
├── shaders_crt.rpy             # CRT monitor effects  
├── shaders_cinematic_presets.rpy # Cinematic color grading presets
├── shaders_complete_grading.rpy # Grading overlay
├── shaders_film_grain.rpy      # Film grain overlay
├── shaders_letterbox(.rpy, _system.rpy) # Letterbox bars
└── SETUP_GUIDE.md              # This file
```

### ✅ **Verification Checklist**

- [ ] Shader Editor opens with `F8`
- [ ] Scanline size keys `1-4` adjust CRT scanline thickness

### Breathing Warp (Per-Object)

- Implemented as Python (no GLSL), driven by `ui/chest_warp.rpy`.
- Per-object settings live in `ROOM_BREATHING_SETTINGS` and are edited via the tuner.
- Keys: F6 (debug bands), F7 (open/close tuner), Tab (cycle target), [ / ] (cycle profiles).
- [ ] Grading/Film Grain overlays render as expected
- [ ] Letterbox bars show during dialogue
- [ ] Debug overlay shows with `I` key
- [ ] All existing room interactions functional

### 🎯 **Success Indicators**

✅ **Working Correctly When:**
- CRT effects apply when enabled with visible scanlines and distortion
- Letterbox bars smoothly animate during cutscenes
- Grading/Film Grain produce the expected look
- Performance remains smooth (60+ FPS)
- All existing game features work unchanged

This simplified system provides essential visual effects without complexity!
## CRT Preset JSON Fields

CRT preset files live under `json/presets/shaders/*.json` (shipped) and `json/custom/shaders/*.json` (user). The `effects.crt` object supports the following fields:

- `enabled` (bool): enable CRT effect
- `warp` (float): screen curvature amount
- `scan` (float): scanline strength
- `scanline_size` (float): scanline thickness
- `aberration` (float): chromatic aberration amplitude (per-channel offset)
- `animated` (bool): enable scanline animation
- `aberration_mode` (string): one of `none|pulse|flicker|sweep`
- `aberration_speed` (float): speed scalar for aberration animation
- `glitch` (float): horizontal row jitter intensity (0..1)
- `glitch_speed` (float): speed of glitch animation
- `vignette` (float): vignette strength (edge darkening)
- `vignette_width` (float): vignette width (edge band width)
- `vignette_feather` (float): falloff power for vignette edge (higher = softer)

Example:
```json
{
  "version": "1.0",
  "effects": {
    "crt": {
      "enabled": true,
      "warp": 0.22,
      "scan": 0.45,
      "scanline_size": 1.2,
      "aberration": 0.02,
      "animated": true,
      "aberration_mode": "pulse",
      "aberration_speed": 1.5,
      "glitch": 0.05,
      "glitch_speed": 2.0,
      "vignette": 0.38,
      "vignette_width": 0.22,
      "vignette_feather": 1.2
    }
  }
}
```

Shipped CRT presets include: `crt_neutral`, `crt_softscan`, `crt_hardscan`, `crt_arcade`, `crt_vhs`, `crt_trinitron`, `crt_warmretro`, `crt_coldblue`, `crt_greenmono`, `crt_ambermono`, `crt_shadowmask`, `crt_aperturegrille`, `crt_heavywarp`, `crt_curvelight`, `crt_scanfine`, `crt_scanbold`, `crt_aberrpulse`, `crt_aberrsweep`, `crt_glitchy`, `crt_cinematic`, `crt_apexgaming`, `crt_tubeclassic`, `crt_flatpanel`, `crt_darkroom`, `crt_broadcast`.

Use the editor (`F8`) → CRT tab to tweak live (aberration/glitch/feather) and save your custom JSON under Presets/IO.
