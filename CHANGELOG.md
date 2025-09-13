# Changelog

## 0.5.5 — 2025-09-10

### 🚀 Major Shader System Improvements

#### **Shader Preset Migration to v2.1**
- **Complete JSON preset migration**: Updated all 58 shader preset files from version 2.0 to 2.1
  - All `grade_*`, `grain_*`, and `light_*` presets now include vignette settings in `color_grade` section
  - Vignette parameters: `vignette_strength` (0.25), `vignette_width` (0.8), `vignette_feather` (0.2)
  - Created `scripts/ensure-grade-vignette.py` migration script for future use
  - All verification checks pass: no version 2.0 files remain, no vignette in CRT sections

#### **Vignette System Migration**
- **Moved vignette controls from CRT to Colour Grading**: Complete architectural change for better visual effects organisation
  - CRT tab now focuses on aberration, scanlines, and display distortion effects only
  - Colour Grading tab includes all vignette controls: strength, width, feather
  - Automatic preset migration from version 2.0 to 2.1 when loading old presets
  - Backward compatibility maintained through `vignette()` API function with deprecation warnings for `crt_params(vignette=...)`

#### **Enhanced Film Grain System**
- **Comprehensive grain controls**: Added size factor and downscale parameters to editor
  - Manual controls for intensity, size factor, downscale in F8 editor
  - Enhanced JSON preset support with full grain animation parameters
  - Removed animation UI controls (but preserved animation data in presets)
  - Fixed grain size factor not updating in real-time during editor adjustments

#### **Intelligent Preset Filtering**
- **Filename-based preset organisation**: Each shader editor tab now shows only relevant preset files
  - CRT tab: shows only `crt_*.json` files
  - Grain tab: shows only `grain_*.json` files  
  - Colour Grading tab: shows only `grade_*.json` files
  - Lighting tab: shows only `light_*.json` files
  - Dramatically improves workflow and reduces visual clutter

### Technical Improvements
- **Enhanced shader editor responsiveness**: Film grain changes now apply immediately via `renpy.restart_interaction()`
- **Improved preset JSON structure**: Version 2.1 format with comprehensive grain parameters and proper vignette location
- **Artifact cleanup**: Removed all `.bak` files and improved repository hygiene
- **API consistency**: Updated all vignette references to point to colour grading system

### Fixed
- **Critical**: Film grain size factor slider now works correctly in shader editor
- **Critical**: Vignette effects now properly apply when controlled via colour grading system  
- Fixed vignette controls not responding when moved to colour grading tab
- Fixed preset save/load system to include full grain animation parameters
- Resolved inconsistent preset directory references in documentation

### Documentation Updates
- Updated all markdown files throughout project to reflect shader system changes
- Enhanced API documentation with vignette migration notes and deprecation warnings
- Updated Wiki documentation for new shader organisation and F8 editor workflow
- Corrected preset directory paths in all documentation files

### Removed/Deprecated  
- **Deprecated**: `crt_params(vignette=...)` now shows deprecation warning and routes to colour grading
- Removed film grain animation controls from editor UI (data still preserved in presets)
- Cleaned up vignette references in CRT documentation and code examples
- Removed conflicting preset directory references

## 0.5.4 — 2025-08-29

### Changed
- Bump framework version to 0.5.4 in code and metadata
  - `game/core/options.rpy`: `config.version = "0.5.4"`
  - `project.json`: version set to `0.5.4`
  - README badges updated to show `0.5.4` (root and `.github/README.md`)

### Docs
- Add `Wiki/STYLE_GUIDE.md` to standardize documentation tone and structure
- Update `Wiki/README.md` to link the style guide and fix the CHANGELOG link
- Fix `SUMMARY.md` link to `CHANGELOG.md` for consistency

### Notes
- This release focuses on documentation consistency and metadata alignment ahead of the next feature drop.

## 0.5.3 — 2025-08-16

### 🚀 Major Features

#### **Complete Documentation Overhaul**
- **Comprehensive Troubleshooting Guide**: New 15-chapter `Wiki/15-Troubleshooting.md` (15,000+ words)
  - Advanced diagnostic methodology with flowcharts and automated information gathering
  - Environment setup troubleshooting with smart Ren'Py SDK detection scripts
  - Runtime issue resolution for interaction problems, shader artifacts, and audio issues
  - Performance troubleshooting with memory leak detection and CPU bottleneck analysis
  - Platform-specific solutions for Windows, macOS, and Linux
  - Emergency recovery procedures and automated health monitoring scripts
  - Professional-grade technical support reference matching enterprise documentation standards

