# Font Configuration
# Defines custom fonts for the game
#
# Overview
# - Central mapping for the project's font face and sizes across UI elements.
# - Loaded after GUI initialization.

# Use init offset to ensure this runs after GUI initialization
init offset = -1

# Override default fonts for all game elements
init python:
    # Register the font for different uses
    style.default.font = "fonts/quaver.ttf"
    style.default.size = 24
    
    # Button fonts
    style.button_text.font = "fonts/quaver.ttf"
    style.button_text.size = 24
    
    # Menu fonts
    style.main_menu_text.font = "fonts/quaver.ttf"
    style.game_menu_label.font = "fonts/quaver.ttf"
    
    # Choice button fonts
    style.choice_button_text.font = "fonts/quaver.ttf"
    style.choice_button_text.size = 24
    
    # Navigation fonts
    style.navigation_button_text.font = "fonts/quaver.ttf"
    
    # Quick menu fonts
    style.quick_button_text.font = "fonts/quaver.ttf"
    style.quick_button_text.size = 16
    
    # Dialogue fonts
    style.dialogue.font = "fonts/quaver.ttf"
    style.dialogue.size = 24
    
    # Say label (character name) fonts
    style.say_label.font = "fonts/quaver.ttf"
    style.say_label.size = 32
    
    # Interface fonts
    style.pref_label_text.font = "fonts/quaver.ttf"
    style.pref_button_text.font = "fonts/quaver.ttf"
    style.check_button_text.font = "fonts/quaver.ttf"
    style.radio_button_text.font = "fonts/quaver.ttf"
    style.bar_label_text.font = "fonts/quaver.ttf"
    
    # File slot fonts
    style.slot_button_text.font = "fonts/quaver.ttf"
    style.slot_time_text.font = "fonts/quaver.ttf"
    style.slot_name_text.font = "fonts/quaver.ttf"
    
    # Notify fonts
    style.notify_text.font = "fonts/quaver.ttf"
    style.notify_text.size = 16
    
    # Skip indicator fonts
    style.skip_text.font = "fonts/quaver.ttf"
    
    # History fonts
    style.history_text.font = "fonts/quaver.ttf"
    style.history_name_text.font = "fonts/quaver.ttf"
    
    # Help fonts
    style.help_text.font = "fonts/quaver.ttf"
    style.help_label_text.font = "fonts/quaver.ttf"
    
    # About fonts
    style.about_text.font = "fonts/quaver.ttf"
    style.about_label_text.font = "fonts/quaver.ttf"
