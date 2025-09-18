# Debug and Editor Styling Configuration
# Centralised font and style definitions for all debug/editor UI
#
# ALL debug, editor, and development UI must use Ubuntu Mono font
# for consistency and professional appearance

## Font Configuration
define DEBUG_FONT = "fonts/UbuntuMono-R.ttf"
define DEBUG_FONT_SIZE_TINY = 10
define DEBUG_FONT_SIZE_SMALL = 11
define DEBUG_FONT_SIZE_NORMAL = 13
define DEBUG_FONT_SIZE_LARGE = 16
define DEBUG_FONT_SIZE_TITLE = 18

## Colour Palette for Debug UI
define DEBUG_COLOR_SUCCESS = "#00ff00"
define DEBUG_COLOR_WARNING = "#ffaa00"
define DEBUG_COLOR_ERROR = "#ff4444"
define DEBUG_COLOR_INFO = "#00aaff"
define DEBUG_COLOR_TEXT = "#ffffff"
define DEBUG_COLOR_MUTED = "#888888"
define DEBUG_COLOR_LABEL = "#ffaa00"
define DEBUG_COLOR_VALUE = "#00ffaa"

## Debug Text Styles
style debug_text:
    font DEBUG_FONT
    size DEBUG_FONT_SIZE_NORMAL
    color DEBUG_COLOR_TEXT
    outlines []  # No outlines for clean look

style debug_label:
    is debug_text
    color DEBUG_COLOR_LABEL
    size DEBUG_FONT_SIZE_NORMAL

style debug_value:
    is debug_text
    color DEBUG_COLOR_VALUE
    size DEBUG_FONT_SIZE_SMALL

style debug_title:
    is debug_text
    size DEBUG_FONT_SIZE_TITLE
    color DEBUG_COLOR_SUCCESS

style debug_error:
    is debug_text
    color DEBUG_COLOR_ERROR
    size DEBUG_FONT_SIZE_NORMAL

style debug_warning:
    is debug_text
    color DEBUG_COLOR_WARNING
    size DEBUG_FONT_SIZE_NORMAL

style debug_info:
    is debug_text
    color DEBUG_COLOR_INFO
    size DEBUG_FONT_SIZE_SMALL

style debug_muted:
    is debug_text
    color DEBUG_COLOR_MUTED
    size DEBUG_FONT_SIZE_SMALL

## Debug Frame Styles
style debug_frame:
    background "#000000cc"
    padding (10, 8)
    xpadding 10
    ypadding 8

style debug_frame_solid:
    is debug_frame
    background "#1a1a1add"

style debug_button:
    padding (8, 4)
    background "#333333"
    hover_background "#444444"
    insensitive_background "#222222"

style debug_button_text:
    is debug_text
    size DEBUG_FONT_SIZE_NORMAL
    idle_color DEBUG_COLOR_TEXT
    hover_color DEBUG_COLOR_SUCCESS
    insensitive_color DEBUG_COLOR_MUTED

## Input Styles
style debug_input:
    font DEBUG_FONT
    size DEBUG_FONT_SIZE_NORMAL
    color DEBUG_COLOR_TEXT
    hover_color DEBUG_COLOR_VALUE

## Scrollbar Styles for Debug Windows
style debug_vscrollbar:
    xsize 10
    base_bar Solid("#333333")
    thumb Solid("#666666")
    hover_thumb Solid("#888888")

style debug_viewport:
    xfill True
    yfill True

## Helper Functions for Debug Display
init python:
    def format_debug_value(value, precision=2):
        """Format a value for debug display.
        
        Args:
            value: Value to format
            precision: Decimal places for floats
            
        Returns:
            Formatted string
        """
        if isinstance(value, bool):
            return "ON" if value else "OFF"
        elif isinstance(value, float):
            return f"{value:.{precision}f}"
        elif value is None:
            return "None"
        else:
            return str(value)
    
    def get_debug_color_for_value(value, threshold_low=0.3, threshold_high=0.7):
        """Get appropriate colour for a normalised value.
        
        Args:
            value: Value between 0 and 1
            threshold_low: Below this is red
            threshold_high: Above this is green
            
        Returns:
            Colour hex string
        """
        if value < threshold_low:
            return DEBUG_COLOR_ERROR
        elif value > threshold_high:
            return DEBUG_COLOR_SUCCESS
        else:
            return DEBUG_COLOR_WARNING

## Debug Overlay Base Screen
screen debug_overlay_base():
    # Base container for all debug overlays
    # Position in top-left by default
    frame:
        style "debug_frame"
        xpos 10
        ypos 10
        
        has vbox
        spacing 4
        
        text "DEBUG MODE" style "debug_title"
        text "F8: Editor | F12: Console" style "debug_muted"

