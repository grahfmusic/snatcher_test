# Snatchernauts Debug System
# Professional debug logging for adventure game development
# 
# Categories:
#   [ROOM] - Room transitions, loading, state changes
#   [OBJ] - Object creation, modification, deletion
#   [INTERACT] - Player interactions with objects
#   [INV] - Inventory operations
#   [DIALOGUE] - Conversation system events
#   [SHADER] - Visual effect changes
#   [STATE] - Game state and flag changes
#   [VAR] - Variable tracking (significant changes)
#   [SYSTEM] - Framework operations
#   [PERF] - Performance metrics
#   [ERROR] - Error conditions
#   [WARNING] - Non-critical issues

init -999 python:
    import time
    
    # Debug configuration
    DEBUG_ENABLED = config.developer  # Only in developer mode
    DEBUG_VERBOSE = False  # Extra verbose logging
    DEBUG_TO_FILE = False  # Also log to file
    DEBUG_SHOW_TIMESTAMP = True  # Include timestamps
    DEBUG_SHOW_MEMORY = False  # Show memory usage in critical operations
    
    # Debug categories that are enabled
    DEBUG_CATEGORIES = {
        "ROOM": True,
        "OBJ": True,
        "INTERACT": True,
        "INV": True,
        "DIALOGUE": True,
        "SHADER": True,
        "STATE": True,
        "VAR": False,  # Disabled by default (too verbose)
        "SYSTEM": True,
        "PERF": True,
        "ERROR": True,
        "WARNING": True
    }
    
    # Color codes for different categories (ANSI-style for console)
    DEBUG_COLORS = {
        "ROOM": "\033[94m",      # Blue
        "OBJ": "\033[92m",        # Green
        "INTERACT": "\033[93m",   # Yellow
        "INV": "\033[95m",        # Magenta
        "DIALOGUE": "\033[96m",   # Cyan
        "SHADER": "\033[35m",     # Purple
        "STATE": "\033[33m",      # Orange
        "VAR": "\033[90m",        # Gray
        "SYSTEM": "\033[37m",     # White
        "PERF": "\033[91m",       # Light Red
        "ERROR": "\033[31m",      # Red
        "WARNING": "\033[33m",    # Yellow
        "RESET": "\033[0m"        # Reset
    }
    
    # Performance tracking
    _perf_timers = {}
    _last_room = None
    _last_state = {}
    
    def debug_log(category, message, data=None, level="INFO"):
        """Main debug logging function.
        
        Args:
            category: Log category (ROOM, OBJ, etc.)
            message: Log message
            data: Optional data dict to display
            level: INFO, WARNING, ERROR
        """
        if not DEBUG_ENABLED:
            return
            
        if category not in DEBUG_CATEGORIES or not DEBUG_CATEGORIES[category]:
            return
        
        # Build log message
        timestamp = ""
        if DEBUG_SHOW_TIMESTAMP:
            timestamp = time.strftime("[%H:%M:%S] ", time.localtime())
        
        # Format the message
        color = DEBUG_COLORS.get(category, "")
        reset = DEBUG_COLORS["RESET"]
        
        # Build the log line
        log_line = f"{timestamp}[{category}] {message}"
        
        # Add data if provided
        if data:
            if isinstance(data, dict):
                data_str = " | ".join([f"{k}={v}" for k, v in data.items()])
                log_line += f" | {data_str}"
            else:
                log_line += f" | {data}"
        
        # Output to Ren'Py's log
        try:
            renpy.log(log_line)
        except:
            # Fallback if renpy.log isn't available
            print(log_line)
        
        # Also output to file if enabled
        if DEBUG_TO_FILE:
            try:
                with open("game/debug.log", "a") as f:
                    f.write(log_line + "\n")
            except:
                pass
    
    def debug_room_enter(room_id, room_data=None):
        """Log room entry."""
        global _last_room
        
        data = {"from": _last_room or "START"}
        if room_data:
            data.update({
                "objects": len(room_data.get("objects", [])),
                "bg": room_data.get("background", "none")
            })
        
        debug_log("ROOM", f"Entering '{room_id}'", data)
        _last_room = room_id
    
    def debug_room_exit(room_id):
        """Log room exit."""
        debug_log("ROOM", f"Exiting '{room_id}'")
    
    def debug_object_create(obj_name, obj_data):
        """Log object creation."""
        data = {
            "pos": f"({obj_data.get('x', 0)}, {obj_data.get('y', 0)})",
            "scale": obj_data.get('scale', 100),
            "visible": obj_data.get('visible', True)
        }
        debug_log("OBJ", f"Created '{obj_name}'", data)
    
    def debug_object_modify(obj_name, changes):
        """Log object modification."""
        debug_log("OBJ", f"Modified '{obj_name}'", changes)
    
    def debug_object_delete(obj_name):
        """Log object deletion."""
        debug_log("OBJ", f"Deleted '{obj_name}'")
    
    def debug_interaction(obj_name, action, result=None):
        """Log player interaction."""
        data = {"action": action}
        if result:
            data["result"] = result
        debug_log("INTERACT", f"Player -> '{obj_name}'", data)
    
    def debug_inventory_add(item_id, item_name=None):
        """Log inventory addition."""
        name = item_name or item_id
        debug_log("INV", f"Added '{name}' to inventory")
    
    def debug_inventory_remove(item_id, item_name=None):
        """Log inventory removal."""
        name = item_name or item_id
        debug_log("INV", f"Removed '{name}' from inventory")
    
    def debug_inventory_use(item_id, target=None):
        """Log inventory item use."""
        data = {}
        if target:
            data["target"] = target
        debug_log("INV", f"Used item '{item_id}'", data)
    
    def debug_dialogue_start(character, dialogue_id=None):
        """Log dialogue start."""
        data = {}
        if dialogue_id:
            data["id"] = dialogue_id
        debug_log("DIALOGUE", f"Started dialogue with '{character}'", data)
    
    def debug_dialogue_choice(choice_text, choice_index):
        """Log dialogue choice."""
        debug_log("DIALOGUE", f"Player chose option {choice_index}: '{choice_text}'")
    
    def debug_shader_change(shader_type, params):
        """Log shader parameter changes."""
        debug_log("SHADER", f"Changed {shader_type} shader", params)
    
    def debug_shader_enable(shader_type):
        """Log shader enablement."""
        debug_log("SHADER", f"Enabled {shader_type} shader")
    
    def debug_shader_disable(shader_type):
        """Log shader disablement."""
        debug_log("SHADER", f"Disabled {shader_type} shader")
    
    def debug_state_change(flag_name, old_value, new_value):
        """Log game state flag changes."""
        data = {"old": old_value, "new": new_value}
        debug_log("STATE", f"Flag '{flag_name}' changed", data)
    
    def debug_var_change(var_name, old_value, new_value):
        """Log variable changes (use sparingly)."""
        if old_value != new_value:  # Only log actual changes
            data = {"old": old_value, "new": new_value}
            debug_log("VAR", f"Variable '{var_name}'", data)
    
    def debug_system(message, data=None):
        """Log system-level events."""
        debug_log("SYSTEM", message, data)
    
    def debug_perf_start(operation):
        """Start performance timer."""
        _perf_timers[operation] = time.time()
    
    def debug_perf_end(operation):
        """End performance timer and log."""
        if operation in _perf_timers:
            elapsed = (time.time() - _perf_timers[operation]) * 1000  # Convert to ms
            del _perf_timers[operation]
            debug_log("PERF", f"Operation '{operation}' took {elapsed:.2f}ms")
    
    def debug_error(message, exception=None):
        """Log error."""
        data = {}
        if exception:
            data["exception"] = str(exception)
        debug_log("ERROR", message, data, "ERROR")
    
    def debug_warning(message, data=None):
        """Log warning."""
        debug_log("WARNING", message, data, "WARNING")
    
    # Memory tracking (optional)
    def debug_memory(operation="check"):
        """Log memory usage."""
        if not DEBUG_SHOW_MEMORY:
            return
        
        try:
            import gc
            import sys
            
            # Force garbage collection
            gc.collect()
            
            # Count objects
            obj_count = len(gc.get_objects())
            
            debug_log("PERF", f"Memory {operation}", {"objects": obj_count})
        except:
            pass
    
    # Adventure game specific helpers
    def debug_hotspot(x, y, width, height, action):
        """Log hotspot/clickable area creation."""
        data = {
            "rect": f"({x},{y},{width},{height})",
            "action": action
        }
        debug_log("OBJ", "Created hotspot", data)
    
    def debug_puzzle_state(puzzle_id, state):
        """Log puzzle state changes."""
        debug_log("STATE", f"Puzzle '{puzzle_id}'", {"state": state})
    
    def debug_achievement(achievement_id, unlocked=True):
        """Log achievement unlocks."""
        action = "unlocked" if unlocked else "locked"
        debug_log("STATE", f"Achievement '{achievement_id}' {action}")
    
    # Batch operations
    def debug_room_snapshot(room_id, room_data):
        """Log complete room state snapshot."""
        if not DEBUG_VERBOSE:
            return
        
        debug_log("ROOM", f"Snapshot of '{room_id}':")
        for obj_name, obj_data in room_data.get("objects", {}).items():
            debug_log("ROOM", f"  - {obj_name}: pos=({obj_data.get('x')},{obj_data.get('y')}), visible={obj_data.get('visible')}")

