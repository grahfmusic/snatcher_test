# Core Game Framework - Main Exploration Screen
# Clean, modular room exploration with proper Ren'Py patterns
#
# This is the main gameplay screen that handles:
# - Room display with objects
# - Mouse/keyboard navigation
# - Shader effects
# - Interaction system

## Core Variables (properly declared with defaults)
default current_room_id = None
default room_objects = {}
default room_background = None
default selected_object = None
default current_hover_object = None
default previous_hover_object = None
default description_fade_state = "hidden"  # "hidden", "fading_in", "visible", "fading_out"
default description_fade_start_time = 0.0
default description_fading_out = False
default description_fade_start = 0.0
default interaction_menu_active = False
default editor_mode = False
default show_description_boxes = True
default gamepad_navigation_enabled = False
default gamepad_selected_object = None

## Room Configuration
# All room configuration (ROOM_DISPLAY_CONFIG, ROOM_BUTTON_CONFIG, etc.) 
# is centralized in config/config_room.rpy

## Main Room Exploration Screen
screen room_exploration():
    # Ensure we have valid room data
    if not current_room_id:
        text "No room loaded" xalign 0.5 yalign 0.5
    else:
        pass
    
    # === BACKGROUND LAYER ===
    # Display room background or fallback
    $ bg = get_room_background()
    if bg:
        add bg
    else:
        add Solid(ROOM_DISPLAY_CONFIG["fallback_background_color"])
    
    # === OBJECT LAYER ===
    # Display all room objects
    for obj_name, obj_data in room_objects.items():
        if should_display_object(obj_data) and not is_object_hidden(obj_data):
            $ props = get_object_display_properties(obj_data)
            
            # Object image with proper positioning
            add props["image"]:
                xpos props["xpos"]
                ypos props["ypos"]
                xsize props["xsize"]
                ysize props["ysize"]
                
                # Apply breathing animation if configured
                if has_breathing_animation(obj_name):
                    at breathing_transform(obj_name)
    
    # === HOVER HIGHLIGHTS ===
    # Show highlight for hovered object (mouse or gamepad)
    $ hover_obj = current_hover_object or gamepad_selected_object
    if hover_obj and hover_obj in room_objects:
        $ obj = room_objects[hover_obj]
        add Solid(ROOM_DISPLAY_CONFIG["object_highlight_color"]):
            alpha ROOM_DISPLAY_CONFIG["object_highlight_alpha"]
            xpos obj["x"]
            ypos obj["y"]
            xsize obj["width"]
            ysize obj["height"]
    
    # === INTERACTION HOTSPOTS ===
    # Create clickable areas for objects
    if not interaction_menu_active and not editor_mode:
        for obj_name, obj_data in room_objects.items():
            if should_display_object(obj_data) and not is_object_hidden(obj_data):
                $ mask = get_object_focus_mask(obj_data)
                button:
                    xpos obj_data["x"]
                    ypos obj_data["y"]
                    xsize obj_data["width"]
                    ysize obj_data["height"]
                    
                    # Use focus mask for pixel-perfect hover if available
                    if mask:
                        focus_mask mask
                    
                    # Actions
                    action Function(handle_object_click, obj_name)
                    hovered Function(handle_object_hover, obj_name)
                    unhovered Function(handle_object_unhover)
                    
                    # Invisible button (objects handle their own display)
                    background None
    
    # === DESCRIPTION BOXES ===
    # Show description for hovered object
    if show_description_boxes and hover_obj and hover_obj in room_objects:
        $ obj = room_objects[hover_obj]
        if "description" in obj and obj["description"]:
            $ desc_x, desc_y, desc_pos = calculate_description_position(obj)
            
            frame:
                xpos desc_x
                ypos desc_y
                xmaximum ROOM_DISPLAY_CONFIG["max_description_width"]
                ymaximum ROOM_DISPLAY_CONFIG["max_description_height"]
                background Frame(ROOM_DISPLAY_CONFIG["description_box_bg"])
                padding ROOM_DISPLAY_CONFIG["description_box_padding"]
                
                text obj["description"]:
                    size 14
                    color "#ffffff"
                    text_align 0.5
    
    # === UI CONTROLS ===
    # Exit button
    textbutton ROOM_BUTTON_CONFIG["exit"]["text"]:
        xpos ROOM_BUTTON_CONFIG["exit"]["xpos"]
        ypos ROOM_BUTTON_CONFIG["exit"]["ypos"]
        style "room_button"
        action get_room_exit_action()
    
    # Editor button removed (use F8 to toggle editor)
    
    # Custom buttons
    for button_id, button_config in ROOM_BUTTON_CONFIG.items():
        if button_id not in ["exit", "editor"]:
            textbutton button_config.get("text", button_id):
                xpos button_config.get("xpos", 20)
                ypos button_config.get("ypos", 60)
                style button_config.get("style", "room_button")
                action button_config.get("action", NullAction())
    
    # === KEYBOARD/GAMEPAD NAVIGATION ===
    if gamepad_navigation_enabled:
        # D-pad/Arrow keys for navigation
        key "K_LEFT" action Function(gamepad_navigate, "left")
        key "K_RIGHT" action Function(gamepad_navigate, "right")
        key "K_UP" action Function(gamepad_navigate, "up")
        key "K_DOWN" action Function(gamepad_navigate, "down")
        
        # Action button
        key "K_RETURN" action Function(handle_gamepad_select)
        key "K_SPACE" action Function(handle_gamepad_select)

## Room Exploration with Shader Effects (Deprecated)
# Removed in favor of unified room_exploration + overlays

## Helper Functions
init python:
    def handle_object_click(obj_name):
        """Handle clicking on an object - show interaction menu."""
        store.interaction_menu_active = True
        store.interaction_target = obj_name
        # The interaction_menu screen doesn't take parameters - it uses interaction_target
        renpy.show_screen("interaction_menu")
        renpy.restart_interaction()
    
    def handle_gamepad_select():
        """Handle gamepad selection of current object."""
        if store.gamepad_selected_object:
            handle_object_click(store.gamepad_selected_object)
    
    def calculate_description_position(obj):
        """Calculate optimal position for description box."""
        box_width = ROOM_DISPLAY_CONFIG["max_description_width"]
        box_height = ROOM_DISPLAY_CONFIG["max_description_height"]
        
        # Get position preference
        pos_pref = obj.get("box_position", "auto")
        
        # Calculate position using the API
        return calculate_box_position(
            obj, box_width, box_height, pos_pref
        )
    
    def has_breathing_animation(obj_name):
        """Check if object has breathing animation configured."""
        if not hasattr(store, 'ROOM_BREATHING_SETTINGS'):
            return False
        
        room_settings = ROOM_BREATHING_SETTINGS.get(store.current_room_id, {})
        obj_settings = room_settings.get(obj_name, {})
        
        # Check for breathing enabled flag
        if isinstance(obj_settings, dict):
            return obj_settings.get('breath_enabled', False)
        return False
    
    def breathing_transform(obj_name):
        """Get breathing transform for an object."""
        # This would return the appropriate breathing transform
        # based on the object's breathing configuration
        # For now, return identity transform
        return Transform()

## Styles
style room_button:
    padding (10, 5)
    background "#333333aa"
    hover_background "#555555aa"
    
style room_button_text:
    size 16
    color "#ffffff"
    hover_color "#00ff00"
