# Letterbox Shader V2 - Speed-Based System
# Creates cinematic letterbox bars with 5 animation speed options
# Integrates with the neo-noir shader layer system

# Letterbox state variables
default letterbox_enabled = False
default letterbox_zorder = 1000  # Render above all UI/screens
default letterbox_speed_mode = 2  # 0=very slow, 1=slow, 2=normal, 3=fast, 4=very fast
default letterbox_height = 80.0
default letterbox_color = (0.0, 0.0, 0.0)  # Black bars
default letterbox_aspect_ratio = None  # Target aspect ratio (None = use letterbox_height)
default letterbox_aspect_mode = -1  # -1=custom height, 0-11=aspect preset indices
default _letterbox_was_enabled = False  # Track previous state for animations

init python:
    # Letterbox speed configuration (duration in seconds)
    letterbox_speeds = {
        0: {"name": "Very Slow", "duration": 2.5},
        1: {"name": "Slow", "duration": 1.5}, 
        2: {"name": "Normal", "duration": 0.8},
        3: {"name": "Fast", "duration": 0.4},
        4: {"name": "Very Fast", "duration": 0.2}
    }
    
    # Common aspect ratio presets
    letterbox_aspect_presets = {
        "21:9": 21.0/9.0,     # Ultra-wide
        "16:9": 16.0/9.0,     # Standard widescreen
        "16:10": 16.0/10.0,   # Slightly taller widescreen
        "4:3": 4.0/3.0,       # Classic 4:3
        "3:2": 3.0/2.0,       # Photography standard
        "1.85:1": 1.85,       # Cinema standard
        "2.35:1": 2.35,       # Anamorphic cinema
        "2.39:1": 2.39,       # Modern cinema
        "5:4": 5.0/4.0,       # Classic computer
        "academy": 1.375,      # Academy ratio (1.375:1)
        "cinemascope": 2.35,   # Classic CinemaScope
        "panavision": 2.39,    # Modern Panavision
    }
    
    # Ordered list for cycling through aspect ratios with 'L' key
    letterbox_cycle_aspects = [
        ("Custom", None),           # -1: Custom height mode
        ("21:9", 21.0/9.0),        # 0: Ultra-wide
        ("16:9", 16.0/9.0),        # 1: Standard widescreen  
        ("2.39:1", 2.39),          # 2: Modern cinema
        ("2.35:1", 2.35),          # 3: Anamorphic cinema
        ("1.85:1", 1.85),          # 4: Cinema standard
        ("16:10", 16.0/10.0),      # 5: Slightly taller widescreen
        ("4:3", 4.0/3.0),          # 6: Classic 4:3
        ("3:2", 3.0/2.0),          # 7: Photography standard
        ("5:4", 5.0/4.0),          # 8: Classic computer
        ("Academy", 1.375),        # 9: Academy ratio
        ("CinemaScope", 2.35),     # 10: Classic CinemaScope
        ("Panavision", 2.39),      # 11: Modern Panavision
    ]
    
    def get_letterbox_duration():
        """Get current letterbox animation duration based on speed mode"""
        return letterbox_speeds.get(letterbox_speed_mode, letterbox_speeds[2])["duration"]
    
    def _parse_aspect_ratio(value):
        """Parse aspect ratio value from string like '21:9' or float, including presets."""
        if value is None:
            return None
        try:
            if isinstance(value, (int, float)):
                return float(value)
            s = str(value).strip().lower().replace(' ', '')
            # Check if it's a preset name first
            if s in letterbox_aspect_presets:
                return letterbox_aspect_presets[s]
            if ':' in s:
                a, b = s.split(':', 1)
                return float(a) / float(b)
            return float(s)
        except Exception:
            return None
    
    def set_letterbox_aspect_ratio(ratio):
        """Set target aspect ratio for letterbox (e.g., '21:9', '16:9', 1.85). Use None to disable aspect targeting."""
        global letterbox_aspect_ratio
        letterbox_aspect_ratio = _parse_aspect_ratio(ratio)
        
        # Show notification
        if letterbox_aspect_ratio:
            if str(ratio).lower() in letterbox_aspect_presets:
                renpy.notify(f"Letterbox: {ratio} aspect ratio")
            else:
                renpy.notify(f"Letterbox: {letterbox_aspect_ratio:.2f}:1 aspect ratio")
        else:
            renpy.notify("Letterbox: custom height mode")
        
        renpy.restart_interaction()
    
    def get_letterbox_aspect_presets():
        """Get list of available aspect ratio preset names."""
        return list(letterbox_aspect_presets.keys())
    
    def get_current_letterbox_height():
        """Get the current calculated letterbox bar height in pixels."""
        return _calc_height_for_aspect()
    
    def _calc_height_for_aspect():
        """Compute horizontal letterbox bar height (top/bottom bars) in pixels."""
        try:
            ar = letterbox_aspect_ratio
            if not ar:
                return float(letterbox_height)
            
            # Screen size
            sw = float(config.screen_width)
            sh = float(config.screen_height)
            screen_ar = sw / sh
            
            
            # Letterboxing (horizontal bars): happens when screen is wider than target
            # AND the content is too tall to fit when using full screen width
            if screen_ar > ar:
                content_height = sw / float(ar)  # Height needed for target aspect ratio with full width
                if content_height > sh:
                    # Content is too tall for letterboxing, let width calculation handle pillarboxing
                    return 0.0
                else:
                    # We can letterbox! Add horizontal bars
                    bar_height = (sh - content_height) / 2.0
                    return max(0.0, bar_height)
            
            # Case 2: Screen is narrower than target, but content is too wide for pillarboxing
            # Fall back to letterboxing (use full screen width)
            elif screen_ar < ar:
                # Check if pillarboxing would work
                content_width_for_pillarbox = sh * float(ar)
                if content_width_for_pillarbox > sw:
                    # Content too wide for pillarboxing, fall back to letterboxing
                    content_height = sw / float(ar)  # Height needed for target AR with full width
                    if content_height < sh:
                        bar_height = (sh - content_height) / 2.0
                        return max(0.0, bar_height)
            
            return 0.0
        except Exception:
            return float(letterbox_height)
    
    def _calc_width_for_aspect():
        """Compute vertical pillarbox bar width (left/right bars) in pixels."""
        try:
            ar = letterbox_aspect_ratio
            if not ar:
                return 0.0  # No pillarboxing for custom height mode
            
            # Screen size
            sw = float(config.screen_width)
            sh = float(config.screen_height)
            screen_ar = sw / sh
            
            
            # Pillarboxing (vertical bars): happens when screen is WIDER than target
            # We use full screen HEIGHT and calculate the content width for target aspect ratio  
            if screen_ar > ar:
                content_width = sh * float(ar)  # Width needed for target aspect ratio with full height
                if content_width <= sw:
                    # We can fit it! Add vertical bars
                    bar_width = (sw - content_width) / 2.0
                    return max(0.0, bar_width)
                else:
                    # Content width would be too wide - this shouldn't happen for screen_ar > ar case
                    return 0.0
            
            return 0.0
        except Exception:
            return 0.0
    
    def get_current_letterbox_width():
        """Get the current calculated letterbox bar width in pixels."""
        return _calc_width_for_aspect()
    
    def get_letterbox_speed_name():
        """Get current letterbox speed name for notifications"""
        return letterbox_speeds.get(letterbox_speed_mode, letterbox_speeds[2])["name"]
    
    def cycle_letterbox_speed():
        """Cycle through letterbox speed options"""
        global letterbox_speed_mode
        letterbox_speed_mode = (letterbox_speed_mode + 1) % len(letterbox_speeds)
        
        # Show notification
        speed_name = get_letterbox_speed_name()
        renpy.notify(f"Letterbox Speed: {speed_name}")
    
    def toggle_letterbox():
        """Toggle letterbox on/off with current speed setting"""
        global letterbox_enabled
        letterbox_enabled = not letterbox_enabled
        
        # Show notification
        if letterbox_enabled:
            speed_name = get_letterbox_speed_name()
            renpy.notify(f"Letterbox ON ({speed_name})")
        else:
            renpy.notify("Letterbox OFF")
        
        # Restart interaction to apply changes
        renpy.restart_interaction()
    
    def letterbox_combined_action():
        """Enhanced 'L' key action: cycles through aspect ratios and speeds, then turns off"""
        global letterbox_enabled, letterbox_speed_mode, letterbox_aspect_mode, letterbox_aspect_ratio, _letterbox_was_enabled
        
        # Update the previous state tracker
        _letterbox_was_enabled = letterbox_enabled
        
        if not letterbox_enabled:
            # Start cycling: turn on with first aspect ratio and first speed
            letterbox_enabled = True
            letterbox_aspect_mode = 0   # Start with first aspect ratio (Custom)
            letterbox_speed_mode = 0    # Start with first speed (Very Slow)
            aspect_name, aspect_value = letterbox_cycle_aspects[0]  # "Custom", None
            letterbox_aspect_ratio = aspect_value
            speed_name = get_letterbox_speed_name()
            renpy.notify(f"Letterbox ON: {aspect_name} ({speed_name})")
            renpy.restart_interaction()
        else:
            # Cycle through speeds first, then aspect ratios
            letterbox_speed_mode = (letterbox_speed_mode + 1) % len(letterbox_speeds)
            
            # If we've cycled through all speeds, move to next aspect ratio
            if letterbox_speed_mode == 0:
                letterbox_aspect_mode = (letterbox_aspect_mode + 1)
                
                # If we've cycled through all aspect ratios, turn off
                if letterbox_aspect_mode >= len(letterbox_cycle_aspects):
                    letterbox_enabled = False
                    renpy.notify("Letterbox OFF")
                    renpy.restart_interaction()
                    return
            
            # Set current aspect ratio
            aspect_name, aspect_value = letterbox_cycle_aspects[letterbox_aspect_mode]
            letterbox_aspect_ratio = aspect_value
            
            # Show current state
            speed_name = get_letterbox_speed_name()
            renpy.notify(f"Letterbox: {aspect_name} ({speed_name})")
            renpy.restart_interaction()
    
    def set_letterbox_speed(speed_index):
        """Set letterbox speed to specific index (0-4)"""
        global letterbox_speed_mode
        if 0 <= speed_index < len(letterbox_speeds):
            letterbox_speed_mode = speed_index
            speed_name = get_letterbox_speed_name()
            
            if letterbox_enabled:
                renpy.notify(f"Letterbox Speed: {speed_name}")
                renpy.restart_interaction()
    
    def letterbox_force_off():
        """Force letterbox off regardless of current state"""
        global letterbox_enabled
        if letterbox_enabled:
            letterbox_enabled = False
            renpy.notify("Letterbox OFF")
            
            # Hide overlay after animation
            duration = get_letterbox_duration()
            renpy.call_in_new_context("letterbox_cleanup", duration)
            renpy.restart_interaction()

