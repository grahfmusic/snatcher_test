# Room Transforms
# Contains all animation transforms for the room exploration system
#
# Overview
# - Reusable transforms and helpers for floating descriptions and hotspot highlighting (no bloom).

init python:
    import hashlib

    def compute_float_phase(key, intensity=1.0, max_delay=0.8):
        """Deterministic per-key offsets and a small start delay.
        Produces mid-amplitude starting offsets so motion feels in-progress.
        """
        try:
            s = f"{key}|float_phase|{float(intensity):.3f}"
        except Exception:
            s = f"{key}|float_phase"
        h = hashlib.sha256(s.encode("utf-8")).hexdigest()

        def unit(idx):
            # 8 hex chars -> 32-bit int -> [0,1)
            return int(h[idx:idx+8], 16) / 0x100000000

        rx, ry, rr, rd = unit(0), unit(8), unit(16), unit(24)
        sx = -1 if int(h[32:34], 16) % 2 == 0 else 1
        sy = -1 if int(h[34:36], 16) % 2 == 0 else 1
        sr = -1 if int(h[36:38], 16) % 2 == 0 else 1

        amp_x = 8.0 * intensity
        amp_y = 6.0 * intensity
        amp_r = 1.5 * intensity

        # Start near mid amplitude (35%..65%) for a natural in-progress feel
        scale = lambda u: 0.35 + 0.30 * u
        x0 = sx * amp_x * scale(rx)
        y0 = sy * amp_y * scale(ry)
        r0 = sr * amp_r * scale(rr)
        delay = rd * max_delay
        return x0, y0, r0, delay

# Transform for dynamic floating animation of speech bubble with configurable intensity
transform floating_bubble(intensity=1.0, x0=0.0, y0=0.0, r0=0.0, start_delay=0.0):
    # Set initial offsets/rotation and wait a tiny per-instance delay
    xoffset x0
    yoffset y0
    rotate r0
    pause start_delay

    # Multi-directional floating motion scaled by intensity
    parallel:
        ease 1.8 xoffset -(8 * intensity)
        ease 1.8 xoffset (8 * intensity)
        repeat
    parallel:
        ease 2.2 yoffset -(6 * intensity)
        ease 2.2 yoffset (6 * intensity)
        repeat
    parallel:
        # Subtle rotation for more organic feel scaled by intensity
        ease 3.0 rotate -(1.5 * intensity)
        ease 3.0 rotate (1.5 * intensity)
        repeat

# Static transform for no floating (when intensity is 0)
transform no_float:
    pass

# Simple description box fade transform - always fades in
transform descbox_fade_simple(fade_duration=0.3):
    # Always start invisible and fade in
    alpha 0.0
    linear fade_duration alpha 1.0

# Fade out transform for disappearing descriptions
transform descbox_fade_out(fade_duration=0.25):
    # Start visible and fade out
    alpha 1.0
    linear fade_duration alpha 0.0

# Enhanced fade transform with proper fade out support
transform descbox_fade_enhanced(fade_in=0.3, fade_out=0.25):
    # Start invisible and fade in
    alpha 0.0
    linear fade_in alpha 1.0
    
    # Stay visible until a fade out is triggered
    block:
        alpha 1.0
        0.01  # Small pause to keep the loop running
        repeat

# Working event-based fade transform
transform descbox_fade_working(fade_in=0.3, fade_out=0.25):
    alpha 0.0
    on show:
        linear fade_in alpha 1.0
    on hide:
        linear fade_out alpha 0.0

# Legacy bloom transforms removed; using desaturation for hover highlights.

# Pulsing border transform for interaction buttons
transform pulsing_border:
    alpha 1.0
    block:
        linear 0.8 alpha 0.3
        linear 0.8 alpha 1.0
        repeat

# Static border transform for non-selected buttons
transform static_border:
    alpha 1.0

# Legacy edge highlight transforms removed.

# Desaturation highlight transform - desaturates and slightly darkens object for clear selection
transform object_desaturation_highlight(pulse_speed=2.0, sat=0.3, bright_low=-0.08, bright_high=0.12, contrast=1.1):
    # Start at normal saturation/contrast and brightness
    matrixcolor (ContrastMatrix(1.0) * SaturationMatrix(1.0) * BrightnessMatrix(0.0))
    alpha 1.0
    subpixel True
    anchor (0, 0)

    # Initial transition to a clearly visible highlight state
    # Lower saturation, modest contrast lift, and slight brighten for visibility under grading
    ease pulse_speed * 0.8 matrixcolor (ContrastMatrix(contrast) * SaturationMatrix(sat) * BrightnessMatrix(bright_high))

    # Pulse between normal and highlighted state for a detectable effect even with heavy grading
    block:
        ease pulse_speed * 0.8 matrixcolor (ContrastMatrix(1.0) * SaturationMatrix(1.0) * BrightnessMatrix(0.0))
        ease pulse_speed * 0.8 matrixcolor (ContrastMatrix(contrast) * SaturationMatrix(sat) * BrightnessMatrix(bright_low))
        repeat

# Graceful desaturation fade-out transform - for when leaving an object during pulse animation
transform object_desaturation_fadeout(fade_duration=0.4):
    # This transform smoothly fades from whatever desaturated state back to normal
    # It's designed to be applied when unhover occurs during active pulsing
    alpha 1.0
    subpixel True
    anchor (0, 0)
    
    # Quick but smooth fade from current state to normal with neutral contrast
    ease fade_duration matrixcolor (ContrastMatrix(1.0) * SaturationMatrix(1.0) * BrightnessMatrix(0.0))

# Normal saturation reset transform - for objects that were never hovered or already normal
transform object_normal_saturation:
    # Instantly set to normal saturation and brightness for objects that should be normal
    matrixcolor SaturationMatrix(1.0) * BrightnessMatrix(0.0)
    alpha 1.0
    subpixel True
    anchor (0, 0)

# Tinted highlight overlay using the object's own image.
# This is drawn on top of all lighting/front passes to guarantee visibility.
transform object_tint_highlight(pulse_speed=0.8, tint="#ffffff", alpha_low=0.35, alpha_high=0.85):
    matrixcolor TintMatrix(tint)
    alpha alpha_low
    additive True
    subpixel True
    anchor (0, 0)
    block:
        ease pulse_speed alpha alpha_high
        ease pulse_speed alpha alpha_low
        repeat
