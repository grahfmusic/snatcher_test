# 2D Lighting Shader (Single-Pass, Point/Spot)
#
# - Applies lighting directly over the scene content via a full-frame shader.
# - Supports up to MAX_LIGHTS lights with point and spot types.
# - Uniforms are packed into vec4 per-light to simplify binding from Ren'Py.

init -5 python:
    MAX_LIGHTS = 8

    # Register the lighting shader
    renpy.register_shader(
        "lighting_2d",
        variables="""
            uniform sampler2D tex0;
            uniform float u_lod_bias;

            uniform float u_strength;     // Global strength multiplier
            uniform float u_light_count;   // Active light count (0..MAX_LIGHTS)
            uniform float u_layer_select;  // 0 = all, 1 = back, 2 = front

            // Per-light packed uniforms (vec4):
            // u_lN = (px, py, radius, type)      type: 0=point, 1=spot
            // u_cN = (r, g, b, intensity)
            // u_sN = (dx, dy, angle, layer)      layer: 0=all,1=back,2=front
            // u_fN = (falloff_mode, falloff_exp, bloom_boost, pad)
            uniform vec4 u_l0;
            uniform vec4 u_c0;
            uniform vec4 u_s0;
            uniform vec4 u_f0;
            uniform vec4 u_l1;
            uniform vec4 u_c1;
            uniform vec4 u_s1;
            uniform vec4 u_f1;
            uniform vec4 u_l2;
            uniform vec4 u_c2;
            uniform vec4 u_s2;
            uniform vec4 u_f2;
            uniform vec4 u_l3;
            uniform vec4 u_c3;
            uniform vec4 u_s3;
            uniform vec4 u_f3;
            uniform vec4 u_l4;
            uniform vec4 u_c4;
            uniform vec4 u_s4;
            uniform vec4 u_f4;
            uniform vec4 u_l5;
            uniform vec4 u_c5;
            uniform vec4 u_s5;
            uniform vec4 u_f5;
            uniform vec4 u_l6;
            uniform vec4 u_c6;
            uniform vec4 u_s6;
            uniform vec4 u_f6;
            uniform vec4 u_l7;
            uniform vec4 u_c7;
            uniform vec4 u_s7;
            uniform vec4 u_f7;

            attribute vec2 a_tex_coord;
            varying vec2 v_tex_coord;
        """,
        vertex_300="""
            v_tex_coord = a_tex_coord;
        """,
        fragment_300="""
            vec2 uv = v_tex_coord;
            vec4 color = texture2D(tex0, uv, u_lod_bias);

            vec3 add = vec3(0.0);
            int count = int(min(max(u_light_count + 0.5, 0.0), 8.0));

            for (int i = 0; i < 8; i++) {
                if (i >= count) break;
                vec4 L; vec4 C; vec4 S; vec4 F;
                if (i==0) { L=u_l0; C=u_c0; S=u_s0; F=u_f0; }
                else if (i==1) { L=u_l1; C=u_c1; S=u_s1; F=u_f1; }
                else if (i==2) { L=u_l2; C=u_c2; S=u_s2; F=u_f2; }
                else if (i==3) { L=u_l3; C=u_c3; S=u_s3; F=u_f3; }
                else if (i==4) { L=u_l4; C=u_c4; S=u_s4; F=u_f4; }
                else if (i==5) { L=u_l5; C=u_c5; S=u_s5; F=u_f5; }
                else if (i==6) { L=u_l6; C=u_c6; S=u_s6; F=u_f6; }
                else { L=u_l7; C=u_c7; S=u_s7; F=u_f7; }

                float intensity = C.a;
                if (intensity <= 0.0) continue;

                vec2 pos = L.xy;       // normalized [0,1]
                float radius = max(L.z, 1e-4);
                float ltype = L.w;     // 0.0 point, 1.0 spot
                vec3 lcolor = C.rgb;
                vec2 dir = S.xy;       // not required for point
                float angle = max(S.z, 1e-4);

                vec2 to_p = uv - pos;
                float dist = length(to_p);

                // Radial falloff (selectable)
                float mode = F.x;
                float fexp = max(F.y, 0.01);
                float nr = clamp(dist / radius, 0.0, 1.0);
                float radial = 0.0;
                if (mode < 0.5) {
                    // smooth
                    radial = 1.0 - smoothstep(radius * 0.2, radius, dist);
                } else if (mode < 1.5) {
                    // linear
                    radial = 1.0 - nr;
                } else if (mode < 2.5) {
                    // quadratic
                    radial = 1.0 - nr*nr;
                } else if (mode < 3.5) {
                    // inverse square (normalized)
                    radial = 1.0 / (1.0 + nr*nr);
                } else {
                    // custom exponent on linear ramp
                    radial = pow(max(1.0 - nr, 0.0), fexp);
                }
                radial = clamp(radial, 0.0, 1.0);

                // Spot factor inline
                float spotf = 1.0;
                if (ltype > 0.5) {
                    float d = dist;
                    if (d <= 1e-6) {
                        spotf = 1.0;
                    } else {
                        vec2 Ln = to_p / d;
                        vec2 dn = normalize(dir);
                        float cosang = dot(Ln, dn);
                        float coscut = cos(angle);
                        spotf = clamp((cosang - coscut) / max(1e-4, (1.0 - coscut)), 0.0, 1.0);
                    }
                }

                // Layer selection (S.w encodes 0=all, 1=back, 2=front)
                if (u_layer_select > 0.5) {
                    // If shader is in layer-specific mode, skip non-matching lights
                    if (abs(S.w - u_layer_select) > 0.1) {
                        continue;
                    }
                }

                float a = radial * spotf;
                add += lcolor * (intensity * a);
            }

            // Apply global strength and clamp
            color.rgb = clamp(color.rgb + add * u_strength, 0.0, 1.0);
            gl_FragColor = color;
        """
    )

    # Defaults for uniforms and counts
    if not hasattr(store, 'lighting_strength'):
        store.lighting_strength = 1.0
    if not hasattr(store, 'lights_count'):
        store.lights_count = 0
    if not hasattr(store, 'lights_layering_enabled'):
        store.lights_layering_enabled = True

    # Each uniform gets a default vec4
    def _reset_light_uniforms():
        zeros = (0.0, 0.0, 0.0, 0.0)
        for idx in range(MAX_LIGHTS):
            setattr(store, f'lights_u_l{idx}', zeros)
            setattr(store, f'lights_u_c{idx}', (0.0, 0.0, 0.0, 0.0))
            setattr(store, f'lights_u_s{idx}', (1.0, 0.0, 0.785398, 0.0))  # dir=(1,0), angle=~45deg, layer=all
            setattr(store, f'lights_u_f{idx}', (0.0, 1.0, 1.0, 0.0))      # falloff=smooth, exp=1.0, bloom_boost=1.0
    _reset_light_uniforms()

    def _parse_color_rgb(c):
        if isinstance(c, (list, tuple)) and len(c) >= 3:
            try:
                return (float(c[0]), float(c[1]), float(c[2]))
            except Exception:
                return (1.0, 1.0, 1.0)
        if isinstance(c, basestring if 'basestring' in globals() else str):
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

    def lighting_sync_uniforms():
        """Build packed uniforms from store.dynamic_lights (compat with api_simple_fx).

        dynamic_lights entries: {
          'kind': 'point'|'spot'|'area', 'pos':(x,y), 'color':(r,g,b), 'intensity':f,
          'radius':f, 'dir':(dx,dy), 'angle':f
        }
        """
        try:
            base = getattr(store, 'dynamic_lights', []) or []
            lights = [e for e in base if bool(e.get('enabled', True))]
        except Exception:
            lights = []

        cnt = min(len(lights), MAX_LIGHTS)
        store.lights_count = int(cnt)

        for i in range(MAX_LIGHTS):
            if i < cnt:
                e = lights[i]
                kind = str(e.get('kind', 'point')).lower()
                ltype = 0.0 if kind == 'point' else 1.0
                px, py = e.get('pos', (0.5, 0.5))
                radius = float(e.get('radius', 0.3))
                r, g, b = _parse_color_rgb(e.get('color', (1.0, 1.0, 1.0)))
                inten = float(e.get('intensity', 1.0))
                dx, dy = e.get('dir', (1.0, 0.0))
                ang = float(e.get('angle', 0.785398))  # ~45° default

                setattr(store, f'lights_u_l{i}', (float(px), float(py), max(0.001, float(radius)), ltype))
                setattr(store, f'lights_u_c{i}', (float(r), float(g), float(b), max(0.0, float(inten))))
                # Encode layer in S.w: 0=all/unspecified, 1=back, 2=front
                layer = 0.0
                try:
                    lay = str(e.get('layer', ''))
                    if 'back' in lay or lay == 'bg':
                        layer = 1.0
                    elif 'front' in lay or lay == 'objects':
                        layer = 2.0
                except Exception:
                    layer = 0.0
                setattr(store, f'lights_u_s{i}', (float(dx), float(dy), max(0.01, float(ang)), layer))
                # Falloff + bloom boost
                fmode = 0.0
                try:
                    fm = str(e.get('falloff', 'smooth')).lower()
                    if fm.startswith('lin'):
                        fmode = 1.0
                    elif fm.startswith('quad'):
                        fmode = 2.0
                    elif 'inv' in fm:
                        fmode = 3.0
                    elif fm.startswith('custom'):
                        fmode = 4.0
                    else:
                        fmode = 0.0
                except Exception:
                    fmode = 0.0
                fexp = 1.0
                try:
                    fexp = float(e.get('falloff_exp', 1.0))
                except Exception:
                    fexp = 1.0
                bboost = 1.0
                try:
                    bboost = float(e.get('bloom_boost', 1.0))
                except Exception:
                    bboost = 1.0
                setattr(store, f'lights_u_f{i}', (float(fmode), float(fexp), float(bboost), 0.0))
            else:
                # Zero out unused slots
                setattr(store, f'lights_u_l{i}', (0.0, 0.0, 0.0, 0.0))
                setattr(store, f'lights_u_c{i}', (0.0, 0.0, 0.0, 0.0))
                setattr(store, f'lights_u_s{i}', (1.0, 0.0, 0.785398, 0.0))
                setattr(store, f'lights_u_f{i}', (0.0, 1.0, 1.0, 0.0))

        # Optionally print debug
        if getattr(store, 'shader_debug_enabled', False) and cnt > 0:
            try:
                print(f"[LIGHTING_2D] Synced {cnt} lights; strength={getattr(store,'lighting_strength',1.0):.2f}")
            except Exception:
                pass

    # Ensure uniforms are synced at least once
    lighting_sync_uniforms()