## Room Debug Info Screen
screen room_debug_info():
    if config.developer:
        frame:
            style "debug_frame"
            xpos 10
            ypos 100
            xsize 300
            
            has vbox
            spacing 2
            
            text "Room Info" style "debug_label"
            
            hbox:
                text "ID: " style "debug_text"
                text current_room_id style "debug_value"
            
            hbox:
                text "Objects: " style "debug_text"
                text str(len(room_objects)) style "debug_value"
            
            if current_hover_object:
                null height 5
                text "Hover: " style "debug_text"
                text current_hover_object style "debug_value"
                
                $ obj = room_objects.get(current_hover_object, {})
                hbox:
                    text "Pos: " style "debug_text"
                    text f"({obj.get('x', 0)}, {obj.get('y', 0)})" style "debug_value"
                
                hbox:
                    text "Size: " style "debug_text"
                    text f"{obj.get('width', 0)}x{obj.get('height', 0)}" style "debug_value"

## Performance Debug Screen
screen performance_debug():
    if config.developer:
        frame:
            style "debug_frame"
            xalign 1.0
            ypos 10
            xsize 200
            
            has vbox
            spacing 2
            
            text "Performance" style "debug_label"
            
            $ fps = renpy.get_fps()
            hbox:
                text "FPS: " style "debug_text"
                text f"{fps:.1f}" style ("debug_value" if fps > 30 else "debug_warning")
            
            $ frame_time = 1000.0 / max(fps, 1)
            hbox:
                text "Frame: " style "debug_text"
                text f"{frame_time:.1f}ms" style "debug_value"

## Shader Debug Screen
screen shader_debug_info():
    if config.developer and shader_debug_enabled:
        frame:
            style "debug_frame"
            xpos 10
            ypos 250
            xsize 300
            
            has vbox
            spacing 2
            
            text "Shader States" style "debug_label"
            
            # CRT Status
            hbox:
                text "CRT: " style "debug_text"
                text format_debug_value(getattr(store, 'crt_enabled', False)) style "debug_value"
                if getattr(store, 'crt_enabled', False) and getattr(store, 'crt_animated', False):
                    text " [ANIM]" style "debug_info" at blink
            
            # Film Grain
            hbox:
                text "Grain: " style "debug_text"
                $ grain_preset = get_current_shader_preset("film_grain") if hasattr(store, 'shader_states') else "off"
                text grain_preset style "debug_value"
            
            # Lighting
            hbox:
                text "Light: " style "debug_text"
                $ light_preset = get_current_shader_preset("lighting") if hasattr(store, 'shader_states') else "off"
                text light_preset style "debug_value"
            
            # Color Grading
            hbox:
                text "Color: " style "debug_text"
                $ color_preset = get_current_shader_preset("color_grading") if hasattr(store, 'shader_states') else "off"
                text color_preset style "debug_value"

## Simple Blink Transform for Indicators
transform blink:
    alpha 1.0
    linear 0.5 alpha 0.3
    linear 0.5 alpha 1.0
    repeat

## Breathing Debug Overlay (Updated with Ubuntu Mono)
screen breathing_debug_overlay():
    if getattr(store, 'chest_breathe_debug', 0) > 0.5:
        $ target = get_tuner_target_object() if 'get_tuner_target_object' in dir() else None
        if target and target in room_objects:
            $ obj = room_objects[target]
            
            frame:
                style "debug_frame_solid"
                xpos int(obj['x']) - 10
                ypos int(obj['y']) - 30
                
                text f"Breathing: {target}" style "debug_label"

## Input Debug Screen
screen input_debug():
    if config.developer:
        frame:
            style "debug_frame"
            xalign 0.5
            yalign 1.0
            yoffset -10
            
            has hbox
            spacing 10
            
            text "Input:" style "debug_label"
            
            if interaction_menu_active:
                text "MENU ACTIVE" style "debug_warning"
            elif editor_visible:
                text "EDITOR MODE" style "debug_info"
            else:
                text "GAMEPLAY" style "debug_value"
            
            if gamepad_navigation_enabled:
                text "| Gamepad: ON" style "debug_value"

## Master Debug Toggle Screen
screen debug_master():
    # Includes all debug overlays when developer mode is on
    if config.developer:
        use room_debug_info
        use performance_debug
        use shader_debug_info
        use input_debug
        
        # Toggle key
        key "K_F11" action ToggleVariable("show_all_debug", True, False)

# Set up debug variables
default show_all_debug = False
# shader_debug_enabled is defined in shaders_system.rpy
