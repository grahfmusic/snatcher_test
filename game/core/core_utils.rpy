# Common Utilities
# Shared functions used across multiple modules
#
# Overview
# - Fonts, dev mode checks, mouse positions, hover checks.
# - Keep small, generic helpers here only.

init python:
    def get_font():
        """Get the appropriate font for text display"""
        if renpy.loadable("fonts/quaver.ttf"):
            return "fonts/quaver.ttf"
        return gui.text_font
    
    def format_object_name(obj_name):
        """Format object name for display"""
        return obj_name.replace('_', ' ').title()
    
    def is_developer_mode():
        """Check if developer mode is active"""
        return config.developer
    
    def get_mouse_position():
        """Get current mouse position"""
        return renpy.get_mouse_pos()
    
    def check_hover_object_exists():
        """Check if current hover object exists and is valid"""
        return (store.current_hover_object and 
                store.current_hover_object in store.room_objects)
