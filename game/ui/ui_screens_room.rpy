# Room Display Screens (Room & Objects)
#
# Overview
# - Composes background, objects, color grading/film grain, and CRT into the exploration scene.
# - Honors fade-in state and routes object display via display_api helpers.

# Common utilities are loaded by Ren'Py loader already.

# Display configuration
# ROOM_DISPLAY_CONFIG is defined in config/config_room.rpy

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
    if not room_has_faded_in:
        timer ROOM_DISPLAY_CONFIG["fade_duration"] action SetVariable('room_has_faded_in', True)

    # Determine active transforms for unified frame-level post-processing
    $ cg_state = shader_states.get("color_grading", {}).get("current", 0) if hasattr(store, 'shader_states') and shader_states else 0
    $ grain_state = shader_states.get("film_grain", {}).get("current", 0) if hasattr(store, 'shader_states') and shader_states else 0

    $ grade_transform = None
    # Print shader states only once per state change to avoid spam
    if shader_debug_enabled:
        $ _shader_state_key = str(cg_state) + "-" + str(grain_state)
        if getattr(store, '_last_shader_state_key', '') != _shader_state_key:
            python:
                try:
                    if hasattr(store, 'shader_states') and shader_states:
                        cg_presets = shader_states.get("color_grading", {}).get("presets", [])
                        gr_presets = shader_states.get("film_grain", {}).get("presets", [])
                        cg_name = cg_presets[cg_state] if cg_state < len(cg_presets) else "n/a"
                        gr_name = gr_presets[grain_state] if grain_state < len(gr_presets) else "n/a"
                        print("[SHADER FLOW] States: CG=" + str(cg_state) + " (" + cg_name + "), GR=" + str(grain_state) + " (" + gr_name + ")")
                    else:
                        print("[SHADER FLOW] States: CG=" + str(cg_state) + " (no state), GR=" + str(grain_state) + " (no state)")
                    store._last_shader_state_key = _shader_state_key
                except Exception as e:
                    print("[SHADER FLOW] Debug print error: " + str(e))
    # Apply color grading preset if active (flexible system)
    if cg_state > 0 and hasattr(store, 'shader_states') and shader_states and "color_grading" in shader_states and cg_state < len(shader_states["color_grading"]["presets"]):
        $ cg_preset = shader_states["color_grading"]["presets"][cg_state]
        # Use dynamic function lookup instead of hardcoded presets
        $ grade_func_name = "color_grade_" + cg_preset
        if hasattr(store, grade_func_name):
            $ grade_transform = getattr(store, grade_func_name)()
        else:
            # Fallback: try to find function without underscore replacement
            $ grade_func_name = "color_grade_" + cg_preset.replace('_', '')
            if hasattr(store, grade_func_name):
                $ grade_transform = getattr(store, grade_func_name)()
            else:
                $ grade_transform = None

    # Live grading (brightness/contrast/saturation/temperature/tint) as a dynamic pass
    $ temp = getattr(store, 'color_temperature', 0.0)
    $ tint = getattr(store, 'color_tint', 0.0)
    $ sat = getattr(store, 'color_saturation', 1.0)
    $ cont = getattr(store, 'shader_contrast', 1.0)
    $ bright = getattr(store, 'shader_brightness', 0.0)
    $ gam = getattr(store, 'shader_gamma', 1.0)
    $ vig = getattr(store, 'grade_vignette_strength', 0.0)
    $ vigs = getattr(store, 'grade_vignette_feather', 1.0)
    $ _live_grade_needed = (getattr(store, 'color_grading_enabled', False) or (bright != 0.0 or cont != 1.0 or sat != 1.0 or temp != 0.0 or tint != 0.0 or getattr(store,'grade_vignette_strength',0.0) != 0.0))
    $ live_grade_transform = complete_grading_transform(temperature=temp, tint=tint, saturation=sat, contrast=cont, brightness=bright, gamma=gam, vignette_amount=vig, vignette_softness=vigs) if _live_grade_needed else None

    # Bloom (after lighting, before grading)
    $ bloom_tr = None
    if getattr(store, 'bloom_enabled', False):
        $ _bt = float(getattr(store, 'bloom_threshold', 0.75))
        $ _bs = float(getattr(store, 'bloom_strength', 0.6))
        $ _br = float(getattr(store, 'bloom_radius', 2.5))
        $ bloom_tr = bloom_transform(threshold=_bt, strength=_bs, radius=_br) if 'bloom_transform' in globals() else None


    $ grain_transform = None
    # Check if film grain is enabled via the preset system
    if getattr(store, 'film_grain_enabled', False) and getattr(store, 'film_grain_intensity', 0.0) > 0:
        # Use the values set by the film grain preset or editor
        $ grain_intensity = getattr(store, 'film_grain_intensity', 0.0)
        $ grain_size = getattr(store, 'film_grain_size', 1.0) * 100.0  # Convert to pixel size
        $ grain_downscale = getattr(store, 'film_grain_downscale', 2.0)
        $ _fg_mode_name = str(getattr(store, 'film_grain_anim_mode', 'none')).lower()
        $ _fg_mode = 0 if _fg_mode_name == 'none' else (1 if _fg_mode_name == 'pulse' else (2 if _fg_mode_name == 'strobe' else 3))
        $ _fg_speed = float(getattr(store, 'film_grain_anim_speed', 1.0))
        $ _fg_amount = float(getattr(store, 'film_grain_anim_amount', 0.35))
        $ grain_transform = room_film_grain_overlay(grain_intensity=grain_intensity, grain_size=grain_size, downscale=grain_downscale, anim_mode=_fg_mode, anim_speed=_fg_speed, anim_amount=_fg_amount)

    # Use stable CRT state to avoid rapid toggling - force persistence
    $ _crt_enabled = getattr(store, 'crt_stable_state', False) or getattr(store, 'crt_enabled', False)
    if _crt_enabled:
        $ _crt_dbg = "CRT ON (warp=" + str(getattr(store,'crt_warp',0.2)) + ", scan=" + str(getattr(store,'crt_scan',0.5)) + ", chroma=" + str(getattr(store,'crt_chroma',0.9)) + ", size=" + str(getattr(store,'crt_scanline_size',1.0)) + ", vignette=(" + str(getattr(store,'grade_vignette_strength',0.0)) + "," + str(getattr(store,'grade_vignette_width',0.25)) + ") [from grading], animated=" + str(getattr(store,'crt_animated',False)) + ")"
        # Only print CRT ON message once per state change to avoid spam
        if shader_debug_enabled and not getattr(store, '_last_crt_debug_on', False):
            $ print("[SHADER FLOW] " + _crt_dbg)
            $ store._last_crt_debug_on = True
            $ store._last_crt_debug_off = False
        $ crt_warp = getattr(store, 'crt_warp', 0.2)
        $ crt_scan = getattr(store, 'crt_scan', 0.5)
        $ crt_chroma = getattr(store, 'crt_chroma', 0.9)
        $ crt_scanline_size = getattr(store, 'crt_scanline_size', 1.0)
        $ crt_vignette_strength = getattr(store, 'grade_vignette_strength', 0.0)
        $ crt_vignette_width = getattr(store, 'grade_vignette_width', 0.25)
        $ crt_vignette_feather = getattr(store, 'grade_vignette_feather', 1.0)
        $ crt_animated = getattr(store, 'crt_animated', False)
        $ crt_glitch = getattr(store, 'crt_glitch', 0.0)
        $ crt_glitch_speed = getattr(store, 'crt_glitch_speed', 1.0)
        $ _ab_mode_name = str(getattr(store, 'crt_aberr_mode', 'none')).lower()
        $ _ab_mode = 0 if _ab_mode_name == 'none' else (1 if _ab_mode_name == 'pulse' else (2 if _ab_mode_name == 'flicker' else 3))
        $ _ab_amp = float(getattr(store, 'crt_aberr_amount', getattr(store, 'crt_chroma', 0.0)))
        $ _ab_speed = float(getattr(store, 'crt_aberr_speed', 1.0))
        $ _ab_r = float(getattr(store, 'crt_aberr_r', 1.0))
        $ _ab_g = float(getattr(store, 'crt_aberr_g', 0.0))
        $ _ab_b = float(getattr(store, 'crt_aberr_b', 1.0))
        $ _scan_spd = float(getattr(store, 'crt_scanline_speed', 2.0))
        $ _scan_amt = float(getattr(store, 'crt_scanline_intensity', 0.1))
        $ lighting_transform = lighting_scene_transform() if hasattr(store, 'lighting_scene_transform') else room_no_fade()
        frame at (lighting_transform, bloom_tr if bloom_tr else room_no_fade(), live_grade_transform if live_grade_transform else room_no_fade(), grade_transform if grade_transform else room_no_fade(), grain_transform if grain_transform else room_no_fade(), (animated_chroma_crt(crt_warp, crt_scan, crt_chroma, crt_scanline_size, animation_intensity=_scan_amt, animation_speed=_scan_spd, vignette_strength=crt_vignette_strength, vignette_width=crt_vignette_width, vignette_feather=crt_vignette_feather, aberr_mode=_ab_mode, aberr_amp=_ab_amp, aberr_speed=_ab_speed, aberr_r=_ab_r, aberr_g=_ab_g, aberr_b=_ab_b, glitch=crt_glitch, glitch_speed=crt_glitch_speed) if crt_animated else static_chroma_crt(crt_warp, crt_scan, crt_chroma, crt_scanline_size, vignette_strength=crt_vignette_strength, vignette_width=crt_vignette_width, vignette_feather=crt_vignette_feather, aberr_mode=_ab_mode, aberr_amp=_ab_amp, aberr_speed=_ab_speed, aberr_r=_ab_r, aberr_g=_ab_g, aberr_b=_ab_b, glitch=crt_glitch, glitch_speed=crt_glitch_speed))):
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

            # Hover tint moved to overlay layer via hover_ui_overlay

            # Debug: show light counts (back/front) and current preset in developer/debug mode
            if (config.developer or (hasattr(store, 'lights_state') and store.lights_state.get('debug', False))):
                if 'get_lights_counts' in globals():
                    $ _lb, _lf = get_lights_counts()
                    text ("Lights back/front: " + str(_lb) + "/" + str(_lf)) size 12 color "#88ff88" xpos 10 ypos 6
                if 'lighting_current_preset_name' in globals():
                    $ _lname = lighting_current_preset_name()
                    if _lname:
                        text ("Preset: " + str(_lname)) size 12 color "#88ffcc" xpos 10 ypos 24
                if 'lighting_current_group_name' in globals():
                    $ _gname = lighting_current_group_name()
                    if _gname:
                        text ("Group: " + str(_gname)) size 12 color "#88ccff" xpos 10 ypos 42
    else:
        # Only print CRT OFF message once per state change to avoid spam
        if shader_debug_enabled and not getattr(store, '_last_crt_debug_off', False):
            $ print("[SHADER FLOW] CRT OFF")
            $ store._last_crt_debug_on = False
            $ store._last_crt_debug_off = True
        $ lighting_transform = lighting_scene_transform() if hasattr(store, 'lighting_scene_transform') else room_no_fade()
        frame at (lighting_transform, bloom_tr if bloom_tr else room_no_fade(), live_grade_transform if live_grade_transform else room_no_fade(), grade_transform if grade_transform else room_no_fade(), grain_transform if grain_transform else room_no_fade()):
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
                $ _lb2 = get_lights_displayable("back") if 'get_lights_displayable' in globals() else None
                $ _lb2 = _lb2 if _lb2 else Null()
                $ print("[UI] Adding back lights composite (no-CRT path, exists={} )".format(_lb2 is not None))
                add _lb2

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
                $ _lf2 = get_lights_displayable("front")
                $ _lf2 = _lf2 if _lf2 else Null()
                $ print("[UI] Adding front lights composite (no-CRT path, exists={} )".format(_lf2 is not None))
                add _lf2

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
    $ selector_open = getattr(store, 'lighting_selector_open', False)
    # Room background and objects
    use room_background_and_objects
    # Lighting overlay
    use lighting_overlay
    # Lighting selector overlay
    use lighting_selector
    # Letterbox overlay (cinematic bars)
    use letterbox_overlay
    # Shader Editor overlay (F8) on top
    use unified_editor
    # Shader hotkeys and help
    use shader_hotkeys

    # Simplified: No longer using pending dialogue system
    # Dialogue is called directly from room logic with proper UI clearing
    
    # Interactive elements
    if (not input_locked) and (not editor_open) and (not lighting_editor_open) and (not selector_open):
        use object_hotspots

    # Description boxes rendered on overlay layer via hover_ui_overlay

    # UI and debug overlays
    if (not input_locked) and (not editor_open) and (not lighting_editor_open) and (not selector_open):
        use room_ui_buttons
    # Debug overlay is registered as an overlay screen; no need to include here
    # Hide info overlay when lighting editor is active
    if not lighting_editor_open and not selector_open:
        use info_overlay

    # Over-grade debug: draw front lights above grade/grain/CRT
    if lights_over_grade_debug:
        $ _fo = get_lights_displayable("front")
        $ _fo = _fo if _fo else Null()
        $ print("[UI] Adding front lights over-grade (exists={} )".format(_fo is not None))
        add _fo
    
    # Lighting editor overlay - completely disables all game UI when active
    if lighting_editor_open:
        use lighting_editor
    
    # Block all interactions when lighting editor is active
    $ input_locked = input_locked or lighting_editor_open or selector_open
    
    # Simple shader controls will be added here later

    # Keyboard navigation for interaction menus
    if (not input_locked) and interaction_menu_active and (not lighting_editor_open) and (not selector_open):
        key "K_UP" action Function(navigate_interaction_menu, "up")
        key "K_DOWN" action Function(navigate_interaction_menu, "down")
        key "K_RETURN" action Function(execute_selected_action)
        key "K_ESCAPE" action Function(keyboard_cancel_action)

    # Allow access to game menu with Escape/Start button

    # Gamepad controls
    if (not input_locked) and gamepad_navigation_enabled and (not lighting_editor_open) and (not selector_open):
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
    if not input_locked and not lighting_editor_open and not selector_open:
        key "l" action Function(letterbox_combined_action)
        key "i" action ToggleVariable("show_info_overlay")
    # ctrl+F8 reserved for Lighting Selector toggle (repurposed from old lighting editor)
    if not input_locked:
        key "ctrl_K_F8" action ToggleVariable("lighting_selector_open")

    # Scanline size testing
    if not input_locked and not lighting_editor_open and not selector_open:
        key "1" action Function(set_crt_parameters, scanline_size=0.5)
        key "2" action Function(set_crt_parameters, scanline_size=1.0)
        key "3" action Function(set_crt_parameters, scanline_size=1.5)
        key "4" action Function(set_crt_parameters, scanline_size=3.0)

    # Debug hotkeys
    if not lighting_editor_open and not selector_open:
        key "K_F6" action Function(debug_light_overlay_toggle)
        key "ctrl_K_F7" action [ToggleVariable("lights_over_grade_debug"), Function(renpy.restart_interaction)]
        key "ctrl_K_F6" action [ToggleVariable("force_runtime_lighting_overlays"), Function(renpy.restart_interaction), Function(renpy.notify, "Runtime lighting overlays: toggled")] 
        # Cycle lighting presets (YAML light_*.yaml)
        key "K_F5" action Function(cycle_light_presets, 1)
        key "shift_K_F5" action Function(cycle_light_presets, -1)
        # Cycle groups (All + groups)
        key "K_F4" action Function(cycle_light_groups, 1)
        key "shift_K_F4" action Function(cycle_light_groups, -1)
        # Toggle selector UI
        key "ctrl_K_F8" action ToggleVariable("lighting_selector_open")

    # Vignette live tuning hotkeys removed; control via F8 editor or API
