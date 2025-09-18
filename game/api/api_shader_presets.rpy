# Shader Preset IO API (YAML)
# Load and save simplified YAML presets for shader effects.

init -1 python:
    import os
    try:
        import yaml
    except Exception:
        # Fallback: attempt relative import from bundled python-packages
        import sys
        sys.path.append(os.path.join(config.gamedir, 'python-packages'))
        import yaml

    def _preset_base_dir():
        # Game directory (place presets under game/yaml)
        try:
            return config.gamedir
        except Exception:
            return "."

    def _resolve_preset_path(path, for_write=False):
        """Resolve a preset path.
        - New layout: 'yaml/shaders/preset/<name>.yaml' (shipped), 'yaml/shaders/custom/<name>.yaml' (user)
        - Back-compat: map 'json/presets/shaders' -> 'yaml/shaders/preset', 'json/custom/shaders' -> 'yaml/shaders/custom'
        - If relative without 'yaml/', assume under 'yaml/' at game dir.
        - Returns (abs_path, exists_bool)
        """
        if not path:
            return None, False
        p = str(path)
        if os.path.isabs(p):
            return p, os.path.exists(p)
        # Normalise legacy segment names and optional leading 'json/'
        p_norm = p
        if p_norm.startswith("json/"):
            p_norm = p_norm[len("json/"):]
        if p_norm.startswith("yaml/"):
            p_norm = p_norm[len("yaml/"):]
        # Replace legacy folders and root segments
        p_norm = p_norm.replace("shader_presets/", "shaders/preset/")
        p_norm = p_norm.replace("shader_custom/", "shaders/custom/")
        p_norm = p_norm.replace("presets/shaders/", "shaders/preset/")
        p_norm = p_norm.replace("custom/shaders/", "shaders/custom/")
        # Default to shaders/preset if bare filename given
        if not (p_norm.startswith("shaders/")):
            # assume shader preset
            p_norm = os.path.join("shaders", "preset", p_norm)
        # Ensure yaml extension
        if p_norm.endswith('.json'):
            p_norm = p_norm[:-5] + '.yaml'
        if not (p_norm.endswith('.yaml') or p_norm.endswith('.yml')):
            p_norm = p_norm + '.yaml'
        base = _preset_base_dir()
        abs_p = os.path.join(base, "yaml", p_norm)
        if for_write:
            d = os.path.dirname(abs_p)
            try:
                if not os.path.exists(d):
                    os.makedirs(d)
            except Exception:
                pass
        return abs_p, os.path.exists(abs_p)

    def shader_preset_list(kind="all"):
        """List available preset files.
        kind: 'shipped' -> yaml/shaders/preset, 'custom' -> yaml/shaders/custom, 'all' -> both
        Returns list of paths relative to 'yaml/' (e.g., 'shaders/preset/noir.yaml')
        """
        base = _preset_base_dir()
        results = []
        def scan(sub):
            root = os.path.join(base, "yaml", "shaders", sub)
            if os.path.isdir(root):
                for name in os.listdir(root):
                    if name.lower().endswith(('.yaml', '.yml')):
                        results.append(f"shaders/{sub}/{name}")
        if kind in ("shipped", "all"):
            scan("preset")
        if kind in ("custom", "all"):
            scan("custom")
        return sorted(results)

    def shader_preset_list_effect(kind="all", effect="lighting"):
        """List preset files that contain a specific effect block.
        effect: one of 'crt'|'grain'|'color_grade'/'color_grading'|'lighting' (case-insensitive, colour variants supported)
        Returns list of paths relative to 'yaml/'.
        """
        files = shader_preset_list(kind)
        out = []
        base = _preset_base_dir()
        effect_keys = []
        filename_prefixes = []
        e = str(effect).strip().lower()
        if e in ("color_grade", "color_grading", "colour_grade", "colour_grading"):
            effect_keys = ["color_grade", "color_grading", "colour_grade", "colour_grading"]
            filename_prefixes = ["grade_", "grading_"]
        elif e == "crt":
            effect_keys = ["crt", "CRT"]
            filename_prefixes = ["crt_"]
        elif e in ("grain", "film_grain"):
            effect_keys = ["grain", "film_grain"]
            filename_prefixes = ["grain_"]
        else:
            effect_keys = ["lighting"]
            filename_prefixes = ["light_", "lighting_"]
        
        for rel in files:
            # First filter by filename prefix for efficiency
            filename = os.path.basename(rel).lower()
            if filename_prefixes and not any(filename.startswith(prefix) for prefix in filename_prefixes):
                continue
            abs_p = os.path.join(base, "yaml", rel)
            try:
                with open(abs_p, 'r', encoding='utf-8') as f:
                    data = yaml.safe_load(f) or {}
                effects = data.get("effects", {})
                for k in effect_keys:
                    if k in effects:
                        out.append(rel)
                        break
            except Exception:
                continue
        return sorted(out)

    def shader_preset_save_lighting_file(path):
        """Save only the current 'lighting' effect to a YAML file under yaml/.
        The resulting file contains effects: { "lighting": { ... } } only.
        """
        abs_p, _ = _resolve_preset_path(path, for_write=True)
        if not abs_p:
            return False
        try:
            # Position (normalised) -> pixels
            try:
                ox, oy = getattr(store, 'lighting_override_pos', (None, None))
            except Exception:
                ox, oy = (None, None)
            data = {
                "version": "2.0",
                "effects": {
                    "lighting": {
                    }
                }
            }
            # Preset name from registry
            try:
                data["effects"]["lighting"]["preset"] = get_current_shader_preset("lighting")
            except Exception:
                data["effects"]["lighting"]["preset"] = "off"
            # Strength
            try:
                data["effects"]["lighting"]["strength"] = float(getattr(store, 'lighting_strength', 1.0))
            except Exception:
                pass
            # Position to pixels if available
            if ox is not None and oy is not None:
                try:
                    sx = float(config.screen_width)
                    sy = float(config.screen_height)
                    data["effects"]["lighting"]["x"] = int(round(float(ox) * sx))
                    data["effects"]["lighting"]["y"] = int(round(float(oy) * sy))
                except Exception:
                    pass
            # Animation override if present
            try:
                anim = getattr(store, 'lighting_anim_override', None)
                if anim:
                    data["effects"]["lighting"]["animation"] = dict(anim)
            except Exception:
                pass
            with open(abs_p, 'w', encoding='utf-8') as f:
                yaml.safe_dump(data, f, sort_keys=False)
            try:
                renpy.show_screen("shader_notification", message=f"Lighting preset saved: {os.path.basename(abs_p)}", duration=1.6)
            except Exception:
                pass
            return True
        except Exception:
            try:
                renpy.notify("Failed to save lighting preset")
            except Exception:
                pass
            return False

    def _migrate_vignette_to_grade(data):
        """Migrate vignette keys from CRT to colour grading for backward compatibility.
        
        Returns the modified data dict with vignette moved from effects.crt to effects.color_grade.
        """
        try:
            if not isinstance(data, dict):
                return data
                
            effects = data.get("effects", {})
            if not isinstance(effects, dict):
                return data
                
            # Check version - only migrate if < 2.1 or missing version
            version = data.get("version", "1.0")
            try:
                version_num = float(version)
                if version_num >= 2.1:
                    return data  # Already migrated
            except (ValueError, TypeError):
                pass  # Treat as old version
            
            crt = effects.get("crt")
            if not isinstance(crt, dict):
                return data
            
            # Check if vignette keys exist in CRT
            vignette_keys = ["vignette", "vignette_width", "vignette_feather"]
            has_vignette = any(key in crt for key in vignette_keys)
            
            if has_vignette:
                # Ensure color_grade section exists
                if "color_grade" not in effects:
                    effects["color_grade"] = {}
                elif not isinstance(effects["color_grade"], dict):
                    effects["color_grade"] = {}
                
                grade = effects["color_grade"]
                
                # Migrate vignette keys with renaming
                if "vignette" in crt:
                    grade["vignette_strength"] = crt.pop("vignette")
                if "vignette_width" in crt:
                    grade["vignette_width"] = crt.pop("vignette_width")
                if "vignette_feather" in crt:
                    grade["vignette_feather"] = crt.pop("vignette_feather")
                
                # Update version to indicate migration completed
                data["version"] = "2.1"
                
            return data
        except Exception:
            return data  # Return unchanged on any error
    
    def _apply_crt_block(crt):
        if crt is None or not hasattr(crt, 'get'):
            return
        try:
            # Core enable
            if "enabled" in crt:
                store.crt_enabled = bool(crt.get("enabled"))
                # Also set a stable flag to avoid state flipping
                store.crt_stable_state = store.crt_enabled

            # Map 'aberration' -> chroma (compat)
            warp = crt.get("warp")
            scan = crt.get("scan")
            chroma = crt.get("aberration", crt.get("chroma"))
            scanline_size = crt.get("scanline_size")
            if any(v is not None for v in (warp, scan, chroma, scanline_size)):
                set_crt_parameters(
                    warp=(getattr(store, 'crt_warp', 0.2) if warp is None else float(warp)),
                    scan=(getattr(store, 'crt_scan', 0.5) if scan is None else float(scan)),
                    chroma=(getattr(store, 'crt_chroma', 0.9) if chroma is None else float(chroma)),
                    scanline_size=(getattr(store, 'crt_scanline_size', 1.0) if scanline_size is None else float(scanline_size)),
                )
                # Keep aberration amount aligned with chroma setting
                try:
                    if chroma is not None:
                        store.crt_aberr_amount = float(chroma)
                except Exception:
                    pass

            # Vignette handling moved to colour grading section (v2.1+)
            # Legacy vignette keys in CRT are ignored after migration

            # Per-channel aberration scaling (optional)
            if "aberration_r" in crt:
                try:
                    store.crt_aberr_r = float(crt.get("aberration_r", 1.0))
                except Exception:
                    pass
            if "aberration_g" in crt:
                try:
                    store.crt_aberr_g = float(crt.get("aberration_g", 0.0))
                except Exception:
                    pass
            if "aberration_b" in crt:
                try:
                    store.crt_aberr_b = float(crt.get("aberration_b", 1.0))
                except Exception:
                    pass

            # Animation and effects
            if "animated" in crt:
                try:
                    store.crt_animated = bool(crt.get("animated"))
                except Exception:
                    pass
            if "aberration_mode" in crt:
                try:
                    store.crt_aberr_mode = str(crt.get("aberration_mode"))
                except Exception:
                    pass
            if "aberration_speed" in crt:
                try:
                    store.crt_aberr_speed = float(crt.get("aberration_speed"))
                except Exception:
                    pass
            if "glitch" in crt:
                try:
                    store.crt_glitch = float(crt.get("glitch"))
                except Exception:
                    pass
            if "glitch_speed" in crt:
                try:
                    store.crt_glitch_speed = float(crt.get("glitch_speed"))
                except Exception:
                    pass
        except Exception:
            pass

    def _apply_grain_block(grain):
        if grain is None or not hasattr(grain, 'get'):
            return
        try:
            preset = grain.get("preset")
            if preset:
                set_grain(str(preset))
                # Don't return here - apply additional manual params if present
            
            # Manual intensity override (for legacy or custom tuning)
            intensity = grain.get("intensity")
            if intensity is not None:
                v = float(intensity)
                store.film_grain_intensity = v
                store.film_grain_enabled = v > 0.01
            
            # Additional grain parameters
            if "size" in grain:
                try:
                    store.film_grain_size = float(grain.get("size", 1.0))
                except Exception:
                    pass
            if "downscale" in grain:
                try:
                    store.film_grain_downscale = float(grain.get("downscale", 2.0))
                except Exception:
                    pass
            if "anim_mode" in grain:
                try:
                    store.film_grain_anim_mode = str(grain.get("anim_mode", "none"))
                except Exception:
                    pass
            if "anim_speed" in grain:
                try:
                    store.film_grain_anim_speed = float(grain.get("anim_speed", 1.0))
                except Exception:
                    pass
            if "anim_amount" in grain:
                try:
                    store.film_grain_anim_amount = float(grain.get("anim_amount", 0.35))
                except Exception:
                    pass
        except Exception:
            pass

    def _apply_grade_block(grade):
        if grade is None or not hasattr(grade, 'get'):
            return
        try:
            # Preset name (if any)
            preset = grade.get("preset") or grade.get("name")
            if preset:
                set_grade(str(preset))
            # Extended controls: brightness/contrast/saturation/temperature/tint/gamma
            if "brightness" in grade:
                try:
                    store.shader_brightness = float(grade.get("brightness", 0.0))
                    store.color_grading_enabled = True
                except Exception:
                    pass
            if "contrast" in grade:
                try:
                    store.shader_contrast = float(grade.get("contrast", 1.0))
                    store.color_grading_enabled = True
                except Exception:
                    pass
            if "saturation" in grade:
                try:
                    store.color_saturation = float(grade.get("saturation", 1.0))
                    store.color_grading_enabled = True
                except Exception:
                    pass
            if "temperature" in grade:
                try:
                    store.color_temperature = float(grade.get("temperature", 0.0))
                    store.color_grading_enabled = True
                except Exception:
                    pass
            if "tint" in grade:
                try:
                    store.color_tint = float(grade.get("tint", 0.0))
                    store.color_grading_enabled = True
                except Exception:
                    pass
            if "gamma" in grade:
                try:
                    store.shader_gamma = float(grade.get("gamma", 1.0))
                    store.color_grading_enabled = True
                except Exception:
                    pass
            
            # Vignette controls (v2.1+)
            if "vignette_strength" in grade:
                try:
                    store.grade_vignette_strength = float(grade.get("vignette_strength", 0.0))
                    store.color_grading_enabled = True
                except Exception:
                    pass
            if "vignette_width" in grade:
                try:
                    store.grade_vignette_width = float(grade.get("vignette_width", 0.25))
                    store.color_grading_enabled = True
                except Exception:
                    pass
            if "vignette_feather" in grade:
                try:
                    store.grade_vignette_feather = float(grade.get("vignette_feather", 1.0))
                    store.color_grading_enabled = True
                except Exception:
                    pass
        except Exception:
            pass

    def _apply_lighting_block(light):
        if light is None or not hasattr(light, 'get'):
            return
        try:
            preset = light.get("preset") or light.get("name")
            if preset:
                set_light(str(preset))
            # Optional strength
            if "strength" in light:
                try:
                    store.lighting_strength = float(light.get("strength", 1.0))
                    store.suppress_room_fade_once = True
                except Exception:
                    pass
            # Optional position (pixels or normalised 0..1)
            x = light.get("x")
            y = light.get("y")
            if x is not None and y is not None:
                try:
                    sx = float(config.screen_width)
                    sy = float(config.screen_height)
                    fx = float(x)
                    fy = float(y)
                    # Treat values <= 1.0 as already normalised
                    nx = fx if fx <= 1.0 else (fx / max(1.0, sx))
                    ny = fy if fy <= 1.0 else (fy / max(1.0, sy))
                    nx = max(0.0, min(1.0, nx))
                    ny = max(0.0, min(1.0, ny))
                    store.lighting_override_pos = (nx, ny)
                except Exception:
                    pass
            # Optional animation (string or object)
            anim = light.get("animation") or light.get("anim")
            if anim is not None:
                # Enable animations globally
                store.lighting_animated = True
                ov = {}
                if isinstance(anim, str):
                    kind = anim.strip().lower()
                    if kind in ("pulse", "breathe", "flicker"):
                        ov = {"mode": "pulse", "amount": 0.35, "speed": 1.2 if kind != "flicker" else 2.0}
                    elif kind in ("orbit", "sweep"):
                        ov = {"mode": "orbit", "radius": 0.05, "speed": 0.6}
                elif isinstance(anim, dict):
                    ov = dict(anim)
                    # Normalise key
                    if "type" in ov and "mode" not in ov:
                        ov["mode"] = str(ov.get("type"))
                if ov:
                    store.lighting_anim_override = ov
        except Exception:
            pass

    def shader_preset_apply_file(path):
        """Apply a simplified preset YAML file to current shader state.
        Accepts 'yaml/shaders/preset/foo.yaml' or 'shaders/preset/foo.yaml'.
        """
        abs_p, exists = _resolve_preset_path(path, for_write=False)
        if not abs_p or not exists:
            try:
                renpy.notify(f"Preset not found: {path}")
            except Exception:
                pass
            return False
        try:
            with open(abs_p, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
            
            # Migrate vignette from CRT to colour grading if needed
            data = _migrate_vignette_to_grade(data)
            
            effects = (data or {}).get("effects", {})
            
            crt_block = effects.get("crt") or effects.get("CRT")
            grain_block = effects.get("grain") or effects.get("film_grain")
            grade_block = effects.get("color_grade") or effects.get("color_grading") or effects.get("colour_grade") or effects.get("colour_grading")
            lighting_block = effects.get("lighting")
            
            # Accept both color_grade/color_grading and colour_*
            _apply_crt_block(crt_block)
            _apply_grain_block(grain_block)
            _apply_grade_block(grade_block)
            _apply_lighting_block(lighting_block)
            try:
                renpy.show_screen("shader_notification", message=f"Preset applied: {os.path.basename(abs_p)}", duration=1.8)
            except Exception:
                pass
            store.suppress_room_fade_once = True
            renpy.restart_interaction()
            return True
        except Exception as e:
            try:
                renpy.notify("Failed to load preset")
            except Exception:
                pass
            return False

    def shader_preset_save_file(path):
        """Save current shader state to a simplified preset YAML file."""
        abs_p, _ = _resolve_preset_path(path, for_write=True)
        if not abs_p:
            return False
        try:
            # Collect current state
            def cur(name):
                try:
                    return get_current_shader_preset(name)
                except Exception:
                    return "off"
            # Lighting overrides (optional)
            try:
                ox, oy = getattr(store, 'lighting_override_pos', (None, None))
            except Exception:
                ox, oy = (None, None)
            try:
                anim = getattr(store, 'lighting_anim_override', None)
            except Exception:
                anim = None
            data = {
                "version": "2.1",
                "effects": {
                    "crt": {
                        "enabled": bool(getattr(store, 'crt_enabled', False)),
                        "aberration": float(getattr(store, 'crt_aberr_amount', getattr(store, 'crt_chroma', 0.9))),
                        "aberration_r": float(getattr(store, 'crt_aberr_r', 1.0)),
                        "aberration_g": float(getattr(store, 'crt_aberr_g', 0.0)),
                        "aberration_b": float(getattr(store, 'crt_aberr_b', 1.0)),
                        "warp": float(getattr(store, 'crt_warp', 0.2)),
                        "scan": float(getattr(store, 'crt_scan', 0.5)),
                        "scanline_size": float(getattr(store, 'crt_scanline_size', 1.0)),
                        "animated": bool(getattr(store, 'crt_animated', False)),
                        "aberration_mode": str(getattr(store, 'crt_aberr_mode', 'none')),
                        "aberration_speed": float(getattr(store, 'crt_aberr_speed', 1.0)),
                        "glitch": float(getattr(store, 'crt_glitch', 0.0)),
                        "glitch_speed": float(getattr(store, 'crt_glitch_speed', 1.5)),
                    },
                    "grain": {
                        "preset": cur("film_grain"),
                        "intensity": float(getattr(store, 'film_grain_intensity', 0.02)),
                        "size": float(getattr(store, 'film_grain_size', 1.0)),
                        "downscale": float(getattr(store, 'film_grain_downscale', 2.0)),
                        "anim_mode": str(getattr(store, 'film_grain_anim_mode', 'none')),
                        "anim_speed": float(getattr(store, 'film_grain_anim_speed', 1.0)),
                        "anim_amount": float(getattr(store, 'film_grain_anim_amount', 0.35))
                    },
                    "color_grade": {
                        "preset": cur("color_grading"),
                        "brightness": float(getattr(store, 'shader_brightness', 0.0)),
                        "contrast": float(getattr(store, 'shader_contrast', 1.0)),
                        "saturation": float(getattr(store, 'color_saturation', 1.0)),
                        "temperature": float(getattr(store, 'color_temperature', 0.0)),
                        "tint": float(getattr(store, 'color_tint', 0.0)),
                        "gamma": float(getattr(store, 'shader_gamma', 1.0)),
                        "vignette_strength": float(getattr(store, 'grade_vignette_strength', 0.0)),
                        "vignette_width": float(getattr(store, 'grade_vignette_width', 0.25)),
                        "vignette_feather": float(getattr(store, 'grade_vignette_feather', 1.0))
                    },
                    "lighting": {
                        "preset": cur("lighting"),
                        "strength": float(getattr(store, 'lighting_strength', 1.0))
                    }
                }
            }
            if ox is not None and oy is not None:
                # Persist normalised coordinates scaled to pixels (screen space)
                try:
                    sx = float(config.screen_width)
                    sy = float(config.screen_height)
                    data["effects"]["lighting"]["x"] = int(round(float(ox) * sx))
                    data["effects"]["lighting"]["y"] = int(round(float(oy) * sy))
                except Exception:
                    pass
            if anim:
                try:
                    data["effects"]["lighting"]["animation"] = dict(anim)
                except Exception:
                    pass
            with open(abs_p, 'w', encoding='utf-8') as f:
                yaml.safe_dump(data, f, sort_keys=False)
            try:
                renpy.show_screen("shader_notification", message=f"Preset saved: {os.path.basename(abs_p)}", duration=1.8)
            except Exception:
                pass
            return True
        except Exception:
            try:
                renpy.notify("Failed to save preset")
            except Exception:
                pass
            return False
