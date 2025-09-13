# Professional Color Grading Shader
# Enhanced color grading system for cinematic looks
# Full-featured shader with all color grading parameters

init python:
    # Enhanced color grading shader with all parameters
    renpy.register_shader("professional_color_grading", variables="""
        uniform sampler2D tex0;
        uniform float u_lod_bias;
        uniform float u_temperature;
        uniform float u_tint;
        uniform float u_saturation;
        uniform float u_contrast;
        uniform float u_brightness;
        uniform float u_gamma;
        uniform vec3 u_color_filter;
        uniform vec3 u_shadow_tint;
        uniform vec3 u_highlight_tint;
        uniform float u_vignette;
        uniform float u_film_grain_amount;
        attribute vec2 a_tex_coord;
        varying vec2 v_tex_coord;
    """, vertex_300="""
        v_tex_coord = a_tex_coord;
    """, fragment_300="""
        vec2 coord = v_tex_coord;
        vec4 color = texture2D(tex0, coord, u_lod_bias);
        
        // Calculate luminance for tone mapping
        float lum = dot(color.rgb, vec3(0.299, 0.587, 0.114));
        
        // Apply shadow and highlight tints (key for noir atmosphere)
        vec3 shadows = mix(color.rgb, color.rgb * u_shadow_tint, (1.0 - lum) * 0.5);
        vec3 highlights = mix(color.rgb, color.rgb * u_highlight_tint, lum * 0.3);
        color.rgb = mix(shadows, highlights, smoothstep(0.2, 0.8, lum));
        
        // Temperature adjustment (warm/cool)
        color.r *= 1.0 + u_temperature * 0.4;
        color.b *= 1.0 - u_temperature * 0.4;
        
        // Tint adjustment (magenta/green)
        color.r *= 1.0 + u_tint * 0.2;
        color.g *= 1.0 - abs(u_tint) * 0.1;
        color.b *= 1.0 - u_tint * 0.2;
        
        // Contrast and brightness
        color.rgb = (color.rgb - 0.5) * u_contrast + 0.5 + u_brightness;
        
        // Gamma correction for that film look
        color.rgb = pow(max(color.rgb, 0.0), vec3(1.0 / u_gamma));
        
        // Saturation adjustment
        float luminance = dot(color.rgb, vec3(0.299, 0.587, 0.114));
        color.rgb = mix(vec3(luminance), color.rgb, u_saturation);
        
        // Color filter overlay
        color.rgb *= u_color_filter;
        
        // Subtle film grain for texture (time-independent here; dynamic grain handled elsewhere)
        float grain = 0.5;
        color.rgb += (grain - 0.5) * u_film_grain_amount;
        
        // Vignette effect for focus
        float dist = distance(coord, vec2(0.5, 0.5));
        color.rgb *= 1.0 - (dist * dist * u_vignette);
        
        // Ensure we stay in valid color range
        color.rgb = clamp(color.rgb, 0.0, 1.0);
        color.a = clamp(color.a, 0.0, 1.0);
        
        gl_FragColor = color;
    """)

# Base transform for professional color grading
transform professional_grading(temperature=0.0, tint=0.0, saturation=1.0, contrast=1.0, 
                           brightness=0.0, gamma=1.0, color_filter=(1.0, 1.0, 1.0),
                           shadow_tint=(1.0, 1.0, 1.0), highlight_tint=(1.0, 1.0, 1.0),
                           vignette=0.0, film_grain=0.0):
    mesh True
    shader "professional_color_grading"
    u_temperature temperature
    u_tint tint
    u_saturation saturation
    u_contrast contrast
    u_brightness brightness
    u_gamma gamma
    u_color_filter color_filter
    u_shadow_tint shadow_tint
    u_highlight_tint highlight_tint
    u_vignette vignette
    u_film_grain_amount film_grain

# 10 Neo-Noir Color Grading Presets

# 1. Classic Noir - High contrast black and white with slight blue tint
transform color_grade_classic_noir():
    professional_grading(
        temperature=-0.2, 
        tint=0.0, 
        saturation=0.3, 
        contrast=1.4, 
        brightness=-0.1,
        gamma=1.1,
        color_filter=(0.95, 0.95, 1.05),
        shadow_tint=(0.8, 0.85, 1.0),
        highlight_tint=(1.0, 1.0, 1.05),
        vignette=0.4,
        film_grain=0.02
    )

