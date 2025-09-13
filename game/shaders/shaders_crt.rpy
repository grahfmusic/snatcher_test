# CRT Shader Integration
#
# Overview
# - GLSL shader for CRT warp, scanlines, chroma offset, and horizontal vignette.
# - Exposes static/animated transforms with tunable uniforms.

init python hide:
    renpy.register_shader(
        "chroma_crt",
        fragment_functions="""
        float hash12(vec2 p) {
            vec3 p3 = fract(vec3(p.xyx) * .1031);
            p3 += dot(p3, p3.yzx + 33.33);
            return fract((p3.x + p3.y) * p3.z);
        }
        vec2 uuv(float wp, vec2 tex_coord)
        {
            vec2 uvv = tex_coord;
            vec2 dc = 0.5 - uvv;
            dc *= dc;
            uvv -= .5; uvv *= 1. + (dc.yx * wp); uvv += .5;
            return uvv;
        }
""", variables="""
    uniform float u_warp;
    uniform float u_scan;
    uniform float u_chroma;            // legacy chroma scale (mapped to aberration amp)
    uniform float u_scanline_size;
    uniform float u_scanline_offset;
    uniform float u_vignette_strength;
    uniform float u_vignette_width;
    uniform float u_vignette_feather;  // new feather for vignette falloff
    uniform float u_time;              // global time
    uniform float u_aberr_amp;         // chromatic aberration amplitude (uv shift)
    uniform float u_aberr_speed;       // speed for aberration animation
    uniform float u_aberr_mode;        // 0=none,1=pulse,2=flicker,3=sweep
    uniform float u_aberr_r;           // per-channel scale for R
    uniform float u_aberr_g;           // per-channel scale for G (vertical)
    uniform float u_aberr_b;           // per-channel scale for B
    uniform float u_glitch;            // 0..1 glitch intensity
    uniform float u_glitch_speed;      // glitch animation speed
    uniform vec2 u_model_size;
    uniform sampler2D tex0;
    attribute vec2 a_tex_coord;
    attribute vec4 a_position;
    varying vec2 v_tex_coord;
""", vertex_300="""
    v_tex_coord = a_position.xy / u_model_size;
""", fragment_300="""
    #define PI 3.14159265359
    // Base warp
    vec2 uv = uuv(u_warp, v_tex_coord);

    // Glitch horizontal jitter by row
    if (u_glitch > 0.001) {
        float row = floor(uv.y * 360.0);
        float g = step(0.92, fract(sin((row + u_time * 37.0 * u_glitch_speed) * 12.9898) * 43758.5453));
        float jitter = (hash12(vec2(row, u_time)) - 0.5) * 0.02 * u_glitch * g;
        uv.x += jitter;
    }

    if (uv.x < 0.0 || uv.x > 1.0 || uv.y < 0.0 || uv.y > 1.0) {
        gl_FragColor = vec4(0.0);
    } else {
        // Compute per-channel offsets for aberration
        vec2 offR = vec2(0.0);
        vec2 offG = vec2(0.0);
        vec2 offB = vec2(0.0);
        float amp = max(u_aberr_amp, 0.0);
        float t = u_time * max(u_aberr_speed, 0.0);
        if (amp > 0.0001 && u_aberr_mode > 0.5) {
            if (u_aberr_mode < 1.5) {
                // pulse: radial oscillation
                float s = sin(t * 6.28318) * amp;
                offR = vec2(+s, 0.0);
                offB = vec2(-s, 0.0);
            } else if (u_aberr_mode < 2.5) {
                // flicker: hash-based random
                float r = (hash12(vec2(floor(t*30.0), uv.y)) - 0.5) * 2.0 * amp;
                offR = vec2(+r, 0.0);
                offB = vec2(-r, 0.0);
            } else {
                // sweep: offset varies across scanline
                float s = sin((uv.y + t * 0.25) * 12.0) * amp;
                offR = vec2(+s, 0.0);
                offB = vec2(-s, 0.0);
            }
        }

        // Apply per-channel scaling to offsets (split RGB)
        offR *= max(u_aberr_r, 0.0);
        offB *= max(u_aberr_b, 0.0);
        // Green channel offset vertically as a subtle drift
        if (u_aberr_g > 0.0001) {
            offG = vec2(0.0, (offR.x != 0.0 ? abs(offR.x) : (offB.x != 0.0 ? abs(offB.x) : 0.0)) * u_aberr_g);
        }

        // Sample color channels with per-channel offsets
        vec4 base = texture2D(tex0, uv);
        float a = base.a;
        float r = texture2D(tex0, uv + offR).r;
        float g = texture2D(tex0, uv + offG).g;
        float b = texture2D(tex0, uv + offB).b;
        vec4 pure = vec4(r, g, b, a);

        // Scanlines
        float scanline_density = 200.0;
        float normalized_y = (uv.y * scanline_density) + u_scanline_offset;
        float scanline_pattern = sin(normalized_y * PI * u_scanline_size);
        float apply = pow(abs(scanline_pattern) * u_scan, 2.0);
        vec4 color = mix(pure, vec4(0.0), apply);

        // Vignette with feathering (rectangular edge-based)
        float edgeh = min(min(uv.x, 1.0 - uv.x), min(uv.y, 1.0 - uv.y));
        float width = max(u_vignette_width, 0.0001);
        float tedge = clamp(edgeh / width, 0.0, 1.0);
        float feather = max(u_vignette_feather, 0.001);
        float eased = pow(tedge, feather);
        float vignette = mix(1.0 - u_vignette_strength, 1.0, smoothstep(0.0, 1.0, eased));
        color.rgb *= vignette;
        gl_FragColor = color;
    }
"""
)

