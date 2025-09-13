# Room2 Configuration and Initialization
# Template for room2 setup - customize as needed
#
# Overview:
# - Defines all room2 objects with their properties
# - Sets up sprite animations and transforms
# - Configures audio assets (music, sfx, speech)
# - Manages room-specific visual effects

## Room2 Asset Paths
################################################################################

# Base path for room2 assets
define ROOM2_BASE_PATH = "rooms/room2/"

# Asset subdirectories
define ROOM2_SPRITES_PATH = ROOM2_BASE_PATH + "sprites/"
define ROOM2_AUDIO_PATH = ROOM2_BASE_PATH + "audio/"
define ROOM2_VIDEO_PATH = ROOM2_BASE_PATH + "video/"

# Audio subdirectories
define ROOM2_MUSIC_PATH = ROOM2_AUDIO_PATH + "music/"
define ROOM2_SFX_PATH = ROOM2_AUDIO_PATH + "sfx/"
define ROOM2_SPEECH_PATH = ROOM2_AUDIO_PATH + "speech/"

## Room2 Sprite Animations
################################################################################

# Example animations - customize for your room2 objects
transform room2_object_idle():
    linear 4.0 yoffset -3
    linear 4.0 yoffset 3
    repeat

transform room2_object_active():
    linear 1.0 xoffset -2 yoffset -2
    linear 1.0 xoffset 2 yoffset 2
    repeat

## Room2 Audio Configuration
################################################################################

# Background music for room2
define ROOM2_AMBIENT_MUSIC = ROOM2_MUSIC_PATH + "room2_ambient.ogg"
define ROOM2_TENSION_MUSIC = ROOM2_MUSIC_PATH + "room2_tension.ogg"

# Sound effects - add your room2 specific sounds
define ROOM2_DOOR_OPEN = ROOM2_SFX_PATH + "door_open.ogg"
define ROOM2_MACHINE_HUM = ROOM2_SFX_PATH + "machine_hum.ogg"

## Room2 Object Definitions
################################################################################

# Define your room2 objects here
define ROOM2_OBJECTS = {
    # Example object - replace with your actual objects
    "example_object": merge_configs({
        "x": 100, "y": 100, 
        "scale_percent": 100,
        "width": 200,
        "height": 200,
        "image": "images/room2_object.png",
        "description": "An example object in room2.",
        "box_position": "auto",
        "float_intensity": 0.3,
        "object_type": "item",
        
        # Animation settings
        "idle_animation": "room2_object_idle",
        "active_animation": "room2_object_active",
        "current_animation": "room2_object_idle",
        
        # Audio settings
        "interaction_sounds": {
            "investigate": ROOM2_MACHINE_HUM
        }
    },
    create_desaturation_config(DESATURATION_PRESETS["neon_subtle"]),
    create_animation_config({
        "hover_scale_boost": 1.02,
        "hover_brightness_boost": 0.1
    }))
}

## Room2 Environmental Effects
################################################################################

define ROOM2_LIGHTING = {
    "ambient_light": 0.8,
    "shadow_intensity": 0.6,
    "light_temperature": "warm",
    "flickering_lights": False,
    "flicker_intensity": 0.0
}

# Atmosphere configuration removed - was unused legacy code

## Room2 Initialization Functions
################################################################################

init python:
    def initialize_room2_objects():
        """Initialize all room2 objects with their animations and properties"""
        try:
            # Initialize your room2 objects here
            debug_log("ROOM", "Room2 objects initialized successfully")
        except Exception as e:
            debug_log("ERROR", f"Room2 object initialization failed: {e}")
    
    def setup_room2_audio():
        """Set up room2 audio channels and preload sounds"""
        try:
            # Use default Ren'Py audio channels:
            # - 'music' for background music
            # - 'sound' for sound effects
            # - 'voice' for character speech
            # No custom channel registration needed
            debug_log("ROOM", "Room2 audio system initialized")
        except Exception as e:
            debug_log("ERROR", f"Room2 audio setup failed: {e}")
    
    def apply_room2_effects():
        """Apply room2 specific visual effects and lighting"""
        try:
            lighting = ROOM2_LIGHTING
            store.room_ambient_light = lighting["ambient_light"]
            store.room_shadow_intensity = lighting["shadow_intensity"]
            debug_log("ROOM", "Room2 visual effects applied")
        except Exception as e:
            debug_log("ERROR", f"Room2 visual effects failed: {e}")

## Room2 Integration with Main System
################################################################################

define ROOM_DEFINITIONS_ROOM2 = {
    "room2": {
        "background": "images/room2.png",
        "objects": ROOM2_OBJECTS,
        "initialization_func": initialize_room2_objects,
        "audio_setup_func": setup_room2_audio,
        "effects_func": apply_room2_effects,
        "music": ROOM2_AMBIENT_MUSIC,
        "ambient_channel": "music"
    }
}

## Initialization Call
################################################################################

init python:
    initialize_room2_objects()
    setup_room2_audio()
    apply_room2_effects()
