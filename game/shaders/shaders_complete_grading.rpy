# Complete Color Grading Shader System
# Full-featured color grading with all parameters properly connected

init python:
    # Register the complete color grading shader
    renpy.register_shader("complete_color_grading", variables="""
        uniform sampler2D tex0;
        uniform float u_lod_bias;
        
        // Basic color adjustments
        uniform float u_temperature;    // -1.0 to 1.0 (cool to warm)
        uniform float u_tint;           // -1.0 to 1.0 (green to magenta)
        uniform float u_saturation;     // 0.0 to 2.0
        uniform float u_contrast;       // 0.5 to 2.0
        uniform float u_brightness;     // -0.5 to 0.5
        uniform float u_gamma;          // 0.5 to 2.0
        
        // Advanced color grading
        uniform vec3 u_lift;            // Shadows adjustment
        uniform vec3 u_gain;            // Highlights adjustment
        uniform vec3 u_offset;          // Overall offset
        
        // Effects
        uniform float u_vignette_amount;  // 0.0 to 1.0
        uniform float u_vignette_softness; // 0.0 to 1.0
        
        attribute vec2 a_tex_coord;
        varying vec2 v_tex_coord;
    """, vertex_300="""
        v_tex_coord = a_tex_coord;
    """, fragment_300="""
        vec2 uv = v_tex_coord;
        vec4 color = texture2D(tex0, uv, u_lod_bias);
        
        // Store original alpha
        float original_alpha = color.a;
        
        // Apply lift, gain, offset (ASC CDL standard)
        color.rgb = color.rgb * u_gain + u_lift * (1.0 - color.rgb) + u_offset;
        
        // Temperature adjustment (more aggressive)
        float temp_factor = u_temperature;
        if (temp_factor > 0.0) {
            // Warm: increase red, decrease blue
            color.r *= 1.0 + temp_factor * 0.5;
            color.g *= 1.0 + temp_factor * 0.1;
            color.b *= 1.0 - temp_factor * 0.5;
        } else {
            // Cool: decrease red, increase blue  
            color.r *= 1.0 + temp_factor * 0.5;
            color.g *= 1.0 + temp_factor * 0.1;
            color.b *= 1.0 - temp_factor * 0.5;
        }
        
        // Tint adjustment (green-magenta axis)
        float tint_factor = u_tint;
        if (tint_factor > 0.0) {
            // Magenta: increase red and blue, decrease green
            color.r *= 1.0 + tint_factor * 0.3;
            color.g *= 1.0 - tint_factor * 0.3;
            color.b *= 1.0 + tint_factor * 0.3;
        } else {
            // Green: increase green, decrease red and blue
            color.r *= 1.0 + tint_factor * 0.3;
            color.g *= 1.0 - tint_factor * 0.3;
            color.b *= 1.0 + tint_factor * 0.3;
        }
        
        // Apply contrast (more aggressive)
        vec3 contrast_pivot = vec3(0.5);
        color.rgb = mix(contrast_pivot, color.rgb, u_contrast);
        
        // Apply brightness
        color.rgb += u_brightness;
        
        // Apply gamma correction (power function)
        vec3 gamma_vec = vec3(1.0 / max(u_gamma, 0.01));
        color.rgb = pow(max(color.rgb, vec3(0.0)), gamma_vec);
        
        // Saturation adjustment (more range)
        float luma = dot(color.rgb, vec3(0.2126, 0.7152, 0.0722));
        color.rgb = mix(vec3(luma), color.rgb, u_saturation);
        
        // Vignette effect
        if (u_vignette_amount > 0.0) {
            vec2 center = vec2(0.5, 0.5);
            float dist = distance(uv, center);
            float vignette = 1.0 - smoothstep(0.5 - u_vignette_softness, 0.8, dist);
            vignette = mix(1.0, vignette, u_vignette_amount);
            color.rgb *= vignette;
        }
        
        // Clamp to valid range
        color.rgb = clamp(color.rgb, 0.0, 1.0);
        color.a = original_alpha;
        
        gl_FragColor = color;
    """)

# Transform for applying complete color grading
transform complete_grading_transform(
    temperature=0.0, tint=0.0, saturation=1.0, contrast=1.0,
    brightness=0.0, gamma=1.0,
    lift=(0.0, 0.0, 0.0), gain=(1.0, 1.0, 1.0), offset=(0.0, 0.0, 0.0),
    vignette_amount=0.0, vignette_softness=0.5):
    
    mesh True
    shader "complete_color_grading"
    u_temperature temperature
    u_tint tint
    u_saturation saturation
    u_contrast contrast
    u_brightness brightness
    u_gamma gamma
    u_lift lift
    u_gain gain
    u_offset offset
    u_vignette_amount vignette_amount
    u_vignette_softness vignette_softness
    gl_texture_wrap (GL_CLAMP_TO_EDGE, GL_CLAMP_TO_EDGE)
    u_lod_bias 0.0
    gl_mipmap True

