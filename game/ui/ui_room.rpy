# Room UI Controls System
# Buttons, hotspots, and interactive elements
#
# Overview
# - Hosts UI buttons (exit) and object hotspots for exploration.
# - Delegates actions to UI/API functions to avoid screen logic bloat.

# UI button configuration
# ROOM_BUTTON_CONFIG is defined in config/config_room.rpy

init python:
    # Moved UI routines to api/api_ui.rpy
    pass

# Screen fragment for object hotspots
screen object_hotspots():
    # Only show interactive hotspots when interaction menu is NOT active
    if not interaction_menu_active:
        # Interactive hotspots for objects
        for obj_name, obj_data in room_objects.items():
            if not is_object_hidden(obj_data):
                button:
                    xpos obj_data["x"]
                    ypos obj_data["y"]
                    xsize obj_data["width"]
                    ysize obj_data["height"]
                    background None
                    if get_object_focus_mask(obj_data):
                        focus_mask get_object_focus_mask(obj_data)
                    action Function(show_interaction_menu, obj_name)
                    hovered Function(handle_object_hover, obj_name)
                    unhovered Function(handle_object_unhover)

# Screen fragment for UI buttons
screen room_ui_buttons():
    # Calculate letterbox offset for UI positioning
    $ letterbox_offset = 0
    if letterbox_enabled:
        $ letterbox_offset = letterbox_height
    
    # Exit button in top right, with confirmation prompt
    textbutton ROOM_BUTTON_CONFIG["exit"]["text"]:
        xpos ROOM_BUTTON_CONFIG["exit"]["xpos"]
        ypos letterbox_offset + ROOM_BUTTON_CONFIG["exit"]["ypos"]
        action get_room_exit_action()
        tooltip "Return to the main menu"
        text_color ROOM_BUTTON_CONFIG["exit"]["text_color"]
        text_hover_color ROOM_BUTTON_CONFIG["exit"]["text_hover_color"]
        background ROOM_BUTTON_CONFIG["exit"]["background"]
        padding (
            ROOM_BUTTON_CONFIG["exit"]["padding"]["horizontal"],
            ROOM_BUTTON_CONFIG["exit"]["padding"]["vertical"]
        )
        text_size ROOM_BUTTON_CONFIG["exit"]["text_size"]
    
    # Editor mode button removed (use F8 to toggle editor)
    

# Utility functions for button customization
init python:
    # Moved customization helpers to api/api_ui.rpy
    pass
