# Lighting Editor Test Plan

## Test Environment Setup
1. Launch game: `scripts/run-game.sh --debug`
2. Navigate to Room 1 (should load automatically)
3. Open lighting editor: **Ctrl+F8**

## Features to Test

### 1. Panel Dragging Functionality ✅
**What to test:** All panels should be draggable by their title bars
**Steps:**
- Open lighting editor (Ctrl+F8)
- Click "Props" button to show Properties panel
- Click "Presets" button to show Presets panel  
- Click "Help" button (or F1) to show Help panel
- **Test:** Drag each panel by their title bars (look for "⋮⋮" drag indicators)
- **Expected:** Panels should move smoothly and position should persist
- **Check:** Console should show "Panel [name] moved to: x, y" messages

### 2. Grid Snapping ✅
**What to test:** Objects snap to grid when grid mode is enabled
**Steps:**
- In lighting editor, click "Grid: OFF" to toggle to "Grid: ON"
- Press 'g' key to toggle grid (alternative method)
- Create a new light (click "Point", "Spot", or "Area")
- **Test:** Move lights around - they should snap to grid positions
- **Expected:** Light positions align to grid when snap is enabled
- **Grid size:** 32 pixels (configurable via `lighting_editor_grid_size`)

### 3. Gizmo Movement ✅
**What to test:** Light gizmos (visual indicators) move properly when lights are manipulated
**Steps:**
- Create some lights using toolbar buttons
- Click "Gizmos: OFF" to toggle to "Gizmos: ON" 
- Press 'h' key to toggle gizmos (alternative method)
- Select a light (click on it)
- **Test:** Selected light should show visual gizmo with different colors
- **Expected:** 
  - Unselected lights: cyan gizmos
  - Selected light: yellow/orange gizmo with radius indicator
  - Gizmos show light type and coordinates as labels

### 4. Keyboard Shortcuts ✅
**What to test:** All documented keyboard shortcuts work correctly
**Key shortcuts to test:**
- **Ctrl+F8:** Open/close editor ✓
- **g:** Toggle grid snapping ✓
- **h:** Toggle gizmos ✓
- **z:** Toggle Z-bands (depth visualization)
- **p:** Toggle presets panel
- **F1:** Toggle help panel
- **F2:** Toggle properties panel
- **Delete:** Delete selected light

### 5. Light Creation and Selection ✅
**What to test:** Creating lights and selecting them works properly
**Steps:**
- Use toolbar buttons: "Point", "Spot", "Area"
- Click on created lights to select them
- **Expected:** 
  - Lights appear as visual gizmos
  - Selected light changes color and shows radius
  - Properties panel updates for selected light

### 6. Preset Loading ✅
**What to test:** Loading lighting presets works correctly
**Steps:**
- Open presets panel (button or 'p' key)
- Try loading different presets (candle, cyberpunk, dawn, etc.)
- **Expected:** 
  - Lights change according to preset
  - Notification shows: "Loaded preset: [name] (X lights)"
  - Scene lighting updates in real-time

## Test Checklist

□ **Panel Dragging:** All 4 panels (toolbar, properties, presets, help) can be dragged by title bars
□ **Grid Snapping:** Grid toggle works, lights snap to 32px grid when enabled  
□ **Gizmo Display:** Gizmos show/hide correctly, selected light has different appearance
□ **Keyboard Shortcuts:** All shortcuts (g, h, z, p, F1, F2, Delete) work as expected
□ **Light Creation:** Point/Spot/Area lights can be created via toolbar buttons
□ **Light Selection:** Clicking lights selects them, updates properties panel
□ **Preset Loading:** All 17 presets load correctly and update scene lighting
□ **Editor Open/Close:** Ctrl+F8 opens/closes editor cleanly
□ **Background Blocking:** Game interactions are blocked when editor is open

## Known Issues to Verify Fixed
- **Panel positioning:** Panels should start hidden and show when toggled
- **Drag handlers:** Panel dragging should work smoothly without errors
- **Grid alignment:** Objects should properly snap to grid boundaries
- **Gizmo rendering:** Light indicators should render at correct positions

## Success Criteria
✅ All panels drag smoothly without console errors
✅ Grid snapping works visibly (objects align to grid)  
✅ Gizmos render correctly for all light types
✅ All keyboard shortcuts respond immediately
✅ Presets load and apply lighting changes
✅ Editor opens/closes cleanly with notifications

Run this test and report any issues found!