# Screen to apply complete color grading as overlay
screen complete_color_grading_overlay():
    # Only apply when color grading is enabled
    if getattr(store, 'color_grading_enabled', True):
        # Get current shader parameters with proper defaults
        $ temp = getattr(store, 'color_temperature', 0.0)
        $ tint = getattr(store, 'color_tint', 0.0)
        $ sat = getattr(store, 'color_saturation', 1.0)
        $ cont = getattr(store, 'shader_contrast', 1.0)
        $ bright = getattr(store, 'shader_brightness', 0.0)
        $ gam = getattr(store, 'shader_gamma', 1.0)
        $ vig = getattr(store, 'grade_vignette_strength', 0.0)
        
        # Calculate lift/gain/offset from shadow and highlight tints
        $ shadow_tint = getattr(store, 'color_shadow_tint', (1.0, 1.0, 1.0))
        $ highlight_tint = getattr(store, 'color_highlight_tint', (1.0, 1.0, 1.0))
        
        # Convert tints to lift/gain
        $ lift = tuple((1.0 - s) * 0.1 for s in shadow_tint)
        $ gain = highlight_tint
        $ offset = (0.0, 0.0, 0.0)
        
        # Debug output
        python:
            if getattr(store, 'shader_debug_enabled', False):
                print(f"[COMPLETE GRADING] Applying - Temp: {temp:.2f}, Sat: {sat:.2f}, Cont: {cont:.2f}, Bright: {bright:.2f}, Gamma: {gam:.2f}, Vignette: {vig:.2f} [from grade_vignette_strength]")
        
        # Apply the complete grading transform
        add Solid("#00000000") at complete_grading_transform(
            temperature=temp,
            tint=tint,
            saturation=sat,
            contrast=cont,
            brightness=bright,
            gamma=gam,
            lift=lift,
            gain=gain,
            offset=offset,
            vignette_amount=vig,
            vignette_softness=0.5
        ):
            xsize config.screen_width
            ysize config.screen_height

