# Display API
# Background, object visibility, and display helpers
#
# Overview
# - Provides helpers to fetch backgrounds and determine object visibility.
# - Consumed by room composition screens and higher-level APIs.
#
# Contracts
# - get_room_background() -> str displayable path or color
# - get_fallback_background() -> color string
# - should_display_object(obj: dict) -> bool
# - get_object_display_properties(obj: dict) -> {image, xpos, ypos, xsize, ysize}
#
# Notes
# - Keep objects as plain dicts; this API translates them for UI screens.

init python:
    def get_room_background():
        """Get the current room background image"""
        if store.room_background:
            return store.room_background
        return ROOM_DISPLAY_CONFIG["default_background"]

    # Alias
    def room_bg():
        return get_room_background()
    
    def get_fallback_background():
        """Get fallback background color"""
        return ROOM_DISPLAY_CONFIG["fallback_background_color"]

    def bg_fallback():
        return get_fallback_background()
    
    def should_display_object(obj_data):
        """Check if an object should be displayed"""
        return "image" in obj_data

    def obj_visible(obj_data):
        return should_display_object(obj_data)
    
    def get_object_display_properties(obj_data):
        """Get display properties for an object"""
        return {
            "image": obj_data["image"],
            "xpos": obj_data["x"],
            "ypos": obj_data["y"],
            "xsize": obj_data["width"],
            "ysize": obj_data["height"]
        }

    def obj_props(obj_data):
        return get_object_display_properties(obj_data)

init python:
    def set_fallback_background_color(color):
        """Set the fallback background color"""
        ROOM_DISPLAY_CONFIG["fallback_background_color"] = color

    def bg_fallback_set(color):
        return set_fallback_background_color(color)
    
    def set_default_background(image_path):
        """Set the default background image"""
        ROOM_DISPLAY_CONFIG["default_background"] = image_path

    def bg_default(image_path):
        return set_default_background(image_path)
    
    def hide_object(obj_name):
        """Temporarily hide an object from display"""
        if obj_name in store.room_objects:
            store.room_objects[obj_name]["_hidden"] = True
            try:
                log_main_event("VAR", f"hide {obj_name}")
            except Exception:
                pass

    def obj_hide(name):
        return hide_object(name)
    
    def show_object(obj_name):
        """Show a previously hidden object"""
        if obj_name in store.room_objects:
            store.room_objects[obj_name]["_hidden"] = False
            try:
                log_main_event("VAR", f"show {obj_name}")
            except Exception:
                pass

    def obj_show(name):
        return show_object(name)
    
    def is_object_hidden(obj_data):
        """Check if an object is hidden"""
        return obj_data.get("_hidden", False)

    def obj_hidden(obj_data):
        return is_object_hidden(obj_data)
