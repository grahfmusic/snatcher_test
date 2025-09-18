# Lighting Editor (Full-Screen Overlay)
# - Opens from Ctrl+F8 Lighting Selector ("Edit Lights…") or from F8 Shader Editor (Lighting tab → Open Lighting Editor)
# - Owns its modal window, blocks room UI, and is mutually exclusive with other editors.

default lighting_editor_alpha = 0.92
default lighting_editor_show_handles = True
default lighting_editor_selected = -1
default lighting_editor_r = 1.0
default lighting_editor_g = 1.0
default lighting_editor_b = 1.0
default lighting_editor_falloff = "smooth"
default lighting_editor_fexp = 1.0
default lighting_editor_temp_intensity = 1.0
default lighting_editor_temp_radius = 0.3
default lighting_editor_temp_angle = 0.7
default lighting_editor_compact = False

style lighting_editor_default is default:
    font "fonts/MapleMono-Regular.ttf"
    size 11

style lighting_editor_text is lighting_editor_default
style lighting_editor_textbutton is textbutton:
    font "fonts/MapleMono-Regular.ttf"

style lighting_editor_textbutton_text is lighting_editor_default
style lighting_editor_small_text is lighting_editor_default:
    size 10
style lighting_editor_title_text is lighting_editor_default:
    font "fonts/MapleMono-Bold.ttf"
    size 12

