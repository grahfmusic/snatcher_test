
# Recreate UI — Shader Editor (Modern, Rounded, Slightly Transparent)

**Audience:** Codex (AI) agent  
**Goal:** Rebuild the Shader Editor screen’s UI to a modern look with **rounded**, **slightly transparent** components, strict **10px** body / **9px** secondary fonts, and improved **preset list boxes** (searchable, consistent).

---

## Constraints (must-haves)

- **Typography:** Only two sizes — **10px** (body, values, buttons, section titles in bold) and **9px** (secondary/hints/help).
- **Visual:** Rounded, glassy/transparent cards and panels; pill/segmented buttons; 10px-thick sliders/scrollbars.
- **Behavior:** Keep throttled updates for sliders (avoid stutter), preserve modal behavior and z-order.
- **Lists:** Preset lists and any tabbed lists should use a compact, searchable list component with hover/selected styling.
- **No other font sizes** or inconsistent paddings introduced.

---

## Affected Scope

- Shader Editor screen (currently `unified_editor` in `game/editor/editor_shader_interface.rpy`), and any preset list UI it shows.
- (Optional but recommended for consistency): `confirm` and `choice` screens.

---

## Deliverables

1. **Theme file:** `game/ui/ui_modern_editor_small.rpy` — defines glass styles, fonts, sizes, pill buttons, bars, scrollbars, backdrop, and a reusable list widget.
2. **Assets (9-slice PNG):** `game/gui/glass/`
   - `glass_panel_16.png`, `glass_card_12.png`
   - `glass_seg_on_12.png`, `glass_seg_off_12.png`
   - `glass_bar_fill_6.png`, `glass_bar_bg_6.png`
   - `glass_thumb_7.png`
3. **Popup overrides (optional):** `game/ui/ui_popups_overrides.rpy` (`screen confirm`, `screen choice`) in the same glass style.
4. **Shader Editor refactor:** Apply new styles, enforce font sizes, replace preset list with the reusable list widget.

---

## Implementation Steps

### 1) Add Theme & Assets

Create **`game/ui/ui_modern_editor_small.rpy`** with the following definitions (excerpt — do not change sizes):

```renpy
init 999 python:
    MX_COL_BG      = "#0B0F15CC"   # backdrop (≈80% opacity)
    MX_COL_TEXT    = "#E6EEF6"
    MX_COL_SUBTLE  = "#AAB6C5"
    MX_FONT        = "fonts/MapleMono-Regular.ttf"
    MX_FONT_BOLD   = "fonts/MapleMono-Bold.ttf"

transform mx_popin:
    alpha 0.0
    zoom 0.98
    easein 0.15 alpha 1.0 zoom 1.0

# Typography (strict)
style igx_default is default:
    font MX_FONT
    size 10
    color MX_COL_TEXT
style igx_small_text is igx_default:
    size 9
    color MX_COL_SUBTLE
style igx_title_text is igx_default:
    font MX_FONT_BOLD
    size 10

# Rounded, translucent frames
style igx_frame is frame:
    background Frame("gui/glass/glass_panel_16.png", 16, 16)
    padding (12, 10)
style igx_card is frame:
    background Frame("gui/glass/glass_card_12.png", 12, 12)
    padding (10, 8)

# Pill buttons
style igx_textbutton is textbutton:
    background Frame("gui/glass/glass_seg_off_12.png", 12, 12)
    hover_background Frame("gui/glass/glass_seg_on_12.png", 12, 12)
    selected_background Frame("gui/glass/glass_seg_on_12.png", 12, 12)
    padding (8, 5)
style igx_textbutton_text is igx_default:
    font MX_FONT_BOLD
    size 10

# Compact bars/scrollbars (10px)
style igx_bar is bar:
    left_bar Frame("gui/glass/glass_bar_fill_6.png", 6, 6)
    right_bar Frame("gui/glass/glass_bar_bg_6.png", 6, 6)
    thumb "gui/glass/glass_thumb_7.png"
    ymaximum 10
style igx_vscrollbar is vscrollbar:
    base_bar Frame("gui/glass/glass_bar_bg_6.png", 6, 6)
    thumb "gui/glass/glass_thumb_7.png"
    xmaximum 10
style igx_hscrollbar is hscrollbar:
    base_bar Frame("gui/glass/glass_bar_bg_6.png", 6, 6)
    thumb "gui/glass/glass_thumb_7.png"
    ymaximum 10

# Backdrop
style igx_backdrop is default:
    background Solid(MX_COL_BG)
```

Add **list styles + reusable list widget** for presets/groups:

