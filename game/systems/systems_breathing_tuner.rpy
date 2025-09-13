# Breathing Tuner UI
# Professional breathing animation tuner using Ubuntu Mono font
#
# Access: F7 in editor mode
# Features: Per-object breathing configuration with profiles

## Import debug styles
init python:
    # Ensure debug styles are available
    if "DEBUG_FONT" not in dir():
        DEBUG_FONT = "fonts/UbuntuMono-R.ttf"
        DEBUG_FONT_SIZE_NORMAL = 13
        DEBUG_FONT_SIZE_SMALL = 11

## Tuner Variables
default chest_tuner_visible = False
default tuner_target_object = None
default chest_tuner_x = 100
default chest_tuner_y = 100
default chest_tuner_w = 540
default chest_tuner_h = 460
default breathing_profile_name = ""

## Breathing Parameters (with sensible defaults)
default chest_breathe_amp = 0.04
default chest_breathe_center_u = 0.5
default chest_breathe_center_v = 0.58
default chest_breathe_half_u = 0.12
default chest_breathe_half_v = 0.13
default chest_breathe_debug = 0.0

default breath_enabled = False
default breath_use_chest = True
default breath_use_shoulder_left = True
default breath_use_shoulder_right = True
default breath_use_head = True

default shoulder_left_center_u = 0.34
default shoulder_left_center_v = 0.42
default shoulder_left_half_u = 0.10
default shoulder_left_half_v = 0.06
default shoulder_left_out_amp = 0.02
default shoulder_left_up_amp = 0.004

default shoulder_right_center_u = 0.66
default shoulder_right_center_v = 0.42
default shoulder_right_half_u = 0.10
default shoulder_right_half_v = 0.06
default shoulder_right_out_amp = 0.02
default shoulder_right_up_amp = 0.004

default head_center_u = 0.5
default head_center_v = 0.18
default head_half_u = 0.10
default head_half_v = 0.08
default head_up_amp = 0.006

## Additional breathing parameters
default breath_rate = 0.25

