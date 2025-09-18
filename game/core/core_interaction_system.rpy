# Interaction System
# Clean, extensible object interaction menu
#
# Features:
# - Context-sensitive actions
# - Customizable per-object actions
# - Smooth animations
# - Keyboard/gamepad support

## Interaction Configuration
default interaction_target = None
default interaction_actions = {}

define INTERACTION_CONFIG = {
    "default_actions": ["Examine", "Use", "Talk"],
    "menu_bg": "#000000dd",
    "menu_padding": 15,
    "button_spacing": 10,
    "text_size": 16,
    "text_color": "#ffffff",
    "text_hover": "#00ff00",
    "animation_time": 0.3
}

## Interaction Menu Screen (Legacy - using core_interaction_menu to avoid conflict)
screen core_interaction_menu(obj_name):
    modal True
    zorder 100
    
    # Get object data
    $ obj_data = room_objects.get(obj_name, {})
    if not obj_data:
        $ interaction_menu_active = False
        # Cannot use return in screen, just don't display anything
        pass
    else:
        # Background dim
        add Solid("#00000066")
        
        # Click outside to close
        button:
            xfill True
            yfill True
            action [
                SetVariable("interaction_menu_active", False),
                SetVariable("interaction_target", None),
                Hide("interaction_menu")
            ]
        # Menu container
        $ menu_x, menu_y = calculate_menu_position(obj_data)
        frame:
            xpos menu_x
            ypos menu_y
            
            background Frame(INTERACTION_CONFIG["menu_bg"])
            padding INTERACTION_CONFIG["menu_padding"]
            
            # Fade in animation
            at transform:
                alpha 0.0
                zoom 0.9
                linear INTERACTION_CONFIG["animation_time"] alpha 1.0 zoom 1.0
            
            vbox:
                spacing INTERACTION_CONFIG["button_spacing"]
                
                # Object name header
                text obj_name:
                    size INTERACTION_CONFIG["text_size"] + 2
                    color "#ffaa00"
                    xalign 0.5
                
                # Separator
                add Solid("#555555"):
                    xsize 150
                    ysize 1
                    xalign 0.5
                
                # Action buttons
                $ actions = get_object_actions(obj_name, obj_data)
                for action in actions:
                    textbutton action:
                        xfill True
                        text_size INTERACTION_CONFIG["text_size"]
                        text_color INTERACTION_CONFIG["text_color"]
                        text_hover_color INTERACTION_CONFIG["text_hover"]
                        text_xalign 0.5
                        action Function(execute_interaction, obj_name, action)
                
                # Cancel button
                add Solid("#555555"):
                    xsize 150
                    ysize 1
                    xalign 0.5
                
                textbutton "Cancel":
                    xfill True
                    text_size INTERACTION_CONFIG["text_size"]
                    text_color "#888888"
                    text_hover_color "#ff4444"
                    text_xalign 0.5
                    action [
                        SetVariable("interaction_menu_active", False),
                        SetVariable("interaction_target", None),
                        Hide("interaction_menu")
                    ]
    
    # Keyboard shortcuts
    key "K_ESCAPE" action [
        SetVariable("interaction_menu_active", False),
        SetVariable("interaction_target", None),
        Hide("interaction_menu")
    ]
    
    # Number keys for quick actions
    for i in range(min(9, len(actions))):
        key str(i+1) action Function(execute_interaction, obj_name, actions[i])

