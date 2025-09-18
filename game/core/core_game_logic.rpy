# Game Logic Module  
# Central game logic with clean hooks and event handling
#
# This module provides:
# - Game lifecycle hooks
# - Room-specific logic handlers
# - Object interaction logic
# - State management

## Game State Variables
default game_started = False
default current_chapter = 1
default player_inventory = []
default game_flags = {}

## Game Logic Registry
init -5 python:
    # Registry for room-specific logic handlers
    ROOM_LOGIC_HANDLERS = {}
    
    def register_room_logic(room_id, handler):
        """Register a logic handler for a specific room.
        
        Args:
            room_id: Room identifier
            handler: Handler object/module with hook methods
        """
        ROOM_LOGIC_HANDLERS[room_id] = handler
        debug_log("SYSTEM", f"Registered logic handler for room '{room_id}'")

## Main Game Logic Hooks
init python:
    def on_game_start():
        """Called once when the game starts.
        
        Initialize game systems, set defaults, etc.
        """
        store.game_started = True
        
        # Initialize shader system defaults (do not force-enable at start)
        if not hasattr(store, 'crt_enabled'):
            store.crt_enabled = False
            store.crt_stable_state = False
        if not hasattr(store, 'crt_animated'):
            store.crt_animated = False
        store.crt_warp = getattr(store, 'crt_warp', 0.2)
        store.crt_scan = getattr(store, 'crt_scan', 0.5)
        store.crt_chroma = getattr(store, 'crt_chroma', 0.9)
        store.crt_scanline_size = getattr(store, 'crt_scanline_size', 1.0)
        store.crt_vignette_strength = getattr(store, 'crt_vignette_strength', 0.35)
        store.crt_vignette_width = getattr(store, 'crt_vignette_width', 0.25)
        
        # Initialize other systems
        store.show_description_boxes = True
        store.gamepad_navigation_enabled = False
        
        debug_log("SYSTEM", "Game started - core systems initialized")
    
    def on_room_enter(room_id):
        """Called when entering a room.
        
        Args:
            room_id: Room being entered
        """
        debug_log("ROOM", f"Entering room '{room_id}'")
        
        # Check for room-specific handler
        if room_id in ROOM_LOGIC_HANDLERS:
            handler = ROOM_LOGIC_HANDLERS[room_id]
            if hasattr(handler, 'on_room_enter'):
                try:
                    handler.on_room_enter(room_id)
                except Exception as e:
                    debug_log("ERROR", f"Room handler error: {e}")
        
        # Default room logic
        if room_id == "room1":
            # First room setup
            if not get_game_flag("room1_visited"):
                set_game_flag("room1_visited", True)
                show_hint("Click on objects to interact. Press F8 for editor mode.")
    
    def on_room_exit(room_id):
        """Called when leaving a room.
        
        Args:
            room_id: Room being exited
        """
        debug_log("ROOM", f"Exiting room '{room_id}'")
        
        # Check for room-specific handler
        if room_id in ROOM_LOGIC_HANDLERS:
            handler = ROOM_LOGIC_HANDLERS[room_id]
            if hasattr(handler, 'on_room_exit'):
                try:
                    handler.on_room_exit(room_id)
                except Exception as e:
                    debug_log("ERROR", f"Room handler error: {e}")
    
    def on_object_hover(room_id, obj_name):
        """Called when hovering over an object.
        
        Args:
            room_id: Current room
            obj_name: Object being hovered
        """
        # Check for room-specific handler
        if room_id in ROOM_LOGIC_HANDLERS:
            handler = ROOM_LOGIC_HANDLERS[room_id]
            if hasattr(handler, 'on_object_hover'):
                try:
                    handler.on_object_hover(room_id, obj_name)
                except Exception as e:
                    debug_log("ERROR", f"Hover handler error: {e}")
        
        # Default hover effects (subtle, non-intrusive)
        # Could adjust bloom, play subtle sound, etc.
    
    def on_object_interact(room_id, obj_name, action):
        """Called when interacting with an object.
        
        Args:
            room_id: Current room
            obj_name: Object being interacted with
            action: Action being performed
            
        Returns:
            True if handled (skip default), False otherwise
        """
        debug_log("INTERACT", f"Player interaction: {action} on {obj_name} in {room_id}")
        
        # Check for room-specific handler
        if room_id in ROOM_LOGIC_HANDLERS:
            handler = ROOM_LOGIC_HANDLERS[room_id]
            if hasattr(handler, 'on_object_interact'):
                try:
                    result = handler.on_object_interact(room_id, obj_name, action)
                    if result:
                        return True
                except Exception as e:
                    debug_log("ERROR", f"Interaction handler error: {e}")
        
        # Global interaction logic
        return handle_global_interaction(room_id, obj_name, action)
    
    def handle_global_interaction(room_id, obj_name, action):
        """Handle interactions that work across all rooms.
        
        Args:
            room_id: Current room
            obj_name: Target object
            action: Action to perform
            
        Returns:
            True if handled, False otherwise
        """
        action_lower = action.lower()
        
        # Detective interactions (work in any room)
        if obj_name == "detective":
            if action_lower == "talk":
                show_dialogue("detective", get_detective_dialogue())
                return True
            elif action_lower == "give item":
                if store.player_inventory:
                    show_inventory_menu("give")
                else:
                    show_dialogue("detective", "You don't have anything to give.")
                return True
        
        # Universal item interactions
        if action_lower == "take":
            if can_take_object(obj_name):
                take_object_to_inventory(obj_name)
                return True
        
        return False