## Main Breathing Tuner Screen
screen chest_breathe_tuner_ui():
    if chest_tuner_visible:
        modal True
        zorder 220
        
        # Hotkeys
        key "K_TAB" action Function(breathing_select_next_object)
        key "K_LEFTBRACKET" action Function(breathing_cycle_profile, -1)
        key "K_RIGHTBRACKET" action Function(breathing_cycle_profile, 1)
        key "K_F7" action SetVariable("chest_tuner_visible", False)
        key "K_ESCAPE" action SetVariable("chest_tuner_visible", False)
        
        drag:
            drag_name "chest_tuner"
            draggable True
            dragged _drag_tuner_update
            xpos chest_tuner_x
            ypos chest_tuner_y
            
            frame:
                xsize chest_tuner_w
                ysize chest_tuner_h
                background "#000000dd"
                padding (15, 12)
                
                vbox:
                    spacing 6
                    
                    # Header
                    text "BREATHING TUNER":
                        font DEBUG_FONT
                        size 18
                        color "#00ffaa"
                    
                    # Instructions
                    text "F7: Close | TAB: Next Object | \[/\]: Cycle Profiles":
                        font DEBUG_FONT
                        size DEBUG_FONT_SIZE_SMALL
                        color "#888888"
                    
                    # Target info
                    hbox:
                        text "Target: ":
                            font DEBUG_FONT
                            size DEBUG_FONT_SIZE_NORMAL
                            color "#ffffff"
                        text (tuner_target_object if tuner_target_object else "(none)"):
                            font DEBUG_FONT
                            size DEBUG_FONT_SIZE_NORMAL
                            color "#00ff00"
                    
                    # Enable/Component toggles
                    hbox:
                        spacing 15
                        
                        textbutton ("Enabled: " + ("ON" if breath_enabled else "OFF")):
                            action Function(_breath_toggle_enabled)
                            text_font DEBUG_FONT
                            text_size DEBUG_FONT_SIZE_NORMAL
                            text_color ("#00ff00" if breath_enabled else "#ff4444")
                            text_hover_color "#ffffff"
                        
                        text "Components:":
                            font DEBUG_FONT
                            size DEBUG_FONT_SIZE_SMALL
                            color "#888888"
                            yalign 0.5
                    
                    # Component toggles
                    hbox:
                        spacing 10
                        
                        textbutton ("Chest: " + ("ON" if breath_use_chest else "OFF")):
                            action Function(_breath_toggle_chest)
                            text_font DEBUG_FONT
                            text_size DEBUG_FONT_SIZE_SMALL
                            text_color ("#00ff00" if breath_use_chest else "#888888")
                        
                        textbutton ("L-Shoulder: " + ("ON" if breath_use_shoulder_left else "OFF")):
                            action Function(_breath_toggle_shoulder_left)
                            text_font DEBUG_FONT
                            text_size DEBUG_FONT_SIZE_SMALL
                            text_color ("#00ff00" if breath_use_shoulder_left else "#888888")
                        
                        textbutton ("R-Shoulder: " + ("ON" if breath_use_shoulder_right else "OFF")):
                            action Function(_breath_toggle_shoulder_right)
                            text_font DEBUG_FONT
                            text_size DEBUG_FONT_SIZE_SMALL
                            text_color ("#00ff00" if breath_use_shoulder_right else "#888888")
                        
                        textbutton ("Head: " + ("ON" if breath_use_head else "OFF")):
                            action Function(_breath_toggle_head)
                            text_font DEBUG_FONT
                            text_size DEBUG_FONT_SIZE_SMALL
                            text_color ("#00ff00" if breath_use_head else "#888888")
                    
                    # Parameters viewport
                    viewport:
                        draggable True
                        mousewheel True
                        scrollbars "vertical"
                        ymaximum 250
                        
                        vbox:
                            spacing 10
                            use breathing_parameter_grid
                    
                    # Profile management
                    vbox:
                        spacing 4
                        
                        $ active_profile = getattr(store, 'breathing_active_profile', None)
                        hbox:
                            text "Active Profile: ":
                                font DEBUG_FONT
                                size DEBUG_FONT_SIZE_SMALL
                                color "#ffffff"
                            text (active_profile if active_profile else "(none)"):
                                font DEBUG_FONT
                                size DEBUG_FONT_SIZE_SMALL
                                color "#00ff00"
                        
                        # Profile list
                        $ profile_list = breathing_list_profiles() if 'breathing_list_profiles' in dir() else []
                        if profile_list:
                            text "Available Profiles:":
                                font DEBUG_FONT
                                size DEBUG_FONT_SIZE_SMALL
                                color "#888888"
                            
                            hbox:
                                spacing 8
                                for prof in profile_list[:5]:  # Show first 5
                                    $ is_current = (prof == active_profile)
                                    textbutton prof:
                                        action Function(breathing_apply_profile, prof)
                                        text_font DEBUG_FONT
                                        text_size DEBUG_FONT_SIZE_SMALL
                                        text_color ("#ffff00" if is_current else "#cccccc")
                                        text_hover_color "#ffffff"
                        
                        # Profile name input and actions
                        hbox:
                            spacing 8
                            
                            text "Name:":
                                font DEBUG_FONT
                                size DEBUG_FONT_SIZE_SMALL
                                color "#888888"
                                yalign 0.5
                            
                            input:
                                value VariableInputValue("breathing_profile_name")
                                font DEBUG_FONT
                                size DEBUG_FONT_SIZE_SMALL
                                color "#ffffff"
                                xsize 120
                            
                            textbutton "Save":
                                action Function(breathing_save_profile_from_input)
                                text_font DEBUG_FONT
                                text_size DEBUG_FONT_SIZE_SMALL
                                text_color "#00ff00"
                                text_hover_color "#ffffff"
                            
                            textbutton "Load":
                                action Function(breathing_apply_profile_from_input)
                                text_font DEBUG_FONT
                                text_size DEBUG_FONT_SIZE_SMALL
                                text_color "#00aaff"
                                text_hover_color "#ffffff"
                            
                            textbutton "Delete":
                                action Function(breathing_delete_profile_from_input)
                                text_font DEBUG_FONT
                                text_size DEBUG_FONT_SIZE_SMALL
                                text_color "#ff4444"
                                text_hover_color "#ffffff"