# 2. Neon Night - Cyan and magenta split with high saturation
transform color_grade_neon_night():
    professional_grading(
        temperature=0.1,
        tint=0.15,
        saturation=1.3,
        contrast=1.2,
        brightness=0.0,
        gamma=0.95,
        color_filter=(1.1, 0.9, 1.2),
        shadow_tint=(0.7, 0.9, 1.3),
        highlight_tint=(1.3, 0.9, 1.1),
        vignette=0.3,
        film_grain=0.01
    )

# 3. Rain Soaked Streets - Cool, desaturated with blue-green tint
transform color_grade_rain_streets():
    professional_grading(
        temperature=-0.3,
        tint=-0.1,
        saturation=0.7,
        contrast=1.1,
        brightness=-0.05,
        gamma=1.05,
        color_filter=(0.9, 1.0, 1.1),
        shadow_tint=(0.85, 0.95, 1.1),
        highlight_tint=(0.95, 1.0, 1.05),
        vignette=0.5,
        film_grain=0.03
    )

# 4. Smoky Bar - Warm amber with reduced clarity
transform color_grade_smoky_bar():
    professional_grading(
        temperature=0.4,
        tint=0.05,
        saturation=0.8,
        contrast=0.95,
        brightness=0.05,
        gamma=1.15,
        color_filter=(1.15, 1.0, 0.85),
        shadow_tint=(1.1, 0.9, 0.7),
        highlight_tint=(1.2, 1.1, 0.9),
        vignette=0.6,
        film_grain=0.04
    )

# 5. Miami Vice - High contrast with pink and teal
transform color_grade_miami_vice():
    professional_grading(
        temperature=0.05,
        tint=0.2,
        saturation=1.4,
        contrast=1.3,
        brightness=0.1,
        gamma=0.9,
        color_filter=(1.15, 0.95, 1.1),
        shadow_tint=(0.8, 1.0, 1.2),
        highlight_tint=(1.3, 1.0, 0.95),
        vignette=0.2,
        film_grain=0.005
    )

# 6. Detective's Office - Muted browns and greens, vintage feel
transform color_grade_detective_office():
    professional_grading(
        temperature=0.2,
        tint=-0.05,
        saturation=0.6,
        contrast=1.05,
        brightness=-0.02,
        gamma=1.2,
        color_filter=(1.05, 1.0, 0.9),
        shadow_tint=(0.9, 0.85, 0.8),
        highlight_tint=(1.1, 1.05, 0.95),
        vignette=0.35,
        film_grain=0.025
    )

# 7. Crime Scene - Cold, clinical with enhanced reds
transform color_grade_crime_scene():
    professional_grading(
        temperature=-0.15,
        tint=0.0,
        saturation=0.9,
        contrast=1.25,
        brightness=0.02,
        gamma=0.95,
        color_filter=(1.1, 0.95, 0.95),
        shadow_tint=(0.9, 0.9, 1.0),
        highlight_tint=(1.15, 1.0, 1.0),
        vignette=0.3,
        film_grain=0.015
    )

# 8. Blade Runner - Deep orange and teal with heavy atmosphere
transform color_grade_blade_runner():
    professional_grading(
        temperature=0.15,
        tint=0.1,
        saturation=1.1,
        contrast=1.15,
        brightness=-0.08,
        gamma=1.1,
        color_filter=(1.2, 1.0, 0.85),
        shadow_tint=(0.7, 0.85, 1.0),
        highlight_tint=(1.3, 1.1, 0.9),
        vignette=0.45,
        film_grain=0.02
    )

# 9. Evidence Room - Neutral with slight green cast, fluorescent lighting
transform color_grade_evidence_room():
    professional_grading(
        temperature=-0.05,
        tint=-0.1,
        saturation=0.75,
        contrast=1.0,
        brightness=0.1,
        gamma=0.95,
        color_filter=(0.98, 1.02, 0.95),
        shadow_tint=(0.95, 1.0, 0.95),
        highlight_tint=(1.0, 1.05, 1.0),
        vignette=0.15,
        film_grain=0.01
    )

