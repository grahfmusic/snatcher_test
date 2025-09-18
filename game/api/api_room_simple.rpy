# Simple Room API (script-style)
# Provides a `room` convenience namespace mirroring examples in editor.md

init -1 python:
    class _RoomAPI(object):
        def set_shader_preset(self, path):
            return preset_load(path)

        def save_shader_preset(self, path):
            return preset_save(path)

        def crt(self, aberration=None, vignette=None, warp=None, scan=None, scanline_size=None, enabled=True, animated=None,
                aberration_mode=None, aberration_speed=None, glitch=None, glitch_speed=None, feather=None):
            try:
                if enabled:
                    crt_on()
                else:
                    crt_off()
            except Exception:
                pass
            try:
                if any(v is not None for v in (warp, scan, aberration, scanline_size)):
                    crt_params(
                        warp=warp if warp is not None else getattr(store, 'crt_warp', 0.2),
                        scan=scan if scan is not None else getattr(store, 'crt_scan', 0.5),
                        chroma=aberration if aberration is not None else getattr(store, 'crt_chroma', 0.9),
                        scanline_size=scanline_size if scanline_size is not None else getattr(store, 'crt_scanline_size', 1.0),
                    )
                if vignette is not None:
                    # treat vignette as strength; keep width
                    _w = getattr(store, 'crt_vignette_width', 0.25)
                    renpy.run(Function(vignette, set_strength=float(vignette), set_width=_w))
                # 'animated' parameter is ignored; CRT animation controlled via editor.
                # Extended FX controls
                changed_fx = False
                if aberration_mode is not None:
                    store.crt_aberr_mode = str(aberration_mode)
                    changed_fx = True
                if aberration_speed is not None:
                    store.crt_aberr_speed = float(aberration_speed)
                    changed_fx = True
                if glitch is not None:
                    store.crt_glitch = float(glitch)
                    changed_fx = True
                if glitch_speed is not None:
                    store.crt_glitch_speed = float(glitch_speed)
                    changed_fx = True
                if feather is not None:
                    store.crt_vignette_feather = float(feather)
                    changed_fx = True
                if changed_fx:
                    store.suppress_room_fade_once = True
                    renpy.restart_interaction()
            except Exception:
                return False
            return True

        def grain(self, intensity=None, size=None, preset=None, downscale=None):
            """Set film grain via preset or direct parameters.

            Args:
                intensity: 0.0..~0.12 (0 disables)
                size: scale factor ~0.5..1.5 (1.0 = default grain size)
                preset: one of 'off','fine','subtle','moderate','coarse','heavy','vintage','cinema','iso800','iso1600','iso3200'
                downscale: sampling downscale factor 1.0..4.0 (higher = chunkier)
            """
            try:
                # If a preset or legacy string passed in size, defer to preset mapping
                if preset is not None or (isinstance(size, str) and size):
                    name = str(preset) if preset is not None else str(size)
                    return set_grain(name)

                # Direct parameter control
                changed = False
                if intensity is not None:
                    store.film_grain_intensity = float(intensity)
                    changed = True
                if size is not None and not isinstance(size, str):
                    store.film_grain_size = float(size)
                    changed = True
                if downscale is not None:
                    store.film_grain_downscale = float(downscale)
                    changed = True
                if changed:
                    # Enable if intensity > 0
                    store.film_grain_enabled = (getattr(store, 'film_grain_intensity', 0.0) > 0.0)
                    renpy.restart_interaction()
                    return True
                # If nothing specified, apply a reasonable default preset
                return set_grain('subtle')
            except Exception:
                return False

        def color_grade(self, name):
            try:
                return set_grade(str(name))
            except Exception:
                return False

        def bloom(self, enabled=True, threshold=None, strength=None, radius=None):
            """Control global bloom. Example: room.bloom(True, 0.75, 0.6, 2.5) or room.bloom(False)

            Args:
                enabled: True to enable, False to disable
                threshold: bright-pass threshold (0..1)
                strength: additive strength of blurred highlights
                radius: blur radius in pixels
            """
            try:
                if enabled:
                    return bloom_on(threshold=threshold, strength=strength, radius=radius)
                else:
                    return bloom_off()
            except Exception:
                return False

        def lighting(self, x=None, y=None, preset=None, strength=None, animation=None):
            try:
                if preset:
                    set_light(str(preset))
                if strength is not None:
                    store.lighting_strength = float(strength)
                # Position overrides (pixels or normalized)
                if x is not None and y is not None:
                    sx = float(config.screen_width)
                    sy = float(config.screen_height)
                    fx = float(x); fy = float(y)
                    nx = fx if fx <= 1.0 else (fx / max(1.0, sx))
                    ny = fy if fy <= 1.0 else (fy / max(1.0, sy))
                    nx = max(0.0, min(1.0, nx)); ny = max(0.0, min(1.0, ny))
                    store.lighting_override_pos = (nx, ny)
                if animation is not None:
                    # Accept string or dict
                    store.lighting_animated = True
                    if isinstance(animation, str):
                        k = animation.strip().lower()
                        if k in ('pulse', 'breathe', 'flicker'):
                            store.lighting_anim_override = { 'mode': 'pulse', 'amount': 0.35, 'speed': 1.2 if k != 'flicker' else 2.0 }
                        elif k in ('orbit', 'sweep'):
                            store.lighting_anim_override = { 'mode': 'orbit', 'radius': 0.05, 'speed': 0.6 }
                    elif isinstance(animation, dict):
                        store.lighting_anim_override = dict(animation)
                store.suppress_room_fade_once = True
                renpy.restart_interaction()
                return True
            except Exception:
                return False

    # Public namespace
    room = _RoomAPI()