## Breathing Parameter Grid
screen breathing_parameter_grid():
    vbox:
        spacing 12
        
        # Chest parameters
        if breath_use_chest:
            text "CHEST":
                font DEBUG_FONT
                size DEBUG_FONT_SIZE_NORMAL
                color "#00ffaa"
            
            grid 3 5:
                spacing 8
                xfill True
                
                # Parameter rows
                for param, var, delta in [
                    ("X (center)", "chest_breathe_center_u", 0.01),
                    ("Y (center)", "chest_breathe_center_v", 0.01),
                    ("Width", "chest_breathe_half_u", 0.01),
                    ("Height", "chest_breathe_half_v", 0.01),
                    ("Amplitude", "chest_breathe_amp", 0.005)
                ]:
                    text param:
                        font DEBUG_FONT
                        size DEBUG_FONT_SIZE_SMALL
                        color "#ffffff"
                        xsize 100
                    
                    $ value = getattr(store, var, 0.0)
                    text f"{value:.3f}":
                        font DEBUG_FONT
                        size DEBUG_FONT_SIZE_SMALL
                        color "#ffff00"
                        xsize 60
                    
                    hbox:
                        spacing 4
                        textbutton "-":
                            action Function(_adjust_parameter, var, -delta)
                            text_font DEBUG_FONT
                            text_size DEBUG_FONT_SIZE_SMALL
                        textbutton "+":
                            action Function(_adjust_parameter, var, delta)
                            text_font DEBUG_FONT
                            text_size DEBUG_FONT_SIZE_SMALL
        
        # Left shoulder parameters
        if breath_use_shoulder_left:
            text "LEFT SHOULDER":
                font DEBUG_FONT
                size DEBUG_FONT_SIZE_NORMAL
                color "#00ffaa"
            
            grid 3 6:
                spacing 8
                xfill True
                
                for param, var, delta in [
                    ("X (center)", "shoulder_left_center_u", 0.01),
                    ("Y (center)", "shoulder_left_center_v", 0.01),
                    ("Width", "shoulder_left_half_u", 0.01),
                    ("Height", "shoulder_left_half_v", 0.01),
                    ("Out Amp", "shoulder_left_out_amp", 0.002),
                    ("Up Amp", "shoulder_left_up_amp", 0.002)
                ]:
                    text param:
                        font DEBUG_FONT
                        size DEBUG_FONT_SIZE_SMALL
                        color "#ffffff"
                        xsize 100
                    
                    $ value = getattr(store, var, 0.0)
                    text f"{value:.3f}":
                        font DEBUG_FONT
                        size DEBUG_FONT_SIZE_SMALL
                        color "#ffff00"
                        xsize 60
                    
                    hbox:
                        spacing 4
                        textbutton "-":
                            action Function(_adjust_parameter, var, -delta)
                            text_font DEBUG_FONT
                            text_size DEBUG_FONT_SIZE_SMALL
                        textbutton "+":
                            action Function(_adjust_parameter, var, delta)
                            text_font DEBUG_FONT
                            text_size DEBUG_FONT_SIZE_SMALL

## Helper Functions
init python:
    def _drag_tuner_update(drags, joined=None, drop=None):
        """Update tuner position when dragged."""
        drag = drags[0]  # Get the first drag object
        store.chest_tuner_x = int(drag.x)
        store.chest_tuner_y = int(drag.y)
        # Keep on screen
        store.chest_tuner_x = max(0, min(config.screen_width - store.chest_tuner_w, store.chest_tuner_x))
        store.chest_tuner_y = max(0, min(config.screen_height - store.chest_tuner_h, store.chest_tuner_y))
    
    def _adjust_parameter(param_name, delta):
        """Adjust a breathing parameter."""
        try:
            current = float(getattr(store, param_name, 0.0))
            new_value = current + delta
            # Clamp to reasonable ranges
            if "amp" in param_name:
                new_value = max(0.0, min(0.2, new_value))
            elif "half" in param_name:
                new_value = max(0.01, min(0.5, new_value))
            else:  # center parameters
                new_value = max(0.0, min(1.0, new_value))
            setattr(store, param_name, new_value)
            
            # Sync to memory if breathing API available
            if 'breathing_sync_current_to_memory' in dir():
                breathing_sync_current_to_memory()
        except Exception:
            pass
        renpy.restart_interaction()
    
    def _breath_toggle_enabled():
        """Toggle breathing enabled state."""
        store.breath_enabled = not store.breath_enabled
        if 'breathing_sync_current_to_memory' in dir():
            breathing_sync_current_to_memory()
        renpy.restart_interaction()
    
    def _breath_toggle_chest():
        """Toggle chest breathing."""
        store.breath_use_chest = not store.breath_use_chest
        if 'breathing_sync_current_to_memory' in dir():
            breathing_sync_current_to_memory()
        renpy.restart_interaction()
    
    def _breath_toggle_shoulder_left():
        """Toggle left shoulder breathing."""
        store.breath_use_shoulder_left = not store.breath_use_shoulder_left
        if 'breathing_sync_current_to_memory' in dir():
            breathing_sync_current_to_memory()
        renpy.restart_interaction()
    
    def _breath_toggle_shoulder_right():
        """Toggle right shoulder breathing."""
        store.breath_use_shoulder_right = not store.breath_use_shoulder_right
        if 'breathing_sync_current_to_memory' in dir():
            breathing_sync_current_to_memory()
        renpy.restart_interaction()
    
    def _breath_toggle_head():
        """Toggle head breathing."""
        store.breath_use_head = not store.breath_use_head
        if 'breathing_sync_current_to_memory' in dir():
            breathing_sync_current_to_memory()
        renpy.restart_interaction()

# Professional breathing tuner with Ubuntu Mono font!
