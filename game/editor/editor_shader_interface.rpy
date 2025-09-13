## Simplified Shader Editor (Working Version)
# Clean implementation of the F8 shader editor with debug output

# Basic editor UI variables (non-shader specific)
default editor_visible = False
default shader_preset_filename = "my_preset"
default editor_alpha = 0.85
default editor_width = 1100
default editor_height = 640

# Preset browsers: toggles and queries
default show_crt_list = False
default show_grain_list = False
default show_grade_list = False
default show_light_list = False
default show_all_list = False
default show_lighting_quickstart = False

default preset_search_crt = ""
default preset_search_grain = ""
default preset_search_grade = ""
default preset_search_light = ""
default preset_search_all = ""

init -2 python:
    import os
    def _preset_label_from_path(p):
        try:
            b = os.path.basename(p)
            if b.endswith('.yaml') or b.endswith('.yml'):
                return b.rsplit('.', 1)[0]
            elif b.endswith('.json'):
                return b[:-5]
            else:
                return b
        except Exception:
            return p

# Transform for window alpha
transform editor_window_alpha(a=0.85):
    alpha a

# Real shader functions connected to editor
init python:
    def _shader_editor_apply_crt():
        """Apply CRT settings using real shader functions"""
        try:
            # Use the actual set_crt_parameters function
            set_crt_parameters(
                warp=getattr(store, 'crt_warp', 0.2),
                scan=getattr(store, 'crt_scan', 0.5),
                chroma=getattr(store, 'crt_chroma', 0.9),
                scanline_size=getattr(store, 'crt_scanline_size', 1.0)
            )
        except Exception as e:
            print("[DEBUG] CRT apply error: " + str(e))
    
    def _shader_editor_apply_grain():
        """Apply film grain settings"""
        try:
            # Enable/disable film grain based on intensity
            intensity = getattr(store, 'film_grain_intensity', 0.02)
            store.film_grain_enabled = (intensity > 0.0)
            # Always restart interaction to apply size changes
            renpy.restart_interaction()
        except Exception as e:
            print("[DEBUG] Grain apply error: " + str(e))
    
    def _shader_editor_apply_grade():
        """Apply colour grading settings including vignette"""
        try:
            # Enable colour grading if any values are non-default
            brightness = getattr(store, 'shader_brightness', 0.0)
            contrast = getattr(store, 'shader_contrast', 1.0)
            saturation = getattr(store, 'color_saturation', 1.0)
            temperature = getattr(store, 'color_temperature', 0.0)
            tint = getattr(store, 'color_tint', 0.0)
            gamma = getattr(store, 'shader_gamma', 1.0)
            
            # Include new vignette variables in enabled detection
            vignette_strength = getattr(store, 'grade_vignette_strength', 0.0)
            vignette_width = getattr(store, 'grade_vignette_width', 0.25)
            vignette_feather = getattr(store, 'grade_vignette_feather', 1.0)
            
            enabled = (brightness != 0.0 or contrast != 1.0 or saturation != 1.0 or 
                      temperature != 0.0 or tint != 0.0 or gamma != 1.0 or 
                      vignette_strength != 0.0 or vignette_width != 0.25 or vignette_feather != 1.0)
            store.color_grading_enabled = enabled
            
            # Apply vignette when grading changes
            _grade_apply_vignette()
        except Exception as e:
            print("[DEBUG] Grading apply error: " + str(e))
    
    def _shader_editor_reset_grade():
        """Reset live grading adjustments to defaults including vignette"""
        try:
            store.shader_brightness = 0.0
            store.shader_contrast = 1.0
            store.color_saturation = 1.0
            store.color_temperature = 0.0
            store.color_tint = 0.0
            store.shader_gamma = 1.0
            
            # Reset new vignette variables
            store.grade_vignette_strength = 0.0
            store.grade_vignette_width = 0.25
            store.grade_vignette_feather = 1.0
            
            # Keep legacy variables for compatibility
            store.shader_vignette = 0.0
            store.shader_vignette_softness = 0.5
            
            store.color_grading_enabled = False
            _grade_apply_vignette()
        except Exception as e:
            print("[DEBUG] Grade reset error: " + str(e))
    
    def _shader_editor_toggle_crt():
        """Toggle CRT on/off using real function"""
        try:
            toggle_crt_effect()
        except Exception as e:
            print("[DEBUG] CRT toggle error: " + str(e))
    
    def _toggle_crt_aberr():
        """Checkbox-like toggle for aberration effect"""
        try:
            amt = float(getattr(store,'crt_aberr_amount', 0.0))
            mode = str(getattr(store,'crt_aberr_mode','none')).lower()
            if amt > 0.0 or mode != 'none':
                store.crt_aberr_amount = 0.0
                store.crt_aberr_mode = 'none'
            else:
                store.crt_aberr_amount = 0.1
                store.crt_aberr_mode = 'pulse'
            renpy.restart_interaction()
        except Exception as e:
            print("[DEBUG] Toggle aberration error: " + str(e))
    
    def _toggle_crt_glitch():
        """Checkbox-like toggle for glitch effect"""
        try:
            val = float(getattr(store,'crt_glitch', 0.0))
            store.crt_glitch = 0.0 if val > 0.0 else 0.1
            renpy.restart_interaction()
        except Exception as e:
            print("[DEBUG] Toggle glitch error: " + str(e))
    
    def _grade_apply_vignette():
        """Apply vignette settings using colour grading variables"""
        try:
            strength = getattr(store, 'grade_vignette_strength', 0.0)
            width = getattr(store, 'grade_vignette_width', 0.25)
            feather = getattr(store, 'grade_vignette_feather', 1.0)
            adjust_vignette(set_strength=strength, set_width=width)
            # Feather is read directly by the transform; set and refresh
            store.grade_vignette_feather = float(feather)
            renpy.restart_interaction()
        except Exception as e:
            print("[DEBUG] Vignette apply error: " + str(e))
    
    def _shader_editor_apply_vignette():
        """Compatibility wrapper for existing calls"""
        return _grade_apply_vignette()
    
    def _shader_editor_reset_crt():
        """Reset CRT to default values (vignette now handled by colour grading)"""
        try:
            # Reset to default values (no longer handling vignette)
            store.crt_warp = 0.2
            store.crt_scan = 0.5
            store.crt_chroma = 0.9
            store.crt_scanline_size = 1.0
            store.crt_anim_type = "none"
            store.crt_animated = False
            store.crt_aberr_amount = 0.0
            store.crt_aberr_speed = 1.0
            store.crt_glitch = 0.0
            store.crt_glitch_speed = 1.5
            store.crt_scanline_speed = 2.0
            store.crt_scanline_intensity = 0.1
            # Apply the reset values
            _shader_editor_apply_crt()
        except Exception as e:
            print("[DEBUG] CRT reset error: " + str(e))

