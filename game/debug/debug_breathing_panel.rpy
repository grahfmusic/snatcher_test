# Breathing Debug Panel
# Professional debug panel for breathing animations using Ubuntu Mono font
# Integrates with the unified debug system

## Breathing Debug Panel Screen
screen breathing_debug_panel():
    if config.developer and getattr(store, 'breathing_debug_visible', False):
        drag:
            drag_name "breathing_debug"
            draggable True
            xpos getattr(store, 'breathing_debug_x', 50)
            ypos getattr(store, 'breathing_debug_y', 200)
            
            frame:
                style "debug_frame"
                xsize 400
                
                vbox:
                    spacing 5
                    
                    # Header
                    hbox:
                        text "BREATHING DEBUG" style "debug_header"
                        textbutton "×" action SetVariable("breathing_debug_visible", False):
                            text_style "debug_close_button"
                            xalign 1.0
                    
                    # Current target
                    if tuner_target_object:
                        text "Target: [tuner_target_object]" style "debug_label"
                    else:
                        text "Target: None" style "debug_warning"
                    
                    # Breathing state
                    $ breath_enabled = getattr(store, 'breath_enabled', False)
                    hbox:
                        text "State: " style "debug_label"
                        if breath_enabled:
                            text "ACTIVE" style "debug_value_active"
                        else:
                            text "INACTIVE" style "debug_value_inactive"
                    
                    # Component states
                    text "Components:" style "debug_label"
                    
                    grid 2 4:
                        spacing 10
                        
                        # Chest
                        text "Chest:" style "debug_small_label"
                        if getattr(store, 'breath_use_chest', True):
                            text "ON" style "debug_small_value_active"
                        else:
                            text "OFF" style "debug_small_value_inactive"
                        
                        # Left Shoulder
                        text "L-Shoulder:" style "debug_small_label"
                        if getattr(store, 'breath_use_shoulder_left', True):
                            text "ON" style "debug_small_value_active"
                        else:
                            text "OFF" style "debug_small_value_inactive"
                        
                        # Right Shoulder
                        text "R-Shoulder:" style "debug_small_label"
                        if getattr(store, 'breath_use_shoulder_right', True):
                            text "ON" style "debug_small_value_active"
                        else:
                            text "OFF" style "debug_small_value_inactive"
                        
                        # Head
                        text "Head:" style "debug_small_label"
                        if getattr(store, 'breath_use_head', True):
                            text "ON" style "debug_small_value_active"
                        else:
                            text "OFF" style "debug_small_value_inactive"
                    
                    # Parameters
                    null height 5
                    text "Parameters:" style "debug_label"
                    
                    # Chest parameters
                    vbox:
                        spacing 2
                        text "Chest Amplitude: {:.3f}".format(getattr(store, 'chest_breathe_amp', 0.04)) style "debug_small_value"
                        text "Chest Center: ({:.2f}, {:.2f})".format(
                            getattr(store, 'chest_breathe_center_u', 0.5),
                            getattr(store, 'chest_breathe_center_v', 0.58)
                        ) style "debug_small_value"
                        text "Chest Half: ({:.2f}, {:.2f})".format(
                            getattr(store, 'chest_breathe_half_u', 0.12),
                            getattr(store, 'chest_breathe_half_v', 0.13)
                        ) style "debug_small_value"
                        text "Period: {:.1f}s".format(getattr(store, 'chest_breathe_period', 5.2)) style "debug_small_value"
                    
                    # Active profile
                    null height 5
                    $ active_profile = getattr(store, 'breathing_active_profile', None)
                    hbox:
                        text "Profile: " style "debug_label"
                        if active_profile:
                            text active_profile style "debug_value"
                        else:
                            text "None" style "debug_value_inactive"
                    
                    # Performance metrics
                    null height 5
                    text "Performance:" style "debug_label"
                    $ obj_count = len([obj for obj in getattr(store, 'room_objects', {}).values() 
                                      if breathing_is_enabled_for(obj.get('name', ''))])
                    text "Active Objects: [obj_count]" style "debug_small_value"
                    
                    # Debug actions
                    null height 5
                    hbox:
                        spacing 5
                        textbutton "Log State" action Function(debug_breathing_state):
                            text_style "debug_button"
                        textbutton "Reset" action Function(reset_breathing_defaults):
                            text_style "debug_button"
                        textbutton "Tuner" action SetVariable("chest_tuner_visible", True):
                            text_style "debug_button"

## Debug Styles for Breathing Panel
style debug_frame:
    background "#000000dd"
    padding (15, 10)
    
style debug_header:
    font "fonts/UbuntuMono-R.ttf"
    size 16
    color "#00ff00"
    bold True
    
style debug_close_button:
    font "fonts/UbuntuMono-R.ttf"
    size 18
    color "#ff4444"
    hover_color "#ff8888"
    
