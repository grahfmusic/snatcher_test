# Chest Strip Warp (MeshWarp-like) Displayable
# Approximates localized chest/shoulder/head breathing by overlaying horizontally-scaled
# center strips over a base sprite. Implemented purely in Python (no GLSL) so it
# composes cleanly with CRT/lighting and runs at the engine's frame cadence (vsync).

init python:
    import math
    from renpy.display.layout import DynamicDisplayable, LiveComposite
    from renpy.display.transform import Transform

    # Tuning variables (share existing names used by the shader tuner)
    # Global breathing toggles (default: effect disabled; components enabled)
    if not hasattr(renpy.store, 'breath_enabled'):
        renpy.store.breath_enabled = False
    if not hasattr(renpy.store, 'breath_use_chest'):
        renpy.store.breath_use_chest = True
    if not hasattr(renpy.store, 'breath_use_shoulder_left'):
        renpy.store.breath_use_shoulder_left = True
    if not hasattr(renpy.store, 'breath_use_shoulder_right'):
        renpy.store.breath_use_shoulder_right = True
    if not hasattr(renpy.store, 'breath_use_head'):
        renpy.store.breath_use_head = True
    if not hasattr(renpy.store, 'chest_breathe_period'):
        renpy.store.chest_breathe_period = 5.2
    if not hasattr(renpy.store, 'chest_breathe_amp'):
        renpy.store.chest_breathe_amp = 0.04
    if not hasattr(renpy.store, 'chest_breathe_center_v'):
        renpy.store.chest_breathe_center_v = 0.58
    if not hasattr(renpy.store, 'chest_breathe_half_v'):
        renpy.store.chest_breathe_half_v = 0.13
    if not hasattr(renpy.store, 'chest_breathe_center_u'):
        renpy.store.chest_breathe_center_u = 0.50
    if not hasattr(renpy.store, 'chest_breathe_half_u'):
        renpy.store.chest_breathe_half_u = 0.12
    if not hasattr(renpy.store, 'chest_breathe_head'):
        renpy.store.chest_breathe_head = 0.012
    if not hasattr(renpy.store, 'chest_breathe_debug'):
        renpy.store.chest_breathe_debug = 0.0

    # Shoulder tuning defaults (independent left/right)
    if not hasattr(renpy.store, 'shoulder_left_center_u'):
        renpy.store.shoulder_left_center_u = 0.34
    if not hasattr(renpy.store, 'shoulder_right_center_u'):
        renpy.store.shoulder_right_center_u = 0.66
    if not hasattr(renpy.store, 'shoulder_left_center_v'):
        renpy.store.shoulder_left_center_v = 0.42
    if not hasattr(renpy.store, 'shoulder_right_center_v'):
        renpy.store.shoulder_right_center_v = 0.42
    if not hasattr(renpy.store, 'shoulder_left_half_u'):
        renpy.store.shoulder_left_half_u = 0.10
    if not hasattr(renpy.store, 'shoulder_right_half_u'):
        renpy.store.shoulder_right_half_u = 0.10
    if not hasattr(renpy.store, 'shoulder_left_half_v'):
        renpy.store.shoulder_left_half_v = 0.06
    if not hasattr(renpy.store, 'shoulder_right_half_v'):
        renpy.store.shoulder_right_half_v = 0.06
    if not hasattr(renpy.store, 'shoulder_left_out_amp'):
        renpy.store.shoulder_left_out_amp = 0.02
    if not hasattr(renpy.store, 'shoulder_right_out_amp'):
        renpy.store.shoulder_right_out_amp = 0.02
    if not hasattr(renpy.store, 'shoulder_left_up_amp'):
        renpy.store.shoulder_left_up_amp = 0.004
    if not hasattr(renpy.store, 'shoulder_right_up_amp'):
        renpy.store.shoulder_right_up_amp = 0.004
    # Head region tuning defaults (restored)
    if not hasattr(renpy.store, 'head_center_u'):
        renpy.store.head_center_u = 0.50
    if not hasattr(renpy.store, 'head_center_v'):
        renpy.store.head_center_v = 0.18
    if not hasattr(renpy.store, 'head_half_u'):
        renpy.store.head_half_u = 0.10
    if not hasattr(renpy.store, 'head_half_v'):
        renpy.store.head_half_v = 0.08
    if not hasattr(renpy.store, 'head_up_amp'):
        renpy.store.head_up_amp = 0.006

    def _breath(st, period):
        # Smooth inhale/exhale 0..1..0 using cosine
        if period <= 0.01:
            return 0.0
        phase = (st % period) / period
        return 0.5 - 0.5 * math.cos(phase * 2.0 * math.pi)

    def chest_warp_displayable(img_path, target_w, target_h, strips=36, values_provider=None):
        """Return a DynamicDisplayable that draws a breathing warp for one sprite.

        - img_path: source image path
        - target_w/target_h: destination size in pixels (object xsize/ysize)
        - strips: number of horizontal strips to overlay (perf/quality tradeoff)
        - values_provider: callable -> dict of per-object values/toggles. If omitted,
          falls back to store defaults. Expected keys include:
          breath_enabled, breath_use_chest, breath_use_shoulder_left/right, breath_use_head,
          chest_breathe_* and shoulder/head parameters.
        """

        def _builder(st, at):
            # Fetch original size via helper if available; fallback to renpy.image_size.
            try:
                from renpy.store import get_original_size_by_path  # type: ignore
                osz = get_original_size_by_path(img_path)
            except Exception:
                try:
                    w, h = renpy.image_size(img_path)
                    osz = {"width": int(w), "height": int(h)}
                except Exception:
                    osz = {"width": int(target_w), "height": int(target_h)}
            ow = int(osz.get('width', 1) or 1)
            oh = int(osz.get('height', 1) or 1)
            sx = float(target_w) / float(ow)
            sy = float(target_h) / float(oh)

            # Breathing and weights (support per-object overrides via values_provider)
            vals = {}
            try:
                vals = (values_provider() if values_provider else {}) or {}
            except Exception:
                vals = {}

            period = float(vals.get('chest_breathe_period', getattr(renpy.store, 'chest_breathe_period', 5.2)))
            breath = _breath(st, period)
            amp = float(vals.get('chest_breathe_amp', getattr(renpy.store, 'chest_breathe_amp', 0.04)))
            cv = float(vals.get('chest_breathe_center_v', getattr(renpy.store, 'chest_breathe_center_v', 0.58)))
            hv = float(vals.get('chest_breathe_half_v', getattr(renpy.store, 'chest_breathe_half_v', 0.13)))
            cu = float(vals.get('chest_breathe_center_u', getattr(renpy.store, 'chest_breathe_center_u', 0.50)))
            hu = float(vals.get('chest_breathe_half_u', getattr(renpy.store, 'chest_breathe_half_u', 0.12)))
            # No head lift in chest warp (debug only)
            dbg = float(vals.get('chest_breathe_debug', getattr(renpy.store, 'chest_breathe_debug', 0.0)))

            # Build LiveComposite with base sprite and overlayed center strips
            parts = []
            # Base sprite goes first (unmodified besides global scaling)
            base = Transform(img_path, crop=(0, 0, ow, oh), xzoom=sx, yzoom=sy)
            parts.extend([(0, 0), base])

            # Chest overlay strips
            if bool(vals.get('breath_use_chest', getattr(renpy.store, 'breath_use_chest', True))):
                N = max(12, int(strips))
                for i in range(N):
                    y0 = int(round(i * oh / float(N)))
                    y1 = int(round((i + 1) * oh / float(N)))
                    sh = max(1, y1 - y0)
                    # Vertical center of this strip in [0,1]
                    v = (y0 + (sh * 0.5)) / float(oh)
                    # Vertical weight around chest band
                    wy = 0.0
                    dy = abs(v - cv)
                    if dy < hv and hv > 1e-6:
                        wy = math.cos((dy / hv) * math.pi) * 0.5 + 0.5
                    if wy <= 0.0:
                        continue  # no need to overlay this strip

                    # Center region horizontally (limit effect to torso center)
                    cx = int(round(cu * ow))
                    half_u_px = int(round(hu * ow))
                    x1 = max(0, cx - half_u_px)
                    x2 = min(ow, cx + half_u_px)
                    cw = max(1, x2 - x1)

                    # Effective scale for this strip
                    s = 1.0 + (amp * breath * wy)
                    # No head lift applied
                    y_shift = 0.0

                    # Scaled widths
                    cw_unscaled = cw * sx
                    cw_scaled = cw_unscaled * s
                    # Place center overlay centered on its original region
                    x_center = x1 * sx + cw_unscaled * 0.5
                    x_overlay = int(round(x_center - (cw_scaled * 0.5)))
                    y_overlay = int(round(y0 * sy + y_shift))

                    center_strip = Transform(img_path, crop=(x1, y0, cw, sh), xzoom=sx * s, yzoom=sy)
                    parts.extend([(x_overlay, y_overlay), center_strip])

                # Optional debug tint over the chest band area
                # Debug tint omitted in Python displayable to avoid import issues; use shader debug instead.

            # Left shoulder - anchor right edge
            if bool(vals.get('breath_use_shoulder_left', getattr(renpy.store, 'breath_use_shoulder_left', True))):
                lcv = float(vals.get('shoulder_left_center_v', getattr(renpy.store, 'shoulder_left_center_v', 0.42)))
                lhv = float(vals.get('shoulder_left_half_v', getattr(renpy.store, 'shoulder_left_half_v', 0.06)))
                lhu = float(vals.get('shoulder_left_half_u', getattr(renpy.store, 'shoulder_left_half_u', 0.10)))
                lcu = float(vals.get('shoulder_left_center_u', getattr(renpy.store, 'shoulder_left_center_u', 0.34)))
                lout = float(vals.get('shoulder_left_out_amp', getattr(renpy.store, 'shoulder_left_out_amp', 0.02)))
                lup = float(vals.get('shoulder_left_up_amp', getattr(renpy.store, 'shoulder_left_up_amp', 0.004)))
                l_y1 = int(round((lcv - lhv) * oh))
                l_y2 = int(round((lcv + lhv) * oh))
                l_h_px = max(1, l_y2 - l_y1)
                lx1 = int(round((lcu - lhu) * ow))
                lx2 = int(round((lcu + lhu) * ow))
                l_w_px = max(1, lx2 - lx1)
                sL = 1.0 + (lout * breath)
                l_right = int(round(lx2 * sx))
                l_scaled = int(round(l_w_px * sx * sL))
                l_x = l_right - l_scaled
                l_y = int(round(l_y1 * sy - (lup * breath * target_h)))
                left_strip = Transform(img_path, crop=(lx1, l_y1, l_w_px, l_h_px), xzoom=sx * sL, yzoom=sy)
                parts.extend([(l_x, l_y), left_strip])

            # Right shoulder - anchor left edge
            if bool(vals.get('breath_use_shoulder_right', getattr(renpy.store, 'breath_use_shoulder_right', True))):
                rcv = float(vals.get('shoulder_right_center_v', getattr(renpy.store, 'shoulder_right_center_v', 0.42)))
                rhv = float(vals.get('shoulder_right_half_v', getattr(renpy.store, 'shoulder_right_half_v', 0.06)))
                rhu = float(vals.get('shoulder_right_half_u', getattr(renpy.store, 'shoulder_right_half_u', 0.10)))
                rcu = float(vals.get('shoulder_right_center_u', getattr(renpy.store, 'shoulder_right_center_u', 0.66)))
                rout = float(vals.get('shoulder_right_out_amp', getattr(renpy.store, 'shoulder_right_out_amp', 0.02)))
                rup = float(vals.get('shoulder_right_up_amp', getattr(renpy.store, 'shoulder_right_up_amp', 0.004)))
                r_y1 = int(round((rcv - rhv) * oh))
                r_y2 = int(round((rcv + rhv) * oh))
                r_h_px = max(1, r_y2 - r_y1)
                rx1 = int(round((rcu - rhu) * ow))
                rx2 = int(round((rcu + rhu) * ow))
                r_w_px = max(1, rx2 - rx1)
                sR = 1.0 + (rout * breath)
                r_left = int(round(rx1 * sx))
                r_x = r_left
                r_y = int(round(r_y1 * sy - (rup * breath * target_h)))
                right_strip = Transform(img_path, crop=(rx1, r_y1, r_w_px, r_h_px), xzoom=sx * sR, yzoom=sy)
                parts.extend([(r_x, r_y), right_strip])

            # Head overlay (vertical lift only)
            if bool(vals.get('breath_use_head', getattr(renpy.store, 'breath_use_head', True))):
                hcvu = float(vals.get('head_center_u', getattr(renpy.store, 'head_center_u', 0.50)))
                hcv = float(vals.get('head_center_v', getattr(renpy.store, 'head_center_v', 0.18)))
                hhu = float(vals.get('head_half_u', getattr(renpy.store, 'head_half_u', 0.10)))
                hhv = float(vals.get('head_half_v', getattr(renpy.store, 'head_half_v', 0.08)))
                hup = float(vals.get('head_up_amp', getattr(renpy.store, 'head_up_amp', 0.006)))
                hx1 = int(round((hcvu - hhu) * ow))
                hx2 = int(round((hcvu + hhu) * ow))
                hy1 = int(round((hcv - hhv) * oh))
                hy2 = int(round((hcv + hhv) * oh))
                h_w_px = max(1, hx2 - hx1)
                h_h_px = max(1, hy2 - hy1)
                h_x = int(round(hx1 * sx))
                h_y = int(round(hy1 * sy - (hup * breath * target_h)))
                head_strip = Transform(img_path, crop=(hx1, hy1, h_w_px, h_h_px), xzoom=sx, yzoom=sy)
                parts.extend([(h_x, h_y), head_strip])

            comp = LiveComposite((int(target_w), int(target_h)), *parts)
            # Return 0 to update every frame; Ren'Py's renderer will sync
            # to the monitor refresh rate when vsync is enabled (default).
            return comp, 0

        return DynamicDisplayable(_builder)
