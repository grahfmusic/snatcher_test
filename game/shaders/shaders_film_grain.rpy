# Film Grain Shader
# Adds procedural film grain texture with various intensity levels

init python:
    from renpy.uguu import GL_CLAMP_TO_EDGE

init python:
    # Film grain shader registration (uses built-in u_time uniform from Ren'Py)
    renpy.register_shader("film_grain_shader", variables="""
        uniform float u_lod_bias;
        uniform float u_time;
        uniform float u_grain_intensity;
        uniform float u_grain_size;
        uniform float u_grain_downscale; // 2.0 means 1280x720 -> 640x360 sampling grid
        uniform float u_grain_anim_mode;  // 0=none,1=pulse,2=strobe,3=drift
        uniform float u_grain_anim_speed; // speed scalar for animation
        uniform float u_grain_anim_amount; // 0..1 amount for modulation
        uniform vec2 u_model_size;
        attribute vec2 a_tex_coord;
        varying vec2 v_tex_coord;
    """, vertex_300="""
        v_tex_coord = a_tex_coord;
    """, fragment_300="""
        vec2 uv = v_tex_coord;
        float time = u_time * 0.1;
        
        // Downscale sampling grid to make grain chunkier (e.g., 2.0 => 640x360 on 1280x720)
        vec2 grid = max(vec2(1.0), u_model_size / max(u_grain_downscale, 1.0));
        vec2 uv_ds = floor(uv * grid) / grid;
        
        // Generate procedural noise at reduced resolution, then apply to full-res color
        vec2 grain_uv = uv_ds * u_grain_size + time;
        float noise = fract(sin(dot(grain_uv, vec2(12.9898, 78.233))) * 43758.5453);
        noise = (noise - 0.5) * 2.0;
        
        // Apply animation modes
        float anim_amp = 1.0;
        if (u_grain_anim_mode > 0.5) {
            if (u_grain_anim_mode < 1.5) {
                // pulse intensity
                anim_amp += sin(time * u_grain_anim_speed * 6.28318) * u_grain_anim_amount;
            } else if (u_grain_anim_mode < 2.5) {
                // strobe flicker
                float s = step(0.5, fract(time * u_grain_anim_speed));
                anim_amp += (s * 2.0 - 1.0) * u_grain_anim_amount;
            } else {
                // drift pattern
                vec2 drift = vec2(sin(time * u_grain_anim_speed), cos(time * u_grain_anim_speed)) * (u_grain_anim_amount * 0.5);
                grain_uv += drift;
            }
        }
        
        // Sample base color with configured LOD bias
        vec4 color = texture2D(tex0, uv, u_lod_bias);
        
        // Fade noise out on transparent/edge pixels to avoid visible rectangles
        float fade = smoothstep(0.0, 0.02, color.a);
        
        // Apply grain based on intensity and alpha fade
        color.rgb += noise * u_grain_intensity * anim_amp * fade;
        
        gl_FragColor = color;
    """)

# Film grain effect transforms
transform film_grain_effect(intensity=0.0, size=100.0, downscale=2.0, anim_mode=0.0, anim_speed=1.0, anim_amount=0.0):
    mesh True
    # Clamp texture edges to avoid sampling outside and remove outlines
    gl_texture_wrap (GL_CLAMP_TO_EDGE, GL_CLAMP_TO_EDGE)
    # Prefer neutral LOD bias to avoid sampling lower mip levels on edges
    u_lod_bias 0.0
    gl_mipmap True

    shader "film_grain_shader"
    u_grain_intensity intensity
    u_grain_size size
    u_grain_downscale downscale
    u_grain_anim_mode anim_mode
    u_grain_anim_speed anim_speed
    u_grain_anim_amount anim_amount
    
    # Ensure time advances by invoking a no-op timepump so u_time updates continuously
    function film_grain_timepump

# Convenience alias used by room composition screens
transform room_film_grain_overlay(grain_intensity=0.05, grain_size=100.0, downscale=2.0, anim_mode=0.0, anim_speed=1.0, anim_amount=0.0):
    film_grain_effect(intensity=grain_intensity, size=grain_size, downscale=downscale, anim_mode=anim_mode, anim_speed=anim_speed, anim_amount=anim_amount)

# Provide a timepump function to keep film grain animated
init python:
    if not hasattr(store, 'film_grain_last_timepump'):
        store.film_grain_last_timepump = 0.0

    def film_grain_timepump(trans, st, at):
        """Return a small non-zero so Ren'Py keeps calling and u_time advances."""
        # st is used by the shader system to feed u_time; just keep re-scheduling
        return 0

    # Film grain is typically adjusted via the Shader Editor (F8) or presets.

# Preset transforms for different grain levels
transform film_grain_off():
    film_grain_effect(0.0, 100.0)

transform film_grain_subtle():
    film_grain_effect(0.02, 120.0)

transform film_grain_moderate():
    film_grain_effect(0.05, 100.0)

transform film_grain_heavy():
    film_grain_effect(0.1, 80.0)