# Enhanced letterbox shader with smooth ease-in/out animations
transform letterbox_ease_in(duration=0.8, height=80.0, width=0.0, color=(0.0, 0.0, 0.0)):
    mesh True
    shader "letterbox_shader"
    u_model_size (config.screen_width, config.screen_height)
    u_letterbox_color color
    u_letterbox_height 0.0
    u_letterbox_width 0.0
    u_letterbox_alpha 0.0
    
    # Parallel animations for smooth effect
    parallel:
        # Ease in the height with smooth easing (height calculation done by calling functions)
        easein_quart duration u_letterbox_height height
    parallel:
        # Ease in the width for pillarboxing
        easein_quart duration u_letterbox_width width
    parallel:
        # Fade in the alpha slightly faster for better visual flow
        ease (duration * 0.7) u_letterbox_alpha 1.0

transform letterbox_ease_out(duration=0.8, height=80.0, width=0.0, color=(0.0, 0.0, 0.0)):
    mesh True
    shader "letterbox_shader"
    u_model_size (config.screen_width, config.screen_height)
    u_letterbox_color color
    u_letterbox_alpha 1.0
    u_letterbox_height height
    u_letterbox_width width
    
    # Parallel animations for smooth effect
    parallel:
        # Ease out the height with smooth easing
        easeout_quart duration u_letterbox_height 0.0
    parallel:
        # Ease out the width for pillarboxing
        easeout_quart duration u_letterbox_width 0.0
    parallel:
        # Fade out the alpha slightly slower for better visual flow
        ease (duration * 1.3) u_letterbox_alpha 0.0