- **Universal Wiki Synchronization**: Robust `scripts/sync-wiki.sh` deployment system
  - Automatic synchronization of 18 documentation files to both GitLab and GitHub wikis
  - Support for dry-run previews and selective platform targeting (--gitlab-only, --github-only)
  - Error handling with detailed progress reporting and cleanup procedures
  - Handles ~8.67 MiB of documentation content including screenshots and assets
  - Professional commit messages with timestamps and platform attribution

#### **Development Tools Integration**
- **Unified Game Launcher**: Complete development workflow enhancement via `scripts/run-game.sh`
  - Debugging, linting, and compilation options in single interface
  - Custom SDK path support via `RENPY_SDK` environment variable
  - Debug mode with console output retention for troubleshooting
  - Cross-platform compatibility with intelligent path detection

#### **Advanced Effects Systems**
- **Desaturation Effects System**: Professional replacement for bloom highlighting
  - New `game/core/desaturation_utils.rpy` with 24 comprehensive presets
  - Variants: subtle, explosive, whisper, heartbeat, flicker, ethereal effects
  - Backward compatibility with existing bloom configurations
  - Performance optimizations with cleaner effect calculations and reduced shader overhead

#### **Debug Infrastructure Overhaul**
- **Centralized Debugging System**: Enterprise-grade debugging infrastructure
  - New `game/debug/bloom_debug.rpy` with categorized, color-coded output
  - Shader debug configuration system (`game/shader_debug_config.rpy`)
  - Toggle-based debug controls for granular system component monitoring
  - Verbose positioning and property debugging for complex object interactions
  - Runtime performance monitoring with memory and CPU usage tracking

### Technical Improvements
- **Shader System Refinements**: Enhanced Neo-Noir shader integration
  - Updated `letterbox_shader_v2.rpy`, `neo_noir_color_grading.rpy`, `neo_noir_lighting.rpy`
  - Improved shader layer management in `neo_noir_shader_layers.rpy`
  - Better hotkey mapping and setup documentation
- **Room System Enhancement**: Improved object interaction and configuration
  - Enhanced room logic handlers for all three example rooms
  - Better object property debugging and display calculations
  - Improved gamepad navigation integration
- **API Improvements**: Cleaner interaction and display APIs
  - Updated `interactions_api.rpy`, `room_api.rpy`, and `ui_api.rpy`
  - Better error handling and parameter validation
  - Enhanced logging integration across all API modules

### New Documentation
- **Development Workflow Guide**: Complete `DEVELOPMENT_TOOLS.md` documentation
- **Shader Setup Updates**: Enhanced shader documentation and troubleshooting
- **Room Structure Guide**: Updated `ROOM_STRUCTURE_GUIDE.md` with latest patterns
- **Wiki Improvements**: Enhanced technical documentation across all wiki pages

### Developer Experience
- **Streamlined Launch Process**: Single script handles all common development tasks
- **Better Error Messages**: Clear validation and troubleshooting guidance
- **Debug Output Control**: Fine-grained control over debug verbosity levels
- **SDK Flexibility**: Easy switching between different Ren'Py SDK versions

### 🔧 Critical Infrastructure Fixes

#### **Wiki Sync Script Resolution**
- **Fixed arithmetic operation failures**: Resolved `scripts/sync-wiki.sh` failing with exit code 1
  - Problem: `((variable++))` operations incompatible with `set -euo pipefail` bash strict mode
  - Solution: Replaced with `variable=$((variable + 1))` format for reliable arithmetic
  - Impact: Script now successfully deploys 18 documentation files to both GitLab and GitHub wikis
  - Added comprehensive error handling and progress reporting for production reliability

- **Enhanced sync script robustness**:
  - Added missing informational messages for GitHub sync operations
  - Implemented proper platform-specific skipping notifications
  - Improved temporary directory cleanup with robust error handling
  - Added detailed commit messages with timestamps and platform attribution

### 📚 Enhanced Documentation Standards
- **Professional Technical Writing**: All documentation now meets enterprise-grade standards
  - Consistent formatting, comprehensive cross-references, and professional tone
  - Detailed troubleshooting procedures with step-by-step resolution guides
  - Advanced diagnostic scripts with automated system information gathering
  - Platform-specific guidance covering Windows, macOS, and Linux environments

### 🗺 Repository Management
- **Tag and Branch Cleanup**: Resolved version control ambiguities
  - Removed conflicting `v0.5.3` tag and `0.5.3` branch to eliminate reference conflicts
  - Streamlined version management with consistent tag naming convention
  - Updated `0.5.3` tag to include all latest fixes and documentation improvements

