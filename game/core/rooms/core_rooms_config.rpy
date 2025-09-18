# Room Configuration
# Contains all room object definitions and constants organized by room
#
# Overview
# - Author rooms declaratively using merge_configs and builder helpers.
# - Keep IDs lowercase; images under game/images/.

# Utility modules loaded by Ren'Py script loader

# Object configuration templates to eliminate duplication
define DEFAULT_DESATURATION_CONFIG = {
    "desaturation_enabled": True,
    "desaturation_intensity": 0.5,
    "desaturation_alpha_min": 0.3,
    "desaturation_alpha_max": 0.7,
    "desaturation_pulse_speed": 1.0,
    "desaturation_fade_duration": 0.3
}

# Legacy bloom config (kept for compatibility)
define DEFAULT_BLOOM_CONFIG = DEFAULT_DESATURATION_CONFIG

define DEFAULT_ANIMATION_CONFIG = {
    "hover_animation_type": "breathe",
    "hover_scale_boost": 1.02,
    "hover_brightness_boost": 0.1
}

define DEFAULT_OBJECT_CONFIG = {
    "float_intensity": 0.5,
    "box_position": "auto"
}


# Room definitions - now integrated with room-based directory structure
# Individual room configurations are defined in their respective directories:
# - rooms/room1/scripts/room1_config.rpy
# - rooms/room2/scripts/room2_config.rpy
# - rooms/room3/scripts/room3_config.rpy

init python:
    # This combines all room definitions from the room-specific configs
    def get_combined_room_definitions():
        """Combine room definitions from all room-specific configuration files"""
        combined_rooms = {}
        
        # Merge room1 definitions if they exist
        if 'ROOM_DEFINITIONS_ROOM1' in globals():
            combined_rooms.update(ROOM_DEFINITIONS_ROOM1)
        
        # Merge room2 definitions if they exist
        if 'ROOM_DEFINITIONS_ROOM2' in globals():
            combined_rooms.update(ROOM_DEFINITIONS_ROOM2)
            
        # Merge room3 definitions if they exist
        if 'ROOM_DEFINITIONS_ROOM3' in globals():
            combined_rooms.update(ROOM_DEFINITIONS_ROOM3)
        
        # No fallback definitions; rooms must provide their own configs
        return combined_rooms

# Initialize room definitions variable
define ROOM_DEFINITIONS = {}

# Dynamic room definitions that update based on loaded room configs
init python:
    def update_room_definitions():
        """Update the global ROOM_DEFINITIONS with combined room data"""
        global ROOM_DEFINITIONS
        ROOM_DEFINITIONS = get_combined_room_definitions()
        debug_log("SYSTEM", f"Loaded {len(ROOM_DEFINITIONS)} room definitions")

# Initialize room definitions
init 2 python:
    # Call after all room config files have loaded
    update_room_definitions()

# BOX POSITION OPTIONS:
# "top+30"    - Above object, 30px distance
# "bottom+50" - Below object, 50px distance  
# "left+25"   - Left of object, 25px distance
# "right+60"  - Right of object, 60px distance
# "auto"      - Let system choose best position (default if not specified)

# Global room interaction variables
# These are defined in core_room_exploration.rpy:
# - current_room_id
# - current_hover_object  
# - previous_hover_object
# - room_objects
# - room_background
default speech_bubble_offset = 0.0

# GLOBAL EDITOR MODE VARIABLES
# editor_mode is defined in core_room_exploration.rpy
# selected_object is defined in core_room_exploration.rpy
default move_speed = 5  # Pixels to move per keypress
default show_editor_help = True

# GAMEPAD NAVIGATION VARIABLES  
# gamepad_selected_object is defined in core_room_exploration.rpy
# gamepad_navigation_enabled is defined in core_room_exploration.rpy

# Room loading should be done at runtime, not during init
# The initial room load is handled by the game start label