# Initialize debug system on game start
init python:
    # Set up debug commands for developer console
    def debug_toggle_category(category):
        """Toggle debug category on/off."""
        if category in DEBUG_CATEGORIES:
            DEBUG_CATEGORIES[category] = not DEBUG_CATEGORIES[category]
            debug_system(f"Debug category '{category}' is now {'ON' if DEBUG_CATEGORIES[category] else 'OFF'}")
    
    def debug_toggle_verbose():
        """Toggle verbose mode."""
        global DEBUG_VERBOSE
        DEBUG_VERBOSE = not DEBUG_VERBOSE
        debug_system(f"Verbose mode is now {'ON' if DEBUG_VERBOSE else 'OFF'}")
    
    def debug_clear_log():
        """Clear debug log file."""
        try:
            with open("game/debug.log", "w") as f:
                f.write("")
            debug_system("Debug log cleared")
        except:
            pass
    
    # Register console commands
    config.console_commands["debug"] = debug_toggle_category
    config.console_commands["debug_verbose"] = debug_toggle_verbose
    config.console_commands["debug_clear"] = debug_clear_log

# Example usage screen for debug info overlay
screen debug_info_overlay():
    if DEBUG_ENABLED:
        frame:
            xalign 0.98
            yalign 0.02
            background "#000000aa"
            padding (10, 5)
            
            vbox:
                spacing 2
                
                text "DEBUG MODE" size 10 color "#00ff00" font "fonts/UbuntuMono-R.ttf"
                
                if _last_room:
                    text f"Room: {_last_room}" size 9 color "#ffffff" font "fonts/UbuntuMono-R.ttf"
                
                $ obj_count = len(getattr(store, 'room_objects', {}))
                text f"Objects: {obj_count}" size 9 color "#ffffff" font "fonts/UbuntuMono-R.ttf"
                
                $ inv_count = len(getattr(store, 'player_inventory', []))
                text f"Inventory: {inv_count}" size 9 color "#ffffff" font "fonts/UbuntuMono-R.ttf"
                
                # Show active debug categories
                $ active_cats = [cat for cat, enabled in DEBUG_CATEGORIES.items() if enabled]
                if len(active_cats) < 12:  # Only show if not all are active
                    text "Active: " + ", ".join(active_cats[:3]) + "..." size 8 color "#888888" font "fonts/UbuntuMono-R.ttf"