init -5 python:
    import time

    if not hasattr(store, '_lighting_editor_next_restart'):
        store._lighting_editor_next_restart = 0.0

    def _lighting_editor_queue_restart(cooldown=0.12):
        now = time.time()
        next_allowed = getattr(store, '_lighting_editor_next_restart', 0.0)
        if now >= next_allowed:
            store._lighting_editor_next_restart = now + cooldown
            renpy.restart_interaction()
        return True

    def open_lighting_editor():
        try:
            # Close other editor UIs
            if hasattr(store, 'shader_editor_open') and store.shader_editor_open:
                store.shader_editor_open = False
                try:
                    renpy.hide_screen("unified_editor")
                except Exception:
                    pass
            if hasattr(store, 'editor_visible') and store.editor_visible:
                store.editor_visible = False
            if hasattr(store, 'lighting_selector_open') and store.lighting_selector_open:
                store.lighting_selector_open = False
            # Open lighting editor
            store.lighting_editor_open = True
            if not hasattr(store, 'dynamic_lights') or store.dynamic_lights is None:
                store.dynamic_lights = []
            if 'lighting_sync_uniforms' in globals():
                try:
                    lighting_sync_uniforms()
                except Exception:
                    pass
            # Ensure screen is visible immediately
            try:
                renpy.show_screen("lighting_editor")
                show_shader_notification("Lighting Editor opened")
            except Exception:
                pass
            renpy.restart_interaction()
            return True
        except Exception:
            return False

    def close_lighting_editor():
        try:
            store.lighting_editor_open = False
            try:
                renpy.hide_screen("lighting_editor")
            except Exception:
                pass
            return True
        except Exception:
            return False

    def open_lighting_editor_from_selector():
        try:
            store.lighting_selector_open = False
        except Exception:
            pass
        return open_lighting_editor()

    def _lighting_editor_toggle_bloom():
        try:
            if getattr(store, 'bloom_enabled', False):
                return bloom_off()
            return bloom_on(
                threshold=float(getattr(store, 'bloom_threshold', 0.75)),
                strength=float(getattr(store, 'bloom_strength', 0.6)),
                radius=float(getattr(store, 'bloom_radius', 2.5)),
            )
        except Exception:
            return False

    def _lighting_editor_apply_bloom():
        try:
            if getattr(store, 'bloom_enabled', False):
                bloom_on(
                    threshold=float(getattr(store, 'bloom_threshold', 0.75)),
                    strength=float(getattr(store, 'bloom_strength', 0.6)),
                    radius=float(getattr(store, 'bloom_radius', 2.5)),
                )
            return True
        except Exception:
            return False

    def lighting_editor_apply_color(idx=None):
        try:
            i = int(idx if idx is not None else getattr(store, 'lighting_editor_selected', -1))
            if i < 0:
                return False
            r = float(getattr(store, 'lighting_editor_r', 1.0))
            g = float(getattr(store, 'lighting_editor_g', 1.0))
            b = float(getattr(store, 'lighting_editor_b', 1.0))
            if 'lighting_set_color' in globals():
                lighting_set_color(i, r, g, b)
                return True
        except Exception:
            pass
        return False

    def lighting_editor_select_index(idx):
        """Select light index and prime editor UI variables safely (handles legacy keys)."""
        try:
            i = int(idx)
            dl = list(getattr(store, 'dynamic_lights', []) or [])
            if i < 0 or i >= len(dl):
                return False
            e = dl[i]
            store.lighting_editor_selected = i
            # Color
            col = e.get('color', (1.0,1.0,1.0))
            try:
                store.lighting_editor_r = float(col[0])
                store.lighting_editor_g = float(col[1])
                store.lighting_editor_b = float(col[2])
            except Exception:
                store.lighting_editor_r = 1.0; store.lighting_editor_g = 1.0; store.lighting_editor_b = 1.0
            # Falloff
            store.lighting_editor_falloff = str(e.get('falloff', 'smooth'))
            try:
                store.lighting_editor_fexp = float(e.get('falloff_exp', 1.0))
            except Exception:
                store.lighting_editor_fexp = 1.0
            # Temp sliders
            try:
                store.lighting_editor_temp_intensity = float(e.get('intensity', 1.0))
            except Exception:
                store.lighting_editor_temp_intensity = 1.0
            try:
                store.lighting_editor_temp_radius = float(e.get('radius', 0.3))
            except Exception:
                store.lighting_editor_temp_radius = 0.3
            try:
                store.lighting_editor_temp_angle = float(e.get('angle', 0.7))
            except Exception:
                store.lighting_editor_temp_angle = 0.7
            # Animation (support 'animation' dict or 'anim' dict or string)
            anim = e.get('animation')
            if isinstance(anim, dict):
                a = anim
            elif isinstance(anim, str):
                a = {'mode': anim}
            else:
                a = e.get('anim') if isinstance(e.get('anim'), dict) else {}
            store.lighting_editor_anim_mode = str(a.get('mode', 'none'))
            store.lighting_editor_anim_min = float(a.get('min', 0.7)) if 'min' in a else getattr(store, 'lighting_editor_anim_min', 0.7)
            store.lighting_editor_anim_max = float(a.get('max', 1.2)) if 'max' in a else getattr(store, 'lighting_editor_anim_max', 1.2)
            store.lighting_editor_anim_speed = float(a.get('speed_hz', a.get('speed', 8.0))) if a else getattr(store, 'lighting_editor_anim_speed', 8.0)
            store.lighting_editor_anim_seed = int(a.get('seed', 0)) if 'seed' in a else getattr(store, 'lighting_editor_anim_seed', 0)
            store.lighting_editor_anim_base = float(a.get('base', 1.0)) if 'base' in a else getattr(store, 'lighting_editor_anim_base', 1.0)
            store.lighting_editor_anim_amp = float(a.get('amplitude', 0.5)) if 'amplitude' in a else getattr(store, 'lighting_editor_anim_amp', 0.5)
            store.lighting_editor_anim_period = float(a.get('period_s', a.get('period', 2.0))) if a else getattr(store, 'lighting_editor_anim_period', 2.0)
            store.lighting_editor_anim_phase = float(a.get('phase', 0.0)) if 'phase' in a else getattr(store, 'lighting_editor_anim_phase', 0.0)
            store.lighting_editor_anim_start_deg = float(a.get('start_angle', 0.0)) if 'start_angle' in a else getattr(store, 'lighting_editor_anim_start_deg', 0.0)
            store.lighting_editor_anim_end_deg = float(a.get('end_angle', 90.0)) if 'end_angle' in a else getattr(store, 'lighting_editor_anim_end_deg', 90.0)
            store.lighting_editor_anim_ang_speed = float(a.get('angular_speed', 1.0)) if 'angular_speed' in a else getattr(store, 'lighting_editor_anim_ang_speed', 1.0)
            store.lighting_editor_anim_loop = str(a.get('loop', 'wrap')) if 'loop' in a else getattr(store, 'lighting_editor_anim_loop', 'wrap')
            renpy.restart_interaction()
            return True
        except Exception:
            return False

    def open_lighting_editor_from_shader():
        try:
            if hasattr(store, 'shader_editor_open') and store.shader_editor_open:
                store.shader_editor_open = False
            try:
                renpy.hide_screen("unified_editor")
            except Exception:
                pass
        except Exception:
            pass
        return open_lighting_editor()

