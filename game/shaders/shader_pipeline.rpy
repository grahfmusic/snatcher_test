# Unified Shader Pipeline Helpers
# --------------------------------
# Centralizes ordering and activation of shader passes (lighting, bloom,
# colour grading, film grain, CRT) so UI and APIs pull from a single
# source of truth.

init -5 python:

    PIPELINE_ORDER = (
        "lighting",
        "bloom",
        "grade_live",
        "grade_preset",
        "grain",
        "crt",
    )

    def shader_pipeline_get_stack(include_meta=False):
        """Build the active shader stack.

        Args:
            include_meta: when True, return (stack, meta) where meta contains
                debug/state information for overlays.

        Returns:
            tuple of transforms (lighting -> bloom -> grade -> grain -> crt)
            or (stack, meta) when include_meta is True.
        """

        meta = {
            "order": PIPELINE_ORDER,
        }

        editing_mode = bool(getattr(store, 'shader_editor_open', False) or getattr(store, 'lighting_editor_open', False))
        meta["editing"] = editing_mode

        stack = []

        lt = _pipeline_lighting(meta)
        if lt:
            stack.append(lt)

        bt = _pipeline_bloom(meta)
        if bt:
            stack.append(bt)

        glive = _pipeline_live_grade(meta)
        if glive:
            stack.append(glive)

        gpreset = _pipeline_grade_preset(meta)
        if gpreset:
            stack.append(gpreset)

        grain = _pipeline_grain(meta)
        if grain:
            stack.append(grain)

        crt = _pipeline_crt(meta)
        if crt:
            stack.append(crt)

        if include_meta:
            meta["stack_count"] = len(stack)
            return tuple(stack), meta
        return tuple(stack)

    def shader_pipeline_reset():
        """Reset all shader-related store variables to defaults."""

        if hasattr(store, "shader_states"):
            for group in store.shader_states:
                try:
                    store.shader_states[group]["current"] = 0
                except Exception:
                    pass

        # Lighting
        try:
            store.dynamic_lights = []
        except Exception:
            store.dynamic_lights = []

        store.lights_count = 0
        store.lighting_strength = 1.0
        store.lighting_override_pos = None
        store.lighting_animated = False
        store.lighting_anim_override = {}
        try:
            if hasattr(store, 'lights_state') and isinstance(store.lights_state, dict):
                store.lights_state.update({
                    'active': [],
                    'enabled': False,
                    'dirty': False,
                })
        except Exception:
            pass

        if "lighting_sync_uniforms" in globals():
            try:
                lighting_sync_uniforms()
            except Exception:
                pass

        # Bloom
        store.bloom_enabled = False
        store.bloom_threshold = 0.75
        store.bloom_strength = 0.6
        store.bloom_radius = 2.5

        # Live grading
        store.color_grading_enabled = False
        store.shader_brightness = 0.0
        store.shader_contrast = 1.0
        store.color_saturation = 1.0
        store.color_temperature = 0.0
        store.color_tint = 0.0
        store.shader_gamma = 1.0
        store.grade_vignette_strength = 0.0
        store.grade_vignette_width = 0.25
        store.grade_vignette_feather = 1.0

        # Film grain
        store.film_grain_enabled = False
        store.film_grain_intensity = 0.0
        store.film_grain_size = 1.0
        store.film_grain_downscale = 2.0
        store.film_grain_anim_mode = "none"
        store.film_grain_anim_speed = 1.0
        store.film_grain_anim_amount = 0.0

        # CRT
        store.crt_enabled = False
        store.crt_animated = False
        store.crt_stable_state = False
        store.crt_warp = 0.2
        store.crt_scan = 0.5
        store.crt_chroma = 0.9
        store.crt_scanline_size = 1.0
        store.crt_aberr_mode = "none"
        store.crt_aberr_amount = 0.0
        store.crt_aberr_speed = 1.0
        store.crt_aberr_r = 1.0
        store.crt_aberr_g = 0.0
        store.crt_aberr_b = 1.0
        store.crt_glitch = 0.0
        store.crt_glitch_speed = 1.0
        store.crt_scanline_speed = 2.0
        store.crt_scanline_intensity = 0.1
        store.crt_vignette_strength = 0.35
        store.crt_vignette_width = 0.25
        store.crt_vignette_feather = 1.0

        renpy.restart_interaction()

    # ----- Stage helpers -------------------------------------------------

    def _pipeline_lighting(meta):
        if "lighting_scene_transform" not in globals():
            meta["lighting"] = {"active": False, "reason": "missing"}
            return None

        if getattr(store, "lights_layering_enabled", False):
            meta["lighting"] = {"active": False, "reason": "layered"}
            return None

        count = int(getattr(store, "lights_count", 0) or 0)
        if count <= 0:
            meta["lighting"] = {"active": False, "count": 0}
            return None

        meta["lighting"] = {
            "active": True,
            "count": count,
            "strength": float(getattr(store, "lighting_strength", 1.0)),
        }
        return lighting_scene_transform()

    def _pipeline_bloom(meta):
        enabled = bool(getattr(store, "bloom_enabled", False))
        threshold = float(getattr(store, "bloom_threshold", 0.75))
        strength = float(getattr(store, "bloom_strength", 0.6))
        radius = float(getattr(store, "bloom_radius", 2.5))

        meta["bloom"] = {
            "active": enabled,
            "threshold": threshold,
            "strength": strength,
            "radius": radius,
        }

        if enabled and "bloom_transform" in globals():
            return bloom_transform(threshold=threshold, strength=strength, radius=radius)
        return None

    def _pipeline_live_grade(meta):
        temp = float(getattr(store, "color_temperature", 0.0))
        tint = float(getattr(store, "color_tint", 0.0))
        sat = float(getattr(store, "color_saturation", 1.0))
        cont = float(getattr(store, "shader_contrast", 1.0))
        bright = float(getattr(store, "shader_brightness", 0.0))
        gam = float(getattr(store, "shader_gamma", 1.0))
        vig = float(getattr(store, "grade_vignette_strength", 0.0))
        vigw = float(getattr(store, "grade_vignette_width", 0.25))
        vigf = float(getattr(store, "grade_vignette_feather", 1.0))

        enabled = bool(getattr(store, "color_grading_enabled", False))
        has_adjustments = any([
            temp != 0.0,
            tint != 0.0,
            sat != 1.0,
            cont != 1.0,
            bright != 0.0,
            gam != 1.0,
            vig != 0.0,
        ])

        meta["grade_live"] = {
            "active": enabled,
            "enabled_flag": enabled,
            "has_adjustments": has_adjustments,
            "settings": {
                "temperature": temp,
                "tint": tint,
                "saturation": sat,
                "contrast": cont,
                "brightness": bright,
                "gamma": gam,
                "vignette_strength": vig,
                "vignette_width": vigw,
                "vignette_feather": vigf,
            }
        }

        if not enabled:
            return None

        if "complete_grading_transform" in globals():
            return complete_grading_transform(
                temperature=temp,
                tint=tint,
                saturation=sat,
                contrast=cont,
                brightness=bright,
                gamma=gam,
                vignette_amount=vig,
                vignette_softness=vigf,
            )
        return None

    def _pipeline_grade_preset(meta):
        preset_name = None
        preset_transform = None

        states = getattr(store, "shader_states", None)
        if states:
            cg_state = states.get("color_grading")
            if cg_state:
                idx = int(cg_state.get("current", 0) or 0)
                presets = list(cg_state.get("presets") or [])
                if 0 <= idx < len(presets):
                    preset_name = presets[idx]
                    if preset_name and preset_name.lower() != "off":
                        preset_transform = _resolve_color_grade_preset_transform(preset_name)

        meta["grade_preset"] = {
            "active": bool(preset_transform),
            "name": preset_name,
        }

        return preset_transform

    def _resolve_color_grade_preset_transform(preset_name):
        if not preset_name:
            return None
        fname = "color_grade_" + str(preset_name)
        if hasattr(store, fname):
            return getattr(store, fname)()
        alt = "color_grade_" + str(preset_name).replace("_", "")
        if hasattr(store, alt):
            return getattr(store, alt)()
        return None

    def _pipeline_grain(meta):
        # Keep grain disabled only when the lighting editor owns the screen so handles stay readable.
        if getattr(store, 'lighting_editor_open', False):
            meta["grain"] = {
                "active": False,
                "reason": "lighting_editor",
            }
            return None

        enabled = bool(getattr(store, "film_grain_enabled", False))
        intensity = float(getattr(store, "film_grain_intensity", 0.0))
        size = float(getattr(store, "film_grain_size", 1.0)) * 100.0
        downscale = float(getattr(store, "film_grain_downscale", 2.0))
        mode = str(getattr(store, "film_grain_anim_mode", "none")).lower()
        anim_speed = float(getattr(store, "film_grain_anim_speed", 1.0))
        anim_amount = float(getattr(store, "film_grain_anim_amount", 0.35))

        preset_name = None
        states = getattr(store, "shader_states", None)
        if states:
            grain_state = states.get("film_grain")
            if grain_state:
                idx = int(grain_state.get("current", 0) or 0)
                presets = list(grain_state.get("presets") or [])
                if 0 <= idx < len(presets):
                    preset_name = presets[idx]

        meta["grain"] = {
            "active": enabled and intensity > 0.0,
            "intensity": intensity,
            "size": size,
            "downscale": downscale,
            "anim_mode": mode,
            "anim_speed": anim_speed,
            "anim_amount": anim_amount,
            "preset": preset_name,
        }

        if enabled and intensity > 0.0 and "room_film_grain_overlay" in globals():
            anim_mode_value = 0.0
            if mode == "pulse":
                anim_mode_value = 1.0
            elif mode == "strobe":
                anim_mode_value = 2.0
            elif mode == "drift":
                anim_mode_value = 3.0
            return room_film_grain_overlay(
                grain_intensity=intensity,
                grain_size=size,
                downscale=downscale,
                anim_mode=anim_mode_value,
                anim_speed=anim_speed,
                anim_amount=anim_amount,
            )
        return None

    def _pipeline_crt(meta):
        # Allow CRT preview inside the shader editor; keep it off during the lighting editor to avoid UI glare on handles.
        if getattr(store, 'lighting_editor_open', False):
            meta["crt"] = {"active": False, "reason": "lighting_editor"}
            return None

        enabled = bool(getattr(store, "crt_enabled", False))
        meta["crt"] = {"active": enabled}
        if not enabled:
            return None

        warp = float(getattr(store, "crt_warp", 0.2))
        scan = float(getattr(store, "crt_scan", 0.5))
        chroma = float(getattr(store, "crt_chroma", 0.9))
        scanline_size = float(getattr(store, "crt_scanline_size", 1.0))
        vignette_strength = float(getattr(store, "grade_vignette_strength", 0.0))
        vignette_width = float(getattr(store, "grade_vignette_width", 0.25))
        vignette_feather = float(getattr(store, "grade_vignette_feather", 1.0))

        ab_mode_name = str(getattr(store, "crt_aberr_mode", "none")).lower()
        if ab_mode_name == "none":
            ab_mode = 0
        elif ab_mode_name == "pulse":
            ab_mode = 1
        elif ab_mode_name == "flicker":
            ab_mode = 2
        else:
            ab_mode = 3

        ab_amp = float(getattr(store, "crt_aberr_amount", chroma))
        ab_speed = float(getattr(store, "crt_aberr_speed", 1.0))
        ab_r = float(getattr(store, "crt_aberr_r", 1.0))
        ab_g = float(getattr(store, "crt_aberr_g", 0.0))
        ab_b = float(getattr(store, "crt_aberr_b", 1.0))

        glitch = float(getattr(store, "crt_glitch", 0.0))
        glitch_speed = float(getattr(store, "crt_glitch_speed", 1.0))
        scanline_speed = float(getattr(store, "crt_scanline_speed", 2.0))
        scanline_intensity = float(getattr(store, "crt_scanline_intensity", 0.1))

        animated = bool(getattr(store, "crt_animated", False))

        meta["crt"].update({
            "animated": animated,
            "aberr_mode": ab_mode_name,
            "glitch": glitch,
            "warp": warp,
            "scan": scan,
        })

        if animated and "animated_chroma_crt" in globals():
            return animated_chroma_crt(
                warp,
                scan,
                chroma,
                scanline_size,
                animation_intensity=scanline_intensity,
                animation_speed=scanline_speed,
                vignette_strength=vignette_strength,
                vignette_width=vignette_width,
                vignette_feather=vignette_feather,
                aberr_mode=ab_mode,
                aberr_amp=ab_amp,
                aberr_speed=ab_speed,
                aberr_r=ab_r,
                aberr_g=ab_g,
                aberr_b=ab_b,
                glitch=glitch,
                glitch_speed=glitch_speed,
            )

        if "static_chroma_crt" in globals():
            return static_chroma_crt(
                warp,
                scan,
                chroma,
                scanline_size,
                vignette_strength=vignette_strength,
                vignette_width=vignette_width,
                vignette_feather=vignette_feather,
                aberr_mode=ab_mode,
                aberr_amp=ab_amp,
                aberr_speed=ab_speed,
                aberr_r=ab_r,
                aberr_g=ab_g,
                aberr_b=ab_b,
                glitch=glitch,
                glitch_speed=glitch_speed,
            )

        return None
