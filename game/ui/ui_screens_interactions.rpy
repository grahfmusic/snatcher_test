################################################################################
## Object Interaction System
################################################################################
##
## This file contains the interaction system for objects in the room.
## When A is pressed on an object, context-sensitive action buttons appear.
##
## Overview
## - Builds action lists per object type and renders a simple vertical menu.
## - Exposes keyboard/gamepad bindings for selection and confirm/cancel.
##

init offset = -1

## Interaction Configuration
################################################################################

## Whether interaction menu is currently active
# interaction_menu_active is defined in core_room_exploration.rpy
# interaction_target is defined in core_interaction_system.rpy
# interaction_target_object is defined in api_interactions.rpy
# interaction_selected_action is defined in api_interactions.rpy
# previous_hover_action is defined in api_interactions.rpy


## Action definitions by object type
define INTERACTION_ACTIONS = {
    "character": [
        {"label": "Talk", "action": "talk"},
        {"label": "Ask About", "action": "ask_about"}, 
        {"label": "Leave", "action": "leave"}
    ],
    "item": [
        {"label": "Take", "action": "take"},
        {"label": "Investigate", "action": "investigate"},
        {"label": "Leave", "action": "leave"}
    ],
    "door": [
        {"label": "Open", "action": "open"},
        {"label": "Knock", "action": "knock"},
        {"label": "Leave", "action": "leave"}
    ],
    "container": [
        {"label": "Open", "action": "open"},
        {"label": "Search", "action": "search"},
        {"label": "Leave", "action": "leave"}
    ]
}

## Button styling with curved frames
define INTERACTION_BUTTON_CONFIG = {
    "width": 112,
    "height": 32,
    "spacing": 5,
    "background_frame": "button_interaction.png",
    "border_size": 15,
    "background_normal": "#383838dd",
    "background_hover": "#335c66dd",  # Dark red-purple
    "background_selected": "#48c4dadd",  # Dark red-purple for selected
    "text_color": "#ffffff",
    "text_hover_color": "#ffffff",  # White text on hover
    "text_selected_color": "#ffffff",  # White text when selected
    "text_size": 14,
    "padding": (8, 6)
}

init python:
    # Moved color and background helpers to api/api_interactions.rpy
    pass

################################################################################
## Interaction Functions
################################################################################

init python:
    # Moved interaction routines to api/api_interactions.rpy
    pass

################################################################################
## Interaction Menu Screen
################################################################################