transform chroma_crt(warp=.2, scan=.5, chroma=.9, scanline_size=1.0, vignette_strength=.35, vignette_width=.25, vignette_feather=1.0, aberr_mode=0, aberr_amp=0.0, aberr_speed=1.0, aberr_r=1.0, aberr_g=0.0, aberr_b=1.0, glitch=0.0, glitch_speed=1.0):
    mesh True
    shader "chroma_crt"
    u_warp warp
    u_scan scan
    u_chroma chroma
    u_scanline_size scanline_size
    u_scanline_offset 0.0
    u_vignette_strength vignette_strength
    u_vignette_width vignette_width
    u_vignette_feather vignette_feather
    u_aberr_amp aberr_amp
    u_aberr_speed aberr_speed
    u_aberr_mode aberr_mode
    u_aberr_r aberr_r
    u_aberr_g aberr_g
    u_aberr_b aberr_b
    u_glitch glitch
    u_glitch_speed glitch_speed

transform animated_chroma_crt(base_warp=.2, base_scan=.5, base_chroma=.9, base_scanline_size=1.0, animation_intensity=0.1, animation_speed=2.0, vignette_strength=.35, vignette_width=.25, vignette_feather=1.0, aberr_mode=0, aberr_amp=0.0, aberr_speed=1.0, aberr_r=1.0, aberr_g=0.0, aberr_b=1.0, glitch=0.0, glitch_speed=1.0):
    mesh True
    shader "chroma_crt"
    u_warp base_warp
    u_scan base_scan
    u_chroma base_chroma
    u_scanline_size base_scanline_size
    u_vignette_strength vignette_strength
    u_vignette_width vignette_width
    u_vignette_feather vignette_feather
    u_aberr_amp aberr_amp
    u_aberr_speed aberr_speed
    u_aberr_mode aberr_mode
    u_aberr_r aberr_r
    u_aberr_g aberr_g
    u_aberr_b aberr_b
    u_glitch glitch
    u_glitch_speed glitch_speed
    block:
        u_scanline_offset 0.0
        linear animation_speed u_scanline_offset (200.0 * animation_intensity)
        repeat

transform static_chroma_crt(warp=.2, scan=.5, chroma=.9, scanline_size=1.0, vignette_strength=.35, vignette_width=.25, vignette_feather=1.0, aberr_mode=0, aberr_amp=0.0, aberr_speed=1.0, aberr_r=1.0, aberr_g=0.0, aberr_b=1.0, glitch=0.0, glitch_speed=1.0):
    mesh True
    shader "chroma_crt"
    u_warp warp
    u_scan scan
    u_chroma chroma
    u_scanline_size scanline_size
    u_scanline_offset 0.0
    u_vignette_strength vignette_strength
    u_vignette_width vignette_width
    u_vignette_feather vignette_feather
    u_aberr_amp aberr_amp
    u_aberr_speed aberr_speed
    u_aberr_mode aberr_mode
    u_aberr_r aberr_r
    u_aberr_g aberr_g
    u_aberr_b aberr_b
    u_glitch glitch
    u_glitch_speed glitch_speed

transform black_chroma_crt(child, warp=.2, scan=.5, chroma=.9, scanline_size=1.0, vignette_strength=.35, vignette_width=.25):
    contains:
        "black"
    contains:
        At(child, chroma_crt(warp, scan, chroma, scanline_size, vignette_strength, vignette_width))