# Full-frame transform applying the lighting shader
transform lighting_scene_transform():
    mesh True
    shader "lighting_2d"
    u_lod_bias 0.0
    u_strength (getattr(store, 'lighting_strength', 1.0))
    # If layering is enabled, make this pass a no-op by forcing zero lights
    u_light_count (0 if getattr(store, 'lights_layering_enabled', False) else getattr(store, 'lights_count', 0))
    u_layer_select 0.0
    u_l0 (getattr(store, 'lights_u_l0', (0.0,0.0,0.0,0.0)))
    u_c0 (getattr(store, 'lights_u_c0', (0.0,0.0,0.0,0.0)))
    u_s0 (getattr(store, 'lights_u_s0', (1.0,0.0,0.785398,0.0)))
    u_f0 (getattr(store, 'lights_u_f0', (0.0,1.0,1.0,0.0)))
    u_l1 (getattr(store, 'lights_u_l1', (0.0,0.0,0.0,0.0)))
    u_c1 (getattr(store, 'lights_u_c1', (0.0,0.0,0.0,0.0)))
    u_s1 (getattr(store, 'lights_u_s1', (1.0,0.0,0.785398,0.0)))
    u_f1 (getattr(store, 'lights_u_f1', (0.0,1.0,1.0,0.0)))
    u_l2 (getattr(store, 'lights_u_l2', (0.0,0.0,0.0,0.0)))
    u_c2 (getattr(store, 'lights_u_c2', (0.0,0.0,0.0,0.0)))
    u_s2 (getattr(store, 'lights_u_s2', (1.0,0.0,0.785398,0.0)))
    u_f2 (getattr(store, 'lights_u_f2', (0.0,1.0,1.0,0.0)))
    u_l3 (getattr(store, 'lights_u_l3', (0.0,0.0,0.0,0.0)))
    u_c3 (getattr(store, 'lights_u_c3', (0.0,0.0,0.0,0.0)))
    u_s3 (getattr(store, 'lights_u_s3', (1.0,0.0,0.785398,0.0)))
    u_f3 (getattr(store, 'lights_u_f3', (0.0,1.0,1.0,0.0)))
    u_l4 (getattr(store, 'lights_u_l4', (0.0,0.0,0.0,0.0)))
    u_c4 (getattr(store, 'lights_u_c4', (0.0,0.0,0.0,0.0)))
    u_s4 (getattr(store, 'lights_u_s4', (1.0,0.0,0.785398,0.0)))
    u_f4 (getattr(store, 'lights_u_f4', (0.0,1.0,1.0,0.0)))
    u_l5 (getattr(store, 'lights_u_l5', (0.0,0.0,0.0,0.0)))
    u_c5 (getattr(store, 'lights_u_c5', (0.0,0.0,0.0,0.0)))
    u_s5 (getattr(store, 'lights_u_s5', (1.0,0.0,0.785398,0.0)))
    u_f5 (getattr(store, 'lights_u_f5', (0.0,1.0,1.0,0.0)))
    u_l6 (getattr(store, 'lights_u_l6', (0.0,0.0,0.0,0.0)))
    u_c6 (getattr(store, 'lights_u_c6', (0.0,0.0,0.0,0.0)))
    u_s6 (getattr(store, 'lights_u_s6', (1.0,0.0,0.785398,0.0)))
    u_f6 (getattr(store, 'lights_u_f6', (0.0,1.0,1.0,0.0)))
    u_l7 (getattr(store, 'lights_u_l7', (0.0,0.0,0.0,0.0)))
    u_c7 (getattr(store, 'lights_u_c7', (0.0,0.0,0.0,0.0)))
    u_s7 (getattr(store, 'lights_u_s7', (1.0,0.0,0.785398,0.0)))
    u_f7 (getattr(store, 'lights_u_f7', (0.0,1.0,1.0,0.0)))