# 10. Midnight Chase - High contrast blue-black with streaking lights
transform color_grade_midnight_chase():
    professional_grading(
        temperature=-0.25,
        tint=0.05,
        saturation=0.85,
        contrast=1.35,
        brightness=-0.12,
        gamma=1.05,
        color_filter=(0.9, 0.95, 1.15),
        shadow_tint=(0.7, 0.75, 0.9),
        highlight_tint=(1.1, 1.15, 1.3),
        vignette=0.55,
        film_grain=0.03
    )

# Default off state
transform color_grade_off():
    professional_grading(
        temperature=0.0,
        tint=0.0,
        saturation=1.0,
        contrast=1.0,
        brightness=0.0,
        gamma=1.0,
        color_filter=(1.0, 1.0, 1.0),
        shadow_tint=(1.0, 1.0, 1.0),
        highlight_tint=(1.0, 1.0, 1.0),
        vignette=0.0,
        film_grain=0.0
    )

# Additional 10 presets (expanded set)

# 11. Cool Moonlight - deep blue night tones with gentle contrast
transform color_grade_cool_moonlight():
    professional_grading(
        temperature=-0.35,
        tint=0.05,
        saturation=0.8,
        contrast=1.2,
        brightness=-0.08,
        gamma=1.05,
        color_filter=(0.9, 0.98, 1.15),
        shadow_tint=(0.8, 0.9, 1.2),
        highlight_tint=(1.05, 1.05, 1.1),
        vignette=0.45,
        film_grain=0.02
    )

# 12. Golden Hour - warm orange glow with lifted shadows
transform color_grade_golden_hour():
    professional_grading(
        temperature=0.45,
        tint=-0.05,
        saturation=1.1,
        contrast=1.05,
        brightness=0.08,
        gamma=0.95,
        color_filter=(1.2, 1.05, 0.9),
        shadow_tint=(1.1, 1.0, 0.9),
        highlight_tint=(1.15, 1.05, 0.95),
        vignette=0.25,
        film_grain=0.015
    )

# 13. Bleach Bypass - desaturated, high contrast silver look
transform color_grade_bleach_bypass():
    professional_grading(
        temperature=-0.05,
        tint=0.0,
        saturation=0.45,
        contrast=1.5,
        brightness=-0.05,
        gamma=1.1,
        color_filter=(1.0, 1.0, 1.0),
        shadow_tint=(0.95, 0.95, 1.0),
        highlight_tint=(1.05, 1.05, 1.05),
        vignette=0.35,
        film_grain=0.03
    )

# 14. Sepia Fade - nostalgic brown tone
transform color_grade_sepia_fade():
    professional_grading(
        temperature=0.5,
        tint=0.05,
        saturation=0.7,
        contrast=1.0,
        brightness=0.05,
        gamma=1.05,
        color_filter=(1.15, 1.0, 0.8),
        shadow_tint=(1.1, 0.95, 0.8),
        highlight_tint=(1.2, 1.05, 0.85),
        vignette=0.4,
        film_grain=0.02
    )

# 15. Teal & Orange Cinema - blockbuster split tone
transform color_grade_teal_orange_cinema():
    professional_grading(
        temperature=0.15,
        tint=0.1,
        saturation=1.25,
        contrast=1.25,
        brightness=0.0,
        gamma=1.0,
        color_filter=(1.1, 0.95, 1.1),
        shadow_tint=(0.75, 0.95, 1.2),
        highlight_tint=(1.25, 1.05, 0.9),
        vignette=0.25,
        film_grain=0.015
    )

# 16. Green Matrix - greenish sci-fi cast
transform color_grade_green_matrix():
    professional_grading(
        temperature=-0.05,
        tint=-0.25,
        saturation=0.9,
        contrast=1.15,
        brightness=-0.02,
        gamma=1.05,
        color_filter=(0.9, 1.1, 0.9),
        shadow_tint=(0.85, 1.05, 0.85),
        highlight_tint=(1.0, 1.15, 1.0),
        vignette=0.3,
        film_grain=0.02
    )

# 17. Pastel Dream - soft, high gamma pastel look
transform color_grade_pastel_dream():
    professional_grading(
        temperature=0.1,
        tint=0.15,
        saturation=0.9,
        contrast=0.95,
        brightness=0.08,
        gamma=0.9,
        color_filter=(1.1, 1.0, 1.1),
        shadow_tint=(1.0, 0.95, 1.1),
        highlight_tint=(1.1, 1.05, 1.1),
        vignette=0.15,
        film_grain=0.005
    )