transform letterbox_static(height=80.0, width=0.0, color=(0.0, 0.0, 0.0)):
    mesh True
    shader "letterbox_shader"
    u_model_size (config.screen_width, config.screen_height)
    u_letterbox_color color
    u_letterbox_alpha 1.0
    u_letterbox_height height
    u_letterbox_width width

# Transform that applies letterbox effect with current settings
# Note: This transform is not used directly - the shader layer system 
# calls letterbox_ease_in/out transforms directly based on letterbox_enabled state

# Speed preset transforms for quick access
transform letterbox_very_slow_in():
    letterbox_ease_in(2.5, _calc_height_for_aspect(), _calc_width_for_aspect(), letterbox_color)

transform letterbox_slow_in():
    letterbox_ease_in(1.5, _calc_height_for_aspect(), _calc_width_for_aspect(), letterbox_color)

transform letterbox_normal_in():
    letterbox_ease_in(0.8, _calc_height_for_aspect(), _calc_width_for_aspect(), letterbox_color)

transform letterbox_fast_in():
    letterbox_ease_in(0.4, _calc_height_for_aspect(), _calc_width_for_aspect(), letterbox_color)

transform letterbox_very_fast_in():
    letterbox_ease_in(0.2, _calc_height_for_aspect(), _calc_width_for_aspect(), letterbox_color)