screen unified_editor():
    # Check if editor should be shown
    if shader_editor_open:
        modal True
        zorder 1000

        # Close keys
        key "K_F8" action Function(toggle_shader_editor, False)
        key "K_ESCAPE" action Function(toggle_shader_editor, False)

        # Dark background
        add Solid("#00000088")

        # Main editor window
        frame at editor_window_alpha(editor_alpha):
            xalign 0.5
            yalign 0.5
            xsize editor_width
            ysize editor_height
            background Solid("#1e1e1e")
            padding (18, 14)

            vbox:
                spacing 10
                
                # Title bar
                hbox:
                    spacing 16
                    text "Shader Editor" size 28 color "#00ffaa"
                    text "(F8/ESC to close)" size 14 color "#bbbbbb"
                
                # Window controls
                hbox:
                    spacing 8
                    text "Window" size 14 color "#dddddd"
                    text "Alpha" size 12 color "#bbbbbb" yalign 0.5
                    bar value VariableValue("editor_alpha", 1.0, offset=0.0) xsize 180 changed Function(renpy.restart_interaction)
                    text ("%.2f" % editor_alpha) size 12 color "#aaaaaa" yalign 0.5

                # Tabs
                hbox:
                    spacing 8
                    $ _tabs = [
                        ("crt", "CRT"),
                        ("grain", "Film Grain"),
                        ("grade", "Colour Grading"),
                        ("lighting", "Lighting"),
                        ("presets", "Presets/IO"),
                    ]
                    for _id, _label in _tabs:
                        textbutton _label:
                            action SetVariable("shader_editor_tab", _id)
                            text_size 16
                            text_color ("#ffffff" if shader_editor_tab == _id else "#bbbbbb")
                            background (Solid("#3a3a3a") if shader_editor_tab == _id else Solid("#2a2a2a"))
                            hover_background Solid("#444444")
                            padding (10, 6)

                # Content area
                viewport:
                    id "editor_scroll"
                    draggable True
                    mousewheel True
                    scrollbars "vertical"
                    xfill True
                    yfill True

                    frame:
                        background Solid("#2a2a2a")
                        padding (20, 16)
                        xfill True
                        yfill True
                        yminimum 300

                        # Tab content
                    if shader_editor_tab == "crt":
                        vbox:
                            spacing 10
                            text "CRT Effects" size 20 color "#ffaa00"

                            # File menu (scrollable)
                            hbox:
                                spacing 8
                                textbutton "Open…":
                                    action ToggleVariable("show_crt_list")
                                    text_size 12
                                    background Solid("#3a3a3a")
                                    hover_background Solid("#444444")
                                    padding (8, 4)
                                text "Search" size 12 color "#bbbbbb" yalign 0.5
                                input value VariableInputValue("preset_search_crt") length 24 xsize 200
                                textbutton "Reload":
                                    action Function(renpy.restart_interaction)
                                    text_size 12
                                    background Solid("#3a3a3a")
                                    hover_background Solid("#444444")
                                    padding (8, 4)

                            if show_crt_list:
                                frame:
                                    background Solid("#242424")
                                    padding (10, 8)
                                    vbox:
                                        spacing 6
                                        text "Available files (shipped + custom)" size 12 color "#aaaaaa"
                                        frame:
                                            background Solid("#1f1f1f")
                                            padding (12, 10)
                                            ysize 180
                                            viewport:
                                                id "crt_list"
                                                draggable True
                                                mousewheel True
                                                scrollbars "vertical"
                                                xfill True
                                                vbox:
                                                    spacing 2
                                                    $ _files = shader_preset_list_effect("all", "crt")
                                                    $ _q = preset_search_crt.strip().lower()
                                                    for p in _files:
                                                        $ _name = _preset_label_from_path(p)
                                                        if (not _q) or (_q in _name.lower()):
                                                            textbutton _name:
                                                                action [Function(preset_load, p), SetVariable("show_crt_list", False)]
                                                                text_size 12
                                                                background Solid("#2a2a2a")
                                                                hover_background Solid("#3a3a3a")
                                                                padding (6, 3)

                            null height 8
                            text "Manual Controls" size 14 color "#dddddd"
                            
                            hbox:
                                spacing 10
                                text "CRT State:" size 12 color "#bbbbbb" yalign 0.5
                                textbutton ("On" if getattr(store, 'crt_enabled', False) else "Off"):
                                    action Function(_shader_editor_toggle_crt)
                                    text_size 12
                                    background Solid("#3a3a3a")
                                    hover_background Solid("#444444")
                                    padding (8, 4)
                            
                            hbox:
                                spacing 10
                                text "Warp:" size 11 color "#bbbbbb" yalign 0.5 xsize 80
                                bar value VariableValue("crt_warp", 0.5, offset=0.0) xsize 250 changed Function(_shader_editor_apply_crt)
                                text ("%.2f" % getattr(store,'crt_warp',0.2)) size 11 color "#aaaaaa" yalign 0.5
                            
                            hbox:
                                spacing 10
                                text "Scanlines:" size 11 color "#bbbbbb" yalign 0.5 xsize 80
                                bar value VariableValue("crt_scan", 1.0, offset=0.0) xsize 250 changed Function(_shader_editor_apply_crt)
                                text ("%.2f" % getattr(store,'crt_scan',0.5)) size 11 color "#aaaaaa" yalign 0.5
                            
                            
                            null height 6
                            text "CRT Effects" size 14 color "#dddddd"
                            $ _scan_on = bool(getattr(store,'crt_animated', False))
                            $ _ab_on = (float(getattr(store,'crt_aberr_amount', 0.0)) > 0.0) or (str(getattr(store,'crt_aberr_mode','none')).lower() != 'none')
                            $ _gl_on = (float(getattr(store,'crt_glitch', 0.0)) > 0.0)
                            vbox:
                                spacing 4
                                textbutton (u"%s Scanline" % (u"☑" if _scan_on else u"☐")):
                                    action [ToggleVariable("crt_animated"), Function(renpy.restart_interaction)]
                                    text_size 11
                                    background Solid("#2a2a2a")
                                    hover_background Solid("#3a3a3a")
                                    padding (6, 3)
                                textbutton (u"%s Aberration" % (u"☑" if _ab_on else u"☐")):
                                    action Function(_toggle_crt_aberr)
                                    text_size 11
                                    background Solid("#2a2a2a")
                                    hover_background Solid("#3a3a3a")
                                    padding (6, 3)
                                textbutton (u"%s Glitch" % (u"☑" if _gl_on else u"☐")):
                                    action Function(_toggle_crt_glitch)
                                    text_size 11
                                    background Solid("#2a2a2a")
                                    hover_background Solid("#3a3a3a")
                                    padding (6, 3)

                            if _scan_on:
                                hbox:
                                    spacing 10
                                    text "Scan Speed:" size 11 color "#bbbbbb" yalign 0.5 xsize 100
                                    bar value VariableValue("crt_scanline_speed", 5.0, offset=0.0) xsize 250 changed Function(renpy.restart_interaction)
                                    text ("%.2f" % getattr(store,'crt_scanline_speed',2.0)) size 11 color "#aaaaaa" yalign 0.5
                                hbox:
                                    spacing 10
                                    text "Scan Amount:" size 11 color "#bbbbbb" yalign 0.5 xsize 100
                                    bar value VariableValue("crt_scanline_intensity", 0.5, offset=0.0) xsize 250 changed Function(renpy.restart_interaction)
                                    text ("%.2f" % getattr(store,'crt_scanline_intensity',0.1)) size 11 color "#aaaaaa" yalign 0.5
                            if _ab_on:
                                hbox:
                                    spacing 10
                                    text "Aberr Speed:" size 11 color "#bbbbbb" yalign 0.5 xsize 100
                                    bar value VariableValue("crt_aberr_speed", 4.0, offset=0.0) xsize 250 changed Function(renpy.restart_interaction)
                                    text ("%.2f" % getattr(store,'crt_aberr_speed',1.0)) size 11 color "#aaaaaa" yalign 0.5
                                hbox:
                                    spacing 10
                                    text "Aberr Amount:" size 11 color "#bbbbbb" yalign 0.5 xsize 100
                                    bar value VariableValue("crt_aberr_amount", 1.0, offset=0.0) xsize 250 changed Function(renpy.restart_interaction)
                                    text ("%.2f" % getattr(store,'crt_aberr_amount',0.0)) size 11 color "#aaaaaa" yalign 0.5
                                hbox:
                                    spacing 10
                                    text "R Scale:" size 11 color "#bbbbbb" yalign 0.5 xsize 100
                                    bar value VariableValue("crt_aberr_r", 2.0, offset=0.0) xsize 250 changed Function(renpy.restart_interaction)
                                    text ("%.2f" % getattr(store,'crt_aberr_r',1.0)) size 11 color "#aaaaaa" yalign 0.5
                                hbox:
                                    spacing 10
                                    text "G Scale:" size 11 color "#bbbbbb" yalign 0.5 xsize 100
                                    bar value VariableValue("crt_aberr_g", 2.0, offset=0.0) xsize 250 changed Function(renpy.restart_interaction)
                                    text ("%.2f" % getattr(store,'crt_aberr_g',0.0)) size 11 color "#aaaaaa" yalign 0.5
                                hbox:
                                    spacing 10
                                    text "B Scale:" size 11 color "#bbbbbb" yalign 0.5 xsize 100
                                    bar value VariableValue("crt_aberr_b", 2.0, offset=0.0) xsize 250 changed Function(renpy.restart_interaction)
                                    text ("%.2f" % getattr(store,'crt_aberr_b',1.0)) size 11 color "#aaaaaa" yalign 0.5
                            if _gl_on:
                                hbox:
                                    spacing 10
                                    text "Glitch Speed:" size 11 color "#bbbbbb" yalign 0.5 xsize 100
                                    bar value VariableValue("crt_glitch_speed", 4.0, offset=0.0) xsize 250 changed Function(renpy.restart_interaction)
                                    text ("%.2f" % getattr(store,'crt_glitch_speed',1.5)) size 11 color "#aaaaaa" yalign 0.5
                                hbox:
                                    spacing 10
                                    text "Glitch Amount:" size 11 color "#bbbbbb" yalign 0.5 xsize 100
                                    bar value VariableValue("crt_glitch", 1.0, offset=0.0) xsize 250 changed Function(renpy.restart_interaction)
                                    text ("%.2f" % getattr(store,'crt_glitch',0.0)) size 11 color "#aaaaaa" yalign 0.5
                            
                            hbox:
                                spacing 10
                                textbutton "Reset CRT":
                                    action Function(_shader_editor_reset_crt)
                                    text_size 11
                                    background Solid("#aa3333")
                                    hover_background Solid("#cc4444")
                                    padding (6, 4)

                    elif shader_editor_tab == "grain":
                        vbox:
                            spacing 10
                            text "Film Grain Effects" size 20 color "#ffaa00"

                            # File menu (scrollable)
                            hbox:
                                spacing 8
                                textbutton "Open…":
                                    action ToggleVariable("show_grain_list")
                                    text_size 12
                                    background Solid("#3a3a3a")
                                    hover_background Solid("#444444")
                                    padding (8, 4)
                                text "Search" size 12 color "#bbbbbb" yalign 0.5
                                input value VariableInputValue("preset_search_grain") length 24 xsize 200
                                textbutton "Reload":
                                    action Function(renpy.restart_interaction)
                                    text_size 12
                                    background Solid("#3a3a3a")
                                    hover_background Solid("#444444")
                                    padding (8, 4)

                            if show_grain_list:
                                frame:
                                    background Solid("#242424")
                                    padding (10, 8)
                                    vbox:
                                        spacing 6
                                        text "Available files (shipped + custom)" size 12 color "#aaaaaa"
                                        frame:
                                            background Solid("#1f1f1f")
                                            padding (12, 10)
                                            ysize 180
                                            viewport:
                                                id "grain_list"
                                                draggable True
                                                mousewheel True
                                                scrollbars "vertical"
                                                xfill True
                                                vbox:
                                                    spacing 2
                                                    $ _files = shader_preset_list_effect("all", "grain")
                                                    $ _q = preset_search_grain.strip().lower()
                                                    for p in _files:
                                                        $ _name = _preset_label_from_path(p)
                                                        if (not _q) or (_q in _name.lower()):
                                                            textbutton _name:
                                                                action [Function(preset_load, p), SetVariable("show_grain_list", False)]
                                                                text_size 12
                                                                background Solid("#2a2a2a")
                                                                hover_background Solid("#3a3a3a")
                                                                padding (6, 3)

                            null height 8
                            text "Manual Controls" size 14 color "#dddddd"
                            
                            hbox:
                                spacing 10
                                text "Intensity:" size 11 color "#bbbbbb" yalign 0.5 xsize 80
                                bar value VariableValue("film_grain_intensity", 0.1, offset=0.0) xsize 250 changed Function(_shader_editor_apply_grain)
                                text ("%.3f" % getattr(store,'film_grain_intensity',0.02)) size 11 color "#aaaaaa" yalign 0.5
                            
                            hbox:
                                spacing 10
                                text "Size Factor:" size 11 color "#bbbbbb" yalign 0.5 xsize 80
                                bar value VariableValue("film_grain_size", 2.0, offset=0.5) xsize 250 changed Function(_shader_editor_apply_grain)
                                text ("%.2f" % getattr(store,'film_grain_size',1.0)) size 11 color "#aaaaaa" yalign 0.5
                            
                            hbox:
                                spacing 10
                                text "Downscale:" size 11 color "#bbbbbb" yalign 0.5 xsize 80
                                bar value VariableValue("film_grain_downscale", 4.0, offset=1.0) xsize 250 changed Function(_shader_editor_apply_grain)
                                text ("%.2f" % getattr(store,'film_grain_downscale',2.0)) size 11 color "#aaaaaa" yalign 0.5
                            
                            hbox:
                                spacing 10
                                textbutton "Reset Grain":
                                    action Function(set_grain, "off")
                                    text_size 11
                                    background Solid("#aa3333")
                                    hover_background Solid("#cc4444")
                                    padding (6, 4)

                    elif shader_editor_tab == "grade":
                        vbox:
                            spacing 10
                            text "Colour Grading" size 20 color "#ffaa00"

                            # File menu (scrollable)
                            hbox:
                                spacing 8
                                textbutton "Open…":
                                    action ToggleVariable("show_grade_list")
                                    text_size 12
                                    background Solid("#3a3a3a")
                                    hover_background Solid("#444444")
                                    padding (8, 4)
                                text "Search" size 12 color "#bbbbbb" yalign 0.5
                                input value VariableInputValue("preset_search_grade") length 24 xsize 200
                                textbutton "Reload":
                                    action Function(renpy.restart_interaction)
                                    text_size 12
                                    background Solid("#3a3a3a")
                                    hover_background Solid("#444444")
                                    padding (8, 4)

                            if show_grade_list:
                                frame:
                                    background Solid("#242424")
                                    padding (10, 8)
                                    vbox:
                                        spacing 6
                                        text "Available files (shipped + custom)" size 12 color "#aaaaaa"
                                        frame:
                                            background Solid("#1f1f1f")
                                            padding (12, 10)
                                            ysize 180
                                            viewport:
                                                id "grade_list"
                                                draggable True
                                                mousewheel True
                                                scrollbars "vertical"
                                                xfill True
                                                vbox:
                                                    spacing 2
                                                    $ _files = shader_preset_list_effect("all", "color_grade")
                                                    $ _q = preset_search_grade.strip().lower()
                                                    for p in _files:
                                                        $ _name = _preset_label_from_path(p)
                                                        if (not _q) or (_q in _name.lower()):
                                                            textbutton _name:
                                                                action [Function(preset_load, p), SetVariable("show_grade_list", False)]
                                                                text_size 12
                                                                background Solid("#2a2a2a")
                                                                hover_background Solid("#3a3a3a")
                                                                padding (6, 3)

                            null height 8
                            text "Live Controls" size 14 color "#dddddd"
                            
                            hbox:
                                spacing 10
                                text "Brightness:" size 11 color "#bbbbbb" yalign 0.5 xsize 80
                                bar value VariableValue("shader_brightness", 1.0, offset=-0.5) xsize 250 changed Function(_shader_editor_apply_grade)
                                text ("%.2f" % getattr(store,'shader_brightness',0.0)) size 11 color "#aaaaaa" yalign 0.5
                            
                            hbox:
                                spacing 10
                                text "Contrast:" size 11 color "#bbbbbb" yalign 0.5 xsize 80
                                bar value VariableValue("shader_contrast", 2.0, offset=0.0) xsize 250 changed Function(_shader_editor_apply_grade)
                                text ("%.2f" % getattr(store,'shader_contrast',1.0)) size 11 color "#aaaaaa" yalign 0.5
                            
                            hbox:
                                spacing 10
                                text "Saturation:" size 11 color "#bbbbbb" yalign 0.5 xsize 80
                                bar value VariableValue("color_saturation", 2.0, offset=0.0) xsize 250 changed Function(_shader_editor_apply_grade)
                                text ("%.2f" % getattr(store,'color_saturation',1.0)) size 11 color "#aaaaaa" yalign 0.5
                            
                            hbox:
                                spacing 10
                                text "Temperature:" size 11 color "#bbbbbb" yalign 0.5 xsize 80
                                bar value VariableValue("color_temperature", 2.0, offset=-1.0) xsize 250 changed Function(_shader_editor_apply_grade)
                                text ("%.2f" % getattr(store,'color_temperature',0.0)) size 11 color "#aaaaaa" yalign 0.5
                            
                            hbox:
                                spacing 10
                                text "Tint:" size 11 color "#bbbbbb" yalign 0.5 xsize 80
                                bar value VariableValue("color_tint", 2.0, offset=-1.0) xsize 250 changed Function(_shader_editor_apply_grade)
                                text ("%.2f" % getattr(store,'color_tint',0.0)) size 11 color "#aaaaaa" yalign 0.5
                            
                            hbox:
                                spacing 10
                                text "Gamma:" size 11 color "#bbbbbb" yalign 0.5 xsize 80
                                bar value VariableValue("shader_gamma", 1.5, offset=0.5) xsize 250 changed Function(_shader_editor_apply_grade)
                                text ("%.2f" % getattr(store,'shader_gamma',1.0)) size 11 color "#aaaaaa" yalign 0.5
                            
                            
                            null height 8
                            text "Vignette" size 14 color "#dddddd"
                            
                            hbox:
                                spacing 10
                                text "Strength:" size 11 color "#bbbbbb" yalign 0.5 xsize 80
                                bar value VariableValue("grade_vignette_strength", 1.0, offset=0.0) xsize 250 changed Function(_grade_apply_vignette)
                                text ("%.2f" % getattr(store,'grade_vignette_strength',0.0)) size 11 color "#aaaaaa" yalign 0.5
                            
                            hbox:
                                spacing 10
                                text "Width:" size 11 color "#bbbbbb" yalign 0.5 xsize 80
                                bar value VariableValue("grade_vignette_width", 0.5, offset=0.05) xsize 250 changed Function(_grade_apply_vignette)
                                text ("%.2f" % getattr(store,'grade_vignette_width',0.25)) size 11 color "#aaaaaa" yalign 0.5
                            
                            hbox:
                                spacing 10
                                text "Feather:" size 11 color "#bbbbbb" yalign 0.5 xsize 80
                                bar value VariableValue("grade_vignette_feather", 3.0, offset=0.5) xsize 250 changed Function(_grade_apply_vignette)
                                text ("%.2f" % getattr(store,'grade_vignette_feather',1.0)) size 11 color "#aaaaaa" yalign 0.5
                            
                            hbox:
                                spacing 10
                                textbutton "Reset Live Grading":
                                    action Function(_shader_editor_reset_grade)
                                    text_size 11
                                    background Solid("#aa3333")
                                    hover_background Solid("#cc4444")
                                    padding (6, 4)


                    elif shader_editor_tab == "presets":
                        vbox:
                            spacing 15
                            text "Presets & I/O" size 20 color "#ffaa00"
                            
                            # Lighting Integration
                            frame:
                                background Solid("#2c2c2c")
                                padding (12, 10)
                                vbox:
                                    spacing 8
                                    text "Lighting (YAML light_*.yaml)" size 14 color "#dddddd"
                                    hbox:
                                        spacing 8
                                        text "Group:" size 12 color "#bbbbbb" yalign 0.5
                                        $ _g = lighting_current_group_name() if 'lighting_current_group_name' in globals() else 'All'
                                        text (str(_g)) size 12 color "#a8ffd9" yalign 0.5
                                        textbutton "Prev Group":
                                            action Function(cycle_light_groups, -1)
                                            text_size 12
                                            background Solid("#3a3a3a")
                                            hover_background Solid("#444444")
                                            padding (8, 4)
                                        textbutton "Next Group":
                                            action Function(cycle_light_groups, 1)
                                            text_size 12
                                            background Solid("#3a3a3a")
                                            hover_background Solid("#444444")
                                            padding (8, 4)
                                        textbutton "All":
                                            action Function(lighting_set_group, None)
                                            text_size 12
                                            background Solid("#3a3a3a")
                                            hover_background Solid("#444444")
                                            padding (8, 4)
                                        textbutton "Reload":
                                            action Function(lighting_refresh_cache)
                                            text_size 12
                                            background Solid("#3a3a3a")
                                            hover_background Solid("#444444")
                                            padding (8, 4)
                                    null height 6
                                    frame:
                                        background Solid("#242424")
                                        padding (8, 8)
                                        vbox:
                                            spacing 6
                                            $ _names = lighting_get_names_for_current_group() if 'lighting_get_names_for_current_group' in globals() else []
                                            if not _names:
                                                text "No lighting presets found." size 12 color "#aaaaaa"
                                            else:
                                                viewport:
                                                    draggable True
                                                    mousewheel True
                                                    scrollbars "vertical"
                                                    ysize 220
                                                    vbox:
                                                        spacing 2
                                                        for n in _names:
                                                            textbutton str(n):
                                                                action Function(lighting_apply_preset, n)
                                                                text_size 12
                                                                background Solid("#2a2a2a")
                                                                hover_background Solid("#3a3a3a")
                                                                padding (6, 4)
                            
                            hbox:
                                spacing 10
                                text "Save Current Settings:" size 14 color "#dddddd" yalign 0.5
                            
                            hbox:
                                spacing 10
                                text "Filename:" size 12 color "#bbbbbb" yalign 0.5
                                input value VariableInputValue("shader_preset_filename") xsize 200
                                text ".yaml" size 12 color "#999999" yalign 0.5
                                textbutton "Save":
                                    action Function(preset_save, "yaml/shaders/custom/" + shader_preset_filename + ".yaml")
                                    text_size 12
                                    background Solid("#3a3a3a")
                                    hover_background Solid("#444444")
                                    padding (8, 4)
                            
                            null height 15
                            text "Open preset file" size 14 color "#dddddd"

                            hbox:
                                spacing 8
                                textbutton "Open…":
                                    action ToggleVariable("show_all_list")
                                    text_size 12
                                    background Solid("#3a3a3a")
                                    hover_background Solid("#444444")
                                    padding (8, 4)
                                text "Search" size 12 color "#bbbbbb" yalign 0.5
                                input value VariableInputValue("preset_search_all") length 24 xsize 200
                                textbutton "Reload":
                                    action Function(renpy.restart_interaction)
                                    text_size 12
                                    background Solid("#3a3a3a")
                                    hover_background Solid("#444444")
                                    padding (8, 4)

                            if show_all_list:
                                frame:
                                    background Solid("#242424")
                                    padding (10, 8)
                                    vbox:
                                        spacing 6
                                        text "All available preset files" size 12 color "#aaaaaa"
                                        frame:
                                            background Solid("#1f1f1f")
                                            padding (12, 10)
                                            ysize 220
                                            viewport:
                                                id "all_list"
                                                draggable True
                                                mousewheel True
                                                scrollbars "vertical"
                                                xfill True
                                                vbox:
                                                    spacing 2
                                                    $ _files = shader_preset_list("all")
                                                    $ _q = preset_search_all.strip().lower()
                                                    for p in _files:
                                                        $ _name = _preset_label_from_path(p)
                                                        if (not _q) or (_q in _name.lower()):
                                                            textbutton _name:
                                                                action [Function(preset_load, p), SetVariable("show_all_list", False)]
                                                                text_size 12
                                                                background Solid("#2a2a2a")
                                                                hover_background Solid("#3a3a3a")
                                                                padding (6, 3)
                            
                            null height 10
                            text "Directory Info:" size 12 color "#bbbbbb"
                            text "• Shipped: yaml/shaders/preset/" size 11 color "#888888"
                            text "• Custom: yaml/shaders/custom/" size 11 color "#888888"
                            
                            text "✓ Basic preset save/load functionality!" size 14 color "#00ff00"

                    elif shader_editor_tab == "lighting":
                        vbox:
                            spacing 10
                            text "Lighting" size 20 color "#ffaa00"
                            text "Open the dedicated Lighting Editor for multi-light editing, animations, and bloom." size 12 color "#bbbbbb"
                            hbox:
                                spacing 10
                                textbutton "Open Lighting Editor":
                                    action Function(open_lighting_editor_from_shader)
                                    text_size 12
                                    background Solid("#3a3a3a")
                                    hover_background Solid("#444444")
                                    padding (8, 4)
                                textbutton "Open Lighting Selector (Ctrl+F8)":
                                    action [ToggleVariable("lighting_selector_open"), Function(toggle_shader_editor, False)]
                                    text_size 12
                                    background Solid("#3a3a3a")
                                    hover_background Solid("#444444")
                                    padding (8, 4)
                                textbutton "Save Lighting…":
                                    action [Function(toggle_shader_editor, False), ToggleVariable("lighting_selector_open"), Function(show_shader_notification, "Use header 'Save As' to save lighting YAML")]
                                    text_size 12
                                    background Solid("#3a3a3a")
                                    hover_background Solid("#444444")
                                    padding (8, 4)
                                textbutton ("Quickstart Tips" if not show_lighting_quickstart else "Hide Tips"):
                                    action ToggleVariable("show_lighting_quickstart")
                                    text_size 12
                                    background Solid("#3a3a3a")
                                    hover_background Solid("#444444")
                                    padding (8, 4)
                            null height 10
                            text "Quick Bloom Controls" size 14 color "#dddddd"
                            hbox:
                                spacing 10
                                text "Bloom" size 12 color "#bbbbbb" yalign 0.5
                                textbutton ("ON" if getattr(store,'bloom_enabled', False) else "OFF"):
                                    action (Function(bloom_off) if getattr(store,'bloom_enabled', False) else Function(bloom_on))
                                    text_size 12
                                    background Solid("#3a3a3a")
                                    hover_background Solid("#444444")
                                    padding (8, 4)
                            hbox:
                                spacing 10
                                text "Threshold" size 11 color "#bbbbbb" yalign 0.5 xsize 90
                                bar value VariableValue("bloom_threshold", 1.0, offset=0.0) xsize 260 changed Function(renpy.restart_interaction)
                                text ("%.2f" % float(getattr(store,'bloom_threshold',0.75))) size 11 color "#aaaaaa" yalign 0.5
                            hbox:
                                spacing 10
                                text "Strength" size 11 color "#bbbbbb" yalign 0.5 xsize 90
                                bar value VariableValue("bloom_strength", 2.0, offset=0.0) xsize 260 changed Function(renpy.restart_interaction)
                                text ("%.2f" % float(getattr(store,'bloom_strength',0.6))) size 11 color "#aaaaaa" yalign 0.5
                            hbox:
                                spacing 10
                                text "Radius" size 11 color "#bbbbbb" yalign 0.5 xsize 90
                                bar value VariableValue("bloom_radius", 8.0, offset=0.0) xsize 260 changed Function(renpy.restart_interaction)
                                text ("%.2f" % float(getattr(store,'bloom_radius',2.5))) size 11 color "#aaaaaa" yalign 0.5
                            if show_lighting_quickstart:
                                null height 6
                                frame:
                                    background Solid("#2a2a2a")
                                    padding (10,8)
                                    vbox:
                                        spacing 6
                                        text "Lighting Editor Quickstart" size 14 color "#dddddd"
                                        text "• Ctrl+F8: browse presets; Ctrl+Shift+F8: edit lights." size 11 color "#bbbbbb"
                                        text "• Drag square to move; small dot to aim (spot/dir)." size 11 color "#bbbbbb"
                                        text "• Falloff: smooth/linear/quadratic/inv-square/custom." size 11 color "#bbbbbb"
                                        text "• Animations: flicker (noise), pulse (sin), sweep (scan)." size 11 color "#bbbbbb"
                                        text "• Bloom: enable and tune threshold/strength/radius." size 11 color "#bbbbbb"
                                        if config.developer:
                                            hbox:
                                                spacing 8
                                                textbutton "Open Full Quickstart (Editor)":
                                                    action Function(renpy.open_file_in_editor, "docs/LIGHTING_EDITOR_QUICKSTART.md")
                                                    text_size 12
                                                    background Solid("#3a3a3a")
                                                    hover_background Solid("#444444")
                                                    padding (8, 4)
                            null height 6
                            text "The Selector is for preset browsing. Editing happens in the Lighting Editor." size 11 color "#999999"
                    else:
                        vbox:
                            spacing 15
                            text "Unknown Tab" size 20 color "#ff0000"
                            text ("Current tab: " + str(shader_editor_tab)) size 14 color "#bbbbbb"