# 18. High Key - bright, low contrast
transform color_grade_high_key():
    professional_grading(
        temperature=0.05,
        tint=0.0,
        saturation=1.0,
        contrast=0.9,
        brightness=0.12,
        gamma=0.95,
        color_filter=(1.05, 1.05, 1.05),
        shadow_tint=(1.05, 1.05, 1.05),
        highlight_tint=(1.05, 1.05, 1.05),
        vignette=0.05,
        film_grain=0.0
    )

# 19. Low Key Crush - dark, high contrast, crushed blacks
transform color_grade_low_key_crush():
    professional_grading(
        temperature=-0.1,
        tint=0.0,
        saturation=0.85,
        contrast=1.45,
        brightness=-0.15,
        gamma=1.1,
        color_filter=(0.95, 0.95, 1.0),
        shadow_tint=(0.9, 0.9, 1.0),
        highlight_tint=(1.05, 1.05, 1.05),
        vignette=0.5,
        film_grain=0.02
    )

# 20. Film Stock 2383 - common print emulation
transform color_grade_film_stock_2383():
    professional_grading(
        temperature=0.1,
        tint=-0.05,
        saturation=1.1,
        contrast=1.15,
        brightness=0.02,
        gamma=1.0,
        color_filter=(1.05, 1.0, 0.95),
        shadow_tint=(0.95, 0.95, 1.0),
        highlight_tint=(1.08, 1.05, 1.0),
        vignette=0.25,
        film_grain=0.012
    )

# 21-30 Additional cinematic presets
transform color_grade_noir_hard():
    professional_grading(temperature=-0.3, tint=0.0, saturation=0.2, contrast=1.6, brightness=-0.12, gamma=1.05,
                         color_filter=(0.95,0.95,1.05), shadow_tint=(0.8,0.85,1.05), highlight_tint=(1.05,1.05,1.1),
                         vignette=0.6, film_grain=0.02)

transform color_grade_neo_tokyo():
    professional_grading(temperature=0.1, tint=0.25, saturation=1.35, contrast=1.2, brightness=0.02, gamma=0.95,
                         color_filter=(1.15,0.95,1.15), shadow_tint=(0.8,0.95,1.2), highlight_tint=(1.25,0.95,1.05),
                         vignette=0.3, film_grain=0.01)

transform color_grade_acid_wave():
    professional_grading(temperature=0.2, tint=0.3, saturation=1.6, contrast=1.1, brightness=0.05, gamma=0.9,
                         color_filter=(1.2,0.9,1.2), shadow_tint=(0.9,0.8,1.25), highlight_tint=(1.2,1.0,1.2),
                         vignette=0.2, film_grain=0.008)

transform color_grade_steel_blue():
    professional_grading(temperature=-0.4, tint=0.0, saturation=0.9, contrast=1.2, brightness=-0.06, gamma=1.05,
                         color_filter=(0.9,0.95,1.15), shadow_tint=(0.7,0.8,1.2), highlight_tint=(1.0,1.05,1.2),
                         vignette=0.4, film_grain=0.015)

transform color_grade_amber_glow():
    professional_grading(temperature=0.5, tint=-0.05, saturation=1.05, contrast=1.05, brightness=0.06, gamma=0.98,
                         color_filter=(1.25,1.05,0.9), shadow_tint=(1.1,1.0,0.9), highlight_tint=(1.2,1.05,0.95),
                         vignette=0.25, film_grain=0.012)

transform color_grade_mono_wash():
    professional_grading(temperature=0.0, tint=0.0, saturation=0.2, contrast=1.1, brightness=0.0, gamma=1.0,
                         color_filter=(1.0,1.0,1.0), shadow_tint=(1.0,1.0,1.0), highlight_tint=(1.0,1.0,1.0),
                         vignette=0.2, film_grain=0.01)

transform color_grade_rust_city():
    professional_grading(temperature=0.35, tint=-0.1, saturation=0.95, contrast=1.1, brightness=-0.02, gamma=1.05,
                         color_filter=(1.15,1.0,0.85), shadow_tint=(1.05,0.9,0.8), highlight_tint=(1.15,1.05,0.9),
                         vignette=0.35, film_grain=0.02)

