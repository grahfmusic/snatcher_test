# Snatchernauts Framework - Control Keys (Simplified System)

This document outlines the essential controls for the simplified CRT, Color Grading, Film Grain, and Letterbox shader system.

## Core System Controls

| Key | Function | Description |
|-----|----------|-------------|
| **i** | Info Overlay | Toggle room/object/performance info display |
| **Cmd+Shift+F12**<br/>**Ctrl+Shift+F12** | Debug Verbosity | Cycle debug overlay levels |
| **F1-F4** | Debug Position | Snap debug overlay to screen corners (TL/TR/BL/BR) |

## Audio Controls

No dedicated audio hotkeys.

## Visual Effects - CRT

| Key | Function | Description |
|-----|----------|-------------|
| **1-4** | Scanline Size | Set CRT scanline thickness (1=thin → 4=thick) |

## Breathing Tuner

| Key | Function | Description |
|-----|----------|-------------|
| **F6** | Debug Bands | Toggle breathing debug overlay |
| **F7** | Tuner UI | Open/close breathing tuner |
| **Tab** | Cycle Target | Switch tuner target object |
| **[** / **]** | Profiles | Cycle active breathing profile |

## Visual Effects - Letterbox

| Key | Function | Description |
|-----|----------|-------------|
| **l** | Letterbox Cycle | Toggle letterbox ON or cycle through 5 speeds |
| **Shift+X** | Force Letterbox Off | Turn off letterbox regardless of current state |

### Letterbox Speed Options:
- **Very Slow** - 2.5 second animation
- **Slow** - 1.5 second animation  
- **Normal** - 0.8 second animation (default)
- **Fast** - 0.4 second animation
- **Very Fast** - 0.2 second animation

## Navigation & Interaction

| Key | Function | Description |
|-----|----------|-------------|
| **Arrow Keys** | Navigate | Move between interactive objects |
| **Enter**<br/>**Space** | Select | Interact with highlighted object |
| **Escape** | Cancel | Close menus, return to exploration |
| **Tab** | Gamepad Mode | Toggle gamepad-style navigation |

## Room Controls

| Key | Function | Description |
|-----|----------|-------------|
| **Mouse Hover** | Object Highlight | Show object info and description (desaturation highlight) |
| **Mouse Click** | Object Interact | Open interaction menu for clicked object |

## Developer/Testing

| Key | Function | Description |
|-----|----------|-------------|
| **F5** | Quick Save | Save current game state (if enabled) |
| **F9** | Quick Load | Load last saved state (if enabled) |
| **~** | Console | Open Ren'Py developer console |
| **Shift+O** | Console Alt | Alternative console access |
| **Shift+R** | Reload | Reload current script/room |

### Command Line Tools
| Command | Function | Description |
|---------|----------|-------------|
| `scripts/run-game.sh` | Launch Game | Normal game launch |
| `scripts/run-game.sh --debug` | Debug Launch | Launch with console output |
| `scripts/run-game.sh --lint` | Lint + Launch | Check code quality then launch |
| `scripts/run-game.sh --help` | Show Help | Display all launcher options |

*See `DEVELOPMENT_TOOLS.md` for complete launcher documentation*

## Context-Sensitive Keys

### During Interaction Menu
| Key | Function | Description |
|-----|----------|-------------|
| **Arrow Keys** | Menu Navigate | Move through interaction options |
| **Enter/Space** | Execute Action | Perform selected action |
| **Escape** | Close Menu | Return to room exploration |

### During Dialogue
| Key | Function | Description |
|-----|----------|-------------|
| **Space**<br/>**Enter**<br/>**Mouse Click** | Continue | Advance dialogue text |
| **Escape** | Skip | Fast-forward through dialogue |
| **Ctrl** | Skip Mode | Hold to skip dialogue quickly |
| **l** | Letterbox | Shows during dialogue scenes |

## Mouse & Gamepad Controls

| Action | Function | Description |
|--------|----------|-------------|
| **Mouse Hover** | Object Highlight | Show desaturation highlight and description |
| **Left Click** | Primary Interact | Open interaction menu or select |
| **D-Pad/Left Stick** | Navigate | Move cursor between objects |
| **A/Cross** | Select | Interact with highlighted object |
| **B/Circle** | Cancel | Close menus, go back |

## Essential Visual Effects

| Effect | Purpose | Control |
|--------|---------|----------|
| **CRT Shader** | Retro computer aesthetic | Via Shader Editor (F8) |
| **Color Grading** | Cinematic looks | Via Shader Editor (F8) |
| **Film Grain** | Texture/noise overlay | Via Shader Editor (F8) |
| **Letterbox** | Cinematic dialogue | **l** key or automatic |

## Performance Notes

| Setting | Performance Impact | Recommendation |
|---------|-------------------|----------------|
| CRT Off | +15-20 FPS | Disable on slower hardware |
| Debug Off | +5-10 FPS | Keep off in production |
| Film Grain | Minimal impact | Safe to keep enabled |

## Quick Reference

**Essential Keys:**
- **i** = Info, **l** = Letterbox
- **0** = Reset CRT

**CRT Tuning:**
- **1-4** = Scanline size, **[ ]** = Vignette strength, **- =** = Vignette width

**Navigation:**  
- **Arrows** = Move, **Enter** = Select, **Escape** = Cancel

## What Was Removed

This simplified system removed most complex atmospheric shader effects but retains essential ones:

The system now focuses on the essential effects: **CRT**, **Color Grading**, **Film Grain**, and **Letterbox**.