## Interaction Functions
init python:
    def calculate_menu_position(obj_data):
        """Calculate optimal position for interaction menu."""
        # Center menu on object
        menu_width = 200
        menu_height = 250
        
        obj_center_x = obj_data["x"] + obj_data["width"] // 2
        obj_center_y = obj_data["y"] + obj_data["height"] // 2
        
        # Adjust position to keep menu on screen
        menu_x = max(50, min(obj_center_x - menu_width // 2, 1280 - menu_width - 50))
        menu_y = max(50, min(obj_center_y - menu_height // 2, 720 - menu_height - 50))
        
        return menu_x, menu_y
    
    def get_object_actions(obj_name, obj_data):
        """Get available actions for an object."""
        # Check for custom actions
        if obj_name in interaction_actions:
            return interaction_actions[obj_name]
        
        # Check object data for actions
        if "actions" in obj_data:
            return obj_data["actions"]
        
        # Use default actions based on object type
        if "character" in obj_data.get("tags", []):
            return ["Talk", "Examine", "Give Item"]
        elif "item" in obj_data.get("tags", []):
            return ["Examine", "Take", "Use"]
        else:
            return INTERACTION_CONFIG["default_actions"]
    
    def execute_interaction(obj_name, action):
        """Execute an interaction action."""
        # Log the interaction
        try:
            log_main_event("INTERACT", f"{action} {obj_name}")
        except Exception:
            pass
        
        # Close menu first
        store.interaction_menu_active = False
        store.interaction_target = None
        renpy.hide_screen("interaction_menu")
        
        # Check game logic hooks
        try:
            if on_object_interact(store.current_room_id, obj_name, action.lower()):
                # Interaction was handled by game logic
                renpy.restart_interaction()
                return
        except Exception:
            pass
        
        # Default handlers
        if action.lower() == "examine":
            examine_object(obj_name)
        elif action.lower() == "use":
            use_object(obj_name)
        elif action.lower() == "talk":
            talk_to_object(obj_name)
        elif action.lower() == "take":
            take_object(obj_name)
        else:
            # Generic handler
            renpy.notify(f"{action}: {obj_name}")
        
        renpy.restart_interaction()
    
    def examine_object(obj_name):
        """Default examine handler."""
        obj_data = store.room_objects.get(obj_name, {})
        desc = obj_data.get("description", f"It's {obj_name}.")
        
        # Show description in a nice way
        renpy.show_screen("object_description", obj_name, desc)
    
    def use_object(obj_name):
        """Default use handler."""
        renpy.notify(f"You try to use the {obj_name}.")
    
    def talk_to_object(obj_name):
        """Default talk handler."""
        obj_data = store.room_objects.get(obj_name, {})
        if "character" in obj_data.get("tags", []):
            renpy.notify(f"{obj_name}: 'Hello there!'")
        else:
            renpy.notify(f"You can't talk to {obj_name}.")
    
    def take_object(obj_name):
        """Default take handler."""
        obj_data = store.room_objects.get(obj_name, {})
        if "item" in obj_data.get("tags", []):
            # Hide the object
            hide_object(obj_name)
            renpy.notify(f"You take the {obj_name}.")
        else:
            renpy.notify(f"You can't take the {obj_name}.")
    
    def register_object_actions(obj_name, actions):
        """Register custom actions for an object."""
        store.interaction_actions[obj_name] = actions
    
    def clear_object_actions(obj_name):
        """Clear custom actions for an object."""
        if obj_name in store.interaction_actions:
            del store.interaction_actions[obj_name]

## Object Description Screen
screen object_description(obj_name, description):
    modal True
    zorder 110
    
    # Background
    add Solid("#00000088")
    
    # Click to close
    button:
        xfill True
        yfill True
        action Hide("object_description")
    
    # Description box
    frame:
        xalign 0.5
        yalign 0.5
        xmaximum 600
        ymaximum 400
        
        background Frame("#000000dd")
        padding 30
        
        # Fade in
        at transform:
            alpha 0.0
            zoom 0.95
            linear 0.2 alpha 1.0 zoom 1.0
        
        vbox:
            spacing 20
            
            # Title
            text obj_name:
                size 24
                color "#ffaa00"
                xalign 0.5
            
            # Separator
            add Solid("#555555"):
                xsize 400
                ysize 2
                xalign 0.5
            
            # Description
            viewport:
                scrollbars "vertical"
                mousewheel True
                draggable True
                
                text description:
                    size 16
                    color "#ffffff"
                    line_spacing 5
            
            # Close button
            textbutton "Close":
                xalign 0.5
                text_size 18
                text_color "#888888"
                text_hover_color "#ffffff"
                action Hide("object_description")
    
    # ESC to close
    key "K_ESCAPE" action Hide("object_description")
    key "K_RETURN" action Hide("object_description")
    key "K_SPACE" action Hide("object_description")
