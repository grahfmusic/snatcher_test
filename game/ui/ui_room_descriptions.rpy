# Room Description Box System
# Floating and fixed description boxes with dynamic sizing
#
# Overview
# - Computes box sizes from text length and renders a curved frame with text.
# - Supports floating animation and bottom area variant.

# Common utilities are loaded by Ren'Py loader already.

# Description box configuration
define DESCRIPTION_BOX_CONFIG = {
    "min_width": 200,
    "max_width": 350,
    "min_height": 60,
    "max_height": 120,
    "padding": {"horizontal": 15, "vertical": 10},
    "text_margin": 30,
    "background": "curved_box_small.png",
    "border_size": 20
}

define DESCRIPTION_TEXT_CONFIG = {
    "color": "#e9af78",
    "size": 16,
    "align": 0.5,
    "font": "fonts/quaver.ttf",
    # Outline used as a soft drop shadow for readability
    "outline": {"size": 2, "color": "#000000aa", "xoffset": 0, "yoffset": 2}
}

define BOTTOM_DESCRIPTION_CONFIG = {
    "xpos": 0,
    "ypos": 620,
    "width": 1280,
    "height": 100,
    "background": "#000000cc",
    "padding": {"horizontal": 30, "vertical": 20},
    "title_color": "#ffff00",
    "title_size": 24,
    "text_color": "#bce7de",
    "text_size": 16,
    "default_color": "#cccccc",
    "default_size": 16
}

# Initialize fade configuration with sensible defaults
init 5 python:
    # Ensure a fade sub-config exists and set defaults if absent.
    if "fade" not in DESCRIPTION_BOX_CONFIG:
        DESCRIPTION_BOX_CONFIG["fade"] = {}

    _fade = DESCRIPTION_BOX_CONFIG["fade"]
    # Force update for quick, smooth fades
    _fade["enabled"] = True
    _fade["in"] = 0.3       # seconds; fade in duration (quick but smooth)
    _fade["out"] = 0.25     # seconds; fade out duration (quick but smooth)
    _fade["cross"] = 0.3    # seconds; crossfade when switching objects

