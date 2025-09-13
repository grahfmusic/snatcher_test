# UI API
# Hotspot creation, hover handling, and button customization
#
# Overview
# - Creates hotspot configs for objects and handles hover/unhover events.
# - Exposes helpers to customize editor/exit buttons and add custom buttons.
#
# Contracts
# - create_object_hotspot(obj_name, obj_data) -> dict{xpos,ypos,xsize,ysize,obj_name}
# - get_all_object_hotspots() -> list of hotspot dicts
# - handle_object_hover(obj_name), handle_object_unhover()
# - customize_exit_button(...), customize_editor_button(...), add_custom_button(...)
#
# Integration
# - handle_object_hover emits on_object_hover(room_id, obj) into game logic hooks.

init python:
    def create_object_hotspot(obj_name, obj_data):
        """Create hotspot configuration for an object"""
        return {
            "xpos": obj_data["x"],
            "ypos": obj_data["y"],
            "xsize": obj_data["width"],
            "ysize": obj_data["height"],
            "obj_name": obj_name
        }

    # Aliases
    def hotspot(obj_name, obj_data):
        return create_object_hotspot(obj_name, obj_data)
    
    def get_all_object_hotspots():
        """Get hotspot configurations for all room objects"""
        hotspots = []
        for obj_name, obj_data in store.room_objects.items():
            hotspots.append(create_object_hotspot(obj_name, obj_data))
        return hotspots

    def hotspots():
        return get_all_object_hotspots()
    
    def get_room_exit_action():
        """Get the action for exiting the room with a confirmation prompt"""
        # Check if we're in a room context
        if hasattr(store, 'current_room_id') and store.current_room_id:
            # In a room - show confirmation to return to main menu
            return Show("confirm", message="Return to main menu?", yes_action=Return(), no_action=Hide("confirm"))
        else:
            # Not in a room context - just hide any dialogs
            return Hide("confirm")

    def exit_action():
        return get_room_exit_action()
    
    def get_editor_mode_action():
        """Get the action for entering unified editor mode."""
        return SetVariable("editor_visible", True)

    def editor_action():
        return get_editor_mode_action()
    
    def handle_object_hover(obj_name):
        """Handle object hover - only update if interaction menu is not active"""
        if not interaction_menu_active:
            # Store previous hover for graceful fade transitions
            store.previous_hover_object = getattr(store, 'current_hover_object', None)
            store.current_hover_object = obj_name
            try:
                # Input: mouse hover
                log_main_event("INPUT", f"hover {obj_name}", scope="mouse")
            except Exception:
                pass
            try:
                on_object_hover(store.current_room_id, obj_name)
            except Exception:
                pass
            renpy.restart_interaction()

    def hover(obj_name):
        return handle_object_hover(obj_name)
    
    def handle_object_unhover():
        """Handle object unhover - only update if interaction menu is not active"""
        if not interaction_menu_active:
            # Store previous hover for graceful fade transitions
            store.previous_hover_object = getattr(store, 'current_hover_object', None) 
            store.current_hover_object = None
            renpy.restart_interaction()

    def unhover():
        return handle_object_unhover()

init python:
    def customize_exit_button(text=None, xpos=None, ypos=None, action=None):
        """Customize the exit button properties"""
        if text:
            ROOM_BUTTON_CONFIG["exit"]["text"] = text
        if xpos is not None:
            ROOM_BUTTON_CONFIG["exit"]["xpos"] = xpos
        if ypos is not None:
            ROOM_BUTTON_CONFIG["exit"]["ypos"] = ypos
        # Action can be customized via get_room_exit_action override

    def ui_exit_cfg(text=None, xpos=None, ypos=None, action=None):
        return customize_exit_button(text, xpos, ypos, action)
    
    def customize_editor_button(text=None, xpos=None, ypos=None, enabled=True):
        """Editor button has been removed; this is a no-op (use F8 to toggle)."""
        return False

    def ui_editor_cfg(text=None, xpos=None, ypos=None, enabled=True):
        """Editor button has been removed; this is a no-op (use F8 to toggle)."""
        return False
    
    def add_custom_button(button_id, config):
        """Add a custom button to the room UI"""
        ROOM_BUTTON_CONFIG[button_id] = config

    def ui_add_button(button_id, config):
        return add_custom_button(button_id, config)

    def get_object_focus_mask(obj_data):
        """Return a displayable to use as a focus mask matching the object's opaque pixels.

        Scales the object's source image to the configured width/height so the
        alpha channel can be used to determine the clickable/hoverable area.
        Returns None if scaling information is unavailable.
        """
        try:
            img = obj_data.get("image")
            if not img:
                return None
            # Cache/resolve original size using the actual image path
            orig = get_original_size_by_path(img)
            ow, oh = int(orig.get("width", 0)), int(orig.get("height", 0))
            w, h = int(obj_data.get("width", 0)), int(obj_data.get("height", 0))
            if ow > 0 and oh > 0 and w > 0 and h > 0:
                import renpy.display.transform as t
                zx = float(w) / float(ow)
                zy = float(h) / float(oh)
                return t.Transform(img, xzoom=zx, yzoom=zy)
        except Exception:
            pass
        return None

    def focus_mask(obj_data):
        return get_object_focus_mask(obj_data)
