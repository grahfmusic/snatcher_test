# Editor State Management
# Centralised state for the shader editor overlay with proper UI gating

# Editor state variables - use shader_editor_open as the authoritative flag
default shader_editor_open = False
default shader_editor_tab = "crt"

# Initialize the enhanced colour grading variables if they don't exist
default color_saturation = 1.0
default color_temperature = 0.0
default color_tint = 0.0
default shader_gamma = 1.0
default shader_brightness = 0.0
default shader_contrast = 1.0
default color_grading_enabled = False
# Vignette controls (now part of colour grading)
default grade_vignette_strength = 0.0
default grade_vignette_width = 0.25
default grade_vignette_feather = 1.0

# Legacy vignette controls (deprecated, kept for save compatibility)
default shader_vignette = 0.0
default shader_vignette_softness = 0.5

# Film grain variables
default film_grain_enabled = False
default film_grain_intensity = 0.02
default film_grain_size = 1.0
default film_grain_downscale = 2.0
# Film grain animation controls
default film_grain_anim_mode = "none"   # none|pulse|strobe|drift
default film_grain_anim_speed = 1.0
default film_grain_anim_amount = 0.35

# CRT variables
default crt_enabled = False
default crt_warp = 0.2
default crt_scan = 0.5
default crt_chroma = 0.9
default crt_scanline_size = 1.0
default crt_vignette_strength = 0.35
default crt_vignette_width = 0.25
default crt_vignette_feather = 1.0
# CRT animation controls
default crt_anim_type = "none"          # none|scanline|aberration|glitch
default crt_scanline_speed = 2.0
default crt_scanline_intensity = 0.1
default crt_aberr_speed = 1.0
default crt_aberr_amount = 0.0
default crt_aberr_r = 1.0
default crt_aberr_g = 0.0
default crt_aberr_b = 1.0
default crt_glitch = 0.0
default crt_glitch_speed = 1.5

# Lighting variables
default lighting_strength = 1.0
default lighting_override_x = 0.5
default lighting_override_y = 0.5

# Lighting animation variables
default lighting_anim_ui_mode = "none"
default lighting_anim_ui_speed = 0.8
default lighting_anim_ui_amount = 0.35
default lighting_anim_ui_radius = 0.05

init python:
    # Migration logic for vignette values from legacy locations
    def migrate_legacy_vignette_values():
        """One-time migration of vignette values from legacy locations to colour grading."""
        try:
            # Check if we need to migrate from CRT vignette fields
            crt_strength = getattr(store, 'crt_vignette_strength', None)
            crt_width = getattr(store, 'crt_vignette_width', None) 
            crt_feather = getattr(store, 'crt_vignette_feather', None)
            
            # Check if we need to migrate from legacy grading fields
            old_vignette = getattr(store, 'shader_vignette', None)
            old_softness = getattr(store, 'shader_vignette_softness', None)
            
            # Only migrate if new fields are at defaults and old fields have non-default values
            grade_strength = getattr(store, 'grade_vignette_strength', 0.0)
            grade_width = getattr(store, 'grade_vignette_width', 0.25)
            grade_feather = getattr(store, 'grade_vignette_feather', 1.0)
            
            # Are new fields at defaults?
            at_defaults = (grade_strength == 0.0 and grade_width == 0.25 and grade_feather == 1.0)
            
            if at_defaults:
                # Migrate from CRT fields if they exist and are non-default
                if crt_strength is not None and crt_strength != 0.35:
                    store.grade_vignette_strength = float(crt_strength)
                if crt_width is not None and crt_width != 0.25:
                    store.grade_vignette_width = float(crt_width)
                if crt_feather is not None and crt_feather != 1.0:
                    store.grade_vignette_feather = float(crt_feather)
                
                # Also migrate from old grading fields if they exist
                if old_vignette is not None and old_vignette != 0.0:
                    store.grade_vignette_strength = float(old_vignette)
                if old_softness is not None and old_softness != 0.5:
                    # Map softness to feather (similar concept)
                    store.grade_vignette_feather = float(old_softness) * 2.0
        except Exception:
            pass  # Silent migration failure to avoid breaking game startup
    
    # Run migration once at startup
    migrate_legacy_vignette_values()
    
    def toggle_shader_editor(force=None):
        """Toggle shader editor overlay with proper UI gating.
        Args:
            force: None (toggle), True (force open), False (force close)
        """
        try:
            current_state = bool(getattr(store, 'shader_editor_open', False))
            
            if force is None:
                new_state = not current_state
            else:
                new_state = bool(force)
            
            # No change needed
            if new_state == current_state:
                return
            
            if new_state:
                # Opening editor
                store.shader_editor_open = True
                # Also set legacy editor_visible for compatibility
                store.editor_visible = True
                
                # Hide gameplay UI elements
                try:
                    renpy.hide_screen("object_description")
                    renpy.hide_screen("floating_description_box")
                    renpy.hide_screen("interaction_menu")
                except Exception:
                    pass
                
                # Clear hover state
                try:
                    store.current_hover_object = None
                    store.interaction_menu_active = False
                except Exception:
                    pass
                
                # Prevent room fades while editing
                try:
                    store.suppress_room_fade_once = True
                except Exception:
                    pass
                
                # Show editor
                renpy.show_screen("unified_editor")
            else:
                # Closing editor
                store.shader_editor_open = False
                store.editor_visible = False
                
                # Hide editor
                renpy.hide_screen("unified_editor")
            
            renpy.restart_interaction()
        except Exception:
            pass

    # Provide backward compatibility wrapper
    def toggle_editor(force=None):
        """Backward compatibility wrapper for existing F8 binding."""
        return toggle_shader_editor(force)