# Child screen: clean, nested properties panel
screen lighting_editor_props(i, sp=8):
    $ e = store.dynamic_lights[i]
    vbox:
        spacing sp
        hbox:
            spacing 8
            text "Type" size 12 color "#cccccc" yalign 0.5
            textbutton "Point":
                action [Function(lighting_set_kind, i, 'point'), Function(lighting_sync_uniforms)]
            textbutton "Spot":
                action [Function(lighting_set_kind, i, 'spot'), Function(lighting_sync_uniforms)]
            textbutton "Dir":
                action [Function(lighting_set_kind, i, 'directional'), Function(lighting_sync_uniforms)]
        hbox:
            spacing 8
            text "Layer" size 12 color "#cccccc" yalign 0.5
            textbutton "Back":
                action Function(lighting_set_layer, i, 'back')
            textbutton "Front":
                action Function(lighting_set_layer, i, 'front')
            textbutton "All":
                action Function(lighting_set_layer, i, 'all')
        hbox:
            spacing 8
            text "Intensity" size 12 color "#cccccc" yalign 0.5 xsize 90
            bar value VariableValue("lighting_editor_temp_intensity", 5.0, offset=0.0) xsize 220 changed [Function(lighting_set_intensity, i, lighting_editor_temp_intensity), Function(lighting_sync_uniforms)]
        hbox:
            spacing 8
            text "Radius" size 12 color "#cccccc" yalign 0.5 xsize 90
            bar value VariableValue("lighting_editor_temp_radius", 1.5, offset=0.0) xsize 220 changed [Function(lighting_set_radius, i, lighting_editor_temp_radius), Function(lighting_sync_uniforms)]
        if str(e.get('kind','point')) in ('spot','directional'):
            hbox:
                spacing 8
                text "Angle" size 12 color "#cccccc" yalign 0.5 xsize 90
                bar value VariableValue("lighting_editor_temp_angle", 1.57, offset=0.0) xsize 220 changed [Function(lighting_set_angle, i, lighting_editor_temp_angle), Function(lighting_sync_uniforms)]
        null height 6
        text "Color" size 12 color "#cccccc"
        hbox:
            spacing 8
            text "R" size 11 color "#ff8888" yalign 0.5 xsize 16
            bar value VariableValue("lighting_editor_r", 1.0, offset=0.0) xsize 240 changed Function(lighting_editor_apply_color, i)
        hbox:
            spacing 8
            text "G" size 11 color "#88ff88" yalign 0.5 xsize 16
            bar value VariableValue("lighting_editor_g", 1.0, offset=0.0) xsize 240 changed Function(lighting_editor_apply_color, i)
        hbox:
            spacing 8
            text "B" size 11 color "#8888ff" yalign 0.5 xsize 16
            bar value VariableValue("lighting_editor_b", 1.0, offset=0.0) xsize 240 changed Function(lighting_editor_apply_color, i)
        null height 6
        text "Falloff" size 12 color "#cccccc"
        hbox:
            spacing 6
            textbutton "Smooth":
                action [SetVariable("lighting_editor_falloff", "smooth"), Function(lighting_set_falloff, i, 'smooth')]
            textbutton "Linear":
                action [SetVariable("lighting_editor_falloff", "linear"), Function(lighting_set_falloff, i, 'linear')]
            textbutton "Quadratic":
                action [SetVariable("lighting_editor_falloff", "quadratic"), Function(lighting_set_falloff, i, 'quadratic')]
            textbutton "InvSq":
                action [SetVariable("lighting_editor_falloff", "inverse_square"), Function(lighting_set_falloff, i, 'inverse_square')]
            textbutton "Custom":
                action [SetVariable("lighting_editor_falloff", "custom"), Function(lighting_set_falloff, i, 'custom')]
        if lighting_editor_falloff == "custom":
            hbox:
                spacing 8
                text "Exponent" size 12 color "#cccccc" yalign 0.5 xsize 90
                bar value VariableValue("lighting_editor_fexp", 8.0, offset=0.05) xsize 220 changed Function(lighting_set_falloff_exp, i, lighting_editor_fexp)
        null height 8
        text "Bloom" size 12 color "#cccccc"
        hbox:
            spacing 8
            text "Enabled" size 11 color "#cccccc" yalign 0.5
            textbutton ("ON" if getattr(store,'bloom_enabled', False) else "OFF"):
                action Function(_lighting_editor_toggle_bloom)
        hbox:
            spacing 8
            text "Threshold" size 12 color "#cccccc" yalign 0.5 xsize 90
            bar value VariableValue("bloom_threshold", 1.0, offset=0.0) xsize 220 changed Function(_lighting_editor_apply_bloom)
        hbox:
            spacing 8
            text "Strength" size 12 color "#cccccc" yalign 0.5 xsize 90
            bar value VariableValue("bloom_strength", 2.0, offset=0.0) xsize 220 changed Function(_lighting_editor_apply_bloom)
        hbox:
            spacing 8
            text "Radius" size 12 color "#cccccc" yalign 0.5 xsize 90
            bar value VariableValue("bloom_radius", 8.0, offset=0.0) xsize 220 changed Function(_lighting_editor_apply_bloom)
        null height 8
        text "Animation" size 12 color "#cccccc"
        hbox:
            spacing 6
            text "Mode" size 12 color "#cccccc" yalign 0.5
            textbutton "None":
                action [SetVariable("lighting_editor_anim_mode","none"), Function(lighting_set_anim_mode, i, 'none')]
            textbutton "Flicker":
                action [SetVariable("lighting_editor_anim_mode","flicker"), Function(lighting_set_anim_mode, i, 'flicker')]
            textbutton "Pulse":
                action [SetVariable("lighting_editor_anim_mode","pulse"), Function(lighting_set_anim_mode, i, 'pulse')]
            textbutton "Sweep":
                action [SetVariable("lighting_editor_anim_mode","sweep"), Function(lighting_set_anim_mode, i, 'sweep')]
        if lighting_editor_anim_mode == 'flicker':
            hbox:
                spacing 8
                text "Min" size 12 color "#cccccc" yalign 0.5 xsize 60
                bar value VariableValue("lighting_editor_anim_min", 2.0, offset=0.0) xsize 220 changed Function(lighting_set_anim_field, i, 'min', lighting_editor_anim_min)
            hbox:
                spacing 8
                text "Max" size 12 color "#cccccc" yalign 0.5 xsize 60
                bar value VariableValue("lighting_editor_anim_max", 2.0, offset=0.0) xsize 220 changed Function(lighting_set_anim_field, i, 'max', lighting_editor_anim_max)
            hbox:
                spacing 8
                text "Speed Hz" size 12 color "#cccccc" yalign 0.5 xsize 60
                bar value VariableValue("lighting_editor_anim_speed", 20.0, offset=0.0) xsize 220 changed Function(lighting_set_anim_field, i, 'speed_hz', lighting_editor_anim_speed)
        elif lighting_editor_anim_mode == 'pulse':
            hbox:
                spacing 8
                text "Base" size 12 color "#cccccc" yalign 0.5 xsize 60
                bar value VariableValue("lighting_editor_anim_base", 2.0, offset=0.0) xsize 220 changed Function(lighting_set_anim_field, i, 'base', lighting_editor_anim_base)
            hbox:
                spacing 8
                text "Amplitude" size 12 color "#cccccc" yalign 0.5 xsize 60
                bar value VariableValue("lighting_editor_anim_amp", 2.0, offset=0.0) xsize 220 changed Function(lighting_set_anim_field, i, 'amplitude', lighting_editor_anim_amp)
            hbox:
                spacing 8
                text "Period s" size 12 color "#cccccc" yalign 0.5 xsize 60
                bar value VariableValue("lighting_editor_anim_period", 10.0, offset=0.0) xsize 220 changed Function(lighting_set_anim_field, i, 'period_s', lighting_editor_anim_period)
            hbox:
                spacing 8
                text "Phase" size 12 color "#cccccc" yalign 0.5 xsize 60
                bar value VariableValue("lighting_editor_anim_phase", 6.283, offset=-3.141) xsize 220 changed Function(lighting_set_anim_field, i, 'phase', lighting_editor_anim_phase)
        elif lighting_editor_anim_mode == 'sweep':
            hbox:
                spacing 8
                text "Start°" size 12 color "#cccccc" yalign 0.5 xsize 60
                bar value VariableValue("lighting_editor_anim_start_deg", 360.0, offset=0.0) xsize 220 changed Function(lighting_set_anim_field, i, 'start_angle', lighting_editor_anim_start_deg)
            hbox:
                spacing 8
                text "End°" size 12 color "#cccccc" yalign 0.5 xsize 60
                bar value VariableValue("lighting_editor_anim_end_deg", 360.0, offset=0.0) xsize 220 changed Function(lighting_set_anim_field, i, 'end_angle', lighting_editor_anim_end_deg)
            hbox:
                spacing 8
                text "Speed" size 12 color "#cccccc" yalign 0.5 xsize 60
                bar value VariableValue("lighting_editor_anim_ang_speed", 10.0, offset=0.0) xsize 220 changed Function(lighting_set_anim_field, i, 'angular_speed', lighting_editor_anim_ang_speed)
            hbox:
                spacing 8
                text "Loop" size 12 color "#cccccc" yalign 0.5 xsize 60
                textbutton ("Wrap" if lighting_editor_anim_loop != 'bounce' else "Bounce"):
                    action [SetVariable("lighting_editor_anim_loop", ('bounce' if lighting_editor_anim_loop!='bounce' else 'wrap')), Function(lighting_set_anim_field, i, 'loop', ('bounce' if lighting_editor_anim_loop!='bounce' else 'wrap'))]

