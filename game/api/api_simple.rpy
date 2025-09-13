# Simple API
# High-level helpers to define rooms and objects with minimal boilerplate.
#
# Goals
# - Let creators define rooms/objects with a tiny, readable DSL.
# - Auto-size from image assets and apply scale, so widths/heights are not repeated.
# - Allow per-object interactions inline, without extra logic code.
# - Register room logic via simple callables without needing a class.

init -1 python:
    try:
        SIMPLE_ROOMS
    except NameError:
        SIMPLE_ROOMS = {}

    def _image_dims(path):
        """Return (w,h) for a loadable image, else (None, None)."""
        try:
            if path and renpy.loadable(path):
                w, h = renpy.image_size(path)
                return int(w), int(h)
        except Exception:
            pass
        return None, None

    def simple_object(
        obj_id,
        image,
        x,
        y,
        *,
        width=None,
        height=None,
        scale_percent=100,
        object_type="item",
        description=None,
        box_position="auto",
        interactions=None,
        transform=None,
        extra=None,
    ):
        """Create a normalized object dict with sensible defaults.

        - Auto-detects width/height from image when possible and applies scale_percent.
        - "interactions" can be a list of {label, action} dicts. If provided, it will
          be used by the interaction menu without extra logic wiring.
        - "extra" allows passing any additional custom keys (merged last).
        """
        ow, oh = _image_dims(image)
        w = int(width) if width is not None else (int(ow) if ow else 0)
        h = int(height) if height is not None else (int(oh) if oh else 0)

        # Apply scale to width/height when we have dimensions
        s = int(scale_percent or 100)
        if w and h and s != 100:
            w = int(round(w * s / 100.0))
            h = int(round(h * s / 100.0))

        data = {
            "x": int(x),
            "y": int(y),
            "scale_percent": s,
            "width": int(w or 0),
            "height": int(h or 0),
            "image": image,
            "object_type": object_type or "item",
            "box_position": box_position or "auto",
        }
        if description:
            data["description"] = description
        if interactions:
            # Normalize to list of {label, action}
            norm = []
            for it in interactions:
                if isinstance(it, dict):
                    lbl = str(it.get("label", "?"))
                    act = str(it.get("action", "leave"))
                    norm.append({"label": lbl, "action": act})
                elif isinstance(it, (list, tuple)) and len(it) >= 2:
                    norm.append({"label": str(it[0]), "action": str(it[1])})
            if norm:
                data["interactions"] = norm
        if transform is not None:
            data["transform"] = transform
        if isinstance(extra, dict):
            data.update(extra)
        return { str(obj_id): data }

    def character(obj_id, image, x, y, **kwargs):
        """Sugar for a character object."""
        kwargs.setdefault("object_type", "character")
        return simple_object(obj_id, image, x, y, **kwargs)

    def item(obj_id, image, x, y, **kwargs):
        """Sugar for an item object."""
        kwargs.setdefault("object_type", "item")
        return simple_object(obj_id, image, x, y, **kwargs)

    def door(obj_id, image, x, y, **kwargs):
        """Sugar for a door object."""
        kwargs.setdefault("object_type", "door")
        return simple_object(obj_id, image, x, y, **kwargs)

    def container(obj_id, image, x, y, **kwargs):
        """Sugar for a container object."""
        kwargs.setdefault("object_type", "container")
        return simple_object(obj_id, image, x, y, **kwargs)

    def simple_room(room_id, background, *object_dicts, music=None, ambient_channel=None, extra=None):
        """Define a room quickly and register it in a simple registry.

        Usage:
            simple_room(
                "roomX",
                "rooms/roomX/sprites/roomX.png",
                character(...)["detective"],
                item(...)["flyer"],
                music="rooms/roomX/audio/music.ogg",
            )
        """
        objs = {}
        for od in object_dicts:
            if isinstance(od, dict):
                objs.update(od)
        entry = {
            "background": background,
            "objects": objs,
        }
        if music:
            entry["music"] = music
        if ambient_channel:
            entry["ambient_channel"] = ambient_channel
        if isinstance(extra, dict):
            entry.update(extra)
        SIMPLE_ROOMS[str(room_id)] = entry
        return entry

    def simple_room_logic(room_id, on_enter=None, on_hover=None, on_interact=None):
        """Register lightweight per-room logic without writing a class.

        on_enter(room_id), on_hover(room_id, obj), on_interact(room_id, obj, action)
        return True from on_interact to consume the action (skip defaults).
        """
        try:
            class _Handler(object):
                def on_room_enter(self, rid):
                    if callable(on_enter):
                        return on_enter(rid)
                def on_object_hover(self, rid, obj):
                    if callable(on_hover):
                        return on_hover(rid, obj)
                def on_object_interact(self, rid, obj, action):
                    if callable(on_interact):
                        return bool(on_interact(rid, obj, action))
                    return False
            register_room_logic(str(room_id), _Handler())
            return True
        except Exception:
            return False

    def go_to_room(room_id):
        """Convenience: load a room and invoke enter hook."""
        load_room(str(room_id))
        on_room_enter(str(room_id))
        try:
            renpy.restart_interaction()
        except Exception:
            pass
        return True

    # ------------------------- Description helpers -------------------------
    def set_description(obj_name, text, room_id=None):
        """Set the description text for an object in the current or given room."""
        rid = room_id or getattr(store, 'current_room_id', None)
        if not rid:
            return False
        obj = (getattr(store, 'room_objects', {}) or {}).get(obj_name)
        if obj is not None:
            obj["description"] = str(text)
        try:
            if rid in ROOM_DEFINITIONS and obj_name in ROOM_DEFINITIONS[rid].get("objects", {}):
                ROOM_DEFINITIONS[rid]["objects"][obj_name]["description"] = str(text)
        except Exception:
            pass
        try:
            renpy.restart_interaction()
        except Exception:
            pass
        return True

    def set_box_position(obj_name, position, room_id=None):
        """Set the description box position (e.g., 'auto', 'right+40')."""
        rid = room_id or getattr(store, 'current_room_id', None)
        if not rid:
            return False
        obj = (getattr(store, 'room_objects', {}) or {}).get(obj_name)
        if obj is not None:
            obj["box_position"] = str(position)
        try:
            if rid in ROOM_DEFINITIONS and obj_name in ROOM_DEFINITIONS[rid].get("objects", {}):
                ROOM_DEFINITIONS[rid]["objects"][obj_name]["box_position"] = str(position)
        except Exception:
            pass
        try:
            renpy.restart_interaction()
        except Exception:
            pass
        return True

    def describe(obj_name, text=None, position=None, room_id=None):
        """Convenience: update description text and/or box position."""
        ok = False
        if text is not None:
            ok = set_description(obj_name, text, room_id=room_id) or ok
        if position is not None:
            ok = set_box_position(obj_name, position, room_id=room_id) or ok
        return ok
    
    # ========================= YAML Room API Wrappers =========================
    # Simple wrappers for all YAML room configuration functions
    
    def register_yaml_room(room_id):
        """Register a room from YAML configuration."""
        return register_room_from_yaml(room_id)
    
    def yaml_room(room_id):
        """Alias for register_yaml_room."""
        return register_room_from_yaml(room_id)
    
    def setup_yaml_room(room_id):
        """Complete room setup from YAML."""
        return setup_room_from_yaml(room_id)
    
    def load_yaml_config(room_id):
        """Load YAML configuration for a room."""
        return load_room_config_yaml(room_id)
    
    # Room info helpers
    def room_background(room_id):
        """Get background image path from YAML."""
        return get_room_background_from_config(room_id)
    
    def room_music(room_id):
        """Get music file path from YAML."""
        return get_room_music_from_config(room_id)
    
    def play_room_music(room_id, channel="music", fadein=2.0):
        """Play room music from YAML config."""
        return play_room_music_from_config(room_id, channel, fadein)
    
    # Object configuration helpers
    def room_objects(room_id):
        """Get all objects from YAML config."""
        return get_room_objects_from_config(room_id)
    
    def object_config(room_id, obj_name):
        """Get specific object config from YAML."""
        return get_room_object_config(room_id, obj_name)
    
    def object_interactions(room_id, obj_name):
        """Get object interactions from YAML."""
        return get_room_object_interactions(room_id, obj_name)
    
    # Lighting configuration
    def room_lighting(room_id):
        """Get lighting config from YAML."""
        return get_room_lighting_config(room_id)
    
    def apply_room_lighting(room_id):
        """Apply lighting from YAML config."""
        return apply_room_lighting_from_config(room_id)
    
    # Audio configuration
    def room_audio(room_id):
        """Get all audio config from YAML."""
        return get_room_audio_config(room_id)
    
    def room_sfx_path(room_id, sfx_name):
        """Get SFX file path from YAML."""
        return get_room_sfx_path(room_id, sfx_name)
    
    def play_room_sfx(room_id, sfx_name, channel="sound"):
        """Play SFX from YAML config."""
        return play_room_sfx_from_config(room_id, sfx_name, channel)
    
    # Conversion helpers
    def yaml_to_room_def(room_id):
        """Convert YAML to ROOM_DEFINITIONS format."""
        return convert_yaml_to_room_definition(room_id)

init 3 python:
    # Merge SIMPLE_ROOMS into ROOM_DEFINITIONS after per-room files load.
    try:
        if SIMPLE_ROOMS:
            ROOM_DEFINITIONS.update(SIMPLE_ROOMS)
            print(f"[SimpleAPI] Registered {len(SIMPLE_ROOMS)} simple room(s)")
    except Exception as e:
        try:
            print(f"[SimpleAPI] Error merging rooms: {e}")
        except Exception:
            pass