```renpy
# List styles
style igx_list_button is button:
    background None
    hover_background Frame("gui/glass/glass_card_12.png", 12, 12)
    selected_background Frame("gui/glass/glass_seg_on_12.png", 12, 12)
    padding (8, 6)
    xfill True
style igx_list_button_text is igx_default:
    size 10
style igx_list_viewport is viewport:
    ymaximum 360
    scrollbars "vertical"

# Reusable list widget
screen igx_list(items=[], on_pick=None, allow_search=False):
    default _q = ""
    style_prefix "igx"
    vbox:
        spacing 8
        if allow_search:
            hbox:
                spacing 8
                text "Search:" style "igx_small_text"
                input value ScreenVariableInputValue("_q") length 32 allow " abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-." pixel_width 260
                textbutton "Clear" action SetScreenVariable("_q", "")
        $ _items = [it for it in items if (not _q) or (_q.lower() in str(it[0]).lower())]
        viewport:
            style "igx_list_viewport"
            mousewheel True
            vbox:
                spacing 6
                for label, payload, is_sel in _items:
                    textbutton str(label) style "igx_list_button" text_style "igx_list_button_text" selected is_sel action (on_pick(payload) if on_pick else NullAction())
```

Copy assets to `game/gui/glass/` with the exact filenames shown in **Deliverables**.

### 2) Map Existing Shader Editor Styles

At the end of the same theme file, **map** the existing shader editor prefix to the glass styles (so we don’t rewrite screens):

```renpy
style shader_editor_default is igx_default
style shader_editor_text is igx_default
style shader_editor_small_text is igx_small_text
style shader_editor_title_text is igx_title_text
style shader_editor_frame is igx_frame
style shader_editor_window is igx_card
style shader_editor_textbutton is igx_textbutton
style shader_editor_textbutton_text is igx_textbutton_text
style shader_editor_bar is igx_bar
style shader_editor_vscrollbar is igx_vscrollbar
style shader_editor_hscrollbar is igx_hscrollbar
```

### 3) Refactor Shader Editor Screen (UI only)

In `game/editor/editor_shader_interface.rpy` (the screen for `unified_editor`):

- Ensure a `style_prefix "shader_editor"` is set at/near the root container of the editor UI.
- Replace **inline sizes** with styles:
  - `size 12` → `style "shader_editor_title_text"` (10px bold)
  - `size 11` → remove (inherit 10px via `shader_editor_default` / `shader_editor_text`)
  - `size 10` (if hints/help) → `style "shader_editor_small_text"` (9px)
- Set outer window frame to use rounded card & pop-in:
  ```renpy
  frame at mx_popin:
      style "shader_editor_frame"
      ...
  ```
- Apply compact bars/scrollbars:
  ```renpy
  bar value <...> style "shader_editor_bar"
  viewport:
      scrollbars "vertical"
      vbar_style "shader_editor_vscrollbar"
  ```

### 4) Replace Preset List Boxes

Where the preset list appears, replace ad-hoc buttons/viewport with the reusable list:

```renpy
$ items = [(k, k, False) for k in sorted(presets.keys())]
use igx_list(items=items,
             on_pick=lambda key: [Function(load_preset_fn, key), Return()],
             allow_search=True)
```

### 5) (Optional) Glass Popups

Create `game/ui/ui_popups_overrides.rpy` and implement:

```renpy
screen confirm(message, yes_action, no_action):
    modal True
    zorder 200
    add Solid(MX_COL_BG)
    style_prefix "igx"
    frame at mx_popin:
        style "igx_card"
        vbox:
            spacing 10
            text message style "igx_title_text"
            hbox:
                spacing 10
                textbutton "OK" action yes_action style "igx_textbutton"
                textbutton "Cancel" action no_action style "igx_textbutton"
    key "K_ESCAPE" action no_action
```

### 6) Keep Interaction Smooth

Ensure sliders use a throttled `changed` function to avoid excessive `renpy.restart_interaction()` calls (keep or add a 0.12s cooldown).

---

## Acceptance Checklist

- [ ] All editor body text is 10px; helper text is 9px; section titles are 10px bold.
- [ ] Outer editor window + inner cards are rounded and slightly transparent.
- [ ] Sliders/scrollbars are ~10px thick; slider thumb is rounded.
- [ ] Preset list uses the reusable list widget (searchable, hover/selected states).
- [ ] Modal confirm popup is glass-styled and uses 10px/9px typography.
- [ ] Dragging sliders feels smooth (no stutter); updates are throttled.
- [ ] No remaining `size 11/12` in editor screens.

---

## Notes

- Images are designed as 9-slice frames; keep the slice radii (`16` for panels, `12` for cards/pills, `6` for bars) as provided.
- If your project uses different fonts, point `MX_FONT`/`MX_FONT_BOLD` to the desired files; **do not change sizes**.
- For additional lists (tabs, groups, pipelines), reuse `igx_list(...)` for consistency.

