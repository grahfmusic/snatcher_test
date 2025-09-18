# Room Configuration
# Centralized configuration for all room-related settings
# This includes display settings, button configurations, and other room parameters

## Room Display Configuration
# Settings for how rooms and objects are displayed
define ROOM_DISPLAY_CONFIG = {
    "fallback_background_color": "#000000",
    "default_background": None,
    "fade_duration": 2.0,
    "object_highlight_color": "#00ff00",
    "object_highlight_alpha": 0.0,
    "description_box_padding": 20,
    "description_box_bg": "#000000cc",
    "max_description_width": 300,
    "max_description_height": 150
}

## UI Button Configuration
# Settings for room UI buttons (exit, custom, etc.)
define ROOM_BUTTON_CONFIG = {
    "exit": {
        "text": "Exit Room",
        "xpos": 1130,
        "ypos": 20,
        "text_color": "#ffffff",
        "text_hover_color": "#ffff00",
        "background": "#333333aa",
        "padding": {"horizontal": 15, "vertical": 8},
        "text_size": 16
    },
}

## Additional Room Settings
# Other room-related configuration can be added here
define ROOM_INTERACTION_CONFIG = {
    "menu_fade_time": 0.3,
    "hover_highlight_time": 0.1,
    "double_click_time": 0.5,
    "gamepad_scroll_speed": 5
}

# Room audio settings
define ROOM_AUDIO_CONFIG = {
    "fade_in_time": 2.0,
    "fade_out_time": 1.5,
    "ambient_volume": 0.7,
    "effect_volume": 0.8
}
