# Shader Preset Menu System Guide

## Overview

The shader preset menu system provides a comprehensive interface for browsing and applying JSON shader presets. It detects available files automatically from both shipped and custom directories and organises them by effect type for easy navigation.

## Features

### Automatic Detection
- Scans `json/presets/shaders/` and `json/custom/shaders/` directories
- Detects files by prefix: `crt_*.json`, `grain_*.json`, `grade_*.json`, `light_*.json`
- Distinguishes between shipped and custom presets
- Caches results for performance (refreshes every 5 seconds)

### Categorised Display
- **All Presets**: Shows all available presets
- **CRT Effects**: CRT shader presets (red indicator)
- **Film Grain**: Grain effect presets (green indicator)
- **Colour Grading**: Colour grading presets (blue indicator)
- **Lighting**: Lighting effect presets (yellow indicator)

### Search and Filter
- Real-time search across preset names
- Filter by category using tabs
- Clear search functionality

### User Interface
- F9 hotkey to toggle menu (available globally)
- Modal interface with escape key support
- Scrollable preset list with colour-coded indicators
- Shows source type (shipped/custom) for each preset
- Displays count of found presets

## Usage

### Opening the Menu
- Press **F9** at any time during gameplay
- Menu appears as a modal overlay

### Navigating Presets
1. Use category tabs to filter by effect type
2. Type in search bar to find specific presets
3. Scroll through the list using mouse wheel or dragging
4. Click on any preset to apply it immediately

### Applying Presets
- Click on a preset to apply it instantly
- Menu closes automatically after successful application
- Notification message shows which preset was applied
- Changes take effect immediately in the game

### Closing the Menu
- Press **F9** again to toggle off
- Press **Escape** to close
- Click the ✕ button in the top-right corner
- Menu auto-closes after applying a preset

## File Structure

### Directory Layout
```
json/
├── presets/
│   └── shaders/          # Shipped presets
│       ├── crt_*.json
│       ├── grain_*.json
│       ├── grade_*.json
│       └── light_*.json
└── custom/
    └── shaders/          # User/custom presets
        ├── crt_*.json
        ├── grain_*.json
        ├── grade_*.json
        └── light_*.json
```

### Naming Convention
- **CRT presets**: `crt_<name>.json` (e.g., `crt_arcade.json`)
- **Grain presets**: `grain_<name>.json` (e.g., `grain_vintage.json`)
- **Grade presets**: `grade_<name>.json` (e.g., `grade_warm.json`)
- **Light presets**: `light_<name>.json` (e.g., `light_candle.json`)

## Integration

### Code Files
- `ui_shader_preset_menu.rpy` - Main menu implementation
- `ui_screens.rpy` - Integration point (comment added)

### Dependencies
- Uses existing `shader_preset_apply_file()` function
- Integrates with `show_shader_notification()` system
- Respects existing JSON preset format (version 2.1)

### Global Availability
- Menu is available from any screen via overlay system
- F9 hotkey works in all game contexts
- No conflicts with existing F8 shader editor

## Technical Details

### Performance
- Caches file discovery for 5 seconds to avoid repeated filesystem access
- Only scans directories when menu is opened
- Efficient filtering and search using Python list comprehensions

### Error Handling
- Graceful handling of missing directories
- Shows appropriate messages for failed preset applications
- Continues working if individual files are corrupted

### Customisation
- Easy to modify colours, sizes, and layout via screen code
- Search functionality can be extended with additional filters
- Categories can be added by modifying `preset_patterns` dictionary

## Examples

### Creating Custom Presets
Place JSON files in `json/custom/shaders/` with appropriate prefixes:

**crt_my_custom.json**:
```json
{
  "version": "2.1",
  "effects": {
    "crt": {
      "enabled": true,
      "warp": 0.3,
      "scan": 0.6,
      "aberration": 0.4
    }
  }
}
```

### Using the Menu
1. Press F9 to open
2. Click "CRT Effects" tab
3. Search for "custom"
4. Click on "my_custom (custom)"
5. Effect applies immediately

## Future Enhancements

Potential improvements for future versions:
- Preset preview thumbnails
- Favourites system
- Preset categories beyond effect type
- Import/export functionality
- Preset creation wizard
- Keyboard navigation
