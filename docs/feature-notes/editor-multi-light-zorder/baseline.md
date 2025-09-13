# Multi-Light Z-Order Feature Development - Baseline Documentation

**Date**: 2025-01-10  
**Feature Branch**: `feature/editor-multi-light-zorder`  
**Status**: Task 1 Complete - Environment Setup & Baseline Preparation

## Purpose and Scope

This baseline documents the current state of the Snatchernauts Framework before implementing the Multi-Light Z-Order feature enhancement. The goal is to:

1. **Record current behavior** for lighting, z-order, and scene editing capabilities
2. **Establish Windows development workflow** using PowerShell scripts
3. **Create reference points** for before/after comparisons during development
4. **Document technical environment** for reproducible testing

## Environment Details

### System Configuration
- **Operating System**: Microsoft Windows 11 Pro
- **OS Version**: 10.0.26100 Build 26100  
- **System Type**: x64-based PC
- **PowerShell**: Version 5.1.26100.6584

### Development Environment
- **RENPY_SDK**: `C:\renpy-8.4.1-sdk` (confirmed functional)
- **Project Directory**: `C:\Users\deant\git\snatchernauts_framework`
- **Feature Branch**: `feature/editor-multi-light-zorder` (tracking `origin/feature/editor-multi-light-zorder`)

### Validated Commands

| Command | Purpose | Status | Log File |
|---------|---------|--------|----------|
| `.\scripts\run-game.ps1 --lint` | Code quality check | ✅ PASSED | `artifacts\logs\windows-lint.txt` |
| `.\scripts\run-game.ps1 --debug` | Debug mode launch | ⏳ Manual testing required | `artifacts\logs\windows-debug.txt` |
| `.\scripts\run-game.ps1` | Normal game launch | ⏳ Manual testing required | `artifacts\logs\windows-run.txt` |

#### Lint Results
```
Starting Snatchernauts Framework...
Using Ren'Py SDK: C:\renpy-8.4.1-sdk
Project directory: C:\Users\deant\git\snatchernauts_framework
Running lint check...
Lint check completed.
```

**Lint Status**: ✅ Clean - No errors detected

## Current Feature Analysis

### Existing Capabilities (To Be Enhanced)
Based on .warp.md analysis and project structure:

1. **F8 Shader Editor** - Full-screen editor with:
   - CRT, Film Grain, Colour Grading, Lighting tabs
   - Preset management from `json/presets/shaders/` and `json/custom/shaders/`
   - Professional controls with sliders, dropdowns, colour pickers

2. **Shader Preset System** - JSON-based presets (v2.1 format):
   - **Shipped presets**: `game/json/presets/shaders/`
   - **Custom presets**: `game/json/custom/shaders/`
   - **Filename prefixes**: `crt_`, `grain_`, `grade_`, `light_`

3. **Current Lighting** - Existing dynamic lighting in F8 editor:
   - Position control and animation support
   - Shader-based lighting presets
   - **Will be moved** to new Scene/Object Editor during this feature

4. **Room System** - Room-based scene management:
   - Objects defined in room configs
   - Some z-order/layer support may exist but needs enhancement

### Planned Enhancements (This Feature)
1. **Multi-Light Support** - Up to 10 concurrent lights with z-mode ordering
2. **Object Z-Order** - Enhanced z-order system with layer support (background/midground/foreground)
3. **Scene/Object Editor** - New unified editor replacing in-game editing
4. **YAML/JSON Data** - Objects in YAML, lights in JSON, separated from shader presets
5. **Advanced Lighting** - 5 animation types (pulse, flicker, strobe, colour_cycle, orbit)

## Baseline Capture Plan

### Manual Testing Required
Since automated GUI testing isn't feasible, the following captures require manual execution:

#### 1. Launch and Navigation
```powershell
# Launch game for baseline capture
.\scripts\run-game.ps1

# Navigate to Room1 or primary test scene
# Use 'S' key for Ren'Py screenshots or Win+Shift+S
```

#### 2. Capture Scenarios
Detailed scenarios defined in: `docs/baseline/editor-multi-light-zorder/20250110/capture-matrix.md`

**Key areas to capture:**
- Main menu and F8 shader editor states
- Room1 with different lighting configurations  
- Shader preset application from both directories
- Current z-order/layering behavior (if any)

#### 3. File Organization
```
docs/baseline/editor-multi-light-zorder/20250110/
├── capture-matrix.md         # Scenario definitions
├── screenshots/              # PNG captures
│   ├── baseline_ui-*.png    # UI states
│   ├── baseline_scene-*.png # Scene rendering
│   └── baseline_preset-*.png# Preset application
└── videos/                   # MP4 captures
    └── baseline_anim-*.mp4   # Animation/transitions
```

## Current Limitations and Observations

### Known Areas for Enhancement
1. **Z-Order Management**: Current object layering capabilities unclear
2. **Multi-Light Constraints**: Current lighting limitations in F8 editor
3. **Scene Editing**: Limited in-place object editing capabilities
4. **Data Separation**: Lighting presets mixed with shader presets

### Integration Points
1. **F8 Editor**: Must preserve shader functionality while removing dynamic lighting UI
2. **Preset Directories**: Keep existing `json/presets/shaders/` and `json/custom/shaders/`
3. **Legacy Compatibility**: Maintain backward compatibility with Room1 definitions

## Next Steps

### Immediate (Task 1 Completion)
1. ✅ Branch created and tracking remote
2. ✅ Windows workflow validated (lint passes)
3. ✅ Environment documented
4. ⏳ Manual baseline captures needed
5. ⏳ Commit baseline artifacts
6. ⏳ Open draft PR

### Upcoming (Task 2+)
1. Implement YAML/JSON IO services (enhanced versions of existing `game/api/io_*.py`)
2. Design object and light schema definitions
3. Build SceneRuntime and DrawQueue systems
4. Create new Scene/Object Editor UI
5. Migrate lighting controls from F8 to new editor

## Technical Notes

### Existing Infrastructure to Leverage
- **JSON/YAML Support**: Already implemented in `game/api/io_json.py` and `game/api/io_yaml.py`
- **Shader System**: Mature shader pipeline with atomic writes and change detection
- **Preset Management**: Proven system for loading/saving configurations

### Windows-Specific Considerations  
- PowerShell script handles both subcommand and flag-style Ren'Py invocation
- Atomic file operations work correctly on Windows filesystem
- Git workflow functional with PowerShell commands

## References

- **Task List**: See original 25-task specification
- **Project Documentation**: `.warp.md` and `AGENTS.md`
- **Current Architecture**: `game/api/README.md` and API documentation
- **Shader Presets**: v2.1 format with vignette migration completed

---

**Baseline Status**: Environment setup complete, manual captures pending  
**Next Milestone**: Complete baseline captures and open draft PR to track feature development
