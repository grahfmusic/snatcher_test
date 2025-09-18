# Room Display Screens (Room & Objects)
#
# Overview
# - Composes background, objects, shader pipeline passes, and CRT into the exploration scene.
# - Honors fade-in state and routes object display via display_api helpers.

# Screen-state defaults
default room_has_faded_in = False
default lights_over_grade_debug = False
default force_runtime_lighting_overlays = False

# Transforms
transform room_fade_in(duration=2.0):
    alpha 0.0
    ease duration alpha 1.0

transform room_no_fade():
    alpha 1.0

transform room_fade_out(duration=2.0):
    alpha 1.0
    ease duration alpha 0.0

transform black_background():
    alpha 1.0

init python:
    # Display helpers live in api/api_display.rpy
    pass

# Combined screen for room background and objects
screen room_background_and_objects():
    $ room_has_faded_in = getattr(store, 'room_has_faded_in', False)
    $ selector_open = getattr(store, 'lighting_selector_open', False)
    $ lighting_editor_open = getattr(store, 'lighting_editor_open', False)
    if not room_has_faded_in:
        timer ROOM_DISPLAY_CONFIG["fade_duration"] action SetVariable('room_has_faded_in', True)

    # Retrieve active shader stack via pipeline (lighting -> bloom -> grade -> grain -> CRT)
    $ _pipeline_stack, _shader_meta = shader_pipeline_get_stack(include_meta=True)
    $ _pipeline_stack = _pipeline_stack if _pipeline_stack else (room_no_fade(), )

    if shader_debug_enabled:
        $ _shader_state_key = repr((_shader_meta.get("grade_preset", {}).get("name"), _shader_meta.get("grain", {}).get("preset"), _shader_meta.get("crt", {}).get("active"), _shader_meta.get("lighting", {}).get("count", 0)))
        if getattr(store, '_last_shader_state_key', '') != _shader_state_key:
            python:
                try:
                    cg_name = _shader_meta.get("grade_preset", {}).get("name") or "off"
                    grain_name = _shader_meta.get("grain", {}).get("preset") or "off"
                    crt_info = _shader_meta.get("crt", {})
                    crt_state = "on" if crt_info.get("active") else "off"
                    if crt_info.get("active") and crt_info.get("animated"):
                        crt_state += " (animated)"
                    lights_count = _shader_meta.get("lighting", {}).get("count", 0)
                    print(f"[SHADER FLOW] CG={cg_name}; Grain={grain_name}; CRT={crt_state}; Lights={lights_count}")
                except Exception as e:
                    print("[SHADER FLOW] Debug print error: " + str(e))
            $ store._last_shader_state_key = _shader_state_key
        $ _crt_active = bool(_shader_meta.get("crt", {}).get("active", False))
        $ store._last_crt_debug_on = _crt_active
        $ store._last_crt_debug_off = not _crt_active

    frame at _pipeline_stack:
        background None
        add get_fallback_background() at black_background()
        if not room_has_faded_in:
            add get_room_background() at room_fade_in(ROOM_DISPLAY_CONFIG["fade_duration"])
        else:
            add get_room_background() at room_no_fade()

        # Lights behind objects (affects background)
        $ _split = getattr(store, 'lights_z_split', 20)
        if getattr(store, 'lights_layering_enabled', False):
            add Solid("#00000000") at lighting_back_transform
        else:
            $ _lights_back_shader = create_lighting_layer_transform_range("lights_back", 0, _split) if 'create_lighting_layer_transform_range' in globals() else None
            if _lights_back_shader:
                add _lights_back_shader
            else:
                $ _lb = get_lights_displayable("back")
                $ _lb = _lb if _lb else Null()
                $ print("[UI] Adding back lights composite (exists={} )".format(_lb is not None))
                add _lb

        for obj_name, obj_data in room_objects.items():
            if should_display_object(obj_data) and not is_object_hidden(obj_data):
                $ props = get_object_display_properties(obj_data)
                $ is_hovered = (current_hover_object == obj_name) and not lighting_editor_open and not selector_open
                $ was_hovered = (getattr(store, 'previous_hover_object', None) == obj_name) and not lighting_editor_open and not selector_open
                $ obj_transform = obj_data.get("transform", None)
                if not room_has_faded_in:
                    if obj_transform:
                        add props["image"] at room_fade_in(ROOM_DISPLAY_CONFIG["fade_duration"]), (object_desaturation_highlight() if is_hovered else (object_desaturation_fadeout(fade_duration=obj_data.get("desaturation_fade_duration", 0.4)) if was_hovered else object_normal_saturation)), obj_transform:
                            xpos props["xpos"]
                            ypos props["ypos"]
                            xsize props["xsize"]
                            ysize props["ysize"]
                    else:
                        add props["image"] at room_fade_in(ROOM_DISPLAY_CONFIG["fade_duration"]), (object_desaturation_highlight() if is_hovered else (object_desaturation_fadeout(fade_duration=obj_data.get("desaturation_fade_duration", 0.4)) if was_hovered else object_normal_saturation)):
                            xpos props["xpos"]
                            ypos props["ypos"]
                            xsize props["xsize"]
                            ysize props["ysize"]
                else:
                    if obj_transform:
                        add props["image"] at room_no_fade(), (object_desaturation_highlight() if is_hovered else (object_desaturation_fadeout(fade_duration=obj_data.get("desaturation_fade_duration", 0.4)) if was_hovered else object_normal_saturation)), obj_transform:
                            xpos props["xpos"]
                            ypos props["ypos"]
                            xsize props["xsize"]
                            ysize props["ysize"]
                    else:
                        add props["image"] at room_no_fade(), (object_desaturation_highlight() if is_hovered else (object_desaturation_fadeout(fade_duration=obj_data.get("desaturation_fade_duration", 0.4)) if was_hovered else object_normal_saturation)):
                            xpos props["xpos"]
                            ypos props["ypos"]
                            xsize props["xsize"]
                            ysize props["ysize"]

        # Lights in front of objects (rim/spot highlights)
        if getattr(store, 'lights_layering_enabled', False):
            add Solid("#00000000") at lighting_front_transform
        else:
            $ _lights_front_shader = create_lighting_layer_transform_range("lights_front", _split, 999) if 'create_lighting_layer_transform_range' in globals() else None
            if _lights_front_shader:
                add _lights_front_shader
            else:
                $ _lf = get_lights_displayable("front")
                $ _lf = _lf if _lf else Null()
                $ print("[UI] Adding front lights composite (exists={} )".format(_lf is not None))
                add _lf

        # Debug overlays for lighting state
        if (config.developer or (hasattr(store, 'lights_state') and store.lights_state.get('debug', False))):
            if 'get_lights_counts' in globals():
                $ _lb_count, _lf_count = get_lights_counts()
                text ("Lights back/front: " + str(_lb_count) + "/" + str(_lf_count)) size 12 color "#88ff88" xpos 10 ypos 6
            if 'lighting_current_preset_name' in globals():
                $ _lname = lighting_current_preset_name()
                if _lname:
                    text ("Preset: " + str(_lname)) size 12 color "#88ffcc" xpos 10 ypos 24
            if 'lighting_current_group_name' in globals():
                $ _gname = lighting_current_group_name()
                if _gname:
                    text ("Group: " + str(_gname)) size 12 color "#88ccff" xpos 10 ypos 42

        # Hover tint moved to overlay layer via hover_ui_overlay