style debug_label:
    font "fonts/UbuntuMono-R.ttf"
    size 13
    color "#ffaa00"
    
style debug_warning:
    font "fonts/UbuntuMono-R.ttf"
    size 13
    color "#ff4444"
    
style debug_value:
    font "fonts/UbuntuMono-R.ttf"
    size 13
    color "#00ffaa"
    
style debug_value_active:
    font "fonts/UbuntuMono-R.ttf"
    size 13
    color "#00ff00"
    
style debug_value_inactive:
    font "fonts/UbuntuMono-R.ttf"
    size 13
    color "#888888"
    
style debug_small_label:
    font "fonts/UbuntuMono-R.ttf"
    size 11
    color "#cccccc"
    
style debug_small_value:
    font "fonts/UbuntuMono-R.ttf"
    size 11
    color "#00ffaa"
    
style debug_small_value_active:
    font "fonts/UbuntuMono-R.ttf"
    size 11
    color "#00ff00"
    
style debug_small_value_inactive:
    font "fonts/UbuntuMono-R.ttf"
    size 11
    color "#666666"
    
style debug_button:
    font "fonts/UbuntuMono-R.ttf"
    size 12
    color "#ffffff"
    hover_color "#00ff00"
    outlines [(1, "#000000", 0, 0)]

## Debug Functions
init python:
    def debug_breathing_state():
        """Log current breathing state to debug system."""
        if not DEBUG_ENABLED:
            return
            
        # Gather state information
        target = getattr(store, 'tuner_target_object', None)
        enabled = getattr(store, 'breath_enabled', False)
        
        components = {
            "chest": getattr(store, 'breath_use_chest', True),
            "l_shoulder": getattr(store, 'breath_use_shoulder_left', True),
            "r_shoulder": getattr(store, 'breath_use_shoulder_right', True),
            "head": getattr(store, 'breath_use_head', True)
        }
        
        params = {
            "amp": getattr(store, 'chest_breathe_amp', 0.04),
            "period": getattr(store, 'chest_breathe_period', 5.2),
            "center_u": getattr(store, 'chest_breathe_center_u', 0.5),
            "center_v": getattr(store, 'chest_breathe_center_v', 0.58)
        }
        
        # Log to debug system
        debug_system("=== BREATHING STATE DUMP ===")
        debug_system(f"Target: {target or 'None'}")
        debug_system(f"Enabled: {enabled}")
        debug_system(f"Components: {components}")
        debug_system(f"Parameters: {params}")
        
        profile = getattr(store, 'breathing_active_profile', None)
        if profile:
            debug_system(f"Active Profile: {profile}")
        
        # Count active objects
        active_count = 0
        if hasattr(store, 'room_objects'):
            for obj_name in store.room_objects:
                if breathing_is_enabled_for(obj_name):
                    active_count += 1
        debug_system(f"Active Objects: {active_count}")
        debug_system("=== END BREATHING STATE ===")
    
    def reset_breathing_defaults():
        """Reset breathing parameters to defaults."""
        store.chest_breathe_amp = 0.04
        store.chest_breathe_center_u = 0.5
        store.chest_breathe_center_v = 0.58
        store.chest_breathe_half_u = 0.12
        store.chest_breathe_half_v = 0.13
        store.chest_breathe_period = 5.2
        
        store.shoulder_left_center_u = 0.34
        store.shoulder_left_center_v = 0.42
        store.shoulder_left_half_u = 0.10
        store.shoulder_left_half_v = 0.06
        store.shoulder_left_out_amp = 0.02
        store.shoulder_left_up_amp = 0.004
        
        store.shoulder_right_center_u = 0.66
        store.shoulder_right_center_v = 0.42
        store.shoulder_right_half_u = 0.10
        store.shoulder_right_half_v = 0.06
        store.shoulder_right_out_amp = 0.02
        store.shoulder_right_up_amp = 0.004
        
        store.head_center_u = 0.50
        store.head_center_v = 0.18
        store.head_half_u = 0.10
        store.head_half_v = 0.08
        store.head_up_amp = 0.006
        
        debug_system("Breathing parameters reset to defaults")
        renpy.restart_interaction()
    
    def toggle_breathing_debug():
        """Toggle breathing debug panel visibility."""
        store.breathing_debug_visible = not getattr(store, 'breathing_debug_visible', False)
        if store.breathing_debug_visible:
            debug_system("Breathing debug panel ENABLED")
        else:
            debug_system("Breathing debug panel DISABLED")

## Default Variables
default breathing_debug_visible = False
default breathing_debug_x = 50
default breathing_debug_y = 200

## Integration with main debug hotkeys
init python:
    # Add to console commands
    config.console_commands["breathing_debug"] = toggle_breathing_debug
