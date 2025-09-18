# Simple FX API
# Friendly wrappers for shader presets, CRT, vignette, letterbox, and breathing.

init -1 python:
    def _set_shader_by_name(group, name):
        try:
            state = shader_states.get(group)
            if not state:
                return False
            presets = list(state.get("presets") or [])
            if name not in presets:
                return False
            idx = presets.index(name)
            state["current"] = idx
            # Prevent room fade and refresh
            try:
                store.suppress_room_fade_once = True
            except Exception:
                pass
            # Apply side effects for certain groups
            if group == "film_grain":
                # Map preset names to intensity and size factors
                nm = str(name).strip().lower()
                mapping = {
                    # name: (intensity, size_factor, downscale)
                    'off': (0.0, 1.0, 2.0),
                    'fine': (0.008, 1.6, 1.2),
                    'subtle': (0.015, 1.3, 1.4),
                    'moderate': (0.035, 1.0, 2.0),
                    'coarse': (0.060, 0.85, 2.5),
                    'heavy': (0.090, 0.75, 3.0),
                    'vintage': (0.050, 0.70, 2.5),
                    'cinema': (0.025, 1.0, 1.6),
                    'iso800': (0.020, 1.1, 1.4),
                    'iso1600': (0.035, 1.0, 1.8),
                    'iso3200': (0.060, 0.9, 2.5),
                }
                intensity, sizef, dscale = mapping.get(nm, (0.03, 1.0, 2.0))
                store.film_grain_enabled = (intensity > 0.0)
                store.film_grain_intensity = float(intensity)
                store.film_grain_size = float(sizef)
                store.film_grain_downscale = float(dscale)
                try:
                    renpy.restart_interaction()
                except Exception:
                    pass
            try:
                renpy.show_screen("shader_notification", message=f"{group.replace('_',' ').title()}: {name.replace('_',' ').title()}", duration=1.5)
            except Exception:
                pass
            return True
        except Exception:
            return False

    # Color grading / lighting / grain
    def set_grade(name):
        return _set_shader_by_name("color_grading", str(name))

    def set_light(name):
        """Set lighting preset using YAML-based loader (light_<name>.yaml)."""
        try:
            return bool(load_lighting(str(name)))
        except Exception:
            return False

    def set_grain(name):
        return _set_shader_by_name("film_grain", str(name))

    # Shorthand aliases
    grade = set_grade
    light = set_light
    grain = set_grain

    # CRT + vignette
    def crt_on():
        try:
            if not getattr(store, 'crt_enabled', False):
                toggle_crt_effect()
            return True
        except Exception:
            return False

    def crt_off():
        try:
            if getattr(store, 'crt_enabled', False):
                toggle_crt_effect()
            return True
        except Exception:
            return False

    def crt_params(warp=None, scan=None, chroma=None, scanline_size=None, vignette=None, vignette_width=None, vignette_feather=None):
        """Set CRT parameters. Vignette args are deprecated - use vignette() function instead."""
        try:
            # Handle deprecated vignette parameters
            if vignette is not None or vignette_width is not None or vignette_feather is not None:
                print("[DEPRECATED] crt_params() vignette arguments are deprecated. Use vignette() function instead.")
                # Route to new vignette function
                vignette(strength=vignette, width=vignette_width, feather=vignette_feather)
            
            # Handle CRT parameters normally
            w = getattr(store, 'crt_warp', 0.2) if warp is None else float(warp)
            s = getattr(store, 'crt_scan', 0.5) if scan is None else float(scan)
            c = getattr(store, 'crt_chroma', 0.9) if chroma is None else float(chroma)
            sl = getattr(store, 'crt_scanline_size', 1.0) if scanline_size is None else float(scanline_size)
            set_crt_parameters(warp=w, scan=s, chroma=c, scanline_size=sl)
            return True
        except Exception:
            return False

    def vignette(strength=None, width=None, feather=None, d_strength=0.0, d_width=0.0):
        """Set vignette parameters (now routed to colour grading).
        
        Args:
            strength: Vignette strength (0.0-1.0), None to keep current
            width: Vignette width (0.05-0.5), None to keep current  
            feather: Vignette feather/softness (0.5-3.0), None to keep current
            d_strength: Delta adjustment to current strength
            d_width: Delta adjustment to current width
        """
        try:
            # Update grading variables (v2.1+)
            if strength is not None:
                store.grade_vignette_strength = max(0.0, min(1.0, float(strength)))
            if width is not None:
                store.grade_vignette_width = max(0.05, min(0.5, float(width)))
            if feather is not None:
                store.grade_vignette_feather = max(0.5, min(3.0, float(feather)))
            
            # Apply delta adjustments
            if d_strength != 0.0:
                current = getattr(store, 'grade_vignette_strength', 0.0)
                store.grade_vignette_strength = max(0.0, min(1.0, current + float(d_strength)))
            if d_width != 0.0:
                current = getattr(store, 'grade_vignette_width', 0.25)
                store.grade_vignette_width = max(0.05, min(0.5, current + float(d_width)))
            
            # Apply via shader system
            final_strength = getattr(store, 'grade_vignette_strength', 0.0) 
            final_width = getattr(store, 'grade_vignette_width', 0.25)
            adjust_vignette(set_strength=final_strength, set_width=final_width)
            
            # Enable colour grading if vignette is non-zero
            if final_strength > 0.0 or final_width != 0.25:
                store.color_grading_enabled = True
            
            return True
        except Exception:
            return False

    # Letterbox wrappers with aspect ratio support
    def letterbox_on(speed="normal", aspect_ratio=None):
        """Turn on cinematic letterbox.

        Args:
            speed: One of 'very_slow'|'slow'|'normal'|'fast'|'very_fast' or an int 0..4.
            aspect_ratio: Target aspect ratio as string ('21:9', '16:9', '4:3', '2.35:1') 
                         or float (e.g., 1.777, 2.35). None uses current letterbox_height setting.
        """
        try:
            # Map speed to internal speed index
            idx = None
            if isinstance(speed, (int, float)):
                try:
                    si = int(speed)
                    if 0 <= si <= 4:
                        idx = si
                except Exception:
                    pass
            if idx is None and isinstance(speed, str):
                s = speed.strip().lower()
                speed_map = {
                    'very_slow': 0,
                    'slow': 1,
                    'normal': 2,
                    'fast': 3,
                    'very_fast': 4,
                }
                if s in speed_map:
                    idx = speed_map[s]
                else:
                    try:
                        si = int(s)
                        if 0 <= si <= 4:
                            idx = si
                    except Exception:
                        pass
            if idx is not None:
                try:
                    set_letterbox_speed(idx)
                except Exception:
                    pass
            
            # Set aspect ratio if provided
            if aspect_ratio is not None:
                try:
                    set_letterbox_aspect_ratio(aspect_ratio)
                except Exception:
                    pass
            
            show_letterbox(duration=None, wait_for_animation=False)
            return True
        except Exception:
            return False

    def letterbox_off(speed="normal"):
        """Turn off cinematic letterbox.

        Args:
            speed: Optional animation speed for the ease-out (same values as letterbox_on).
        """
        try:
            # Optionally set the speed before turning off so the ease-out uses it
            idx = None
            if isinstance(speed, (int, float)):
                try:
                    si = int(speed)
                    if 0 <= si <= 4:
                        idx = si
                except Exception:
                    pass
            if idx is None and isinstance(speed, str):
                s = speed.strip().lower()
                speed_map = {
                    'very_slow': 0,
                    'slow': 1,
                    'normal': 2,
                    'fast': 3,
                    'very_fast': 4,
                }
                if s in speed_map:
                    idx = speed_map[s]
                else:
                    try:
                        si = int(s)
                        if 0 <= si <= 4:
                            idx = si
                    except Exception:
                        pass
            if idx is not None:
                try:
                    set_letterbox_speed(idx)
                except Exception:
                    pass
            hide_letterbox(duration=None, wait_for_animation=False)
            return True
        except Exception:
            return False
    
    def letterbox_aspect(ratio):
        """Set letterbox aspect ratio.
        
        Args:
            ratio: Aspect ratio as string ('21:9', '16:9', 'cinemascope') or float (e.g., 1.85, 2.35)
        """
        try:
            set_letterbox_aspect_ratio(ratio)
            return True
        except Exception:
            return False
    
    def letterbox_cinema(style="cinemascope"):
        """Apply common cinematic letterbox ratios.
        
        Args:
            style: 'cinemascope' (2.35:1), 'panavision' (2.39:1), 'academy' (1.375:1)
        """
        try:
            letterbox_on(aspect_ratio=style)
            return True
        except Exception:
            return False

    # Preset YAML helpers
    def preset_load(path):
        """Apply a YAML shader preset file. Path relative to 'yaml/'."""
        try:
            # The shader_preset_apply_file already calls renpy.restart_interaction()
            # so we don't need to call it again here
            result = shader_preset_apply_file(path)
            return result
        except Exception:
            return False

    def preset_save(path):
        """Save current shader state to a YAML preset file. Path relative to 'yaml/'."""
        try:
            return shader_preset_save_file(path)
        except Exception:
            return False

    # Bloom helpers (post-light thresholded blur)
    def bloom_on(threshold=0.75, strength=0.6, radius=2.5):
        try:
            store.bloom_enabled = True
            if threshold is not None:
                store.bloom_threshold = float(threshold)
            if strength is not None:
                store.bloom_strength = float(strength)
            if radius is not None:
                store.bloom_radius = float(radius)
            try:
                renpy.notify("Bloom: ON")
            except Exception:
                pass
            renpy.restart_interaction()
            return True
        except Exception:
            return False

    def bloom_off():
        try:
            store.bloom_enabled = False
            try:
                renpy.notify("Bloom: OFF")
            except Exception:
                pass
            renpy.restart_interaction()
            return True
        except Exception:
            return False

    # Diagnostics: Force Grade toggle for quick visual verification
    def toggle_force_grade():
        """Toggle a dramatic colour grade for quick visual verification, preserving previous settings."""
        try:
            if not getattr(store, 'lighting_force_grade_on', False):
                store.lighting_force_grade_backup = {
                    'enabled': getattr(store, 'color_grading_enabled', False),
                    'brightness': getattr(store, 'shader_brightness', 0.0),
                    'contrast': getattr(store, 'shader_contrast', 1.0),
                    'saturation': getattr(store, 'color_saturation', 1.0),
                    'temperature': getattr(store, 'color_temperature', 0.0),
                    'tint': getattr(store, 'color_tint', 0.0),
                    'gamma': getattr(store, 'shader_gamma', 1.0),
                    'vig_s': getattr(store, 'grade_vignette_strength', 0.0),
                    'vig_w': getattr(store, 'grade_vignette_width', 0.25),
                    'vig_f': getattr(store, 'grade_vignette_feather', 1.0),
                }
                store.color_grading_enabled = True
                store.shader_brightness = 0.05
                store.shader_contrast = 1.35
                store.color_saturation = 1.6
                store.color_temperature = 0.2
                store.color_tint = -0.1
                store.shader_gamma = 1.0
                store.grade_vignette_strength = 0.2
                store.grade_vignette_width = 0.35
                store.grade_vignette_feather = 1.0
                store.lighting_force_grade_on = True
                try:
                    renpy.notify("Force Grade: ON")
                except Exception:
                    pass
            else:
                b = getattr(store, 'lighting_force_grade_backup', None)
                if isinstance(b, dict):
                    store.color_grading_enabled = bool(b.get('enabled', False))
                    store.shader_brightness = float(b.get('brightness', 0.0))
                    store.shader_contrast = float(b.get('contrast', 1.0))
                    store.color_saturation = float(b.get('saturation', 1.0))
                    store.color_temperature = float(b.get('temperature', 0.0))
                    store.color_tint = float(b.get('tint', 0.0))
                    store.shader_gamma = float(b.get('gamma', 1.0))
                    store.grade_vignette_strength = float(b.get('vig_s', 0.0))
                    store.grade_vignette_width = float(b.get('vig_w', 0.25))
                    store.grade_vignette_feather = float(b.get('vig_f', 1.0))
                store.lighting_force_grade_on = False
                try:
                    renpy.notify("Force Grade: OFF")
                except Exception:
                    pass
            renpy.restart_interaction()
        except Exception:
            return False

    # Breathing conveniences (wrap existing API)
    def breathe_enable(obj_name=None, save=False, room_id=None):
        return breathing_enable_for(obj_name=obj_name, save=save, room_id=room_id)

    def breathe_disable(obj_name=None, save=False, room_id=None):
        return breathing_disable_for(obj_name=obj_name, save=save, room_id=room_id)

    def breathe_param(key, value, obj_name=None, save=False, room_id=None):
        return breathing_set_param(key, value, obj_name=obj_name, save=save, room_id=room_id)

    def breathe_profile_apply(name, room_id=None, obj_name=None):
        return breathing_apply_profile(name, room_id=room_id, obj_name=obj_name)

    def breathe_profile_save(name, room_id=None, obj_name=None):
        return breathing_save_profile(name, room_id=room_id, obj_name=obj_name)

    # --- Dynamic Lighting (multi-light) ---
    def _parse_color(c):
        # Accept (r,g,b) 0..1 or #RRGGBB/#RGB
        if isinstance(c, (list, tuple)) and len(c) == 3:
            try:
                r, g, b = float(c[0]), float(c[1]), float(c[2])
                return (max(0.0, min(1.0, r)), max(0.0, min(1.0, g)), max(0.0, min(1.0, b)))
            except Exception:
                return (1.0, 1.0, 1.0)
        if isinstance(c, str):
            s = c.strip()
            if s.startswith('#'):
                s = s[1:]
            if len(s) == 3:
                s = ''.join(ch*2 for ch in s)
            try:
                r = int(s[0:2], 16) / 255.0
                g = int(s[2:4], 16) / 255.0
                b = int(s[4:6], 16) / 255.0
                return (r, g, b)
            except Exception:
                return (1.0, 1.0, 1.0)
        return (1.0, 1.0, 1.0)

    def _ensure_dyn_list():
        if not hasattr(store, 'dynamic_lights') or store.dynamic_lights is None:
            store.dynamic_lights = []
        return store.dynamic_lights

    def light_add(kind='point', x=None, y=None, pos=None, color=(1.0,1.0,1.0), intensity=1.0, radius=0.5, dir=(1.0,0.0), angle=0.5, anim=None):
        try:
            lights = _ensure_dyn_list()
            if pos is None:
                pos = (float(x) if x is not None else 0.5, float(y) if y is not None else 0.5)
            entry = {
                'kind': str(kind),
                'pos': (float(pos[0]), float(pos[1])),
                'color': _parse_color(color),
                'intensity': float(intensity),
                'radius': float(radius),
                'dir': (float(dir[0]), float(dir[1])),
                'angle': float(angle),
            }
            if anim:
                entry['anim'] = dict(anim)
            lights.append(entry)
            try:
                store.suppress_room_fade_once = True
            except Exception:
                pass
            # Sync shader uniforms if lighting shader is present
            try:
                if 'lighting_sync_uniforms' in globals():
                    lighting_sync_uniforms()
            except Exception:
                pass
            renpy.restart_interaction()
            return len(lights) - 1
        except Exception:
            return -1

    def light_set(index, **kwargs):
        try:
            lights = _ensure_dyn_list()
            if index < 0 or index >= len(lights):
                return False
            e = lights[index]
            if 'kind' in kwargs: e['kind'] = str(kwargs['kind'])
            if 'pos' in kwargs or ('x' in kwargs and 'y' in kwargs):
                p = kwargs.get('pos', (kwargs.get('x', e['pos'][0]), kwargs.get('y', e['pos'][1])))
                e['pos'] = (float(p[0]), float(p[1]))
            if 'color' in kwargs: e['color'] = _parse_color(kwargs['color'])
            if 'intensity' in kwargs: e['intensity'] = float(kwargs['intensity'])
            if 'radius' in kwargs: e['radius'] = float(kwargs['radius'])
            if 'dir' in kwargs: e['dir'] = (float(kwargs['dir'][0]), float(kwargs['dir'][1]))
            if 'angle' in kwargs: e['angle'] = float(kwargs['angle'])
            if 'anim' in kwargs: e['anim'] = dict(kwargs['anim']) if kwargs['anim'] is not None else None
            store.suppress_room_fade_once = True
            try:
                if 'lighting_sync_uniforms' in globals():
                    lighting_sync_uniforms()
            except Exception:
                pass
            renpy.restart_interaction()
            return True
        except Exception:
            return False

    def light_remove(index):
        try:
            lights = _ensure_dyn_list()
            if index < 0 or index >= len(lights):
                return False
            lights.pop(index)
            store.suppress_room_fade_once = True
            try:
                if 'lighting_sync_uniforms' in globals():
                    lighting_sync_uniforms()
            except Exception:
                pass
            renpy.restart_interaction()
            return True
        except Exception:
            return False

    def light_clear():
        try:
            _ensure_dyn_list()
            store.dynamic_lights = []
            store.suppress_room_fade_once = True
            try:
                if 'lighting_sync_uniforms' in globals():
                    lighting_sync_uniforms()
            except Exception:
                pass
            renpy.restart_interaction()
            return True
        except Exception:
            return False

    def light_anim(index, mode='pulse', **params):
        try:
            lights = _ensure_dyn_list()
            if index < 0 or index >= len(lights):
                return False
            anim = dict(params)
            anim['mode'] = mode
            lights[index]['anim'] = anim
            store.lighting_animated = True
            store.suppress_room_fade_once = True
            try:
                if 'lighting_sync_uniforms' in globals():
                    lighting_sync_uniforms()
            except Exception:
                pass
            renpy.restart_interaction()
            return True
        except Exception:
            return False

    def light_strength(value):
        try:
            store.lighting_strength = float(value)
            store.suppress_room_fade_once = True
            renpy.restart_interaction()
            return True
        except Exception:
            return False

    def light_anim_toggle():
        try:
            store.lighting_animated = not bool(getattr(store, 'lighting_animated', False))
            store.suppress_room_fade_once = True
            renpy.restart_interaction()
            return store.lighting_animated
        except Exception:
            return False