transform letterbox_very_slow_out():
    letterbox_ease_out(2.5, _calc_height_for_aspect(), _calc_width_for_aspect(), letterbox_color)

transform letterbox_slow_out():
    letterbox_ease_out(1.5, _calc_height_for_aspect(), _calc_width_for_aspect(), letterbox_color)

transform letterbox_normal_out():
    letterbox_ease_out(0.8, _calc_height_for_aspect(), _calc_width_for_aspect(), letterbox_color)

transform letterbox_fast_out():
    letterbox_ease_out(0.4, _calc_height_for_aspect(), _calc_width_for_aspect(), letterbox_color)

transform letterbox_very_fast_out():
    letterbox_ease_out(0.2, _calc_height_for_aspect(), _calc_width_for_aspect(), letterbox_color)

# Letterbox overlay screen (renders above all content)
screen letterbox_overlay():
    # Very high z-order to appear above all content and UI
    zorder letterbox_zorder
    
    # Calculate height and width based on aspect ratio or use letterbox_height
    $ calculated_height = _calc_height_for_aspect()
    $ calculated_width = _calc_width_for_aspect()
    
    # Show overlay for both ease-in and ease-out animations
    if letterbox_enabled:
        # Ease-in animation when turning on
        add Solid("#0000") at letterbox_ease_in(
            get_letterbox_duration(), 
            calculated_height, 
            calculated_width,
            letterbox_color
        ):
            xsize config.screen_width
            ysize config.screen_height
    else:
        # Ease-out animation when turning off (only if we were previously on)
        $ was_enabled = getattr(store, '_letterbox_was_enabled', False)
        if was_enabled:
            add Solid("#0000") at letterbox_ease_out(
                get_letterbox_duration(), 
                calculated_height, 
                calculated_width,
                letterbox_color
            ):
                xsize config.screen_width
                ysize config.screen_height
            
            # Clear the was_enabled flag after the animation duration
            timer get_letterbox_duration() action SetVariable('_letterbox_was_enabled', False)

# Register letterbox overlay as a global overlay screen
init python:
    # Ensure the letterbox overlay is an overlay screen so it renders globally
    # at a high zorder (95) above all content but below debug overlays
    if "letterbox_overlay" not in config.overlay_screens:
        config.overlay_screens.append("letterbox_overlay")

# Cleanup label for removing letterbox screen after fade-out
label letterbox_cleanup(duration):
    $ renpy.pause(duration, hard=True)
    $ renpy.hide_screen("letterbox_overlay")
    return