# Layer-specific transforms
transform lighting_back_transform():
    mesh True
    shader "lighting_2d"
    u_lod_bias 0.0
    u_strength (getattr(store, 'lighting_strength', 1.0))
    u_light_count (getattr(store, 'lights_count', 0))
    u_layer_select 1.0
    u_l0 (getattr(store, 'lights_u_l0', (0.0,0.0,0.0,0.0)))
    u_c0 (getattr(store, 'lights_u_c0', (0.0,0.0,0.0,0.0)))
    u_s0 (getattr(store, 'lights_u_s0', (1.0,0.0,0.785398,0.0)))
    u_f0 (getattr(store, 'lights_u_f0', (0.0,1.0,1.0,0.0)))
    u_l1 (getattr(store, 'lights_u_l1', (0.0,0.0,0.0,0.0)))
    u_c1 (getattr(store, 'lights_u_c1', (0.0,0.0,0.0,0.0)))
    u_s1 (getattr(store, 'lights_u_s1', (1.0,0.0,0.785398,0.0)))
    u_f1 (getattr(store, 'lights_u_f1', (0.0,1.0,1.0,0.0)))
    u_l2 (getattr(store, 'lights_u_l2', (0.0,0.0,0.0,0.0)))
    u_c2 (getattr(store, 'lights_u_c2', (0.0,0.0,0.0,0.0)))
    u_s2 (getattr(store, 'lights_u_s2', (1.0,0.0,0.785398,0.0)))
    u_f2 (getattr(store, 'lights_u_f2', (0.0,1.0,1.0,0.0)))
    u_l3 (getattr(store, 'lights_u_l3', (0.0,0.0,0.0,0.0)))
    u_c3 (getattr(store, 'lights_u_c3', (0.0,0.0,0.0,0.0)))
    u_s3 (getattr(store, 'lights_u_s3', (1.0,0.0,0.785398,0.0)))
    u_f3 (getattr(store, 'lights_u_f3', (0.0,1.0,1.0,0.0)))
    u_l4 (getattr(store, 'lights_u_l4', (0.0,0.0,0.0,0.0)))
    u_c4 (getattr(store, 'lights_u_c4', (0.0,0.0,0.0,0.0)))
    u_s4 (getattr(store, 'lights_u_s4', (1.0,0.0,0.785398,0.0)))
    u_f4 (getattr(store, 'lights_u_f4', (0.0,1.0,1.0,0.0)))
    u_l5 (getattr(store, 'lights_u_l5', (0.0,0.0,0.0,0.0)))
    u_c5 (getattr(store, 'lights_u_c5', (0.0,0.0,0.0,0.0)))
    u_s5 (getattr(store, 'lights_u_s5', (1.0,0.0,0.785398,0.0)))
    u_f5 (getattr(store, 'lights_u_f5', (0.0,1.0,1.0,0.0)))
    u_l6 (getattr(store, 'lights_u_l6', (0.0,0.0,0.0,0.0)))
    u_c6 (getattr(store, 'lights_u_c6', (0.0,0.0,0.0,0.0)))
    u_s6 (getattr(store, 'lights_u_s6', (1.0,0.0,0.785398,0.0)))
    u_f6 (getattr(store, 'lights_u_f6', (0.0,1.0,1.0,0.0)))
    u_l7 (getattr(store, 'lights_u_l7', (0.0,0.0,0.0,0.0)))
    u_c7 (getattr(store, 'lights_u_c7', (0.0,0.0,0.0,0.0)))
    u_s7 (getattr(store, 'lights_u_s7', (1.0,0.0,0.785398,0.0)))
    u_f7 (getattr(store, 'lights_u_f7', (0.0,1.0,1.0,0.0)))