screen room_background():
    use room_background_and_objects

screen room_objects():
    pass

# Main exploration composition screen (easy to edit)
screen room_exploration():
    # Lock input until the initial fade completes
    $ input_locked = not room_has_faded_in
    $ editor_open = getattr(store, 'shader_editor_open', False) or getattr(store, 'editor_visible', False)
    # Room background and objects
    use room_background_and_objects
    # Lighting overlay
    use lighting_overlay
    # Letterbox overlay (cinematic bars)
    use letterbox_overlay
    # Shader Editor overlay (F8) on top
    use unified_editor
    # Shader hotkeys and help
    use shader_hotkeys

    # Simplified: No longer using pending dialogue system
    # Dialogue is called directly from room logic with proper UI clearing
    
    # Interactive elements
    if (not input_locked) and (not editor_open) and (not lighting_editor_open):
        use object_hotspots

    # Description system - show floating descriptions on hover (hidden while editor is open)
    # Wrap in stable container to enable crossfade transitions between objects
    fixed id "descbox_slot":
        if (not input_locked) and (not editor_open) and (not lighting_editor_open) and current_hover_object:
            $ obj = room_objects[current_hover_object]
            $ box_width, box_height = calculate_description_box_size(obj["description"])
            $ position_setting = obj.get("box_position", "auto")
            $ box_x, box_y, box_position = calculate_box_position(obj, box_width, box_height, position_setting)
            $ float_intensity = obj.get("float_intensity", 1.0)
            use floating_description_box(obj, box_width, box_height, box_x, box_y, float_intensity)

    # UI and debug overlays
    if (not input_locked) and (not editor_open) and (not lighting_editor_open):
        use room_ui_buttons
    # Debug overlay is registered as an overlay screen; no need to include here
    # Hide info overlay when lighting editor is active
    if not lighting_editor_open:
        use info_overlay
    
    # Lighting editor overlay - completely disables all game UI when active
    if lighting_editor_open:
        use lighting_editor_overlay
    
    # Block all interactions when lighting editor is active
    $ input_locked = input_locked or lighting_editor_open
    
    # Simple shader controls will be added here later

    # Keyboard navigation for interaction menus
    if (not input_locked) and interaction_menu_active and (not lighting_editor_open):
        key "K_UP" action Function(navigate_interaction_menu, "up")
        key "K_DOWN" action Function(navigate_interaction_menu, "down")
        key "K_RETURN" action Function(execute_selected_action)
        key "K_ESCAPE" action Function(keyboard_cancel_action)

    # Allow access to game menu with Escape/Start button

    # Gamepad controls
    if (not input_locked) and gamepad_navigation_enabled and (not lighting_editor_open):
        if interaction_menu_active:
            key "pad_dpup_press" action Function(navigate_interaction_menu, "up")
            key "pad_dpdown_press" action Function(navigate_interaction_menu, "down")
            key "pad_lefty_neg" action Function(navigate_interaction_menu, "up")
            key "pad_lefty_pos" action Function(navigate_interaction_menu, "down")
        else:
            key "pad_dpleft_press" action Function(gamepad_navigate, "left")
            key "pad_dpright_press" action Function(gamepad_navigate, "right")
            key "pad_dpup_press" action Function(gamepad_navigate, "up")
            key "pad_dpdown_press" action Function(gamepad_navigate, "down")
            key "pad_leftx_neg" action Function(gamepad_navigate, "left")
            key "pad_leftx_pos" action Function(gamepad_navigate, "right")
            key "pad_lefty_neg" action Function(gamepad_navigate, "up")
            key "pad_lefty_pos" action Function(gamepad_navigate, "down")

        key "pad_a_press" action Function(gamepad_confirm_action)
        if interaction_menu_active:
            key "pad_b_press" action Function(gamepad_cancel_action)
        else:
            key "pad_b_press" action Function(gamepad_select_first_object)
        key "pad_back_press" action Function(toggle_gamepad_navigation)

    # Global shortcuts
    if not input_locked and not lighting_editor_open:
        key "l" action Function(letterbox_combined_action)
        key "i" action ToggleVariable("show_info_overlay")
    if not input_locked:  # Allow lighting editor toggle even when locked
        key "ctrl_K_F8" action Function(toggle_lighting_editor)

    # Scanline size testing
    if not input_locked and not lighting_editor_open:
        key "1" action Function(set_crt_parameters, scanline_size=0.5)
        key "2" action Function(set_crt_parameters, scanline_size=1.0)
        key "3" action Function(set_crt_parameters, scanline_size=1.5)
        key "4" action Function(set_crt_parameters, scanline_size=3.0)

    # Vignette live tuning hotkeys removed; control via F8 editor or API
