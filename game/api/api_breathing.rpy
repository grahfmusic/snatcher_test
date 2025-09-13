# Breathing Settings API
# Public helpers to apply, select, and save per-room/object breathing settings

init python:
    # Central registry populated by room scripts (generated files)
    # Format: ROOM_BREATHING_SETTINGS[room_id][object_name] = { param: value }
    try:
        ROOM_BREATHING_SETTINGS
    except NameError:
        ROOM_BREATHING_SETTINGS = {}

    def _breath_param_names():
        return [
            'chest_breathe_amp',
            'chest_breathe_center_u', 'chest_breathe_center_v',
            'chest_breathe_half_u', 'chest_breathe_half_v',
            'shoulder_left_center_u', 'shoulder_left_center_v',
            'shoulder_left_half_u', 'shoulder_left_half_v',
            'shoulder_left_out_amp', 'shoulder_left_up_amp',
            'shoulder_right_center_u', 'shoulder_right_center_v',
            'shoulder_right_half_u', 'shoulder_right_half_v',
            'shoulder_right_out_amp', 'shoulder_right_up_amp',
            'head_center_u', 'head_center_v',
            'head_half_u', 'head_half_v',
            'head_up_amp',
            # toggles
            'breath_enabled',
            'breath_use_chest',
            'breath_use_shoulder_left',
            'breath_use_shoulder_right',
            'breath_use_head',
        ]

    def get_current_breathing_values():
        vals = {}
        toggles = {
            'breath_enabled', 'breath_use_chest', 'breath_use_shoulder_left', 'breath_use_shoulder_right', 'breath_use_head'
        }
        for k in _breath_param_names():
            try:
                v = getattr(store, k)
                if k in toggles:
                    vals[k] = bool(v)
                else:
                    vals[k] = float(v)
            except Exception:
                # Leave missing keys out to avoid serializing bogus defaults
                pass
        return vals

    def apply_breathing_values(values):
        """Apply a dict of breathing values to the current store and refresh UI."""
        for k, v in (values or {}).items():
            try:
                if isinstance(v, bool) or k.startswith('breath_'):
                    setattr(store, k, bool(v))
                else:
                    setattr(store, k, float(v))
            except Exception:
                setattr(store, k, v)
        try:
            renpy.restart_interaction()
        except Exception:
            pass

    def _normalize_object_entry(entry):
        """Return a normalized tuple (profiles_dict, active_name).

        - Supports legacy flat dicts by mapping to {'default': values}.
        - For structured entries, expects {'profiles': {...}, 'active_profile': name}.
        """
        if not isinstance(entry, dict):
            return ({}, None)
        if 'profiles' in entry:
            profs = entry.get('profiles') or {}
            active = entry.get('active_profile') or (list(profs.keys())[0] if profs else None)
            return (profs, active)
        # Legacy flat
        return ({'default': entry.copy()}, 'default')

    def _set_object_entry(room_id, obj_name, profiles, active):
        ROOM_BREATHING_SETTINGS.setdefault(room_id, {})[obj_name] = {
            'profiles': profiles,
            'active_profile': active,
        }

    def get_tuner_target_object():
        """Return the currently selected tuner target object, or pick a default."""
        tgt = getattr(store, 'tuner_target_object', None)
        objs = getattr(store, 'room_objects', {}) or {}
        if tgt in objs:
            return tgt
        # Prefer detective if present
        if 'detective' in objs:
            store.tuner_target_object = 'detective'
            return 'detective'
        # Fallback to first object
        if objs:
            first = list(objs.keys())[0]
            store.tuner_target_object = first
            return first
        return None

    # Short alias
    def breath_target():
        return get_tuner_target_object()

    def breathing_select_next_object():
        """Cycle tuner target through visible room objects (TAB in the tuner)."""
        objs = list((getattr(store, 'room_objects', {}) or {}).keys())
        if not objs:
            return
        cur = get_tuner_target_object()
        try:
            idx = objs.index(cur) if cur in objs else -1
        except Exception:
            idx = -1
        nxt = objs[(idx + 1) % len(objs)]
        store.tuner_target_object = nxt
        # Load this object's saved settings so toggles reflect per-object state
        try:
            rid = getattr(store, 'current_room_id', None) or 'room1'
            apply_room_breathing_settings(rid, nxt)
        except Exception:
            pass
        try:
            renpy.notify(f"Tuner target: {nxt}")
        except Exception:
            pass
        try:
            renpy.restart_interaction()
        except Exception:
            pass

    def breath_next():
        return breathing_select_next_object()

    def get_room_breathing(room_id):
        return (ROOM_BREATHING_SETTINGS.get(room_id) or {}).copy()

    def breath_room(room_id):
        return get_room_breathing(room_id)

    def apply_room_breathing_settings(room_id, obj_name=None):
        """Apply room breathing settings to the active store for a given object.

        - Picks obj_name or a sensible default (detective, else first key).
        - Falls back silently if the room has no settings.
        """
        room_map = ROOM_BREATHING_SETTINGS.get(room_id) or {}
        if not room_map:
            return False
        target = obj_name or get_tuner_target_object()
        if target in room_map:
            entry = room_map[target]
            profiles, active = _normalize_object_entry(entry)
            values = None
            if profiles:
                if active and active in profiles:
                    values = profiles[active]
                else:
                    # Fallback to first profile
                    values = profiles[list(profiles.keys())[0]]
            else:
                values = entry if isinstance(entry, dict) else {}
            apply_breathing_values(values)
            try:
                store.breathing_active_profile = active
            except Exception:
                pass
            return True
        # Prefer detective if present
        if 'detective' in room_map:
            store.tuner_target_object = 'detective'
            entry = room_map['detective']
            profiles, active = _normalize_object_entry(entry)
            values = profiles.get(active) if profiles else (entry if isinstance(entry, dict) else {})
            apply_breathing_values(values)
            try:
                store.breathing_active_profile = active
            except Exception:
                pass
            return True
        # Else first entry
        first_obj, first_entry = next(iter(room_map.items()))
        store.tuner_target_object = first_obj
        profiles, active = _normalize_object_entry(first_entry)
        values = profiles.get(active) if profiles else (first_entry if isinstance(first_entry, dict) else {})
        apply_breathing_values(values)
        try:
            store.breathing_active_profile = active
        except Exception:
            pass
        return True

    def breath_apply(room_id, obj_name=None):
        return apply_room_breathing_settings(room_id, obj_name)

    def breathing_save_current_to_room(room_id=None, obj_name=None):
        """Save current breathing values for this room/object and write file.

        - If object uses profiles, updates the active profile in-place.
        - If legacy flat entry, overwrites flat values (legacy behavior).
        """
        try:
            import os, json
            rid = room_id or getattr(store, 'current_room_id', None) or 'room1'
            obj = obj_name or get_tuner_target_object() or 'detective'
            # Merge/update with any existing in-memory settings first
            existing = ROOM_BREATHING_SETTINGS.get(rid, {}).get(obj)
            cur = get_current_breathing_values()
            if isinstance(existing, dict) and 'profiles' in existing:
                profs, active = _normalize_object_entry(existing)
                active = active or 'default'
                profs[active] = cur
                _set_object_entry(rid, obj, profs, active)
            else:
                ROOM_BREATHING_SETTINGS.setdefault(rid, {})[obj] = cur

            gamedir = renpy.config.gamedir
            path = os.path.join(gamedir, 'rooms', rid, 'scripts', f'{rid}_breathing_settings.rpy')

            # Write a clean, human-friendly rpy with a single dict entry for this room
            room_dict = ROOM_BREATHING_SETTINGS.get(rid, {})
            def fmt(v):
                if isinstance(v, bool):
                    return "True" if v else "False"
                if isinstance(v, float) or isinstance(v, int):
                    return f"{float(v):.12g}"
                return repr(v)
            with open(path, 'w', encoding='utf-8') as f:
                f.write("# Auto-generated breathing settings (per-object)\n")
                f.write("init 5 python:\n")
                f.write("    try:\n        ROOM_BREATHING_SETTINGS\n    except NameError:\n        ROOM_BREATHING_SETTINGS = {}\n")
                f.write(f"    ROOM_BREATHING_SETTINGS['{rid}'] = {{\n")
                for o, vals in room_dict.items():
                    # Support flat legacy dicts or structured profile dicts
                    if isinstance(vals, dict) and 'profiles' in vals:
                        f.write(f"        '{o}': {{\n")
                        # active profile name
                        ap = vals.get('active_profile') or 'default'
                        f.write(f"            'active_profile': {repr(ap)},\n")
                        f.write(f"            'profiles': {{\n")
                        for pname, pvals in (vals.get('profiles') or {}).items():
                            f.write(f"                {repr(pname)}: {{\n")
                            for k, v in pvals.items():
                                f.write(f"                    '{k}': {fmt(v)},\n")
                            f.write("                },\n")
                        f.write("            },\n")
                        f.write("        },\n")
                    else:
                        f.write(f"        '{o}': {{\n")
                        for k, v in (vals or {}).items():
                            f.write(f"            '{k}': {fmt(v)},\n")
                        f.write("        },\n")
                f.write("    }\n")
            try:
                renpy.notify(f"Saved breathing settings → {path}")
            except Exception:
                pass
            return True
        except Exception as e:
            print(f"Error saving breathing settings: {e}")
            try:
                renpy.notify("Error saving breathing settings (see console)")
            except Exception:
                pass
            return False

    def breath_save(room_id=None, obj_name=None):
        return breathing_save_current_to_room(room_id, obj_name)

    # Named profile management
    def breathing_list_profiles(room_id=None, obj_name=None):
        rid = room_id or getattr(store, 'current_room_id', None) or 'room1'
        obj = obj_name or get_tuner_target_object() or 'detective'
        entry = (ROOM_BREATHING_SETTINGS.get(rid) or {}).get(obj)
        profiles, _active = _normalize_object_entry(entry or {})
        return list(profiles.keys())

    def breath_profiles(room_id=None, obj_name=None):
        return breathing_list_profiles(room_id, obj_name)

    def breathing_get_active_profile(room_id=None, obj_name=None):
        rid = room_id or getattr(store, 'current_room_id', None) or 'room1'
        obj = obj_name or get_tuner_target_object() or 'detective'
        entry = (ROOM_BREATHING_SETTINGS.get(rid) or {}).get(obj)
        _profiles, active = _normalize_object_entry(entry or {})
        return active

    def breath_profile(room_id=None, obj_name=None):
        return breathing_get_active_profile(room_id, obj_name)

    def breathing_apply_profile(profile_name, room_id=None, obj_name=None):
        rid = room_id or getattr(store, 'current_room_id', None) or 'room1'
        obj = obj_name or get_tuner_target_object() or 'detective'
        entry = (ROOM_BREATHING_SETTINGS.get(rid) or {}).get(obj)
        profiles, active = _normalize_object_entry(entry or {})
        if not profiles:
            try:
                renpy.notify("No profiles available for this object")
            except Exception:
                pass
            return False
        name = profile_name or active
        if not name or name not in profiles:
            try:
                renpy.notify("Profile not found")
            except Exception:
                pass
            return False
        apply_breathing_values(profiles[name])
        try:
            store.breathing_active_profile = name
        except Exception:
            pass
        # Update active profile and persist
        _set_object_entry(rid, obj, profiles, name)
        ok = breathing_save_current_to_room(rid, obj)
        try:
            renpy.notify(f"Applied profile: {name}")
        except Exception:
            pass
        return ok

    def breath_apply_profile(profile_name, room_id=None, obj_name=None):
        return breathing_apply_profile(profile_name, room_id, obj_name)

    def breathing_save_profile(profile_name, room_id=None, obj_name=None):
        """Capture current values as a named profile and save to file."""
        if not profile_name:
            try:
                renpy.notify("Enter a profile name first")
            except Exception:
                pass
            return False
        rid = room_id or getattr(store, 'current_room_id', None) or 'room1'
        obj = obj_name or get_tuner_target_object() or 'detective'
        entry = (ROOM_BREATHING_SETTINGS.get(rid) or {}).get(obj)
        profiles, _active = _normalize_object_entry(entry or {})
        profiles[profile_name] = get_current_breathing_values()
        _set_object_entry(rid, obj, profiles, profile_name)
        try:
            store.breathing_active_profile = profile_name
        except Exception:
            pass
        ok = breathing_save_current_to_room(rid, obj)
        try:
            renpy.notify(f"Saved profile: {profile_name}")
        except Exception:
            pass
        return ok

    def breath_save_profile(profile_name, room_id=None, obj_name=None):
        return breathing_save_profile(profile_name, room_id, obj_name)

    def breathing_delete_profile(profile_name, room_id=None, obj_name=None):
        """Delete a named profile. Falls back to another profile if deleting active."""
        rid = room_id or getattr(store, 'current_room_id', None) or 'room1'
        obj = obj_name or get_tuner_target_object() or 'detective'
        entry = (ROOM_BREATHING_SETTINGS.get(rid) or {}).get(obj)
        profiles, active = _normalize_object_entry(entry or {})
        if not profiles or not profile_name or profile_name not in profiles:
            try:
                renpy.notify("Profile not found")
            except Exception:
                pass
            return False
        del profiles[profile_name]
        # Pick new active
        new_active = active
        if active == profile_name:
            new_active = (list(profiles.keys())[0] if profiles else None)
        _set_object_entry(rid, obj, profiles, new_active)
        try:
            store.breathing_active_profile = new_active
        except Exception:
            pass
        ok = breathing_save_current_to_room(rid, obj)
        try:
            renpy.notify(f"Deleted profile: {profile_name}")
        except Exception:
            pass
        return ok

    def breathing_cycle_profile(direction=1, room_id=None, obj_name=None):
        """Cycle to next/previous profile; direction=+1 or -1."""
        rid = room_id or getattr(store, 'current_room_id', None) or 'room1'
        obj = obj_name or get_tuner_target_object() or 'detective'
        names = breathing_list_profiles(rid, obj)
        if not names:
            try:
                renpy.notify("No profiles to cycle")
            except Exception:
                pass
            return False
        cur = breathing_get_active_profile(rid, obj)
        try:
            idx = names.index(cur) if cur in names else -1
        except Exception:
            idx = -1
        nxt = names[(idx + (1 if direction >= 0 else -1)) % len(names)]
        return breathing_apply_profile(nxt, rid, obj)

    # In-memory sync (no file write): keep per-object values updated while editing
    def breathing_sync_current_to_memory(room_id=None, obj_name=None):
        """Merge current store values into ROOM_BREATHING_SETTINGS for target object.

        - Does not write to disk; use breathing_save_current_to_room to persist.
        - Keeps profiles structure intact by updating the active profile in-place.
        """
        rid = room_id or getattr(store, 'current_room_id', None) or 'room1'
        obj = obj_name or get_tuner_target_object() or 'detective'
        existing = (ROOM_BREATHING_SETTINGS.get(rid) or {}).get(obj)
        cur = get_current_breathing_values()
        if isinstance(existing, dict) and 'profiles' in existing:
            profs, active = _normalize_object_entry(existing)
            active = active or 'default'
            profs[active] = cur
            _set_object_entry(rid, obj, profs, active)
        else:
            ROOM_BREATHING_SETTINGS.setdefault(rid, {})[obj] = cur
        return True

    def breath_delete_profile(profile_name, room_id=None, obj_name=None):
        return breathing_delete_profile(profile_name, room_id, obj_name)

    def breathing_get_effective_values(room_id=None, obj_name=None):
        """Return the effective per-object breathing values dict for rendering.

        - Prefers the object's active profile values if available.
        - Returns an empty dict if no settings were saved for the object (caller may fallback).
        - Ensures toggle keys are booleans when present.
        """
        rid = room_id or getattr(store, 'current_room_id', None) or 'room1'
        obj = obj_name or get_tuner_target_object() or 'detective'
        entry = (ROOM_BREATHING_SETTINGS.get(rid) or {}).get(obj)
        if not entry:
            return {}
        profiles, active = _normalize_object_entry(entry)
        vals = (profiles.get(active) if profiles else entry) or {}
        # Normalize toggles
        out = {}
        for k, v in vals.items():
            if k.startswith('breath_'):
                out[k] = bool(v)
            else:
                out[k] = v
        return out

    def breath_values(room_id=None, obj_name=None):
        return breathing_get_effective_values(room_id, obj_name)

    # Convenience wrappers for room logic (avoid duplicating patterns)
    def breathing_enable_for(obj_name=None, save=False, room_id=None):
        """Enable breathing for a specific object and optionally persist.

        - obj_name: object id (defaults to current tuner target)
        - save: when True, writes the change to the room settings file
        - room_id: explicit room id (defaults to current room)
        """
        rid = room_id or getattr(store, 'current_room_id', None) or 'room1'
        obj = obj_name or get_tuner_target_object() or 'detective'
        apply_room_breathing_settings(rid, obj)
        try:
            store.breath_enabled = True
        except Exception:
            store.breath_enabled = True
        breathing_sync_current_to_memory(rid, obj)
        if save:
            breathing_save_current_to_room(rid, obj)
        try:
            renpy.restart_interaction()
        except Exception:
            pass
        return True

    def breath_on(obj_name=None, save=False, room_id=None):
        return breathing_enable_for(obj_name, save, room_id)

    def breathing_disable_for(obj_name=None, save=False, room_id=None):
        """Disable breathing for a specific object and optionally persist."""
        rid = room_id or getattr(store, 'current_room_id', None) or 'room1'
        obj = obj_name or get_tuner_target_object() or 'detective'
        apply_room_breathing_settings(rid, obj)
        try:
            store.breath_enabled = False
        except Exception:
            store.breath_enabled = False
        breathing_sync_current_to_memory(rid, obj)
        if save:
            breathing_save_current_to_room(rid, obj)
        try:
            renpy.restart_interaction()
        except Exception:
            pass
        return True

    def breath_off(obj_name=None, save=False, room_id=None):
        return breathing_disable_for(obj_name, save, room_id)

    def breathing_set_param(key, value, obj_name=None, save=False, room_id=None):
        """Set a single breathing parameter for an object and optionally persist.

        Example keys: 'chest_breathe_amp', 'breath_use_chest', etc.
        """
        rid = room_id or getattr(store, 'current_room_id', None) or 'room1'
        obj = obj_name or get_tuner_target_object() or 'detective'
        apply_room_breathing_settings(rid, obj)
        try:
            setattr(store, key, value)
        except Exception:
            pass
        breathing_sync_current_to_memory(rid, obj)
        if save:
            breathing_save_current_to_room(rid, obj)
        try:
            renpy.restart_interaction()
        except Exception:
            pass
        return True

    def breath_set(key, value, obj_name=None, save=False, room_id=None):
        return breathing_set_param(key, value, obj_name, save, room_id)

    def breathing_disable_all(save=False, room_id=None):
        """Disable breathing for all objects in the current (or given) room."""
        rid = room_id or getattr(store, 'current_room_id', None) or 'room1'
        objs = list((getattr(store, 'room_objects', {}) or {}).keys())
        for o in objs:
            breathing_disable_for(o, save=save, room_id=rid)
        return True

    def breath_off_all(save=False, room_id=None):
        return breathing_disable_all(save, room_id)

    # Convenience helpers for screens: read name from store.breathing_profile_name
    def breathing_save_profile_from_input():
        name = (getattr(store, 'breathing_profile_name', '') or '').strip()
        return breathing_save_profile(name)

    def breathing_apply_profile_from_input():
        name = (getattr(store, 'breathing_profile_name', '') or '').strip()
        return breathing_apply_profile(name)

    def breathing_delete_profile_from_input():
        name = (getattr(store, 'breathing_profile_name', '') or '').strip()
        return breathing_delete_profile(name)

    # Aliases from input helpers
    def breath_save_from_input():
        return breathing_save_profile_from_input()
    def breath_apply_from_input():
        return breathing_apply_profile_from_input()
    def breath_delete_from_input():
        return breathing_delete_profile_from_input()