## Inventory System
init python:
    def add_to_inventory(item_id, item_data=None):
        """Add an item to player inventory.
        
        Args:
            item_id: Item identifier
            item_data: Optional item data dict
        """
        if item_data is None:
            item_data = {"id": item_id, "name": item_id}
        
        store.player_inventory.append(item_data)
        renpy.notify(f"Added {item_data.get('name', item_id)} to inventory")
    
    def remove_from_inventory(item_id):
        """Remove an item from inventory.
        
        Args:
            item_id: Item to remove
        """
        for i, item in enumerate(store.player_inventory):
            if item.get("id") == item_id:
                store.player_inventory.pop(i)
                renpy.notify(f"Removed {item.get('name', item_id)}")
                return True
        return False
    
    def has_item(item_id):
        """Check if player has an item.
        
        Args:
            item_id: Item to check for
            
        Returns:
            True if in inventory, False otherwise
        """
        for item in store.player_inventory:
            if item.get("id") == item_id:
                return True
        return False
    
    def can_take_object(obj_name):
        """Check if an object can be taken.
        
        Args:
            obj_name: Object to check
            
        Returns:
            True if takeable, False otherwise
        """
        obj_data = store.room_objects.get(obj_name, {})
        return "item" in obj_data.get("tags", [])
    
    def take_object_to_inventory(obj_name):
        """Take an object and add to inventory.
        
        Args:
            obj_name: Object to take
        """
        obj_data = store.room_objects.get(obj_name, {})
        
        # Add to inventory
        add_to_inventory(obj_name, {
            "id": obj_name,
            "name": obj_name.replace("_", " ").title(),
            "description": obj_data.get("description", ""),
            "image": obj_data.get("image", "")
        })
        
        # Hide object from room
        hide_object(obj_name)

## Game Flags System
init python:
    def set_game_flag(flag_name, value=True):
        """Set a game flag.
        
        Args:
            flag_name: Flag identifier
            value: Flag value (default True)
        """
        store.game_flags[flag_name] = value
    
    def get_game_flag(flag_name, default=False):
        """Get a game flag value.
        
        Args:
            flag_name: Flag identifier
            default: Default value if not set
            
        Returns:
            Flag value or default
        """
        return store.game_flags.get(flag_name, default)
    
    def clear_game_flag(flag_name):
        """Clear a game flag.
        
        Args:
            flag_name: Flag to clear
        """
        if flag_name in store.game_flags:
            del store.game_flags[flag_name]

## Dialogue System Helpers
init python:
    def show_dialogue(character_name, text):
        """Show dialogue for a character.
        
        Args:
            character_name: Speaking character
            text: Dialogue text
        """
        renpy.say(None, f"{character_name}: {text}")
    
    def show_hint(text):
        """Show a hint message.
        
        Args:
            text: Hint text
        """
        renpy.notify(text)
    
    def get_detective_dialogue():
        """Get contextual dialogue for the detective.
        
        Returns:
            Appropriate dialogue string
        """
        # Check game state for contextual dialogue
        if not get_game_flag("detective_introduced"):
            set_game_flag("detective_introduced", True)
            return "Name's Sam. I'm working this case. You?"
        
        if has_item("evidence"):
            return "That evidence... let me take a look at it."
        
        # Random idle dialogue
        import random
        idle_lines = [
            "This city never sleeps.",
            "Something doesn't add up here.",
            "I've seen things you wouldn't believe.",
            "The rain washes away everything but the truth."
        ]
        return random.choice(idle_lines)

## Room 1 Logic Handler (Example)
# NOTE: This is just an example. The actual Room1Logic is in game/rooms/room1/scripts/room1_logic.rpy
# Commenting out to avoid duplicate registration
# init -1 python:
#     class Room1LogicExample:
#         """Example logic handler for a room."""
#         
#         def on_room_enter(self, room_id):
#             """Called when entering room."""
#             pass
#         
#         def on_object_interact(self, room_id, obj_name, action):
#             """Handle room-specific interactions."""
#             return False

## Debug Commands (Developer Mode)
init python:
    def debug_give_all_items():
        """Give all items to player (debug)."""
        if not config.developer:
            return
        
        items = ["note", "evidence", "key", "photo"]
        for item in items:
            add_to_inventory(item)
        renpy.notify("Debug: Added all items")
    
    def debug_set_chapter(chapter):
        """Set game chapter (debug).
        
        Args:
            chapter: Chapter number
        """
        if not config.developer:
            return
        
        store.current_chapter = chapter
        renpy.notify(f"Debug: Set chapter to {chapter}")
    
    def debug_teleport(room_id):
        """Teleport to a room (debug).
        
        Args:
            room_id: Target room
        """
        if not config.developer:
            return
        
        transition_to_room(room_id)
        renpy.notify(f"Debug: Teleported to {room_id}")