### Removed/Deprecated
- Consolidated shader files: removed redundant/experimental shader implementations
- Cleaned up bloom system files in favor of desaturation approach
- Removed deprecated screen files (`screens_bloom.rpy`)
- Eliminated conflicting version tags (`v0.5.3`) and branches (`0.5.3`) for cleaner repository state

### ✅ Fixed
- **Critical**: Wiki sync script arithmetic operations now compatible with bash strict mode
- **Critical**: Resolved exit code 1 failures preventing documentation deployment
- Room interaction timing and state management
- Shader effect stacking and performance issues
- Debug output formatting and categorization
- Development workflow reliability across different environments
- Repository version control conflicts and tag ambiguities

## 0.5.2 — 2025-08-13

### Major Features
- **Shader-Based Letterbox System**: Complete rewrite from GUI bars to GLSL shader rendering
  - Proper Ren'Py shader registration using variables string and 300-stage pipeline
  - Smooth fade in/out animations via shader uniforms (height + alpha)
  - Letterbox disabled during normal gameplay, smoothly activates for detective conversations
  - Backward compatibility maintained for existing `show_letterbox()`/`hide_letterbox()` calls
- **Comprehensive Shader Infrastructure**: 15+ atmospheric shaders for detective ambiance
  - Film grain, fog, lighting, vintage/sepia, rain, depth-of-field, edge detection
  - Mystery reveal, flashlight, color grading with detective-specific presets
  - Hotkey system: `Shift+G/F/V/L/W` for individual effects, `Alt+A/I` for presets
  - `R` to reset all shaders, `H` for help overlay
- **Detective Interaction System**: Enhanced conversation system with proper UI clearing
  - Fixed ui.interact stack error by simplifying dialogue approach
  - Room-specific logic with dynamic interaction options
  - Character definitions and conversation state tracking

### Technical Improvements
- **Room System Restructuring**: Organized assets under modular `game/rooms/` structure
  - Room-specific sprites moved to proper directories (`game/rooms/roomN/sprites/`)
  - Enhanced configuration system with `scripts/` subdirectories
  - 3 rooms with complete logic and asset separation
- **UI Stack Management**: Comprehensive layer clearing before dialogue scenes
  - Clear transient and screens layers to prevent conflicts
  - Proper interaction menu and object state cleanup
- **Shader Integration**: All shaders work seamlessly with existing CRT and bloom systems
  - Proper mesh True transforms for coordinate computation
  - Developer controls for testing different parameters

### Assets & Documentation
- **New High-Resolution Backgrounds**: itch.io marketing assets (1920x1080, 2560x1440)
- **Detective Assets**: Character sprites, interaction graphics, room backgrounds
- **Comprehensive Shader Documentation**: `SETUP_GUIDE.md` and `HOTKEY_MAPPING.md`
- **Updated README**: Version 0.5.2 with shader system features and enhanced controls

### Fixed
- Detective dialogue no longer causes ui.interact stack errors
- Letterbox effects now use proper shader rendering instead of GUI overlays
- Room exploration returns cleanly to interaction mode after conversations
- All shader effects properly clear and don't interfere with each other

## 0.5.1 — 2025-08-13

### Changed
- Logging: guard ORIG_PRINT resolution on reload using fallback `_get_orig_print` to avoid `NameError`.
- Interactions: `on_object_interact` now returns `bool`; default handlers short-circuit when handled.
- UI: add confirmations for Exit/Main Menu; disable accidental game_menu during exploration.
- Room1: custom examines and patreon take handling; return `True` when handled.
- Minor: tooltip tweaks and logging cosmetics.

### Chore
- Save local edits; add `game/core/common_init.rpy`.

## 0.5 — 2025-08-13

### Added
- Centralized game logic hooks in `game/logic/game_logic.rpy` with per-room registry.
- Example room handler in `game/logic/rooms/room1_logic.rpy`.
- Hook wiring: `on_room_enter`, `on_object_hover`, `on_object_interact`.
- Color-coded, truncating logging with print interception and runtime toggles.
- Developer docs: `Wiki/DeveloperManual.md` and `Wiki/Modules.md`.
- Standardized module headers (Overview/Contracts/Integration) across major files.

### Changed
- `script.rpy`: calls `on_game_start()` after info overlay; calls `on_room_enter(room)` after `load_room`.
- `ui_api.handle_object_hover`: emits hook into logic.
- `interactions_api.execute_object_action`: emits hook before built-in effects.

### Removed
- `game/script.rpy.bak` backup file.

### Notes
- Legacy files moved to `game/legacy/` and marked as legacy.
