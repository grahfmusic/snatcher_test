# Lighting stub: removes 2D lighting/editor while keeping API surface safe.

# Keep a simple state dict so existing UI/debug checks don't break.
default lighting_editor_open = False
default lights_state = {
    "active": [],
    "enabled": False,
    "debug": False,
    "dirty": False,
    "quality": "high",
}

init -100 python:
    # Prefer direct PyYAML safe_load for lighting presets (simpler, robust)
    # Minimal Light class so any legacy constructions don't crash.
    class Light(object):
        def __init__(self, **kwargs):
            for k, v in kwargs.items():
                setattr(self, k, v)

    # Editor toggle becomes a no-op (kept for keybind references).
    def toggle_lighting_editor(force=None):
        try:
            if force is None:
                store.lighting_editor_open = False
            else:
                store.lighting_editor_open = bool(force) and False
        except Exception:
            pass
        return False

    # Runtime lighting public surface — all no-ops.
    def lights_runtime_apply_lights(lights, replace=True):
        try:
            store.lights_state["active"] = list(lights) if lights else []
            store.lights_state["enabled"] = bool(store.lights_state["active"])
            store.lights_state["dirty"] = False
        except Exception:
            pass
        return False

    def lights_runtime_clear_visual_lighting():
        return None

    def lights_debug(flag=None):
        try:
            if flag is None:
                store.lights_state["debug"] = not store.lights_state.get("debug", False)
            else:
                store.lights_state["debug"] = bool(flag)
            return store.lights_state["debug"]
        except Exception:
            return False

    # Legacy/simple APIs used by room code or presets.
    # YAML-backed loader for lighting presets under game/yaml/shaders/
    def load_lighting(preset_name):
        """Load lights from YAML presets and populate dynamic_lights.

        Looks in:
          - game/yaml/shaders/custom/light_<name>.yaml
          - game/yaml/shaders/preset/light_<name>.yaml
        """
        try:
            import os
            # Loaders: prefer YAMLIOService, then PyYAML safe_load
            _svc = None
            try:
                from api_io_yaml import YAMLIOService
                _svc = YAMLIOService()
            except Exception:
                _svc = None
            try:
                import yaml as _pyyaml
            except Exception:
                _pyyaml = None
            name = str(preset_name).strip()
            candidates = [
                f"yaml/shaders/custom/light_{name}.yaml",
                f"yaml/shaders/preset/light_{name}.yaml",
            ]
            data = None
            src = None
            base = getattr(config, 'gamedir', '.')
            for rel in candidates:
                pabs = os.path.join(base, rel)
                if os.path.exists(pabs):
                    try:
                        print(f"[LIGHTING] Loading YAML from: {pabs}")
                    except Exception:
                        pass
                    # First try shared service
                    data = None
                    if _svc:
                        try:
                            data = _svc.load_yaml(pabs)
                            try:
                                with open(pabs, 'r', encoding='utf-8') as _tf:
                                    _raw = _tf.read()
                                print(f"[LIGHTING] Raw len={len(_raw)}, has_lights_token={'lights:' in _raw}")
                            except Exception:
                                pass
                        except Exception:
                            data = None
                    # Fallback to direct PyYAML
                    if (not data) and _pyyaml:
                        try:
                            with open(pabs, 'r', encoding='utf-8') as f:
                                data = _pyyaml.safe_load(f)
                        except Exception:
                            data = None
                    src = rel
                    break
            if not data:
                # Fallback: try direct PyYAML safe_load
                # Already attempted safe_load; nothing more to do
                if not data:
                    print(f"[LIGHTING] Preset not found or unreadable: {preset_name}")
                    return []
            # Resolve lights block robustly
            def _is_light_dict(d):
                try:
                    if not isinstance(d, dict):
                        return False
                    t = str(d.get('type', '')).lower()
                    if t in ('point', 'spot', 'directional', 'ambient'):
                        return True
                    # heuristic: has at least color/intensity or position
                    return ('color' in d) or ('intensity' in d) or ('position' in d)
                except Exception:
                    return False

            def _find_lights(obj, depth=0):
                if depth > 4:
                    return None
                if isinstance(obj, list):
                    if obj and all(isinstance(x, dict) for x in obj) and any(_is_light_dict(x) for x in obj):
                        return obj
                    # search children
                    for x in obj:
                        res = _find_lights(x, depth+1)
                        if isinstance(res, list):
                            return res
                    return None
                if isinstance(obj, dict):
                    # direct key
                    v = obj.get('lights')
                    if isinstance(v, list):
                        return v
                    # effects->lighting->lights
                    try:
                        eff = obj.get('effects') or {}
                        lig = eff.get('lighting') or {}
                        v2 = lig.get('lights') if isinstance(lig, dict) else None
                        if isinstance(v2, list):
                            return v2
                    except Exception:
                        pass
                    # any key containing 'lights'
                    try:
                        for k, val in obj.items():
                            if 'lights' in str(k).lower() and isinstance(val, list):
                                return val
                    except Exception:
                        pass
                    # search children
                    for val in obj.values():
                        res = _find_lights(val, depth+1)
                        if isinstance(res, list):
                            return res
                return None

            def _simple_extract_lights(path):
                try:
                    import ast
                    with open(path, 'r', encoding='utf-8') as f:
                        lines = f.readlines()
                    lights = []
                    in_lights = False
                    current = None
                    base_indent = None
                    for raw in lines:
                        line = raw.rstrip('\n')
                        # Track section
                        if not in_lights:
                            if line.strip().startswith('lights:'):
                                in_lights = True
                                continue
                            else:
                                continue
                        # Stop if a new top-level key appears
                        if in_lights and (line and not line[0].isspace()) and not line.strip().startswith('- '):
                            break
                        s = line.lstrip()
                        if not s:
                            continue
                        indent = len(line) - len(s)
                        if s.startswith('- '):
                            # Start new entry
                            current = {}
                            lights.append(current)
                            base_indent = indent
                            # If there is an inline key after '- '
                            rest = s[2:].strip()
                            if rest and ':' in rest:
                                k, v = rest.split(':', 1)
                                current[k.strip()] = v.strip()
                            continue
                        if current is None:
                            continue
                        # Parse key: value
                        if ':' in s:
                            k, v = s.split(':', 1)
                            key = k.strip()
                            val = v.strip()
                            if val.startswith('[') and val.endswith(']'):
                                try:
                                    parsed = ast.literal_eval(val)
                                    current[key] = parsed
                                except Exception:
                                    current[key] = val
                            elif val.lower() in ('true', 'false'):
                                current[key] = (val.lower() == 'true')
                            else:
                                # try float then int else string
                                try:
                                    fv = float(val)
                                    current[key] = fv
                                except Exception:
                                    try:
                                        iv = int(val)
                                        current[key] = iv
                                    except Exception:
                                        current[key] = val.strip('"\'')
                    return lights
                except Exception:
                    return None

            lights_block = _find_lights(data)
            if not isinstance(lights_block, list):
                # Try simple extractor as final fallback
                pabs2 = os.path.join(base, src or '')
                if os.path.exists(pabs2):
                    lights_block = _simple_extract_lights(pabs2)
            if not isinstance(lights_block, list):
                try:
                    keys = []
                    if isinstance(data, dict):
                        for k in data.keys():
                            keys.append(str(k))
                    info = f"type={type(data).__name__}, keys={keys} from {src}"
                except Exception:
                    info = "n/a"
                print(f"[LIGHTING] Invalid YAML structure (missing 'lights' list): {src or preset_name} ({info})")
                return []

            # Apply optional globals (strength/bloom)
            try:
                g = None
                if isinstance(data, dict):
                    g = data.get('globals') or data.get('global') or None
                if isinstance(g, dict):
                    if 'strength' in g:
                        store.lighting_strength = float(g.get('strength', 1.0))
                    if 'bloom_threshold' in g:
                        store.bloom_threshold = float(g.get('bloom_threshold', 0.75))
                        store.bloom_enabled = True
                    if 'bloom_strength' in g:
                        store.bloom_strength = float(g.get('bloom_strength', 0.6))
                        store.bloom_enabled = True
                    if 'bloom_radius' in g:
                        store.bloom_radius = float(g.get('bloom_radius', 2.5))
                        store.bloom_enabled = True
            except Exception:
                pass

            # Convert YAML lights to dynamic_lights entries
            sw = float(getattr(config, 'screen_width', 1280))
            sh = float(getattr(config, 'screen_height', 720))
            diag = max(sw, sh)
            dyn = []
            max_lights = 8
            for idx, item in enumerate(lights_block or []):
                if not item or (isinstance(item, dict) and not item.get('enabled', True)):
                    continue
                if len(dyn) >= max_lights:
                    print(f"[LIGHTING] Skipping extra light at index {idx} (max {max_lights})")
                    continue
                ltype = str(item.get('type', 'point')).lower()
                kind = 'point' if ltype in ('point', 'ambient') else 'spot'
                # position may be pixels; default to center
                px, py = 0.5, 0.5
                pos = item.get('position') or item.get('pos')
                if isinstance(pos, (list, tuple)) and len(pos) >= 2:
                    try:
                        px = float(pos[0]) / sw
                        py = float(pos[1]) / sh
                    except Exception:
                        px, py = 0.5, 0.5
                # radius in pixels -> normalized
                try:
                    radius_px = float(item.get('radius', 320.0))
                except Exception:
                    radius_px = 320.0
                radius_uv = max(0.01, radius_px / diag)
                # color: [r,g,b,(a)] -> rgb, intensity
                col = item.get('color', [1.0, 1.0, 1.0, 1.0])
                try:
                    r = float(col[0]); g = float(col[1]); b = float(col[2])
                    a = float(col[3]) if len(col) > 3 else 1.0
                except Exception:
                    r, g, b, a = 1.0, 1.0, 1.0, 1.0
                try:
                    intensity = float(item.get('intensity', 1.0)) * a
                except Exception:
                    intensity = 1.0 * a
                # direction for directional/spot
                dirv = item.get('direction') or item.get('dir') or (1.0, 0.0)
                try:
                    dx = float(dirv[0]); dy = float(dirv[1])
                except Exception:
                    dx, dy = 1.0, 0.0
                # angle: if directional, use broad cone; spot use moderate default
                if ltype == 'directional':
                    angle = 1.2  # wide cone
                else:
                    try:
                        angle = float(item.get('angle', 0.7))
                    except Exception:
                        angle = 0.7
                # map layer labels
                layer = str(item.get('layer', '')).lower()
                if layer in ('bg', 'background'):
                    layer_out = 'back'
                elif layer in ('objects', 'fg', 'front'):
                    layer_out = 'front'
                else:
                    layer_out = ''

                # Falloff + bloom
                falloff = str(item.get('falloff', 'smooth')).lower()
                try:
                    fallexp = float(item.get('falloff_exp', 1.0))
                except Exception:
                    fallexp = 1.0
                try:
                    bboost = float(item.get('bloom_boost', 1.0))
                except Exception:
                    bboost = 1.0
                # Animation block (store raw; runtime will interpret)
                anim = item.get('animation') or {}

                dyn.append({
                    'kind': kind,
                    'pos': (px, py),
                    'radius': radius_uv,
                    'color': (r, g, b),
                    'intensity': intensity,
                    'dir': (dx, dy),
                    'angle': angle,
                    'layer': layer_out,
                    'enabled': bool(item.get('enabled', True)),
                    'falloff': falloff,
                    'falloff_exp': fallexp,
                    'bloom_boost': bboost,
                    'animation': anim,
                })

            store.dynamic_lights = dyn
            store.lights_state["active"] = []  # retired path
            store.lights_state["enabled"] = bool(dyn)
            # Sync uniforms for shader
            try:
                if 'lighting_sync_uniforms' in globals():
                    lighting_sync_uniforms()
            except Exception:
                pass
            renpy.restart_interaction()
            print(f"[LIGHTING] Loaded YAML preset '{preset_name}' from {src} with {len(dyn)} lights")
            return dyn
        except Exception as e:
            print(f"[LIGHTING] YAML load error for '{preset_name}': {e}")
            return []

    def apply_custom_lighting(lights_config):
        """Apply lights from a YAML-like dict structure directly."""
        try:
            if isinstance(lights_config, dict) and 'lights' in lights_config:
                return bool(load_lighting_from_dict(lights_config))
            return False
        except Exception:
            return False

    def load_lighting_from_dict(data):
        try:
            sw = float(getattr(config, 'screen_width', 1280))
            sh = float(getattr(config, 'screen_height', 720))
            diag = max(sw, sh)
            dyn = []
            for item in data.get('lights', []) or []:
                if not item or (isinstance(item, dict) and not item.get('enabled', True)):
                    continue
                ltype = str(item.get('type', 'point')).lower()
                kind = 'point' if ltype in ('point', 'ambient') else 'spot'
                pos = item.get('position') or item.get('pos')
                if isinstance(pos, (list, tuple)) and len(pos) >= 2:
                    try:
                        px = float(pos[0]) / sw
                        py = float(pos[1]) / sh
                    except Exception:
                        px, py = 0.5, 0.5
                else:
                    px, py = 0.5, 0.5
                radius_px = float(item.get('radius', 320.0))
                radius_uv = max(0.01, radius_px / diag)
                col = item.get('color', [1.0, 1.0, 1.0, 1.0])
                try:
                    r = float(col[0]); g = float(col[1]); b = float(col[2])
                    a = float(col[3]) if len(col) > 3 else 1.0
                except Exception:
                    r, g, b, a = 1.0, 1.0, 1.0, 1.0
                intensity = float(item.get('intensity', 1.0)) * a
                dirv = item.get('direction') or item.get('dir') or (1.0, 0.0)
                try:
                    dx = float(dirv[0]); dy = float(dirv[1])
                except Exception:
                    dx, dy = 1.0, 0.0
                if ltype == 'directional':
                    angle = 1.2
                else:
                    angle = float(item.get('angle', 0.7))
                layer = str(item.get('layer', '')).lower()
                if layer in ('bg', 'background'):
                    layer_out = 'back'
                elif layer in ('objects', 'fg', 'front'):
                    layer_out = 'front'
                else:
                    layer_out = ''
                dyn.append({
                    'kind': kind,
                    'pos': (px, py),
                    'radius': radius_uv,
                    'color': (r, g, b),
                    'intensity': intensity,
                    'dir': (dx, dy),
                    'angle': angle,
                    'layer': layer_out,
                })
            store.dynamic_lights = dyn
            try:
                if 'lighting_sync_uniforms' in globals():
                    lighting_sync_uniforms()
            except Exception:
                pass
            renpy.restart_interaction()
            return dyn
        except Exception as e:
            print(f"[LIGHTING] apply dict error: {e}")
            return []

    def clear_lighting():
        try:
            store.lights_state["active"] = []
            store.lights_state["enabled"] = False
        except Exception:
            pass
        return True

    # Drag handlers and save function for selector UI
    def lighting_move_light(index, px, py):
        try:
            sw = float(getattr(config, 'screen_width', 1280))
            sh = float(getattr(config, 'screen_height', 720))
            nx = max(0.0, min(1.0, float(px) / sw))
            ny = max(0.0, min(1.0, float(py) / sh))
            if not hasattr(store, 'dynamic_lights') or index < 0 or index >= len(store.dynamic_lights):
                return False
            store.dynamic_lights[index]['pos'] = (nx, ny)
            if 'lighting_sync_uniforms' in globals():
                lighting_sync_uniforms()
            renpy.restart_interaction()
            return True
        except Exception:
            return False

    def lighting_dragged(drags, drop):
        try:
            d = drags[0]
            idx = int(d.drag_name)
            return lighting_move_light(idx, d.x+6, d.y+6)
        except Exception:
            return False

    def lighting_save_current_to_yaml(name, overwrite=False):
        try:
            import os
            # sanitize name
            n = ''.join(ch for ch in str(name).strip() if ch.isalnum() or ch in ('_', '-', '.')).strip('_-')
            if not n:
                n = 'custom'
            if not n.lower().startswith('light_'):
                n = 'light_' + n
            if not n.lower().endswith('.yaml'):
                n = n + '.yaml'
            base = getattr(config, 'gamedir', '.')
            path = os.path.join(base, 'yaml', 'shaders', 'custom', n)
            if (not overwrite) and os.path.exists(path):
                try:
                    renpy.show_screen('shader_notification', message='Exists: ' + os.path.basename(path), duration=1.6)
                except Exception:
                    pass
                return False
            # build data
            sw = float(getattr(config, 'screen_width', 1280))
            sh = float(getattr(config, 'screen_height', 720))
            diag = max(sw, sh)
            lights = []
            for e in (store.dynamic_lights or []):
                kind = str(e.get('kind', 'point')).lower()
                pos = e.get('pos', (0.5,0.5))
                radius_uv = float(e.get('radius', 0.3))
                radius_px = max(1, int(round(radius_uv * diag)))
                color = list(e.get('color', (1.0,1.0,1.0)))
                if len(color) < 4:
                    color.append(1.0)
                entry = {
                    'type': 'point' if kind not in ('spot','directional','ambient') else kind,
                    'position': [int(round(pos[0]*sw)), int(round(pos[1]*sh))],
                    'radius': radius_px,
                    'color': [float(color[0]), float(color[1]), float(color[2]), float(color[3])],
                    'intensity': float(e.get('intensity', 1.0)),
                }
                if kind in ('spot','directional'):
                    entry['direction'] = [float(e.get('dir', (1.0,0.0))[0]), float(e.get('dir', (1.0,0.0))[1])]
                    entry['angle'] = float(e.get('angle', 0.7))
                lay = str(e.get('layer',''))
                if lay:
                    entry['layer'] = lay
                lights.append(entry)
            data = {
                'version': '1.0',
                'meta': {
                    'name': n.replace('light_','').replace('.yaml','').replace('_',' ').title(),
                    'description': 'Custom lighting saved from selector',
                },
                'globals': {
                    'strength': float(getattr(store, 'lighting_strength', 1.0)),
                    'bloom_threshold': float(getattr(store, 'bloom_threshold', 0.75)) if getattr(store,'bloom_enabled', False) else 0.75,
                    'bloom_strength': float(getattr(store, 'bloom_strength', 0.6)) if getattr(store,'bloom_enabled', False) else 0.0,
                    'bloom_radius': float(getattr(store, 'bloom_radius', 2.5)) if getattr(store,'bloom_enabled', False) else 2.5,
                },
                'lights': lights,
            }
            # save
            written = False
            try:
                from api_io_yaml import YAMLIOService
                svc = YAMLIOService()
                written = svc.save_yaml_if_changed(path, data, force=True)
            except Exception:
                written = False
            if not written:
                try:
                    import yaml as _pyyaml
                    os.makedirs(os.path.dirname(path), exist_ok=True)
                    with open(path, 'w', encoding='utf-8') as f:
                        _pyyaml.safe_dump(data, f, sort_keys=False, allow_unicode=True)
                    written = True
                except Exception:
                    written = False
            if written:
                try:
                    renpy.show_screen('shader_notification', message=f"Saved: {os.path.basename(path)}", duration=1.6)
                except Exception:
                    pass
            else:
                try:
                    renpy.show_screen('shader_notification', message="Save failed", duration=1.6)
                except Exception:
                    pass
            return written
        except Exception:
            return False

    def _select_index():
        try:
            idx = int(getattr(store, 'lighting_selected_index', -1))
            dl = getattr(store, 'dynamic_lights', []) or []
            if 0 <= idx < len(dl):
                return idx
            # fallback to hover
            h = int(getattr(store, 'lighting_hover_index', -1))
            if 0 <= h < len(dl):
                return h
        except Exception:
            pass
        return -1

    def lighting_adjust_radius(index, delta):
        try:
            dl = getattr(store, 'dynamic_lights', []) or []
            if index < 0 or index >= len(dl):
                return False
            r = float(dl[index].get('radius', 0.3))
            r = max(0.01, min(1.5, r + float(delta)))
            dl[index]['radius'] = r
            if 'lighting_sync_uniforms' in globals():
                lighting_sync_uniforms()
            renpy.restart_interaction()
            return True
        except Exception:
            return False

    def lighting_adjust_intensity(index, delta):
        try:
            dl = getattr(store, 'dynamic_lights', []) or []
            if index < 0 or index >= len(dl):
                return False
            it = float(dl[index].get('intensity', 1.0))
            it = max(0.0, min(5.0, it + float(delta)))
            dl[index]['intensity'] = it
            if 'lighting_sync_uniforms' in globals():
                lighting_sync_uniforms()
            renpy.restart_interaction()
            return True
        except Exception:
            return False

    def lighting_wheel_adjust(step):
        try:
            idx = _select_index()
            if idx < 0:
                return False
            # wheel step adjusts radius by 0.02 per step
            return lighting_adjust_radius(idx, 0.02 * (1 if int(step) > 0 else -1))
        except Exception:
            return False

    def lighting_adjust_radius_selected(delta):
        return lighting_adjust_radius(_select_index(), delta)

    def lighting_adjust_intensity_selected(delta):
        return lighting_adjust_intensity(_select_index(), delta)

    def lighting_delete(index):
        try:
            dl = getattr(store, 'dynamic_lights', []) or []
            if index < 0 or index >= len(dl):
                return False
            dl.pop(index)
            store.lighting_selected_index = -1
            store.lighting_hover_index = -1
            if 'lighting_sync_uniforms' in globals():
                lighting_sync_uniforms()
            renpy.restart_interaction()
            return True
        except Exception:
            return False

    def lighting_delete_hovered():
        try:
            h = int(getattr(store, 'lighting_hover_index', -1))
            return lighting_delete(h)
        except Exception:
            return False

    def lighting_set_angle(index, value):
        try:
            dl = getattr(store, 'dynamic_lights', []) or []
            if index < 0 or index >= len(dl):
                return False
            ang = max(0.05, min(1.57, float(value)))
            dl[index]['angle'] = ang
            if 'lighting_sync_uniforms' in globals():
                lighting_sync_uniforms()
            renpy.restart_interaction()
            return True
        except Exception:
            return False

    def lighting_set_radius(index, value):
        try:
            dl = getattr(store, 'dynamic_lights', []) or []
            if index < 0 or index >= len(dl):
                return False
            r = max(0.01, min(1.5, float(value)))
            dl[index]['radius'] = r
            if 'lighting_sync_uniforms' in globals():
                lighting_sync_uniforms()
            renpy.restart_interaction()
            return True
        except Exception:
            return False

    def lighting_set_intensity(index, value):
        try:
            dl = getattr(store, 'dynamic_lights', []) or []
            if index < 0 or index >= len(dl):
                return False
            it = max(0.0, min(5.0, float(value)))
            dl[index]['intensity'] = it
            if 'lighting_sync_uniforms' in globals():
                lighting_sync_uniforms()
            renpy.restart_interaction()
            return True
        except Exception:
            return False

    def lighting_dir_dragged(drags, drop):
        try:
            d = drags[0]
            name = d.drag_name
            if not name.startswith('dir_'):
                return False
            idx = int(name.split('_', 1)[1])
            dl = getattr(store, 'dynamic_lights', []) or []
            if idx < 0 or idx >= len(dl):
                return False
            # current light position in pixels
            sw = float(getattr(config, 'screen_width', 1280))
            sh = float(getattr(config, 'screen_height', 720))
            px = float(dl[idx].get('pos', (0.5,0.5))[0]) * sw
            py = float(dl[idx].get('pos', (0.5,0.5))[1]) * sh
            vx = float(d.x + 6) - px
            vy = float(d.y + 6) - py
            mag = (vx*vx + vy*vy) ** 0.5
            if mag < 1e-6:
                vx, vy = 1.0, 0.0
            else:
                vx /= mag; vy /= mag
            dl[idx]['dir'] = (vx, vy)
            if 'lighting_sync_uniforms' in globals():
                lighting_sync_uniforms()
            renpy.restart_interaction()
            return True
        except Exception:
            return False

    def lighting_add_light(kind='point'):
        try:
            dl = getattr(store, 'dynamic_lights', None)
            if dl is None:
                store.dynamic_lights = []
                dl = store.dynamic_lights
            k = str(kind).lower()
            if k not in ('point','spot','directional','ambient'):
                k = 'point'
            entry = {
                'kind': k,
                'pos': (0.5, 0.5),
                'radius': 0.30,
                'color': (1.0, 1.0, 1.0),
                'intensity': 1.0,
                'dir': (1.0, 0.0),
                'angle': 0.70,
                'layer': 'front',
                'enabled': True,
                'falloff': 'smooth',
                'falloff_exp': 1.0,
                'bloom_boost': 1.0,
            }
            dl.append(entry)
            store.lighting_selected_index = len(dl) - 1
            if 'lighting_sync_uniforms' in globals():
                lighting_sync_uniforms()
            renpy.restart_interaction()
            return True
        except Exception:
            return False

    def lighting_toggle_enable(index):
        try:
            dl = getattr(store, 'dynamic_lights', []) or []
            if index < 0 or index >= len(dl):
                return False
            curr = bool(dl[index].get('enabled', True))
            dl[index]['enabled'] = (not curr)
            if 'lighting_sync_uniforms' in globals():
                lighting_sync_uniforms()
            renpy.restart_interaction()
            return True
        except Exception:
            return False

    def lighting_set_kind(index, kind):
        try:
            dl = getattr(store, 'dynamic_lights', []) or []
            if index < 0 or index >= len(dl):
                return False
            k = str(kind).lower()
            if k not in ('point','spot','directional'):
                k = 'point'
            dl[index]['kind'] = k
            if 'lighting_sync_uniforms' in globals():
                lighting_sync_uniforms()
            renpy.restart_interaction()
            return True
        except Exception:
            return False

    def lighting_set_layer(index, layer):
        try:
            dl = getattr(store, 'dynamic_lights', []) or []
            if index < 0 or index >= len(dl):
                return False
            lay = str(layer).lower()
            if lay not in ('back','front','all','bg','objects'):
                lay = ''
            dl[index]['layer'] = lay
            if 'lighting_sync_uniforms' in globals():
                lighting_sync_uniforms()
            renpy.restart_interaction()
            return True
        except Exception:
            return False

    def lighting_set_color(index, r=None, g=None, b=None):
        try:
            dl = getattr(store, 'dynamic_lights', []) or []
            if index < 0 or index >= len(dl):
                return False
            cr, cg, cb = dl[index].get('color', (1.0,1.0,1.0))
            if r is not None: cr = max(0.0, min(1.0, float(r)))
            if g is not None: cg = max(0.0, min(1.0, float(g)))
            if b is not None: cb = max(0.0, min(1.0, float(b)))
            dl[index]['color'] = (cr, cg, cb)
            if 'lighting_sync_uniforms' in globals():
                lighting_sync_uniforms()
            renpy.restart_interaction()
            return True
        except Exception:
            return False

    def lighting_set_falloff(index, mode):
        try:
            dl = getattr(store, 'dynamic_lights', []) or []
            if index < 0 or index >= len(dl):
                return False
            m = str(mode).lower()
            if m not in ('smooth','linear','quadratic','inverse_square','custom'):
                m = 'smooth'
            dl[index]['falloff'] = m
            if 'lighting_sync_uniforms' in globals():
                lighting_sync_uniforms()
            renpy.restart_interaction()
            return True
        except Exception:
            return False

    def lighting_set_falloff_exp(index, value):
        try:
            dl = getattr(store, 'dynamic_lights', []) or []
            if index < 0 or index >= len(dl):
                return False
            v = max(0.05, min(8.0, float(value)))
            dl[index]['falloff_exp'] = v
            if 'lighting_sync_uniforms' in globals():
                lighting_sync_uniforms()
            renpy.restart_interaction()
            return True
        except Exception:
            return False

    def lighting_set_anim_mode(index, mode):
        try:
            dl = getattr(store, 'dynamic_lights', []) or []
            if index < 0 or index >= len(dl):
                return False
            anim = dl[index].get('animation') or {}
            anim['mode'] = str(mode).lower()
            dl[index]['animation'] = anim
            renpy.restart_interaction()
            return True
        except Exception:
            return False

    def lighting_set_anim_field(index, key, value):
        try:
            dl = getattr(store, 'dynamic_lights', []) or []
            if index < 0 or index >= len(dl):
                return False
            anim = dl[index].get('animation') or {}
            anim[str(key)] = value
            dl[index]['animation'] = anim
            renpy.restart_interaction()
            return True
        except Exception:
            return False

    # UI helpers referenced from room screens.
    def get_lights_displayable(zone):
        # We rely on shader passes; no separate displayable needed.
        return None

    def get_lights_counts():
        return (0, 0)

    def create_lighting_layer_transform_range(name, zmin, zmax):
        """Return layer-specific shader transform when layering is enabled.

        name: contains 'back' or 'front'; zmin/zmax are ignored here.
        """
        try:
            if not getattr(store, 'lights_layering_enabled', False):
                return None
            nm = str(name).lower()
            if 'back' in nm:
                return Transform(function=None, at_list=[lighting_back_transform])
            if 'front' in nm:
                return Transform(function=None, at_list=[lighting_front_transform])
        except Exception:
            pass
        return None

    # Optional: programmatic toggle for layering
    def lights_layering(flag=None):
        if flag is None:
            store.lights_layering_enabled = not getattr(store, 'lights_layering_enabled', False)
        else:
            store.lights_layering_enabled = bool(flag)
        renpy.restart_interaction()
        return store.lights_layering_enabled

    # Preset scanning and cycling (YAML light_*.yaml)
    def lighting_scan_presets(kind="all"):
        import os
        base = getattr(config, 'gamedir', '.')
        results = []
        def scan(sub):
            root = os.path.join(base, 'yaml', 'shaders', sub)
            if os.path.isdir(root):
                for name in os.listdir(root):
                    lname = name.lower()
                    if lname.startswith('light_') and lname.endswith(('.yaml', '.yml')):
                        results.append((sub, name))
        if kind in ("preset", "all"):
            scan('preset')
        if kind in ("custom", "all"):
            scan('custom')
        # sort by filename for stable order
        results.sort(key=lambda t: t[1].lower())
        names = []
        groups = {}
        for sub, fn in results:
            n = fn
            if n.lower().startswith('light_'):
                n = n[6:]
            if n.lower().endswith('.yaml'):
                n = n[:-5]
            elif n.lower().endswith('.yml'):
                n = n[:-4]
            names.append(n)
            g = _lighting_assign_group_for_name(n)
            groups.setdefault(g, []).append(n)

        # Sort within groups and all names
        names.sort()
        for g in groups:
            groups[g] = sorted(groups[g])

        store.available_light_presets = names
        store.available_light_groups = sorted(groups.keys())
        store.group_to_names = groups
        if not hasattr(store, 'current_light_preset_index'):
            store.current_light_preset_index = -1
        if not hasattr(store, 'current_light_group_index'):
            store.current_light_group_index = -1
        if not hasattr(store, 'current_light_group'):
            store.current_light_group = None  # None means "all"
        return list(names)

    def _lighting_assign_group_for_name(name):
        try:
            n = str(name).lower()
            if n == 'off':
                return 'off'
            if n.startswith('ambient_'):
                return 'ambient'
            if n.startswith('window_'):
                return 'window'
            if n in ('dawn', 'sunset', 'moonlight'):
                return 'natural'
            if n in ('candle', 'candlelit_room', 'firelight'):
                return 'warm'
            if n in ('spotlight', 'museum'):
                return 'spot'
            if n in ('streetlamp', 'back_alley'):
                return 'street'
            if n in ('neon', 'cyberpunk', 'disco', 'arcade'):
                return 'stylized'
            # fallback by first token if present
            if '_' in n:
                return n.split('_', 1)[0]
            return 'misc'
        except Exception:
            return 'misc'

    def cycle_light_presets(step=1):
        try:
            # Determine the active name list (group or all)
            active_group = getattr(store, 'current_light_group', None)
            names = None
            if active_group and getattr(store, 'group_to_names', None):
                names = store.group_to_names.get(active_group) or []
            if not names:
                names = getattr(store, 'available_light_presets', None)
            if not names:
                names = lighting_scan_presets('all')
            if not names:
                try:
                    renpy.show_screen("shader_notification", message="No lighting presets found", duration=1.6)
                except Exception:
                    renpy.notify('No lighting presets found')
                return False
            idx = int(getattr(store, 'current_light_preset_index', -1))
            idx = (idx + int(step)) % len(names)
            name = names[idx]
            store.current_light_preset_index = idx
            load_lighting(name)
            try:
                renpy.show_screen("shader_notification", message=f"Lighting: {name}", duration=1.6)
            except Exception:
                try:
                    renpy.notify(f"Lighting: {name}")
                except Exception:
                    pass
            return True
        except Exception:
            return False

    def lighting_groups():
        try:
            if not getattr(store, 'available_light_groups', None):
                lighting_scan_presets('all')
            return list(getattr(store, 'available_light_groups', []) or [])
        except Exception:
            return []

    def lighting_set_group(group_name=None):
        try:
            # None or 'all' clears group selection
            if not group_name or str(group_name).lower() == 'all':
                store.current_light_group = None
                store.current_light_group_index = -1
                store.current_light_preset_index = -1
                renpy.show_screen("shader_notification", message="Group: All", duration=1.2)
                return True
            groups = lighting_groups()
            g = str(group_name).lower()
            if g not in [x.lower() for x in groups]:
                renpy.show_screen("shader_notification", message=f"Group not found: {group_name}", duration=1.6)
                return False
            # set exact case from groups
            for real in groups:
                if real.lower() == g:
                    store.current_light_group = real
                    break
            store.current_light_group_index = [x.lower() for x in groups].index(g)
            store.current_light_preset_index = -1
            renpy.show_screen("shader_notification", message=f"Group: {store.current_light_group}", duration=1.2)
            return True
        except Exception:
            return False

    def cycle_light_groups(step=1):
        try:
            groups = lighting_groups()
            if not groups:
                renpy.show_screen("shader_notification", message="No groups", duration=1.2)
                return False
            idx = int(getattr(store, 'current_light_group_index', -1))
            idx = (idx + int(step)) % (len(groups) + 1)  # +1 for "All"
            if idx == len(groups):
                # All
                return lighting_set_group(None)
            store.current_light_group_index = idx
            store.current_light_group = groups[idx]
            store.current_light_preset_index = -1
            renpy.show_screen("shader_notification", message=f"Group: {groups[idx]}", duration=1.2)
            return True
        except Exception:
            return False

    def lighting_current_group_name():
        try:
            g = getattr(store, 'current_light_group', None)
            return g if g else 'All'
        except Exception:
            return 'All'

    def lighting_get_names_for_current_group():
        try:
            if not getattr(store, 'available_light_presets', None):
                lighting_scan_presets('all')
            active_group = getattr(store, 'current_light_group', None)
            if active_group and getattr(store, 'group_to_names', None):
                names = store.group_to_names.get(active_group) or []
                return list(names)
            return list(getattr(store, 'available_light_presets', []) or [])
        except Exception:
            return []

    def lighting_refresh_cache():
        try:
            lighting_scan_presets('all')
            return True
        except Exception:
            return False

    def lighting_apply_preset(name):
        """Load a preset by name and sync current indices to match UI selection."""
        try:
            if not name:
                return False
            names = lighting_get_names_for_current_group()
            if not names:
                lighting_refresh_cache()
                names = lighting_get_names_for_current_group()
            lname = str(name)
            load_lighting(lname)
            if names:
                try:
                    idx = names.index(lname)
                except ValueError:
                    idx = -1
                store.current_light_preset_index = idx
            try:
                renpy.show_screen("shader_notification", message=f"Lighting: {lname}", duration=1.6)
            except Exception:
                pass
            return True
        except Exception:
            return False

    def lighting_current_preset_name():
        try:
            names = getattr(store, 'available_light_presets', None)
            idx = int(getattr(store, 'current_light_preset_index', -1))
            if names and 0 <= idx < len(names):
                return names[idx]
            return None
        except Exception:
            return None
