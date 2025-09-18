# Lighting Editor Quickstart

This guide helps you get productive with the multi‑light Lighting Editor.

## Open & Navigation
- F8 → Shader Editor → Lighting → Open Lighting Editor
- Ctrl+F8 → Lighting Selector (preset browser)
- Lighting Editor opens from Ctrl+F8 (Lighting Selector → “Edit Lights…”) or from F8 Shader Editor → Lighting → “Open Lighting Editor”
- ESC closes the Lighting Editor; “Back to Selector” returns to Ctrl+F8

## Layout
- Left: Lights list — add (+), enable/disable, delete, select
- Center: Scene canvas — draggable handles for each light
  - Square = light position; drag to move
  - Small dot = spot/directional aim; drag to set direction
- Right: Properties — type, layer, intensity, radius, angle, color, falloff, bloom, animation

## Basic Workflow
1) Start with a preset (Ctrl+F8) or add a light with +Add
2) Move/aim on canvas; fine‑tune in Properties
3) Set falloff: Smooth (default), Linear, Quadratic, Inverse Square, or Custom (with exponent)
4) Toggle Bloom if you want highlight glow; tune threshold/strength/radius
5) Add motion: Flicker (noisy), Pulse (sinus), Sweep (scan a cone)
6) Save via the Lighting Selector header (Save As) or YAML utilities

## Presets (YAML v2.1)
- Location: `game/yaml/shaders/preset/light_*.yaml` (shipped), `game/yaml/shaders/custom/light_*.yaml` (user)
- Globals (optional): `strength`, `bloom_threshold`, `bloom_strength`, `bloom_radius`
- Per‑light: `type, position, radius, color, intensity, direction, angle, layer, enabled, falloff, falloff_exp, bloom_boost, animation{...}`

## Animations
- Flicker: `{ min, max, speed_hz, seed }` — intensity jitter
- Pulse: `{ base, amplitude, period_s, phase }` — smooth intensity cycle
- Sweep: `{ start_angle, end_angle, angular_speed, loop }` — aim rotation
- The animation driver runs ~30 Hz and pauses while the Lighting Editor is open (configurable)

## Quick Bloom
- F8 → Lighting tab has a Bloom On/Off toggle and global sliders
- Script helpers: `bloom_on(threshold, strength, radius)`, `bloom_off()`, or `room.bloom(True, ...)`

## Tips
- Use `Layer: back` for background illumination, `front` for rim/highlights
- Keep radius reasonable; use falloff to control edge softness
- Bloom: lower threshold → more pixels bloom; strength controls overall glow
- Performance: fewer, larger lights are generally cheaper than many small lights

## Troubleshooting
- No effect? Ensure lights are enabled and `lighting_strength > 0`
- Artifacts: try Smooth/Quadratic falloff; reduce Bloom strength/radius
- Preset not loading: check filename prefix `light_*.yaml`

Happy lighting!