transform lighting_front_transform():
    mesh True
    shader "lighting_2d"
    u_lod_bias 0.0
    u_strength (getattr(store, 'lighting_strength', 1.0))
    u_light_count (getattr(store, 'lights_count', 0))
    u_layer_select 2.0
    u_l0 (getattr(store, 'lights_u_l0', (0.0,0.0,0.0,0.0)))
    u_c0 (getattr(store, 'lights_u_c0', (0.0,0.0,0.0,0.0)))
    u_s0 (getattr(store, 'lights_u_s0', (1.0,0.0,0.785398,0.0)))
    u_f0 (getattr(store, 'lights_u_f0', (0.0,1.0,1.0,0.0)))
    u_l1 (getattr(store, 'lights_u_l1', (0.0,0.0,0.0,0.0)))
    u_c1 (getattr(store, 'lights_u_c1', (0.0,0.0,0.0,0.0)))
    u_s1 (getattr(store, 'lights_u_s1', (1.0,0.0,0.785398,0.0)))
    u_f1 (getattr(store, 'lights_u_f1', (0.0,1.0,1.0,0.0)))
    u_l2 (getattr(store, 'lights_u_l2', (0.0,0.0,0.0,0.0)))
    u_c2 (getattr(store, 'lights_u_c2', (0.0,0.0,0.0,0.0)))
    u_s2 (getattr(store, 'lights_u_s2', (1.0,0.0,0.785398,0.0)))
    u_f2 (getattr(store, 'lights_u_f2', (0.0,1.0,1.0,0.0)))
    u_l3 (getattr(store, 'lights_u_l3', (0.0,0.0,0.0,0.0)))
    u_c3 (getattr(store, 'lights_u_c3', (0.0,0.0,0.0,0.0)))
    u_s3 (getattr(store, 'lights_u_s3', (1.0,0.0,0.785398,0.0)))
    u_f3 (getattr(store, 'lights_u_f3', (0.0,1.0,1.0,0.0)))
    u_l4 (getattr(store, 'lights_u_l4', (0.0,0.0,0.0,0.0)))
    u_c4 (getattr(store, 'lights_u_c4', (0.0,0.0,0.0,0.0)))
    u_s4 (getattr(store, 'lights_u_s4', (1.0,0.0,0.785398,0.0)))
    u_f4 (getattr(store, 'lights_u_f4', (0.0,1.0,1.0,0.0)))
    u_l5 (getattr(store, 'lights_u_l5', (0.0,0.0,0.0,0.0)))
    u_c5 (getattr(store, 'lights_u_c5', (0.0,0.0,0.0,0.0)))
    u_s5 (getattr(store, 'lights_u_s5', (1.0,0.0,0.785398,0.0)))
    u_f5 (getattr(store, 'lights_u_f5', (0.0,1.0,1.0,0.0)))
    u_l6 (getattr(store, 'lights_u_l6', (0.0,0.0,0.0,0.0)))
    u_c6 (getattr(store, 'lights_u_c6', (0.0,0.0,0.0,0.0)))
    u_s6 (getattr(store, 'lights_u_s6', (1.0,0.0,0.785398,0.0)))
    u_f6 (getattr(store, 'lights_u_f6', (0.0,1.0,1.0,0.0)))
    u_l7 (getattr(store, 'lights_u_l7', (0.0,0.0,0.0,0.0)))
    u_c7 (getattr(store, 'lights_u_c7', (0.0,0.0,0.0,0.0)))
    u_s7 (getattr(store, 'lights_u_s7', (1.0,0.0,0.785398,0.0)))
    u_f7 (getattr(store, 'lights_u_f7', (0.0,1.0,1.0,0.0)))

