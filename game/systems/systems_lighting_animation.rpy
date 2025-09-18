# Lighting Animation System
# - Drives per-light animations based on `dynamic_lights[*]['animation']` blocks.
# - Modes: flicker, pulse, sweep. Optional pause while editor open.

default lighting_animation_enabled = True
default lighting_anim_pause_in_editor = True
default lighting_anim_tick_rate = 0.033  # ~30 Hz

init -5 python:
    import math, time

    def _ensure_anim_base(e):
        base = e.get('anim_base')
        if not isinstance(base, dict):
            base = {
                'intensity': float(e.get('intensity', 1.0)),
                'dir': tuple(e.get('dir', (1.0, 0.0))),
                'angle': float(e.get('angle', 0.785398)),
                'pos': tuple(e.get('pos', (0.5, 0.5))),
                'radius': float(e.get('radius', 0.3)),
            }
            e['anim_base'] = base
        return base

    def _hash_seed(idx, extra=0):
        return (idx * 7349 + 0x9E3779B9 + extra) & 0xffffffff

    def _noise_sine(t, seed=0):
        # Smooth periodic pseudo-noise [0..1]
        return 0.5 + 0.5 * math.sin(t + (seed % 1024) * 0.001)

    def _mode_flicker(e, idx, t):
        base = _ensure_anim_base(e)
        anim = e.get('animation') or {}
        spd = float(anim.get('speed_hz', anim.get('speed', 8.0)))
        vmin = float(anim.get('min', 0.7))
        vmax = float(anim.get('max', 1.2))
        seed = int(anim.get('seed', _hash_seed(idx)))
        n = _noise_sine(t * (2.0 * math.pi) * spd, seed)
        k = vmin + (vmax - vmin) * n
        e['intensity'] = max(0.0, base['intensity'] * k)

    def _mode_pulse(e, idx, t):
        base = _ensure_anim_base(e)
        anim = e.get('animation') or {}
        period = float(anim.get('period_s', anim.get('period', 2.0)))
        if period <= 1e-4:
            period = 2.0
        amp = float(anim.get('amplitude', 0.5))  # fraction of base intensity
        center = float(anim.get('base', 1.0))
        phase = float(anim.get('phase', 0.0))
        s = math.sin((t / period) * (2.0 * math.pi) + phase)
        scale = center + amp * s
        e['intensity'] = max(0.0, base['intensity'] * scale)

    def _deg_or_rad(val):
        try:
            v = float(val)
            if abs(v) > 6.283185:  # looks like degrees
                return v * (math.pi / 180.0)
            return v
        except Exception:
            return 0.0

    def _rot(vec, ang):
        dx, dy = vec
        c = math.cos(ang); s = math.sin(ang)
        return (dx*c - dy*s, dx*s + dy*c)

    def _mode_sweep(e, idx, t):
        base = _ensure_anim_base(e)
        anim = e.get('animation') or {}
        mode = str(anim.get('loop', 'wrap')).lower()
        has_range = ('start_angle' in anim) and ('end_angle' in anim)
        if has_range:
            a0 = _deg_or_rad(anim.get('start_angle', 0.0))
            a1 = _deg_or_rad(anim.get('end_angle', math.pi/2))
            spd = float(anim.get('angular_speed', 1.0))
            if mode == 'bounce':
                # triangle wave 0..1..0
                x = (t * spd) % 2.0
                x = 2.0 - x if x > 1.0 else x
            else:
                x = (t * spd) % 1.0
            ang = a0 + (a1 - a0) * x
            e['dir'] = _rot(base['dir'], ang)
        else:
            # constant spin
            spd = float(anim.get('angular_speed', 1.0))  # rad/s or deg/s
            ang = _deg_or_rad(spd) * t
            e['dir'] = _rot(base['dir'], ang)

    def lighting_animation_tick():
        try:
            if not getattr(store, 'lighting_animation_enabled', True):
                return False
            if getattr(store, 'lighting_anim_pause_in_editor', True) and getattr(store, 'lighting_editor_open', False):
                return True
            lights = getattr(store, 'dynamic_lights', None)
            if not lights:
                return True
            t = time.time()
            changed = False
            for idx, e in enumerate(lights):
                anim = e.get('animation') or {}
                mode = str(anim.get('mode', 'none')).lower()
                if mode == 'flicker':
                    _mode_flicker(e, idx, t)
                    changed = True
                elif mode == 'pulse':
                    _mode_pulse(e, idx, t)
                    changed = True
                elif mode == 'sweep':
                    _mode_sweep(e, idx, t)
                    changed = True
            if changed and 'lighting_sync_uniforms' in globals():
                lighting_sync_uniforms()
                renpy.restart_interaction()
            return True
        except Exception:
            return True

    def lighting_animation_toggle(flag=None):
        if flag is None:
            store.lighting_animation_enabled = not getattr(store, 'lighting_animation_enabled', True)
        else:
            store.lighting_animation_enabled = bool(flag)
        return store.lighting_animation_enabled

screen lighting_animation_driver():
    # Lightweight ticking screen; pauses when disabled or editor-open based on flags
    if getattr(store, 'lighting_animation_enabled', True):
        timer (getattr(store, 'lighting_anim_tick_rate', 0.033)) repeat True action Function(lighting_animation_tick)

init -2 python:
    # Register as an overlay screen so it always runs with the room
    if hasattr(config, 'overlay_screens') and 'lighting_animation_driver' not in config.overlay_screens:
        config.overlay_screens.append('lighting_animation_driver')