# No overlay registration needed; `room_exploration` includes `use lighting_editor` when open

screen lighting_editor():
    if lighting_editor_open:
        style_prefix "lighting_editor"
        modal True
        zorder 2100

        # Close & hotkeys
        key "K_ESCAPE" action Function(close_lighting_editor)
        key "ctrl_K_F8" action [Function(close_lighting_editor), SetVariable("lighting_selector_open", True)]

        # Dimmed backdrop
        add Solid("#000000AA")

        # Window + responsive column sizes
        # Slightly widen the editor and make columns adaptable so the
        # right-side Properties panel never extends off-screen.
        $ _pad = (6 if lighting_editor_compact else 8)
        $ _sp = (6 if lighting_editor_compact else 8)
        $ _title_sz = (11 if lighting_editor_compact else 12)
        $ _fw = min(config.screen_width - 20, int(config.screen_width * 0.96))
        $ _fh = min(config.screen_height - 20, int(config.screen_height * 0.94))

        # Baseline column targets (clamped for readability)
        $ _left_w = (max(200, min(300, int(_fw * 0.20))) if lighting_editor_compact else max(240, min(340, int(_fw * 0.24))))
        $ _right_w = (max(260, min(360, int(_fw * 0.22))) if lighting_editor_compact else max(300, min(420, int(_fw * 0.26))))

        # Ensure total content fits inside the outer frame by shrinking
        # side columns if necessary (preferring to shrink the right first).
        $ _inner_w = _fw - 2*(_pad+8)
        $ _min_center = (280 if lighting_editor_compact else 360)
        $ _required = _left_w + _right_w + 2*_sp + _min_center
        if _required > _inner_w:
            $ _over = _required - _inner_w
            # Shrink right column down to a reasonable floor
            $ _right_floor = (260 if lighting_editor_compact else 300)
            $ _r_room = max(0, _right_w - _right_floor)
            if _r_room > 0:
                $ _sh = min(_over, _r_room)
                $ _right_w -= _sh
                $ _over -= _sh
            # Shrink left column if still overflowing
            if _over > 0:
                $ _left_floor = (200 if lighting_editor_compact else 240)
                $ _l_room = max(0, _left_w - _left_floor)
                if _l_room > 0:
                    $ _sh2 = min(_over, _l_room)
                    $ _left_w -= _sh2
                    $ _over -= _sh2
            # As a last resort, let the center area shrink
            if _over > 0:
                $ _min_center = max(200, _min_center - _over)

        frame:
            at editor_window_alpha(lighting_editor_alpha)
            background Solid("#151515")
            xalign 0.5
            yalign 0.5
            xsize _fw
            ysize _fh
            padding (_pad+8, _pad+4)

            vbox:
                spacing _sp

                # Header
                hbox:
                    spacing 12
                    xfill True
                    text "Lighting Editor" size _title_sz font "fonts/MapleMono-Bold.ttf" color "#e8e8e8" yalign 0.5
                    null width 16 xfill True
                    textbutton ("Compact: ON" if lighting_editor_compact else "Compact: OFF"):
                        action [ToggleVariable("lighting_editor_compact"), Function(_lighting_editor_queue_restart)]
                        background Solid("#333333")
                        hover_background Solid("#444444")
                        padding (6,4)
                    textbutton ("Handles: ON" if lighting_editor_show_handles else "Handles: OFF"):
                        action [ToggleVariable("lighting_editor_show_handles"), Function(_lighting_editor_queue_restart)]
                        background Solid("#333333")
                        hover_background Solid("#444444")
                        padding (6,4)
                    textbutton "Back to Selector":
                        action [Function(close_lighting_editor), SetVariable("lighting_selector_open", True)]
                        background Solid("#333333")
                        hover_background Solid("#444444")
                        padding (6,4)
                    textbutton "Close":
                        action Function(close_lighting_editor)
                        background Solid("#aa3333")
                        hover_background Solid("#cc4444")
                        padding (6,4)

                # Body: List | Canvas | Properties
                hbox:
                    spacing _sp
                    xfill True
                    yfill True

                    # Left: Lights list
                    frame:
                        background Solid("#1d1d1d")
                        xsize _left_w
                        yfill True
                        padding (_pad,_pad)
                        vbox:
                            spacing _sp
                            hbox:
                                spacing 6
                                text "Lights" size 12 font "fonts/MapleMono-Bold.ttf" color "#ffffff" yalign 0.5
                                null width 6
                                textbutton "+Add":
                                    action Function(lighting_add_light, 'point')
                                    text_size 12
                                    background Solid("#2f2f2f")
                                    hover_background Solid("#3f3f3f")
                                    padding (6,4)
                            viewport:
                                draggable True
                                mousewheel True
                                scrollbars "vertical"
                                yfill True
                                vbox:
                                    spacing 4
                                    $ _dl = list(getattr(store, 'dynamic_lights', []) or [])
                                    if not _dl:
                                        text "No active lights." size 12 color "#999999"
                                        textbutton "Add Point Light":
                                            action Function(lighting_add_light, 'point')
                                            text_size 11
                                            background Solid("#2f2f2f")
                                            hover_background Solid("#3f3f3f")
                                            padding (6,3)
                                        textbutton "Open Presets":
                                            action [Function(close_lighting_editor), SetVariable("lighting_selector_open", True)]
                                            text_size 11
                                            background Solid("#2f2f2f")
                                            hover_background Solid("#3f3f3f")
                                            padding (6,3)
                                    for i, e in enumerate(_dl):
                                        $ _name = str(e.get('name', f"Light {i+1}"))
                                        $ _en = bool(e.get('enabled', True))
                                        hbox:
                                            spacing 6
                                            textbutton (_name):
                                                action Function(lighting_editor_select_index, i)
                                                background (Solid("#3a3a3a") if i == lighting_editor_selected else Solid("#2a2a2a"))
                                                hover_background Solid("#444444")
                                                text_color ("#ffffff" if i == lighting_editor_selected else "#cccccc")
                                                padding (6,4)
                                            null width 6
                                            textbutton ("ON" if _en else "OFF"):
                                                action Function(lighting_toggle_enable, i)
                                                background Solid("#2f2f2f")
                                                hover_background Solid("#3f3f3f")
                                                padding (6,4)
                                            null width 4
                                            textbutton "✕":
                                                action Function(lighting_delete, i)
                                                background Solid("#552222")
                                                hover_background Solid("#884444")
                                                padding (4,2)

                    # Center: Canvas (handles overlayed outside this frame)
                    frame:
                        background Solid("#101010")
                        xfill True
                        yfill True
                        padding (_pad,_pad)
                        vbox:
                            spacing _sp
                            text "Canvas" size 12 font "fonts/MapleMono-Bold.ttf" color "#dddddd"
                            text "Handles are shown directly over the scene when enabled." size 12 color "#999999"
                            text "Use Ctrl+F8 to return to Selector; ESC to close." size 11 color "#777777"

                    # Right: Properties (scrollable)
                    frame:
                        background Solid("#1d1d1d")
                        xsize _right_w
                        yfill True
                        padding (_pad,_pad)
                        viewport:
                            xfill True
                            draggable True
                            mousewheel True
                            scrollbars "vertical"
                            yfill True
                            vbox:
                                spacing _sp
                                text "Properties" size 12 font "fonts/MapleMono-Bold.ttf" color "#ffffff"
                                $ idx = int(getattr(store, 'lighting_editor_selected', -1))
                                if idx < 0 or not getattr(store, 'dynamic_lights', None) or idx >= len(store.dynamic_lights):
                                    text "Select a light to edit." size 12 color "#999999"
                                else:
                                    use lighting_editor_props(i=idx, sp=_sp)

        # Edit overlays (draggables)
        if lighting_editor_show_handles and (getattr(store, 'dynamic_lights', None)):
            # Mouse wheel adjust radius; middle click deletes hovered
            key "mousedown_4" action Function(lighting_wheel_adjust, 1)
            key "mousedown_5" action Function(lighting_wheel_adjust, -1)
            key "mouseup_2" action Function(lighting_delete_hovered)
            $ sw = float(config.screen_width)
            $ sh = float(config.screen_height)
            $ _dl = list(store.dynamic_lights)
            for _i, _e in enumerate(_dl):
                $ _pos = _e.get('pos', (0.5,0.5))
                $ _px = float(_pos[0]) * sw
                $ _py = float(_pos[1]) * sh
                drag:
                    drag_name str(_i)
                    draggable True
                    dragged Function(lighting_dragged)
                    hovered SetVariable("lighting_hover_index", _i)
                    unhovered SetVariable("lighting_hover_index", -1)
                    clicked SetVariable("lighting_editor_selected", _i)
                    pos (_px-6, _py-6)
                    add Solid("#00FFAA") xsize 12 ysize 12
                if str(_e.get('kind','point')) in ('spot','directional'):
                    $ _dir = _e.get('dir', (1.0,0.0))
                    $ _ax = _px + float(_dir[0]) * 60.0
                    $ _ay = _py + float(_dir[1]) * 60.0
                    drag:
                        drag_name ("dir_" + str(_i))
                        draggable True
                        dragged Function(lighting_dir_dragged)
                        hovered SetVariable("lighting_hover_index", _i)
                        unhovered SetVariable("lighting_hover_index", -1)
                        clicked SetVariable("lighting_editor_selected", _i)
                        pos (_ax-5, _ay-5)
                        add Solid("#FFAA00") xsize 10 ysize 10