init python:
    def calculate_description_box_size(description):
        """Calculate dynamic box dimensions based on description length"""
        text_length = len(description)
        
        box_width = min(
            DESCRIPTION_BOX_CONFIG["max_width"],
            max(DESCRIPTION_BOX_CONFIG["min_width"], text_length * 3 + 100)
        )
        
        # Add extra height for better line spacing with pixel font
        line_height = 26  # 16px font + 10px extra spacing
        estimated_lines = (text_length // 40 + 2)
        calculated_height = estimated_lines * line_height
        
        box_height = min(
            DESCRIPTION_BOX_CONFIG["max_height"] + 20,  # Allow slightly taller boxes
            max(DESCRIPTION_BOX_CONFIG["min_height"], calculated_height)
        )
        
        return box_width, box_height

# Screen fragment for floating description box - using property functions to eliminate duplication
screen floating_description_box(obj, box_width, box_height, box_x, box_y, float_intensity):
    # Put description boxes on high z-order to appear above letterbox
    zorder 150
    
    # Pull fade configuration into screen scope
    $ _cfg = DESCRIPTION_BOX_CONFIG
    $ _fade_cfg = _cfg.get("fade", {})
    $ _fade_enabled = _fade_cfg.get("enabled", True)
    $ _fade_in = _fade_cfg.get("in", 0.35)
    $ _fade_out = _fade_cfg.get("out", 0.25)
    $ _fade_cross = _fade_cfg.get("cross", _fade_in)
    
    $ frame_props = get_description_frame_properties(box_x, box_y, box_width, box_height)
    $ text_props = get_description_text_properties(box_width)
    
    # Compose fade and floating transforms
    if float_intensity > 0.0:
        $ x0, y0, r0, dly = compute_float_phase(current_hover_object, float_intensity)
        if _fade_enabled:
            frame at descbox_fade_simple(_fade_in), floating_bubble(float_intensity, x0, y0, r0, dly):
                xpos frame_props["xpos"]
                ypos frame_props["ypos"]
                xsize frame_props["xsize"]
                ysize frame_props["ysize"]
                background frame_props["background"]
                padding frame_props["padding"]
                
                text obj["description"]:
                    xalign text_props["xalign"]
                    yalign text_props["yalign"]
                    color text_props["color"]
                    size text_props["size"]
                    text_align text_props["text_align"]
                    xmaximum text_props["xmaximum"]
                    font text_props["font"]
                    outlines text_props["outlines"]
                    line_spacing 2
        else:
            frame at floating_bubble(float_intensity, x0, y0, r0, dly):
                xpos frame_props["xpos"]
                ypos frame_props["ypos"]
                xsize frame_props["xsize"]
                ysize frame_props["ysize"]
                background frame_props["background"]
                padding frame_props["padding"]
                
                text obj["description"]:
                    xalign text_props["xalign"]
                    yalign text_props["yalign"]
                    color text_props["color"]
                    size text_props["size"]
                    text_align text_props["text_align"]
                    xmaximum text_props["xmaximum"]
                    font text_props["font"]
                    outlines text_props["outlines"]
                    line_spacing 2
    else:
        if _fade_enabled:
            frame at descbox_fade_simple(_fade_in), no_float:
                xpos frame_props["xpos"]
                ypos frame_props["ypos"]
                xsize frame_props["xsize"]
                ysize frame_props["ysize"]
                background frame_props["background"]
                padding frame_props["padding"]
                
                text obj["description"]:
                    xalign text_props["xalign"]
                    yalign text_props["yalign"]
                    color text_props["color"]
                    size text_props["size"]
                    text_align text_props["text_align"]
                    xmaximum text_props["xmaximum"]
                    font text_props["font"]
                    outlines text_props["outlines"]
                    line_spacing 2
        else:
            frame at no_float:
                xpos frame_props["xpos"]
                ypos frame_props["ypos"]
                xsize frame_props["xsize"]
                ysize frame_props["ysize"]
                background frame_props["background"]
                padding frame_props["padding"]
                
                text obj["description"]:
                    xalign text_props["xalign"]
                    yalign text_props["yalign"]
                    color text_props["color"]
                    size text_props["size"]
                    text_align text_props["text_align"]
                    xmaximum text_props["xmaximum"]
                    font text_props["font"]
                    outlines text_props["outlines"]
                    line_spacing 2

# Screen fragment for fading out description box
screen floating_description_box_fadeout(obj, box_width, box_height, box_x, box_y, float_intensity, fade_duration):
    # Put description boxes on high z-order to appear above letterbox
    zorder 150
    
    $ frame_props = get_description_frame_properties(box_x, box_y, box_width, box_height)
    $ text_props = get_description_text_properties(box_width)
    
    # Apply fade-out transform
    if float_intensity > 0.0:
        $ x0, y0, r0, dly = compute_float_phase(obj.get("name", "unknown"), float_intensity)
        frame at descbox_fade_out(fade_duration), floating_bubble(float_intensity, x0, y0, r0, dly):
            xpos frame_props["xpos"]
            ypos frame_props["ypos"]
            xsize frame_props["xsize"]
            ysize frame_props["ysize"]
            background frame_props["background"]
            padding frame_props["padding"]
            
            text obj["description"]:
                xalign text_props["xalign"]
                yalign text_props["yalign"]
                color text_props["color"]
                size text_props["size"]
                text_align text_props["text_align"]
                xmaximum text_props["xmaximum"]
                font text_props["font"]
                outlines text_props["outlines"]
                line_spacing 2
    else:
        frame at descbox_fade_out(fade_duration), no_float:
            xpos frame_props["xpos"]
            ypos frame_props["ypos"]
            xsize frame_props["xsize"]
            ysize frame_props["ysize"]
            background frame_props["background"]
            padding frame_props["padding"]
            
            text obj["description"]:
                xalign text_props["xalign"]
                yalign text_props["yalign"]
                color text_props["color"]
                size text_props["size"]
                text_align text_props["text_align"]
                xmaximum text_props["xmaximum"]
                font text_props["font"]
                outlines text_props["outlines"]
                line_spacing 2

# Overlay screen to render hover tint + floating description on the overlay layer
screen hover_ui_overlay():
    # Same layer as interaction menu; above most content
    zorder 150

    # Determine whether overlay should render
    $ editor_open = getattr(store, 'shader_editor_open', False) or getattr(store, 'editor_visible', False)
    $ selector_open = getattr(store, 'lighting_selector_open', False)
    $ lighting_editor_open = getattr(store, 'lighting_editor_open', False)
    $ _blocked = editor_open or selector_open or lighting_editor_open

    if not _blocked:
        # Wrap overlay in CRT transform when active so geometry aligns
        $ _crt_enabled = getattr(store, 'crt_stable_state', False) or getattr(store, 'crt_enabled', False)
        if _crt_enabled:
            $ crt_warp = getattr(store, 'crt_warp', 0.2)
            $ crt_scan = getattr(store, 'crt_scan', 0.5)
            $ crt_chroma = getattr(store, 'crt_chroma', 0.9)
            $ crt_scanline_size = getattr(store, 'crt_scanline_size', 1.0)
            $ crt_vignette_strength = getattr(store, 'grade_vignette_strength', 0.0)
            $ crt_vignette_width = getattr(store, 'grade_vignette_width', 0.25)
            $ crt_vignette_feather = getattr(store, 'grade_vignette_feather', 1.0)
            $ crt_animated = getattr(store, 'crt_animated', False)
            $ _ab_mode_name = str(getattr(store, 'crt_aberr_mode', 'none')).lower()
            $ _ab_mode = 0 if _ab_mode_name == 'none' else (1 if _ab_mode_name == 'pulse' else (2 if _ab_mode_name == 'flicker' else 3))
            $ _ab_amp = float(getattr(store, 'crt_aberr_amount', getattr(store, 'crt_chroma', 0.0)))
            $ _ab_speed = float(getattr(store, 'crt_aberr_speed', 1.0))
            $ _ab_r = float(getattr(store, 'crt_aberr_r', 1.0))
            $ _ab_g = float(getattr(store, 'crt_aberr_g', 0.0))
            $ _ab_b = float(getattr(store, 'crt_aberr_b', 1.0))
            $ _scan_spd = float(getattr(store, 'crt_scanline_speed', 2.0))
            $ _scan_amt = float(getattr(store, 'crt_scanline_intensity', 0.1))

            fixed at (animated_chroma_crt(crt_warp, crt_scan, crt_chroma, crt_scanline_size, animation_intensity=_scan_amt, animation_speed=_scan_spd, vignette_strength=crt_vignette_strength, vignette_width=crt_vignette_width, vignette_feather=crt_vignette_feather, aberr_mode=_ab_mode, aberr_amp=_ab_amp, aberr_speed=_ab_speed, aberr_r=_ab_r, aberr_g=_ab_g, aberr_b=_ab_b, glitch=getattr(store,'crt_glitch',0.0), glitch_speed=getattr(store,'crt_glitch_speed',1.0)) if crt_animated else static_chroma_crt(crt_warp, crt_scan, crt_chroma, crt_scanline_size, vignette_strength=crt_vignette_strength, vignette_width=crt_vignette_width, vignette_feather=crt_vignette_feather, aberr_mode=_ab_mode, aberr_amp=_ab_amp, aberr_speed=_ab_speed, aberr_r=_ab_r, aberr_g=_ab_g, aberr_b=_ab_b, glitch=getattr(store,'crt_glitch',0.0), glitch_speed=getattr(store,'crt_glitch_speed',1.0))):
                xsize config.screen_width
                ysize config.screen_height
                use _hover_overlay_inner
        # Always render description unwarped on overlay layer
        $ hov2 = getattr(store, 'current_hover_object', None) or getattr(store, 'gamepad_selected_object', None)
        if hov2 and hov2 in room_objects:
            $ obj2 = room_objects[hov2]
            $ box_w2, box_h2 = calculate_description_box_size(obj2.get("description", ""))
            $ pos_setting2 = obj2.get("box_position", "auto")
            $ box_x2, box_y2, _ = calculate_box_position(obj2, box_w2, box_h2, pos_setting2)
            $ float_intensity2 = obj2.get("float_intensity", 1.0)
            use floating_description_box(obj2, box_w2, box_h2, box_x2, box_y2, float_intensity2)
        else:
            use _hover_overlay_inner
            $ hov3 = getattr(store, 'current_hover_object', None) or getattr(store, 'gamepad_selected_object', None)
            if hov3 and hov3 in room_objects:
                $ obj3 = room_objects[hov3]
                $ box_w3, box_h3 = calculate_description_box_size(obj3.get("description", ""))
                $ pos_setting3 = obj3.get("box_position", "auto")
                $ box_x3, box_y3, _ = calculate_box_position(obj3, box_w3, box_h3, pos_setting3)
                $ float_intensity3 = obj3.get("float_intensity", 1.0)
                use floating_description_box(obj3, box_w3, box_h3, box_x3, box_y3, float_intensity3)

screen _hover_overlay_inner():
    # Choose hover target; prefer current_hover_object
    $ hov = getattr(store, 'current_hover_object', None) or getattr(store, 'gamepad_selected_object', None)
    if hov and hov in room_objects:
        $ obj = room_objects[hov]
        $ props = get_object_display_properties(obj)
        $ tr = obj.get("transform", None)
        
        # Compute auto-tint based on object dominant color
        $ _auto_tint = get_highlight_tint_for_object(hov) if 'get_highlight_tint_for_object' in globals() else '#ffffff'

        # Prefer pixel-perfect focus mask (scaled image) for exact alignment
        $ _mask = get_object_focus_mask(obj) if 'get_object_focus_mask' in globals() else None
        $ _x = props["xpos"]
        $ _y = props["ypos"]

        # Top-layer additive tint highlight for visibility (inside CRT wrapper)
        if tr:
            add (_mask if _mask else props["image"]) at object_tint_highlight(tint=_auto_tint), tr:
                xpos _x
                ypos _y
        else:
            add (_mask if _mask else props["image"]) at object_tint_highlight(tint=_auto_tint):
                xpos _x
                ypos _y

        # Floating description box (outside CRT wrapper via caller) is handled separately

init python:
    # Register the hover overlay so it renders globally on the overlay layer
    if 'hover_ui_overlay' not in config.overlay_screens:
        config.overlay_screens.append('hover_ui_overlay')

# Python function to create shared frame properties
init python:
    def get_description_frame_properties(box_x, box_y, box_width, box_height):
        """Get common frame properties for description boxes"""
        return {
            "xpos": box_x,
            "ypos": box_y,
            "xsize": box_width,
            "ysize": box_height,
            "background": Frame(
                DESCRIPTION_BOX_CONFIG["background"], 
                DESCRIPTION_BOX_CONFIG["border_size"], 
                DESCRIPTION_BOX_CONFIG["border_size"], 
                tile=False
            ),
            "padding": (
                DESCRIPTION_BOX_CONFIG["padding"]["horizontal"], 
                DESCRIPTION_BOX_CONFIG["padding"]["vertical"]
            )
        }
    
    def get_description_text_properties(box_width):
        """Get common text properties for description text"""
        outline_cfg = DESCRIPTION_TEXT_CONFIG.get("outline") or {}
        outlines = [
            (
                outline_cfg.get("size", 2),
                outline_cfg.get("color", "#000000aa"),
                outline_cfg.get("xoffset", 0),
                outline_cfg.get("yoffset", 2),
            )
        ]
        return {
            "xalign": DESCRIPTION_TEXT_CONFIG["align"],
            "yalign": DESCRIPTION_TEXT_CONFIG["align"],
            "color": DESCRIPTION_TEXT_CONFIG["color"],
            "size": DESCRIPTION_TEXT_CONFIG["size"],
            "text_align": DESCRIPTION_TEXT_CONFIG["align"],
            "xmaximum": box_width - DESCRIPTION_BOX_CONFIG["text_margin"],
            "font": get_font(),
            "outlines": outlines
        }

# Screen fragment for bottom description area
screen bottom_description_area():
    frame:
        xpos BOTTOM_DESCRIPTION_CONFIG["xpos"]
        ypos BOTTOM_DESCRIPTION_CONFIG["ypos"]
        xsize BOTTOM_DESCRIPTION_CONFIG["width"]
        ysize BOTTOM_DESCRIPTION_CONFIG["height"]
        background BOTTOM_DESCRIPTION_CONFIG["background"]
        padding (
            BOTTOM_DESCRIPTION_CONFIG["padding"]["horizontal"], 
            BOTTOM_DESCRIPTION_CONFIG["padding"]["vertical"]
        )
        
        if current_hover_object:
            vbox:
                text "Examining: [format_object_name(current_hover_object)]":
                    color BOTTOM_DESCRIPTION_CONFIG["title_color"]
                    size BOTTOM_DESCRIPTION_CONFIG["title_size"]
                    font get_font()
                text room_objects[current_hover_object]["description"]:
                    color BOTTOM_DESCRIPTION_CONFIG["text_color"]
                    size BOTTOM_DESCRIPTION_CONFIG["text_size"]
                    font get_font()
        else:
            text "Hover over objects in the room to examine them.":
                color BOTTOM_DESCRIPTION_CONFIG["default_color"]
                size BOTTOM_DESCRIPTION_CONFIG["default_size"]
                font get_font()
