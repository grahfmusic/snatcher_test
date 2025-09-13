# Simple Bloom Shader (single-pass thresholded blur + add)

default bloom_enabled = False
default bloom_threshold = 0.75
default bloom_strength = 0.6
default bloom_radius = 2.5

init -5 python:
    renpy.register_shader(
        "bloom_simple",
        variables="""
            uniform sampler2D tex0;
            uniform float u_lod_bias;
            uniform float u_threshold;
            uniform float u_strength;
            uniform float u_radius;      // blur radius in pixels
            uniform vec2 u_texel;        // (1/width, 1/height)

            attribute vec2 a_tex_coord;
            varying vec2 v_tex_coord;
        """,
        vertex_300="""
            v_tex_coord = a_tex_coord;
        """,
        fragment_300="""
            vec2 uv = v_tex_coord;
            vec4 base = texture2D(tex0, uv, u_lod_bias);

            // Convert radius in pixels to UV step
            float r = max(u_radius, 0.0);
            vec2 step = u_texel * r;

            // 9-tap approximate Gaussian kernel over a 3x3 grid
            vec2 offsets[9];
            offsets[0] = vec2(-1.0, -1.0);
            offsets[1] = vec2( 0.0, -1.0);
            offsets[2] = vec2( 1.0, -1.0);
            offsets[3] = vec2(-1.0,  0.0);
            offsets[4] = vec2( 0.0,  0.0);
            offsets[5] = vec2( 1.0,  0.0);
            offsets[6] = vec2(-1.0,  1.0);
            offsets[7] = vec2( 0.0,  1.0);
            offsets[8] = vec2( 1.0,  1.0);

            float weights[9];
            weights[0] = 1.0; weights[1] = 2.0; weights[2] = 1.0;
            weights[3] = 2.0; weights[4] = 4.0; weights[5] = 2.0;
            weights[6] = 1.0; weights[7] = 2.0; weights[8] = 1.0;

            vec3 acc = vec3(0.0);
            float wsum = 0.0;
            for (int i = 0; i < 9; i++) {
                vec2 co = uv + offsets[i] * step;
                vec3 c = texture2D(tex0, co, u_lod_bias).rgb;
                float l = dot(c, vec3(0.2126, 0.7152, 0.0722));
                float m = clamp((l - u_threshold) / max(1e-4, (1.0 - u_threshold)), 0.0, 1.0);
                float w = weights[i];
                acc += c * (m * w);
                wsum += w * m;
            }
            vec3 bloom = (wsum > 0.0) ? (acc / wsum) : vec3(0.0);
            vec3 outc = clamp(base.rgb + bloom * u_strength, 0.0, 1.0);
            gl_FragColor = vec4(outc, base.a);
        """
    )

transform bloom_transform(threshold=0.75, strength=0.6, radius=2.5):
    mesh True
    shader "bloom_simple"
    u_threshold threshold
    u_strength strength
    u_radius radius
    u_texel (1.0/float(config.screen_width), 1.0/float(config.screen_height))
    u_lod_bias 0.0

