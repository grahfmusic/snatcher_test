# Lighting Manager (Ctrl+F8)

default lighting_selector_open = False
default lighting_selector_alpha = 0.90
default lighting_edit_mode = False  # retained for compatibility; UI editing controls removed
default lighting_save_name = "my_custom"
default lighting_selected_index = -1
default lighting_hover_index = -1
default lighting_overwrite = False
default lighting_preset_filter = ""

transform lighting_selector_window_alpha(a=0.90):
    alpha a

screen lighting_selector():
    if lighting_selector_open:
        modal True
        zorder 2000

        key "K_ESCAPE" action ToggleVariable("lighting_selector_open")
        key "ctrl_K_F8" action ToggleVariable("lighting_selector_open")

        # Keep cache fresh every time the menu opens
        $ lighting_scan_presets('all')

        # Edit gestures removed from selector UI

        # Dim background
        add Solid("#000000AA")

        # Compute adaptive size
        $ _fw = int(config.screen_width * 0.9)
        $ _fh = int(config.screen_height * 0.9)
        $ _rp_h = max(260, _fh - 180)
        # Use nearly full height for the preset list now that the toolbox lives in the header
        $ _plist_h = max(220, _rp_h - 40)

        frame at lighting_selector_window_alpha(lighting_selector_alpha):
            background Solid("#111111")
            xalign 0.5
            yalign 0.5
            xsize _fw
            ysize _fh
            padding (16, 14)

            # Main stacked content (no fixed to avoid overlap)
            vbox:
                spacing 10

                # Header with toolbar
                # Wrap the toolbar into multiple rows earlier on smaller widths
                $ _is_compact = (_fw < 1300)
                $ _bar_len = 200 if _is_compact else 280
                frame:
                    background Solid("#1A1A1A")
                    xfill True
                    padding (8,8)
                    vbox:
                        spacing 6
                        # Title row
                        hbox:
                            spacing 12
                            xfill True
                            text "Lighting Manager" size 22 color "#ffffff" yalign 0.5
                            text "(Ctrl+F8 to close)" size 12 color "#cccccc" yalign 0.5
                            null width 0 xfill True
                            textbutton "Edit Lights…":
                                action Function(open_lighting_editor_from_selector)
                                background Solid("#2f2f2f")
                                hover_background Solid("#3f3f3f")
                                padding (6,4)
                            textbutton "Close":
                                action ToggleVariable("lighting_selector_open")
                                background Solid("#333333")
                                hover_background Solid("#444444")
                                padding (6,4)
                        
                        # Toolbar rows (wrap when compact)
                        if _is_compact:
                            vbox:
                                spacing 6
                                hbox:
                                    spacing 12
                                    text "Alpha" size 12 color "#cccccc" yalign 0.5
                                    bar value VariableValue("lighting_selector_alpha", 1.0, offset=0.0) xsize _bar_len changed Function(renpy.restart_interaction)
                                    text ("%.2f" % lighting_selector_alpha) size 11 color "#aaaaaa" yalign 0.5
                                hbox:
                                    spacing 12
                                    text "Set:" size 12 color "#cccccc" yalign 0.5
                                    textbutton "None":
                                        action Function(lighting_apply_preset, 'off')
                                        background Solid("#333333")
                                        hover_background Solid("#444444")
                                        padding (6,4)
                                    null width 0 xfill True
                                    # Save controls (right-aligned)
                                    text "Save As" size 12 color "#cccccc" yalign 0.5
                                    input value VariableInputValue("lighting_save_name") length 18 xsize 220
                                    text ".yaml" size 12 color "#888888" yalign 0.5
                                    textbutton "Save":
                                        action Function(lighting_save_current_to_yaml, lighting_save_name, lighting_overwrite)
                                        background Solid("#333333")
                                        hover_background Solid("#444444")
                                        padding (6,4)
                                    text "Overwrite" size 12 color "#cccccc" yalign 0.5
                                    textbutton ("ON" if lighting_overwrite else "OFF"):
                                        action ToggleVariable("lighting_overwrite")
                                        background Solid("#333333")
                                        hover_background Solid("#444444")
                                        padding (6,4)
                        else:
                            hbox:
                                spacing 12
                                # Alpha
                                text "Alpha" size 12 color "#cccccc" yalign 0.5
                                bar value VariableValue("lighting_selector_alpha", 1.0, offset=0.0) xsize _bar_len changed Function(renpy.restart_interaction)
                                text ("%.2f" % lighting_selector_alpha) size 11 color "#aaaaaa" yalign 0.5
                                null width 20
                                # Set control
                                text "Set:" size 12 color "#cccccc" yalign 0.5
                                textbutton "None":
                                    action Function(lighting_apply_preset, 'off')
                                    background Solid("#333333")
                                    hover_background Solid("#444444")
                                    padding (6,4)
                                null width 0 xfill True
                                # Save controls (right-aligned)
                                text "Save As" size 12 color "#cccccc" yalign 0.5
                                input value VariableInputValue("lighting_save_name") length 18 xsize 220
                                text ".yaml" size 12 color "#888888" yalign 0.5
                                textbutton "Save":
                                    action Function(lighting_save_current_to_yaml, lighting_save_name, lighting_overwrite)
                                    background Solid("#333333")
                                    hover_background Solid("#444444")
                                    padding (6,4)
                                text "Overwrite" size 12 color "#cccccc" yalign 0.5
                                textbutton ("ON" if lighting_overwrite else "OFF"):
                                    action ToggleVariable("lighting_overwrite")
                                    background Solid("#333333")
                                    hover_background Solid("#444444")
                                    padding (6,4)

                # Content area: groups | presets (flows below header)
                hbox:
                    spacing 12

                    # Groups column (fixed width)
                    frame:
                        background Solid("#1E1E1E")
                        xsize 280
                        # Let content determine height to keep below header
                        padding (10,10)
                        vbox:
                            spacing 8
                            hbox:
                                spacing 6
                                text "Groups" size 14 color "#ffffff" yalign 0.5
                                textbutton "Reload":
                                    action Function(lighting_refresh_cache)
                                    text_size 12
                                    background Solid("#333333")
                                    hover_background Solid("#444444")
                                    padding (6,4)
                            viewport:
                                draggable True
                                mousewheel True
                                scrollbars "vertical"
                                # Match preset list height to avoid header overlap
                                ysize _plist_h
                                vbox:
                                    spacing 4
                                    $ _gsel = lighting_current_group_name()
                                    textbutton "All":
                                        action Function(lighting_set_group, None)
                                        background (Solid("#3a3a3a") if _gsel == 'All' else Solid("#242424"))
                                        hover_background Solid("#444444")
                                        text_color ("#ffffff" if _gsel == 'All' else "#cccccc")
                                        padding (8,4)
                                    $ _groups = lighting_groups()
                                    if not _groups:
                                        text "(no groups found)" size 12 color "#999999"
                                    for g in _groups:
                                        $ _is = (_gsel.lower() == str(g).lower())
                                        textbutton str(g):
                                            action Function(lighting_set_group, g)
                                            background (Solid("#3a3a3a") if _is else Solid("#242424"))
                                            hover_background Solid("#444444")
                                            text_color ("#ffffff" if _is else "#cccccc")
                                            padding (8,4)

                    # Presets column
                    # Right column (presets)
                    frame:
                        background Solid("#1E1E1E")
                        xfill True
                        padding (10,10)
                        # Right column content (no outer viewport; only list scrolls)
                        vbox:
                            spacing 10
                            # Presets list header + search
                            hbox:
                                spacing 10
                                text "Presets" size 14 color "#ffffff" yalign 0.5
                                null width 10
                                text "Search" size 12 color "#cccccc" yalign 0.5
                                input value VariableInputValue("lighting_preset_filter") length 18 xsize 240
                                textbutton "Clear":
                                    action SetVariable("lighting_preset_filter", "")
                                    text_size 11
                                    background Solid("#333333")
                                    hover_background Solid("#444444")
                                    padding (6,4)
                            # Scrollable preset list only
                            viewport:
                                draggable True
                                mousewheel True
                                scrollbars "vertical"
                                ysize _plist_h
                                vbox:
                                    spacing 4
                                    $ _names = lighting_get_names_for_current_group()
                                    $ _idx = int(getattr(store, 'current_light_preset_index', -1))
                                    $ _q = lighting_preset_filter.strip().lower()
                                    if _q:
                                        $ _names = [n for n in _names if _q in str(n).lower()]
                                    if not _names:
                                        text "(no presets)" size 12 color "#999999"
                                    for i, n in enumerate(_names):
                                        $ _is = (i == _idx)
                                        textbutton str(n):
                                            action Function(lighting_apply_preset, n)
                                            background (Solid("#3a3a3a") if _is else Solid("#242424"))
                                            hover_background Solid("#444444")
                                            text_color ("#ffffff" if _is else "#cccccc")
                                            padding (8,4)
                                # Toolbox moved to header; no duplicate here

                # Floating toolbox overlay removed to avoid duplicate controls.
                # The single toolbox now lives in the header under the title.

        # Edit overlays (draggables) removed from selector UI