screen interaction_menu():
    # Put interaction menu above letterbox
    zorder 160
    
    $ _target = getattr(store, 'interaction_target', None)
    if interaction_menu_active and _target and not lighting_editor_open:
        # Modal overlay to capture clicks outside the menu
        button:
            xpos 0
            ypos 0
            xsize config.screen_width
            ysize config.screen_height
            background None
            action Function(hide_interaction_menu)
        $ obj = room_objects[_target]
        $ obj_type = obj.get("object_type", "item")
        $ actions = get_actions_for_object(_target)
        
        # Get float intensity from the target object
        $ float_intensity = obj.get("float_intensity", 1.0)
        $ should_float = float_intensity > 0.0
        
        # Get base position for the entire menu
        $ menu_x, menu_y = get_menu_base_position(_target)
        
        # Create menu container with floating animation
        if should_float:
            $ x0, y0, r0, dly = compute_float_phase(_target, float_intensity)
            vbox at floating_bubble(float_intensity, x0, y0, r0, dly):
                xpos menu_x
                ypos menu_y
                spacing INTERACTION_BUTTON_CONFIG["spacing"]
                
                for i, action_data in enumerate(actions):
                    $ is_selected = (i == interaction_selected_action)
                    
                    frame:
                        xsize INTERACTION_BUTTON_CONFIG["width"]
                        ysize INTERACTION_BUTTON_CONFIG["height"]
                        
                        # Create curved frame background with tint based on state
                        if is_selected:
                            # Use pulsing cyan border as the main background for selected button
                            background Frame(
                                Transform(INTERACTION_BUTTON_CONFIG["background_frame"], matrixcolor=TintMatrix("#00ffff")),
                                INTERACTION_BUTTON_CONFIG["border_size"],
                                INTERACTION_BUTTON_CONFIG["border_size"],
                                tile=False
                            ) at pulsing_border
                        else:
                            # Static background for non-selected buttons
                            background Frame(
                                Transform(INTERACTION_BUTTON_CONFIG["background_frame"], matrixcolor=TintMatrix(INTERACTION_BUTTON_CONFIG["background_normal"])), 
                                INTERACTION_BUTTON_CONFIG["border_size"], 
                                INTERACTION_BUTTON_CONFIG["border_size"], 
                                tile=False
                            )
                            
                            # Hover background for non-selected buttons
                            hover_background Frame(
                                Transform(INTERACTION_BUTTON_CONFIG["background_frame"], matrixcolor=TintMatrix(INTERACTION_BUTTON_CONFIG["background_hover"])), 
                                INTERACTION_BUTTON_CONFIG["border_size"], 
                                INTERACTION_BUTTON_CONFIG["border_size"], 
                                tile=False
                            )
                        
                        padding INTERACTION_BUTTON_CONFIG["padding"]
                        
                        # Button with transparent background since frame handles the visuals
                        textbutton action_data["label"]:
                            background None
                            hover_background None
                            # Use helper function to get appropriate action
                            action get_button_action(_target, action_data)
                            
                            # Mouse interaction: update selection on hover with sound feedback
                            hovered [
                                Function(lambda i=i: renpy.sound.play(
                                    "audio/ui/down.wav" if i > previous_hover_action else "audio/ui/up.wav",
                                    channel="menu_nav"
                                ) if previous_hover_action != i else None),
                                SetVariable("previous_hover_action", i),
                                SetVariable("interaction_selected_action", i)
                            ]
                            unhovered NullAction()
                            
                            if is_selected:
                                text_color INTERACTION_BUTTON_CONFIG["text_selected_color"]
                            else:
                                text_color INTERACTION_BUTTON_CONFIG["text_color"]
                                text_hover_color INTERACTION_BUTTON_CONFIG["text_hover_color"]
                            
                            text_size INTERACTION_BUTTON_CONFIG["text_size"]
                            xalign 0.5
                            yalign 0.5
        else:
            vbox at no_float:
                xpos menu_x
                ypos menu_y
                spacing INTERACTION_BUTTON_CONFIG["spacing"]
                
                for i, action_data in enumerate(actions):
                    $ is_selected = (i == interaction_selected_action)
                    
                    frame:
                        xsize INTERACTION_BUTTON_CONFIG["width"]
                        ysize INTERACTION_BUTTON_CONFIG["height"]
                        
                        # Create curved frame background with tint based on state
                        if is_selected:
                            # Use pulsing cyan border as the main background for selected button
                            background Frame(
                                Transform(INTERACTION_BUTTON_CONFIG["background_frame"], matrixcolor=TintMatrix("#00ffff")),
                                INTERACTION_BUTTON_CONFIG["border_size"],
                                INTERACTION_BUTTON_CONFIG["border_size"],
                                tile=False
                            ) at pulsing_border
                        else:
                            # Static background for non-selected buttons
                            background Frame(
                                Transform(INTERACTION_BUTTON_CONFIG["background_frame"], matrixcolor=TintMatrix(INTERACTION_BUTTON_CONFIG["background_normal"])), 
                                INTERACTION_BUTTON_CONFIG["border_size"], 
                                INTERACTION_BUTTON_CONFIG["border_size"], 
                                tile=False
                            )
                            
                            # Hover background for non-selected buttons
                            hover_background Frame(
                                Transform(INTERACTION_BUTTON_CONFIG["background_frame"], matrixcolor=TintMatrix(INTERACTION_BUTTON_CONFIG["background_hover"])), 
                                INTERACTION_BUTTON_CONFIG["border_size"], 
                                INTERACTION_BUTTON_CONFIG["border_size"], 
                                tile=False
                            )
                        
                        padding INTERACTION_BUTTON_CONFIG["padding"]
                        
                        # Button with transparent background since frame handles the visuals
                        textbutton action_data["label"]:
                            background None
                            hover_background None
                            # Use helper function to get appropriate action
                            action get_button_action(_target, action_data)
                            
                            # Mouse interaction: update selection on hover (optimized for responsiveness)
                            hovered [
                                Function(lambda i=i: renpy.sound.play(
                                    "audio/ui/down.wav" if i > previous_hover_action else "audio/ui/up.wav",
                                    channel="menu_nav"
                                ) if previous_hover_action != i else None),
                                SetVariable("previous_hover_action", i),
                                SetVariable("interaction_selected_action", i)
                            ]
                            unhovered NullAction()
                            
                            if is_selected:
                                text_color INTERACTION_BUTTON_CONFIG["text_selected_color"]
                            else:
                                text_color INTERACTION_BUTTON_CONFIG["text_color"]
                                text_hover_color INTERACTION_BUTTON_CONFIG["text_hover_color"]
                            
                            text_size INTERACTION_BUTTON_CONFIG["text_size"]
                            xalign 0.5
                            yalign 0.5

################################################################################
## Enhanced Gamepad Functions
################################################################################

init python:
    # Moved gamepad and button helpers to api/api_interactions.rpy
    pass

## Initialize interaction menu screen
# Add interaction_menu to overlay screens so it shows automatically when interaction_menu_active is True
init python:
    config.overlay_screens.append("interaction_menu")
