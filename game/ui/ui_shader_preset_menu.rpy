# Shader Preset Menu System
# Provides a comprehensive menu interface for JSON shader presets
# Detects available files from both shipped and custom directories
# Organised by effect type with search and filtering capabilities

init -1 python:
    from collections import defaultdict

# Menu state variables
default shader_menu_visible = False
default shader_menu_category = "all"  # all, crt, grain, grade
default shader_menu_search = ""
default shader_menu_scroll_value = 0.0

# Detected presets cache
default shader_preset_cache = {}
default shader_preset_last_scan = 0

init python:
    def scan_shader_preset_directories():
        """
        Scan for shader preset JSON files using the shared helper.
        Returns a dictionary organised by category (all, crt, grain, grade).
        """
        import time
        # Check if we need to rescan (cache for performance)
        current_time = time.time()
        if (current_time - store.shader_preset_last_scan < 5.0 and 
            store.shader_preset_cache):
            return store.shader_preset_cache
        scanned = store.presets_scan_shader()
        store.shader_preset_cache = dict(scanned)
        store.shader_preset_last_scan = current_time
        return store.shader_preset_cache
    
    def get_filtered_presets(category="all", search_term=""):
        """
        Get presets filtered by category and search term.
        """
        all_presets = scan_shader_preset_directories()
        
        if category not in all_presets:
            return []
        
        presets = all_presets[category]
        
        if search_term:
            search_lower = search_term.lower()
            presets = [p for p in presets if search_lower in p['name'].lower()]
        
        return presets
    
    def apply_shader_preset_from_menu(preset_info):
        """
        Apply a shader preset selected from the menu.
        Shows notification when applied.
        """
        try:
            # Use existing shader preset application function
            success = shader_preset_apply_file(preset_info['full_path'])
            
            if success:
                message = "Applied " + preset_info['effect_type'].title() + " Preset: " + preset_info['name']
                show_shader_notification(message)
                # Close menu after successful application
                store.shader_menu_visible = False
            else:
                show_shader_notification("Failed to apply preset")
                
        except Exception as e:
            print("Error applying preset " + preset_info['name'] + ": " + str(e))
            show_shader_notification("Error applying preset")
        
        # Force interaction restart to reflect changes
        renpy.restart_interaction()
    
    def toggle_shader_preset_menu():
        """
        Toggle the shader preset menu visibility.
        """
        store.shader_menu_visible = not store.shader_menu_visible
        if store.shader_menu_visible:
            # Refresh preset cache when opening menu
            scan_shader_preset_directories()
        renpy.restart_interaction()
    
    def get_category_display_name(category):
        """
        Get display name for category.
        """
        category_names = {
            "all": "All Presets",
            "crt": "CRT Effects", 
            "grain": "Film Grain",
            "grade": "Colour Grading",
        }
        return category_names.get(category, category.title())

# Shader Preset Menu Screen
screen shader_preset_menu():
    if shader_menu_visible:
        modal True
        zorder 1000
        
        # Close keys
        key "K_ESCAPE" action SetVariable("shader_menu_visible", False)
        key "K_F9" action SetVariable("shader_menu_visible", False)  # F9 to toggle
        
        # Dark background overlay
        add Solid("#000000aa")
        
        # Main menu frame
        frame:
            background Frame("gui/frame.png", gui.frame_borders, tile=gui.frame_tile)
            xalign 0.5
            yalign 0.5
            xsize 800
            ysize 600
            padding (20, 20)
            
            vbox:
                spacing 15
                
                # Header
                hbox:
                    xfill True
                    text "Shader Preset Menu" size 24 color "#ffffff" bold True
                    textbutton "✕":
                        action SetVariable("shader_menu_visible", False)
                        text_size 20
                        background None
                        text_color "#cccccc"
                        text_hover_color "#ffffff"
                        xalign 1.0
                
                # Category tabs
                hbox:
                    spacing 5
                    for cat in ["all", "crt", "grain", "grade"]:
                        textbutton get_category_display_name(cat):
                            action SetVariable("shader_menu_category", cat)
                            text_size 14
                            text_color ("#ffffff" if shader_menu_category == cat else "#aaaaaa")
                            background (Solid("#444444") if shader_menu_category == cat else Solid("#333333"))
                            hover_background Solid("#555555")
                            padding (10, 5)
                
                # Search bar
                hbox:
                    spacing 10
                    text "Search:" size 14 color "#cccccc" yalign 0.5
                    input:
                        value VariableInputValue("shader_menu_search")
                        length 30
                        pixel_width 300
                    textbutton "Clear":
                        action SetVariable("shader_menu_search", "")
                        text_size 12
                        background Solid("#555555")
                        hover_background Solid("#666666")
                        padding (8, 4)
                
                # Preset list
                frame:
                    background Solid("#222222")
                    xfill True
                    yfill True
                    padding (10, 10)
                    
                    viewport:
                        id "preset_viewport"
                        draggable True
                        mousewheel True
                        scrollbars "vertical"
                        xfill True
                        yfill True
                        
                        vbox:
                            spacing 2
                            
                            $ filtered_presets = get_filtered_presets(shader_menu_category, shader_menu_search)
                            
                            if not filtered_presets:
                                text "No presets found" size 16 color "#888888" xalign 0.5 yalign 0.5
                            else:
                                for preset in filtered_presets:
                                    button:
                                        action Function(apply_shader_preset_from_menu, preset)
                                        background Solid("#333333")
                                        hover_background Solid("#444444")
                                        selected_background Solid("#555555")
                                        xfill True
                                        padding (12, 8)
                                        
                                        hbox:
                                            spacing 15
                                            
                                            # Effect type indicator
                                            frame:
                                                background Solid({
                                                    "crt": "#ff6666",
                                                    "grain": "#66ff66", 
                                                    "grade": "#6666ff",
                                                    "light": "#ffff66"
                                                }.get(preset["effect_type"], "#ffffff"))
                                                xsize 8
                                                ysize 20
                                            
                                            vbox:
                                                spacing 2
                                                text preset["name"] size 16 color "#ffffff"
                                                text f"{preset['effect_type'].title()} • {preset['source'].title()}" size 12 color "#aaaaaa"
                
                # Footer info
                hbox:
                    spacing 15
                    text f"Found {len(get_filtered_presets(shader_menu_category, shader_menu_search))} presets" size 12 color "#888888"
                    text "ESC or F9 to close" size 12 color "#888888"

# Global keymap for opening the menu
init python:
    config.keymap['shader_menu'] = ['K_F9']
    
    # Add the global overlay to Ren'Py's default overlays
    config.overlay_screens.append("shader_preset_global_overlay")

screen global_shader_menu_keys():
    key "K_F9" action Function(toggle_shader_preset_menu)

# Global overlay screen that's always active
screen shader_preset_global_overlay():
    zorder 1000
    
    # Global hotkeys available everywhere
    key "K_F9" action Function(toggle_shader_preset_menu)
    
    # Display the shader preset menu when visible
    if shader_menu_visible:
        use shader_preset_menu
