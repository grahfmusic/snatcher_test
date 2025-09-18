# Shader System Integration
# Clean, modular shader management with proper Ren'Py patterns
#
# This module handles:
# - Shader state management
# - Effect cycling and presets
# - Clean hotkey integration
# - Notification system

## Dynamic Shader State Registry (JSON-based)
# Shader states are now dynamically populated from JSON preset files
default shader_states = {}

# Initialize dynamic shader state discovery
init 10 python:
    def scan_shader_preset_files():
        """Scan for shader preset JSON files and populate shader_states dynamically using shared helper."""
        try:
            from api_presets import presets_scan_shader
        except Exception:
            # Fallback: empty discovery
            presets_scan_shader = None
        
        discovered_presets = {}
        
        # Ensure shader_states exists
        if not hasattr(store, 'shader_states') or store.shader_states is None:
            store.shader_states = {}
        
        if presets_scan_shader:
            scanned = presets_scan_shader()
            # Map helper categories to internal names
            category_map = {
                "crt": "crt",
                "grade": "color_grading",
                "grain": "film_grain",
            }
            for key, items in scanned.items():
                if key == "all":
                    continue
                cat = category_map.get(key)
                if not cat:
                    continue
                names = ["off"]
                names.extend(sorted([i["name"] for i in items]))
                discovered_presets[cat] = names
        
        # Initialize shader_states with discovered presets
        for category, presets in discovered_presets.items():
            if category not in store.shader_states:
                store.shader_states[category] = {
                    "current": 0,
                    "presets": presets
                }
            else:
                store.shader_states[category]["presets"] = presets
        
        # Ensure we have at least basic categories
        essential_categories = ["color_grading", "film_grain", "crt"]
        for category in essential_categories:
            if category not in store.shader_states:
                store.shader_states[category] = {
                    "current": 0,
                    "presets": ["off"]
                }
        
        print("Shader presets discovered (shared helper)")
    
    # Auto-scan on initialization
    scan_shader_preset_files()

## Legacy help/menu removed; use F8 Shader Editor instead
default shader_debug_enabled = False
default suppress_room_fade_once = False

## Shader Configuration
define SHADER_CONFIG = {
    "notification_duration": 1.6,
    "notification_bg": "#000080cc",
    "notification_text_color": "#ffffff",
    "notification_text_size": 20
}

## Shader Management Functions
init python:
    def toggle_editor():
        """Legacy toggle_editor function - redirects to new shader editor system."""
        try:
            # Use the new centralized shader editor toggle
            toggle_shader_editor()
        except Exception:
            pass
    def reset_all_shaders():
        """Reset all shader effects to off state."""
        shader_pipeline_reset()
        store.suppress_room_fade_once = True
        show_shader_notification("All Shaders Reset")
    
    def get_current_shader_preset(shader_name):
        """Get the current preset name for a shader.
        
        Args:
            shader_name: Name of the shader
            
        Returns:
            Current preset name
        """
        if shader_name not in store.shader_states:
            return "off"
        
        state = store.shader_states[shader_name]
        return state["presets"][state["current"]]
    
    def set_shader_preset(shader_name, preset_name):
        """Set a specific preset for a shader.
        
        Args:
            shader_name: Name of the shader
            preset_name: Name of the preset to apply
        """
        if shader_name not in store.shader_states:
            return
        
        state = store.shader_states[shader_name]
        if preset_name in state["presets"]:
            state["current"] = state["presets"].index(preset_name)
            store.suppress_room_fade_once = True
            renpy.restart_interaction()
    
    def show_shader_notification(message):
        """Show a temporary notification for shader changes.
        
        Args:
            message: Notification text
        """
        renpy.show_screen(
            "shader_notification",
            message=message,
            duration=SHADER_CONFIG["notification_duration"]
        )
    
    # No install hook required; editor/preset IO drive state

## Shader Notification Screen
screen shader_notification(message, duration=2.0):
    timer duration action Hide("shader_notification")
    
    frame:
        background SHADER_CONFIG["notification_bg"]
        padding (20, 10)
        xalign 0.5
        yalign 0.1
        
        text message:
            color SHADER_CONFIG["notification_text_color"]
            size SHADER_CONFIG["notification_text_size"]
            text_align 0.5

## Shader Help Screen
## Legacy shader_help removed

## Shader Menu Screen (DEPRECATED - Use editor instead)
# This screen is kept for compatibility but should not be used directly
# All shader controls are now in the unified editor (F8)
## Legacy shader_menu removed

## Shader Hotkeys Screen (Editor-only - no gameplay access)
screen shader_hotkeys():
    # Lightweight global hotkeys to match documented defaults.
    # Keep it minimal: open editor, help, menu, and reset.
    if config.developer and not getattr(store,'interactions_paused', False):
        # Toggle Shader Editor
        key "K_F8" action Function(toggle_editor)
        # Reset
        key "r" action Function(reset_all_shaders)