init python:
    def apply_complete_shader_preset(genre, style):
        """Apply shader preset using the complete grading system."""
        
        # Enhanced presets with dramatic values
        COMPLETE_PRESETS = {
            "Film Noir": {
                "Classic": {
                    "temperature": -0.4,
                    "tint": 0.1,
                    "saturation": 0.2,  # Very desaturated
                    "contrast": 1.8,    # High contrast
                    "brightness": -0.2,
                    "gamma": 1.2,
                    "vignette": 0.7,
                    "shadow_tint": (0.7, 0.8, 1.0),
                    "highlight_tint": (1.0, 1.0, 1.1)
                },
                "Smoky Bar": {
                    "temperature": 0.6,  # Very warm
                    "tint": 0.1,
                    "saturation": 0.6,
                    "contrast": 0.8,    # Low contrast for haze
                    "brightness": 0.1,
                    "gamma": 1.3,
                    "vignette": 0.8,
                    "shadow_tint": (1.2, 0.9, 0.6),
                    "highlight_tint": (1.3, 1.1, 0.8)
                },
                "Neon Night": {
                    "temperature": -0.2,
                    "tint": 0.5,       # Heavy magenta
                    "saturation": 1.8,  # Oversaturated
                    "contrast": 1.6,
                    "brightness": 0.1,
                    "gamma": 0.8,
                    "vignette": 0.5,
                    "shadow_tint": (0.6, 0.8, 1.3),
                    "highlight_tint": (1.4, 0.9, 1.2)
                }
            },
            "Sci-Fi": {
                "Cyberpunk": {
                    "temperature": -0.3,
                    "tint": 0.6,       # Very heavy magenta/cyan
                    "saturation": 2.0,  # Maximum saturation
                    "contrast": 1.7,
                    "brightness": 0.2,
                    "gamma": 0.7,
                    "vignette": 0.4,
                    "shadow_tint": (0.5, 0.9, 1.4),
                    "highlight_tint": (1.5, 0.8, 1.3)
                },
                "Space Station": {
                    "temperature": -0.5,  # Very cold
                    "tint": -0.1,
                    "saturation": 0.7,
                    "contrast": 1.3,
                    "brightness": 0.15,
                    "gamma": 0.9,
                    "vignette": 0.2,
                    "shadow_tint": (0.8, 0.9, 1.2),
                    "highlight_tint": (1.0, 1.0, 1.1)
                }
            },
            "Western": {
                "High Noon": {
                    "temperature": 0.8,  # Very hot
                    "tint": 0.0,
                    "saturation": 0.8,
                    "contrast": 2.0,    # Extreme contrast
                    "brightness": 0.2,
                    "gamma": 0.7,
                    "vignette": 0.4,
                    "shadow_tint": (1.2, 1.0, 0.7),
                    "highlight_tint": (1.4, 1.2, 0.9)
                },
                "Sunset Showdown": {
                    "temperature": 0.9,  # Golden hour extreme
                    "tint": 0.3,
                    "saturation": 1.5,
                    "contrast": 1.6,
                    "brightness": 0.1,
                    "gamma": 0.85,
                    "vignette": 0.6,
                    "shadow_tint": (1.4, 1.0, 0.6),
                    "highlight_tint": (1.6, 1.3, 0.8)
                }
            },
            "Horror": {
                "Blood Moon": {
                    "temperature": 0.5,
                    "tint": 0.7,       # Heavy red
                    "saturation": 1.3,
                    "contrast": 1.8,
                    "brightness": -0.4, # Very dark
                    "gamma": 1.5,
                    "vignette": 0.9,   # Almost black edges
                    "shadow_tint": (1.5, 0.6, 0.6),
                    "highlight_tint": (1.6, 0.8, 0.8)
                }
            },
            "Action": {
                "Explosion": {
                    "temperature": 0.9,  # Hot orange
                    "tint": 0.2,
                    "saturation": 1.6,
                    "contrast": 1.9,
                    "brightness": 0.3,
                    "gamma": 0.6,
                    "vignette": 0.5,
                    "shadow_tint": (1.3, 0.9, 0.5),
                    "highlight_tint": (1.5, 1.2, 0.7)
                }
            },
            "Neutral": {
                "Off": {
                    "temperature": 0.0,
                    "tint": 0.0,
                    "saturation": 1.0,
                    "contrast": 1.0,
                    "brightness": 0.0,
                    "gamma": 1.0,
                    "vignette": 0.0,
                    "shadow_tint": (1.0, 1.0, 1.0),
                    "highlight_tint": (1.0, 1.0, 1.0)
                },
                "Subtle": {
                    "temperature": 0.05,
                    "tint": 0.0,
                    "saturation": 1.1,
                    "contrast": 1.1,
                    "brightness": 0.05,
                    "gamma": 0.95,
                    "vignette": 0.15,
                    "shadow_tint": (0.98, 0.99, 1.02),
                    "highlight_tint": (1.02, 1.01, 0.98)
                }
            }
        }
        
        # Check if we have this preset
        if genre in COMPLETE_PRESETS and style in COMPLETE_PRESETS[genre]:
            preset = COMPLETE_PRESETS[genre][style]
            
            # Apply all values
            store.color_grading_enabled = True
            store.current_shader_genre = genre
            store.current_shader_style = style
            
            store.color_temperature = preset["temperature"]
            store.color_tint = preset["tint"]
            store.color_saturation = preset["saturation"]
            store.shader_contrast = preset["contrast"]
            store.shader_brightness = preset["brightness"]
            store.shader_gamma = preset["gamma"]
            store.grade_vignette_strength = preset["vignette"]
            store.color_shadow_tint = preset["shadow_tint"]
            store.color_highlight_tint = preset["highlight_tint"]
            
            print(f"[COMPLETE SHADER] Applied {genre} - {style}")
            print(f"  Temperature: {preset['temperature']:.2f}")
            print(f"  Saturation: {preset['saturation']:.2f}")
            print(f"  Contrast: {preset['contrast']:.2f}")
            print(f"  Brightness: {preset['brightness']:.2f}")
            print(f"  Gamma: {preset['gamma']:.2f}")
            print(f"  Vignette: {preset['vignette']:.2f}")
            
            renpy.restart_interaction()
            return True
        else:
            # Fall back to original preset system
            if hasattr(store, 'get_shader_preset'):
                preset = get_shader_preset(genre, style)
                if preset:
                    store.color_grading_enabled = True
                    store.current_shader_genre = genre
                    store.current_shader_style = style
                    
                    store.color_temperature = preset.get("temperature", 0.0)
                    store.color_tint = preset.get("tint", 0.0)
                    store.color_saturation = preset.get("saturation", 1.0)
                    store.shader_contrast = preset.get("contrast", 1.0)
                    store.shader_brightness = preset.get("brightness", 0.0)
                    store.shader_gamma = preset.get("gamma", 1.0)
                    store.grade_vignette_strength = preset.get("vignette", 0.0)
                    store.color_shadow_tint = preset.get("shadow_tint", (1.0, 1.0, 1.0))
                    store.color_highlight_tint = preset.get("highlight_tint", (1.0, 1.0, 1.0))
                    
                    print(f"[COMPLETE SHADER] Applied fallback {genre} - {style}")
                    renpy.restart_interaction()
                    return True
            return False
    
    # Override the original apply function, preserving any prior implementation if present
    if not hasattr(store, '_original_apply_shader_preset'):
        store._original_apply_shader_preset = globals().get('apply_shader_preset_to_screen', None)
    
    def apply_shader_preset_to_screen(genre, style):
        """Enhanced wrapper that uses complete grading."""
        result = apply_complete_shader_preset(genre, style)
        if (not result) and getattr(store, '_original_apply_shader_preset', None):
            # Fall back to original if no complete preset
            result = store._original_apply_shader_preset(genre, style)
        return result
