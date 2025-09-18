# Detective Interaction System Implementation

## Overview

This implementation enhances the room1 objects with a sophisticated detective interaction system that includes:

1. **Dynamic interaction menus** - Options that appear/disappear based on story progress
2. **Dialogue cutscenes** - Full conversation scenes with two characters
3. **ESC key support** - Already implemented in the base system
4. **State tracking** - Conversation progress affects future interactions

## Files Modified/Added

### Modified Files:
- `game/logic/rooms/room1_logic.rpy` - Enhanced with detective interaction logic
- `game/logic/game_logic.rpy` - Added `get_room_logic()` function

### New Files:
- `game/dialogue/detective_scenes.rpy` - Detective dialogue scenes and cutscenes

## Features Implemented

### 1. Detective Character Interactions
The detective now has three interaction options:
- **Talk** - Always available, initiates conversation
- **Ask About** - Unlocked after first conversation, allows deeper questioning  
- **Leave** - Always available, exits the interaction menu

### 2. Dynamic Option Management
The system can dynamically enable/disable interaction options:
- "Ask About" is initially hidden
- After first conversation with detective, "Ask About" becomes available
- Options are updated through the `update_detective_interactions()` method

### 3. Dialogue Cutscenes
- **Letterbox activation** - Cinematic black bars during conversations
- **Character definitions** - Detective Blake and Player characters with distinct colors
- **Branching dialogue** - Different conversations based on progress
- **Menu choices** - "Ask About" presents multiple conversation topics

### 4. State Tracking
The system tracks:
- `detective_talked_to` - Whether initial conversation happened
- `detective_ask_about_available` - Whether Ask About option is unlocked
- `detective_conversation_stage` - Current conversation progression (0, 1, 2+)

### 5. ESC Key Support
ESC key support is already implemented in the base system:
- `K_ESCAPE` action mapped to `keyboard_cancel_action()` 
- Works during interaction menus to exit gracefully
- Located in `game/ui/screens_room.rpy` line 133

## Usage Instructions

### For Players:
1. Navigate to the detective in room1
2. Press A/Enter to bring up interaction menu
3. Use arrow keys to select options, Enter to confirm
4. ESC key exits the interaction menu at any time
5. Talk to the detective first to unlock "Ask About"

### For Developers:
To disable an interaction option completely:
```python
# In room1_logic.py, modify update_detective_interactions()
def update_detective_interactions(self):
    new_actions = []
    new_actions.append({"label": "Talk", "action": "talk"})
    # Remove this line to disable "Ask About":
    # if store.detective_ask_about_available:
    #     new_actions.append({"label": "Ask About", "action": "ask_about"})
    new_actions.append({"label": "Leave", "action": "leave"})
    INTERACTION_ACTIONS["character"] = new_actions
```

## Technical Implementation Details

### Cutscene System
- Uses `renpy.call_in_new_context()` to launch dialogue scenes
- Automatically manages letterbox show/hide
- Returns to exploration seamlessly after dialogue

### Character System
- Characters defined with distinct colors for visual distinction
- Detective Blake: Blue (#4a90e2)
- Player: Orange (#e2a04a)

### Integration Points
- Room logic called via `on_object_interact()` hook
- Returns `True` when interactions are handled to prevent default behavior
- Updates interaction options dynamically via room re-entry

## Example Dialogue Flow

1. First interaction: Detective introduces themselves, unlocks "Ask About"
2. Second interaction: Detective explains their need for help
3. Subsequent interactions: Detective asks for observations
4. "Ask About" menu offers three conversation topics:
   - Missing persons case details
   - Detective's background story  
   - Connection to the current location

This implementation provides a solid foundation for complex character interactions while maintaining the framework's modular architecture.

## Summary of Current Interaction Options

### Object Types and Their Actions:

**Character Type (Detective):**
- **Talk** - Always available, initiates conversation cutscenes
- **Ask About** - Unlocked after first conversation, provides deeper dialogue options
- **Leave** - Always available, exits interaction menu

**Item Type (Patreon flyer):**
- **Take** - Always available, allows player to collect the item
- **Investigate** - Always available, provides detailed examination with object description
- **Leave** - Always available, exits interaction menu

**Other Object Types:**
- **Door Type**: Open, Knock, Leave
- **Container Type**: Open, Search, Leave

### Recent Changes:
- **Removed "Examine" option** from character type interactions
- **Renamed "Use" to "Investigate"** for item type interactions  
- **Removed "Examine" option** from item type interactions
- Streamlined interaction menus for cleaner, more focused gameplay