# Minimal gizmo overlay for lights (dev/debug)
default lighting_gizmos = False

init python:
    def debug_light_overlay_toggle():
        try:
            store.lighting_gizmos = not bool(getattr(store, 'lighting_gizmos', False))
            renpy.restart_interaction()
            return store.lighting_gizmos
        except Exception:
            return False

screen lighting_overlay():
    if (config.developer or (hasattr(store, 'lights_state') and store.lights_state.get('debug', False))) and lighting_gizmos:
        $ dl = getattr(store, 'dynamic_lights', []) or []
        $ sw = float(config.screen_width)
        $ sh = float(config.screen_height)
        for i, e in enumerate(dl):
            $ px = float(e.get('pos',(0.5,0.5))[0]) * sw
            $ py = float(e.get('pos',(0.5,0.5))[1]) * sh
            $ rad = float(e.get('radius', 0.25)) * max(sw, sh)
            $ dx, dy = e.get('dir', (1.0,0.0))
            $ ax = px + dx * min(60, rad)
            $ ay = py + dy * min(60, rad)
            # Dot at position
            add Solid("#00ff22") pos (px-2, py-2) xsize 4 ysize 4
            # Direction dot (for spot)
            if str(e.get('kind','point')) != 'point':
                add Solid("#ffaa00") pos (ax-2, ay-2) xsize 4 ysize 4
            # Label
            text (f"{i}:{e.get('kind','?')} r={int(rad)}") size 12 color "#00ff88" xpos px+6 ypos py-6

# Compatibility no-op screen for removed lighting editor
screen lighting_editor_overlay():
    # Intentionally empty; legacy reference in room_exploration
    pass