transform color_grade_ice_storm():
    professional_grading(temperature=-0.45, tint=0.05, saturation=0.85, contrast=1.25, brightness=-0.1, gamma=1.08,
                         color_filter=(0.85,0.95,1.15), shadow_tint=(0.75,0.85,1.2), highlight_tint=(1.0,1.05,1.2),
                         vignette=0.5, film_grain=0.02)

transform color_grade_night_vision():
    professional_grading(temperature=-0.1, tint=-0.6, saturation=1.1, contrast=1.0, brightness=0.05, gamma=1.0,
                         color_filter=(0.7,1.2,0.7), shadow_tint=(0.8,1.05,0.8), highlight_tint=(0.9,1.2,0.9),
                         vignette=0.3, film_grain=0.01)

transform color_grade_underworld():
    professional_grading(temperature=-0.2, tint=0.1, saturation=0.9, contrast=1.3, brightness=-0.1, gamma=1.05,
                         color_filter=(0.9,0.95,1.1), shadow_tint=(0.75,0.85,1.15), highlight_tint=(1.05,1.05,1.15),
                         vignette=0.55, film_grain=0.02)

# Store current color grade preset
default current_color_grade = "off"
default color_grade_presets = [
    ("off", "Off", color_grade_off),
    ("classic_noir", "Classic Noir", color_grade_classic_noir),
    ("neon_night", "Neon Night", color_grade_neon_night),
    ("rain_streets", "Rain Soaked Streets", color_grade_rain_streets),
    ("smoky_bar", "Smoky Bar", color_grade_smoky_bar),
    ("miami_vice", "Miami Vice", color_grade_miami_vice),
    ("detective_office", "Detective's Office", color_grade_detective_office),
    ("crime_scene", "Crime Scene", color_grade_crime_scene),
    ("blade_runner", "Blade Runner", color_grade_blade_runner),
    ("evidence_room", "Evidence Room", color_grade_evidence_room),
    ("midnight_chase", "Midnight Chase", color_grade_midnight_chase),
    ("cool_moonlight", "Cool Moonlight", color_grade_cool_moonlight),
    ("golden_hour", "Golden Hour", color_grade_golden_hour),
    ("bleach_bypass", "Bleach Bypass", color_grade_bleach_bypass),
    ("sepia_fade", "Sepia Fade", color_grade_sepia_fade),
    ("teal_orange_cinema", "Teal & Orange", color_grade_teal_orange_cinema),
    ("green_matrix", "Green Matrix", color_grade_green_matrix),
    ("pastel_dream", "Pastel Dream", color_grade_pastel_dream),
    ("high_key", "High Key", color_grade_high_key),
    ("low_key_crush", "Low Key Crush", color_grade_low_key_crush),
    ("film_stock_2383", "Film Stock 2383", color_grade_film_stock_2383),
    ("noir_hard", "Noir Hard", color_grade_noir_hard),
    ("neo_tokyo", "Neo Tokyo", color_grade_neo_tokyo),
    ("acid_wave", "Acid Wave", color_grade_acid_wave),
    ("steel_blue", "Steel Blue", color_grade_steel_blue),
    ("amber_glow", "Amber Glow", color_grade_amber_glow),
    ("mono_wash", "Mono Wash", color_grade_mono_wash),
    ("rust_city", "Rust City", color_grade_rust_city),
    ("ice_storm", "Ice Storm", color_grade_ice_storm),
    ("night_vision", "Night Vision", color_grade_night_vision),
    ("underworld", "Underworld", color_grade_underworld)
]

init python:
    def cycle_color_grade(direction=1):
        """Cycle through color grade presets"""
        global current_color_grade
        current_index = 0
        for i, (preset_id, _, _) in enumerate(store.color_grade_presets):
            if preset_id == store.current_color_grade:
                current_index = i
                break
        
        new_index = (current_index + direction) % len(store.color_grade_presets)
        store.current_color_grade = store.color_grade_presets[new_index][0]
        preset_name = store.color_grade_presets[new_index][1]
        renpy.notify(f"Color Grade: {preset_name}")
        renpy.restart_interaction()
    
    def set_color_grade(preset_id):
        """Set a specific color grade preset"""
        global current_color_grade
        store.current_color_grade = preset_id
        for pid, pname, _ in store.color_grade_presets:
            if pid == preset_id:
                renpy.notify(f"Color Grade: {pname}")
                break
        renpy.restart_interaction()
