# Room3 Configuration and Initialization
# Template for room3 setup - customize as needed

## Room3 Asset Paths
################################################################################

define ROOM3_BASE_PATH = "rooms/room3/"
define ROOM3_SPRITES_PATH = ROOM3_BASE_PATH + "sprites/"
define ROOM3_AUDIO_PATH = ROOM3_BASE_PATH + "audio/"
define ROOM3_VIDEO_PATH = ROOM3_BASE_PATH + "video/"
define ROOM3_MUSIC_PATH = ROOM3_AUDIO_PATH + "music/"
define ROOM3_SFX_PATH = ROOM3_AUDIO_PATH + "sfx/"
define ROOM3_SPEECH_PATH = ROOM3_AUDIO_PATH + "speech/"

## Room3 Sprite Animations
################################################################################

transform room3_object_pulse():
    linear 2.0 alpha 0.8
    linear 2.0 alpha 1.0
    repeat

## Room3 Audio Configuration
################################################################################

define ROOM3_AMBIENT_MUSIC = ROOM3_MUSIC_PATH + "room3_ambient.ogg"
define ROOM3_MYSTERY_SFX = ROOM3_SFX_PATH + "mystery_sound.ogg"

## Room3 Object Definitions
################################################################################

define ROOM3_OBJECTS = {
    # Add your room3 objects here
}

## Room3 Environmental Effects
################################################################################

define ROOM3_LIGHTING = {
    "ambient_light": 0.6,
    "shadow_intensity": 0.9,
    "light_temperature": "cool",
    "flickering_lights": True,
    "flicker_intensity": 0.2
}

# Atmosphere configuration removed - was unused legacy code

## Room3 Initialization Functions
################################################################################

init python:
    def initialize_room3_objects():
        """Initialize all room3 objects"""
        try:
            debug_log("ROOM", "Room3 objects initialized successfully")
        except Exception as e:
            debug_log("ERROR", f"Room3 object initialization failed: {e}")
    
    def setup_room3_audio():
        """Set up room3 audio channels"""
        try:
            # Use default Ren'Py audio channels:
            # - 'music' for background music
            # - 'sound' for sound effects
            # - 'voice' for character speech
            # No custom channel registration needed
            debug_log("ROOM", "Room3 audio system initialized")
        except Exception as e:
            debug_log("ERROR", f"Room3 audio setup failed: {e}")
    
    def apply_room3_effects():
        """Apply room3 specific effects"""
        try:
            lighting = ROOM3_LIGHTING
            store.room_ambient_light = lighting["ambient_light"]
            debug_log("ROOM", "Room3 visual effects applied")
        except Exception as e:
            debug_log("ERROR", f"Room3 visual effects failed: {e}")

## Room3 Integration with Main System
################################################################################

define ROOM_DEFINITIONS_ROOM3 = {
    "room3": {
        "background": "images/room3.png",
        "objects": ROOM3_OBJECTS,
        "initialization_func": initialize_room3_objects,
        "audio_setup_func": setup_room3_audio,
        "effects_func": apply_room3_effects,
        "music": ROOM3_AMBIENT_MUSIC,
        "ambient_channel": "music"
    }
}

## Initialization Call
################################################################################

init python:
    initialize_room3_objects()
    setup_room3_audio()
    apply_room3_effects()
