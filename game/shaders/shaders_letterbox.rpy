# Letterbox Shader
# Creates cinematic letterbox bars with smooth animations
# Renders above all content but below UI elements

# Letterbox shader definition
init python:
    # Register the letterbox shader with proper Ren'Py syntax (variables string + 300 stages)
    renpy.register_shader(
        "letterbox_shader",
        variables="""
            uniform float u_letterbox_height;
            uniform float u_letterbox_width;
            uniform float u_letterbox_alpha;
            uniform vec3 u_letterbox_color;
            uniform vec2 u_model_size;
            uniform sampler2D tex0;
            attribute vec2 a_tex_coord;
            attribute vec4 a_position;
            varying vec2 v_tex_coord;
        """,
        vertex_300="""
            v_tex_coord = a_position.xy / u_model_size;
        """,
        fragment_300="""
            // Calculate horizontal letterbox thresholds using normalised coordinates (0..1)
            float screen_height = max(u_model_size.y, 1.0);
            float bar_height_px = max(u_letterbox_height, 0.0);
            float height_frac = clamp(bar_height_px / screen_height, 0.0, 0.5);
            float top_threshold = height_frac;
            float bottom_threshold = 1.0 - height_frac;
            
            // Calculate vertical letterbox thresholds using normalised coordinates (0..1)
            float screen_width = max(u_model_size.x, 1.0);
            float bar_width_px = max(u_letterbox_width, 0.0);
            float width_frac = clamp(bar_width_px / screen_width, 0.0, 0.5);
            float left_threshold = width_frac;
            float right_threshold = 1.0 - width_frac;

            // Check if pixel is in horizontal bars (top or bottom)
            bool in_horizontal_bars = (v_tex_coord.y < top_threshold || v_tex_coord.y > bottom_threshold);
            
            // Check if pixel is in vertical bars (left or right)
            bool in_vertical_bars = (v_tex_coord.x < left_threshold || v_tex_coord.x > right_threshold);

            if (in_horizontal_bars || in_vertical_bars) {
                gl_FragColor = vec4(u_letterbox_color, u_letterbox_alpha);
            } else {
                gl_FragColor = vec4(0.0, 0.0, 0.0, 0.0);
            }
        """
    )

# OLD LETTERBOX TRANSFORMS REMOVED - NOW USING letterbox_shader_system.rpy

# OLD LETTERBOX SYSTEM REMOVED - NOW USING letterbox_shader_system.rpy

# Integration with existing letterbox functions (backward compatibility)
init python:
    # Redirect old letterbox functions to new V2 system
    def show_letterbox(duration=None, wait_for_animation=True):
        """Backward compatibility wrapper - uses new letterbox V2 system"""
        # Set speed based on duration if provided
        if duration is not None:
            if duration >= 2.0:
                set_letterbox_speed(0)  # Very Slow
            elif duration >= 1.2:
                set_letterbox_speed(1)  # Slow  
            elif duration >= 0.6:
                set_letterbox_speed(2)  # Normal
            elif duration >= 0.3:
                set_letterbox_speed(3)  # Fast
            else:
                set_letterbox_speed(4)  # Very Fast
        
        # Turn on letterbox
        if not store.letterbox_enabled:
            store.letterbox_enabled = True
            renpy.restart_interaction()
        
        # Wait if requested
        if wait_for_animation:
            actual_duration = get_letterbox_duration() if hasattr(store, 'get_letterbox_duration') else 0.8
            renpy.pause(actual_duration, hard=True)
    
    def hide_letterbox(duration=None, wait_for_animation=True):
        """Backward compatibility wrapper - uses new letterbox V2 system"""
        if store.letterbox_enabled:
            store.letterbox_enabled = False
            renpy.restart_interaction()
            
            if wait_for_animation:
                actual_duration = get_letterbox_duration() if hasattr(store, 'get_letterbox_duration') else 0.8
                renpy.pause(actual_duration, hard=True)
    
    def toggle_letterbox():
        """Backward compatibility wrapper - uses new letterbox V2 system"""
        if hasattr(store, 'toggle_letterbox') and callable(store.toggle_letterbox):
            # Use new V2 toggle function if available
            return store.toggle_letterbox()
        else:
            # Fallback toggle
            store.letterbox_enabled = not store.letterbox_enabled
            renpy.restart_interaction()
