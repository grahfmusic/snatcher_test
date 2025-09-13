# Room API
# Consolidated room management and object manipulation functions
#
# Overview
# - Manipulates object positions/scales; persists and resets room changes.
# - Toggles CRT settings and exposes navigation helpers.
#
# Contracts
# - move_object(name, dx, dy) / scale_object(name, delta|'reset')
# - save_room_changes(), reset_room_changes(), clear_persistent_overrides()
# - toggle_crt_effect(), set_crt_parameters(...)
# - get_object_list_for_navigation(), gamepad_navigate(dir), ...
#
# Notes
# - Functions operate on store.room_objects (current room) and definitions.

init python:
    def move_object(obj_name, dx, dy, room_id=None):
        """Move an object by dx, dy pixels in specified room (or current room)"""
        if room_id is None:
            room_id = store.current_room_id
        
        sw = getattr(config, 'screen_width', 1280)
        sh = getattr(config, 'screen_height', 720)
        if room_id == store.current_room_id and obj_name in store.room_objects:
            max_x = max(0, sw - store.room_objects[obj_name]["width"])
            max_y = max(0, sh - store.room_objects[obj_name]["height"])
            store.room_objects[obj_name]["x"] = max(0, min(max_x, store.room_objects[obj_name]["x"] + dx))
            store.room_objects[obj_name]["y"] = max(0, min(max_y, store.room_objects[obj_name]["y"] + dy))
        
        if room_id in ROOM_DEFINITIONS and obj_name in ROOM_DEFINITIONS[room_id]["objects"]:
            obj_ref = ROOM_DEFINITIONS[room_id]["objects"][obj_name]
            max_x = max(0, sw - obj_ref["width"])
            max_y = max(0, sh - obj_ref["height"])
            obj_ref["x"] = max(0, min(max_x, obj_ref["x"] + dx))
            obj_ref["y"] = max(0, min(max_y, obj_ref["y"] + dy))
        
        renpy.restart_interaction()

    # Short alias: move object
    def obj_move(name, dx, dy, room_id=None):
        return move_object(name, dx, dy, room_id)
    
    def scale_object(obj_name, scale_change, room_id=None):
        """Scale an object by percentage change or reset to 100% in specified room (or current room)"""
        if room_id is None:
            room_id = store.current_room_id
            
        target_objects = None
        if room_id == store.current_room_id and obj_name in store.room_objects:
            target_objects = store.room_objects
        elif room_id in ROOM_DEFINITIONS and obj_name in ROOM_DEFINITIONS[room_id]["objects"]:
            target_objects = ROOM_DEFINITIONS[room_id]["objects"]
        
        if target_objects and obj_name in target_objects:
            if scale_change == "reset":
                new_scale = 100
            else:
                current_scale = target_objects[obj_name]["scale_percent"]
                new_scale = max(10, min(500, current_scale + scale_change))
            
            target_objects[obj_name]["scale_percent"] = new_scale
            
            # Ensure we have the original size for this object (cache lazily)
            if obj_name not in ORIGINAL_SIZES:
                try:
                    img_path = target_objects[obj_name].get("image")
                    if img_path and renpy.loadable(img_path):
                        w, h = renpy.image_size(img_path)
                        ORIGINAL_SIZES[obj_name] = {"width": int(w), "height": int(h)}
                except Exception:
                    pass
            if obj_name in ORIGINAL_SIZES:
                orig = ORIGINAL_SIZES[obj_name]
                new_width = int(orig["width"] * new_scale / 100)
                new_height = int(orig["height"] * new_scale / 100)
                
                target_objects[obj_name]["width"] = new_width
                target_objects[obj_name]["height"] = new_height
                
                sw = getattr(config, 'screen_width', 1280)
                sh = getattr(config, 'screen_height', 720)
                max_x = max(0, sw - new_width)
                max_y = max(0, sh - new_height)
                target_objects[obj_name]["x"] = max(0, min(max_x, target_objects[obj_name]["x"]))
                target_objects[obj_name]["y"] = max(0, min(max_y, target_objects[obj_name]["y"]))
            
            if room_id == store.current_room_id:
                if room_id in ROOM_DEFINITIONS and obj_name in ROOM_DEFINITIONS[room_id]["objects"]:
                    ROOM_DEFINITIONS[room_id]["objects"][obj_name].update(target_objects[obj_name])
            elif obj_name in store.room_objects:
                store.room_objects[obj_name].update(target_objects[obj_name])
            
            renpy.restart_interaction()

    # Short alias: scale object (delta or 'reset')
    def obj_scale(name, delta, room_id=None):
        return scale_object(name, delta, room_id)

    def calculate_box_position(obj, box_width, box_height, position_setting):
        """Calculate the position of a description box relative to an object"""
        if "+" in position_setting:
            direction, distance_str = position_setting.split("+")
            try:
                margin = int(distance_str)
            except ValueError:
                margin = 50
        else:
            direction = position_setting
            margin = 50
        
        if direction == "top":
            box_x = obj["x"] + obj["width"] // 2 - box_width // 2
            box_y = obj["y"] - box_height - margin
            box_position = "top"
        elif direction == "bottom":
            box_x = obj["x"] + obj["width"] // 2 - box_width // 2
            box_y = obj["y"] + obj["height"] + margin
            box_position = "bottom"
        elif direction == "left":
            box_x = obj["x"] - box_width - margin
            box_y = obj["y"] + (obj["height"] - box_height) // 2
            box_position = "left"
        elif direction == "right":
            box_x = obj["x"] + obj["width"] + margin
            box_y = obj["y"] + (obj["height"] - box_height) // 2
            box_position = "right"
        else:
            positions = [
                (obj["x"] + obj["width"] // 2 - box_width // 2, obj["y"] - box_height - 50, "top"),
                (obj["x"] + obj["width"] // 2 - box_width // 2, obj["y"] + obj["height"] + 50, "bottom"),
                (obj["x"] + obj["width"] + 50, obj["y"] + (obj["height"] - box_height) // 2, "right"),
                (obj["x"] - box_width - 50, obj["y"] + (obj["height"] - box_height) // 2, "left"),
            ]
            box_x, box_y, box_position = positions[0]
            for pos_x, pos_y, pos_name in positions:
                if (pos_x >= 30 and pos_x + box_width <= 1250 and
                    pos_y >= 30 and pos_y + box_height <= 590):
                    box_x, box_y, box_position = pos_x, pos_y, pos_name
                    break
        
        box_x = max(30, min(box_x, 1250 - box_width))
        box_y = max(30, min(box_y, 590 - box_height))
        return box_x, box_y, box_position
    
    def get_room_list():
        return list(ROOM_DEFINITIONS.keys())

    # Alias
    def room_list():
        return get_room_list()
    
    def get_room_objects(room_id):
        if room_id in ROOM_DEFINITIONS:
            return ROOM_DEFINITIONS[room_id]["objects"]
        return {}

    # Alias
    def room_objs(room_id):
        return get_room_objects(room_id)
    
    def add_room_object(room_id, obj_name, obj_data):
        if room_id in ROOM_DEFINITIONS:
            # Ensure object has z-order and lighting properties
            obj_data = ensure_object_z_properties(obj_data, obj_name)
            ROOM_DEFINITIONS[room_id]["objects"][obj_name] = obj_data
            if room_id == store.current_room_id:
                store.room_objects[obj_name] = obj_data
            return True
        return False

    # Alias
    def room_obj_add(room_id, name, data):
        return add_room_object(room_id, name, data)
    
    def remove_room_object(room_id, obj_name):
        if room_id in ROOM_DEFINITIONS and obj_name in ROOM_DEFINITIONS[room_id]["objects"]:
            del ROOM_DEFINITIONS[room_id]["objects"][obj_name]
            if room_id == store.current_room_id and obj_name in store.room_objects:
                del store.room_objects[obj_name]
            return True
        return False

    # Alias
    def room_obj_del(room_id, name):
        return remove_room_object(room_id, name)
    
    def create_new_room(room_id, background_image="", objects=None):
        if objects is None:
            objects = {}
        ROOM_DEFINITIONS[room_id] = {"background": background_image, "objects": objects}
        return True

    # Alias
    def room_new(room_id, background="", objects=None):
        return create_new_room(room_id, background, objects)
    
    def delete_room(room_id):
        if room_id in ROOM_DEFINITIONS and room_id != store.current_room_id:
            del ROOM_DEFINITIONS[room_id]
            return True
        return False
    
    # Z-order and lighting support functions
    def z_to_bucket(z):
        """Map a numeric z-order to a named layer bucket.

        Buckets:
          - 0..16   -> 'room_bg'  (background)
          - 17..33  -> 'room_mid' (midground)
          - 34..50+ -> 'room_fg'  (foreground)
        """
        try:
            zi = int(z)
        except Exception:
            zi = 12
        if zi <= 16:
            return "room_bg"
        if zi <= 33:
            return "room_mid"
        return "room_fg"
    def ensure_object_z_properties(obj_data, obj_name=None):
        """Ensure object has proper z-order and lighting properties with backward compatibility"""
        # Make a copy to avoid modifying the original
        obj = obj_data.copy() if obj_data else {}
        
        # Add z-order if missing (default to midground)
        if "z" not in obj:
            obj["z"] = 12  # Default to midground z-order
        
        # Clamp z-order to valid range (0-50)
        obj["z"] = max(0, min(50, int(obj["z"])))
        
        # Add light_affectable property if missing (default True for game objects)
        if "light_affectable" not in obj:
            obj["light_affectable"] = True
        
        # Add id/name if missing
        if "id" not in obj and obj_name:
            obj["id"] = obj_name
        
        # Derive layer from z-order
        obj["layer"] = z_to_bucket(obj["z"])
        
        return obj
    
    def place_room_object(obj, z_order=None):
        """Place object on appropriate layer based on z-order"""
        if z_order is not None:
            obj["z"] = max(0, min(50, int(z_order)))
        
        # Ensure object has all required properties
        obj = ensure_object_z_properties(obj)
        
        # Compute and assign layer
        bucket = z_to_bucket(obj["z"])
        obj["layer"] = bucket
        
        # Ensure light_affectable objects reside on lit layers
        if obj.get("light_affectable", True):
            # Objects that can be affected by lights should be on lit layers
            obj["lighting_enabled"] = True
        else:
            # UI/overlay objects opt out of lighting
            obj["lighting_enabled"] = False
        
        return bucket
    
    def obj_set_z_order(obj_name, z_order, room_id=None):
        """Set z-order for an object and update its layer"""
        if room_id is None:
            room_id = store.current_room_id
        
        z_order = max(0, min(50, int(z_order)))
        
        # Update in current room objects
        if room_id == store.current_room_id and obj_name in store.room_objects:
            store.room_objects[obj_name]["z"] = z_order
            store.room_objects[obj_name]["layer"] = z_to_bucket(z_order)
        
        # Update in room definitions
        if room_id in ROOM_DEFINITIONS and obj_name in ROOM_DEFINITIONS[room_id]["objects"]:
            ROOM_DEFINITIONS[room_id]["objects"][obj_name]["z"] = z_order
            ROOM_DEFINITIONS[room_id]["objects"][obj_name]["layer"] = z_to_bucket(z_order)
        
        # Restart interaction to reflect changes
        renpy.restart_interaction()
        return z_order
    
    def obj_get_z_order(obj_name, room_id=None):
        """Get z-order for an object"""
        if room_id is None:
            room_id = store.current_room_id
        
        # Check current room objects first
        if room_id == store.current_room_id and obj_name in store.room_objects:
            return store.room_objects[obj_name].get("z", 12)
        
        # Check room definitions
        if room_id in ROOM_DEFINITIONS and obj_name in ROOM_DEFINITIONS[room_id]["objects"]:
            return ROOM_DEFINITIONS[room_id]["objects"][obj_name].get("z", 12)
        
        return 12  # Default midground
    
    def obj_move_to_front(obj_name, room_id=None):
        """Move object to highest z-order (foreground)"""
        return obj_set_z_order(obj_name, 50, room_id)
    
    def obj_move_to_back(obj_name, room_id=None):
        """Move object to lowest z-order (background)"""
        return obj_set_z_order(obj_name, 0, room_id)
    
    def obj_move_up(obj_name, room_id=None):
        """Increase z-order by 1"""
        current_z = obj_get_z_order(obj_name, room_id)
        return obj_set_z_order(obj_name, min(50, current_z + 1), room_id)
    
    def obj_move_down(obj_name, room_id=None):
        """Decrease z-order by 1"""
        current_z = obj_get_z_order(obj_name, room_id)
        return obj_set_z_order(obj_name, max(0, current_z - 1), room_id)

    # Compatibility wrappers used by tests and scripts
    def get_object_z_order(obj_name):
        return obj_get_z_order(obj_name)

    def set_object_z_order(obj_name, z_order):
        return obj_set_z_order(obj_name, z_order) is not None
    
    def get_objects_by_z_order(room_id=None, ascending=True):
        """Get objects sorted by z-order"""
        if room_id is None:
            room_id = store.current_room_id
        
        objects = []
        
        # Get objects from current room if it matches
        if room_id == store.current_room_id and hasattr(store, 'room_objects'):
            for obj_name, obj_data in store.room_objects.items():
                obj_data = ensure_object_z_properties(obj_data, obj_name)
                objects.append((obj_name, obj_data))
        
        # Get objects from room definitions
        elif room_id in ROOM_DEFINITIONS:
            for obj_name, obj_data in ROOM_DEFINITIONS[room_id]["objects"].items():
                obj_data = ensure_object_z_properties(obj_data, obj_name)
                objects.append((obj_name, obj_data))
        
        # Sort by z-order
        objects.sort(key=lambda x: x[1]["z"], reverse=not ascending)
        
        return objects
    
    def get_z_order_range(room_id=None):
        """Get min/max z-order values in room"""
        objects = get_objects_by_z_order(room_id)
        if not objects:
            return (0, 24)
        
        z_orders = [obj_data["z"] for _, obj_data in objects]
        return (min(z_orders), max(z_orders))
    
    def migrate_room_objects_z_order(room_id=None):
        """Migrate existing room objects to include z-order properties"""
        if room_id is None:
            room_id = store.current_room_id
        
        updated_count = 0
        
        # Update current room objects
        if room_id == store.current_room_id and hasattr(store, 'room_objects'):
            for obj_name in store.room_objects:
                old_obj = store.room_objects[obj_name]
                new_obj = ensure_object_z_properties(old_obj, obj_name)
                if new_obj != old_obj:
                    store.room_objects[obj_name].update(new_obj)
                    updated_count += 1
        
        # Update room definitions
        if room_id in ROOM_DEFINITIONS:
            for obj_name in ROOM_DEFINITIONS[room_id]["objects"]:
                old_obj = ROOM_DEFINITIONS[room_id]["objects"][obj_name]
                new_obj = ensure_object_z_properties(old_obj, obj_name)
                if new_obj != old_obj:
                    ROOM_DEFINITIONS[room_id]["objects"][obj_name].update(new_obj)
                    updated_count += 1
        
        if updated_count > 0:
            print("Migrated {} objects in room {} to include z-order properties".format(updated_count, room_id))
        
        return updated_count

    # Alias
    def room_del(room_id):
        return delete_room(room_id)
    
    def duplicate_room(source_room_id, new_room_id):
        if source_room_id in ROOM_DEFINITIONS:
            import copy
            ROOM_DEFINITIONS[new_room_id] = copy.deepcopy(ROOM_DEFINITIONS[source_room_id])
            return True
        return False

    # Alias
    def room_copy(src, dst):
        return duplicate_room(src, dst)
    
    def save_room_changes():
        if store.current_room_id and store.current_room_id in ROOM_DEFINITIONS:
            log("=== SAVING ROOM CHANGES ===")
            print(f"Current room: {store.current_room_id}")
            if not hasattr(persistent, 'room_overrides') or persistent.room_overrides is None:
                persistent.room_overrides = {}
            if store.current_room_id not in persistent.room_overrides:
                persistent.room_overrides[store.current_room_id] = {}
            
            # Save object changes including z-order and lighting properties
            for obj_name, obj_data in store.room_objects.items():
                if obj_name in ROOM_DEFINITIONS[store.current_room_id]["objects"]:
                    # Ensure object has z-order properties
                    obj_data = ensure_object_z_properties(obj_data, obj_name)
                    
                    print(f"Saving {obj_name}: x={obj_data['x']}, y={obj_data['y']}, scale={obj_data['scale_percent']}%, z={obj_data.get('z', 20)}")
                    orig_obj = ROOM_DEFINITIONS[store.current_room_id]["objects"][obj_name]
                    orig_obj["x"] = obj_data["x"]
                    orig_obj["y"] = obj_data["y"]
                    orig_obj["scale_percent"] = obj_data["scale_percent"]
                    orig_obj["width"] = obj_data["width"]
                    orig_obj["height"] = obj_data["height"]
                    
                    # Save z-order and lighting properties
                    orig_obj["z"] = obj_data.get("z", 12)
                    orig_obj["light_affectable"] = obj_data.get("light_affectable", True)
                    orig_obj["layer"] = obj_data.get("layer", z_to_bucket(obj_data.get("z", 12)))
                    if "id" in obj_data:
                        orig_obj["id"] = obj_data["id"]
            
            # Save lighting configuration if available
            if hasattr(store, 'lights_state') and store.lights_state.get("active"):
                if "lighting" not in persistent.room_overrides[store.current_room_id]:
                    persistent.room_overrides[store.current_room_id]["lighting"] = {}
                
                # Save active lights as dictionaries
                lights_data = []
                for light in store.lights_state["active"]:
                    if hasattr(light, 'to_dict'):
                        lights_data.append(light.to_dict())
                    elif isinstance(light, dict):
                        lights_data.append(light)
                
                persistent.room_overrides[store.current_room_id]["lighting"]["lights"] = lights_data
                persistent.room_overrides[store.current_room_id]["lighting"]["quality"] = store.lights_state.get("quality", "high")
                print(f"Saved {len(lights_data)} lights for room {store.current_room_id}")
            
            log("=== SAVE COMPLETE ===")
            renpy.notify("Room changes saved to memory & persistent storage!")
            return True
        else:
            print(f"ERROR: Cannot save - room_id={store.current_room_id}, exists={store.current_room_id in ROOM_DEFINITIONS}")
            renpy.notify("Error: Cannot save room changes!")
        return False

    # Alias
    def room_save():
        return save_room_changes()
    
    def reset_room_changes():
        if store.current_room_id:
            if (hasattr(persistent, 'room_overrides') and 
                persistent.room_overrides and 
                store.current_room_id in persistent.room_overrides):
                del persistent.room_overrides[store.current_room_id]
                print(f"Cleared persistent overrides for room: {store.current_room_id}")
            load_room(store.current_room_id)
            renpy.notify("Room reset to original positions!")
            renpy.restart_interaction()
            return True
        return False

    # Alias
    def room_reset():
        return reset_room_changes()
    
    def clear_persistent_overrides():
        if store.current_room_id:
            if (hasattr(persistent, 'room_overrides') and 
                persistent.room_overrides and 
                store.current_room_id in persistent.room_overrides):
                del persistent.room_overrides[store.current_room_id]
                print(f"Cleared persistent overrides for room: {store.current_room_id}")
                renpy.notify("Persistent overrides cleared for current room!")
                return True
            else:
                renpy.notify("No persistent overrides found for current room.")
                return False
        renpy.notify("Error: No current room ID found.")
        return False

    # Alias
    def room_clear_persist():
        return clear_persistent_overrides()
    
    def update_room_config_file():
        try:
            import os
            import re
            # Prefer per-room config: game/rooms/<room>/scripts/<room>_config.rpy
            room_id = store.current_room_id
            per_room_path = os.path.join(renpy.config.gamedir, "rooms", room_id, "scripts", f"{room_id}_config.rpy")
            core_path = os.path.join(renpy.config.gamedir, "core", "rooms", "core_rooms_config.rpy")
            config_file_path = per_room_path if os.path.exists(per_room_path) else core_path
            if not os.path.exists(config_file_path):
                renpy.notify("Error: no room config file found to update.")
                return False
            with open(config_file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            print(f"=== UPDATING {config_file_path} ===")
            for obj_name, obj_data in store.room_objects.items():
                if obj_name in ROOM_DEFINITIONS[store.current_room_id]["objects"]:
                    print(f"Updating {obj_name}: x={obj_data['x']}, y={obj_data['y']}, scale={obj_data['scale_percent']}%")
                    # Try merge_configs pattern first
                    obj_pattern = rf'("{obj_name}"\s*:\s*merge_configs\s*\(\s*\{{.*?)"x"\s*:\s*\d+\s*,\s*"y"\s*:\s*\d+\s*,(.*?"scale_percent"\s*:\s*)\d+(\s*,)'
                    replacement = rf'\g<1>"x": {obj_data["x"]}, "y": {obj_data["y"]},\g<2>{obj_data["scale_percent"]}\g<3>'
                    new_content = re.sub(obj_pattern, replacement, content, flags=re.DOTALL)
                    if new_content != content:
                        content = new_content
                        print(f"✓ Updated {obj_name} in file")
                    else:
                        # Fallback: plain dict style
                        basic_pattern = rf'("{obj_name}"\s*:\s*\{{.*?)"x"\s*:\s*\d+\s*,\s*"y"\s*:\s*\d+\s*,(.*?"scale_percent"\s*:\s*)\d+(\s*,)'
                        basic_replacement = rf'\g<1>"x": {obj_data["x"]}, "y": {obj_data["y"]},\g<2>{obj_data["scale_percent"]}\g<3>'
                        new_content = re.sub(basic_pattern, basic_replacement, content, flags=re.DOTALL)
                        if new_content != content:
                            content = new_content
                            print(f"✓ Updated {obj_name} in file (basic pattern)")
                        else:
                            print(f"⚠ Could not find pattern for {obj_name}")
            with open(config_file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            log("=== FILE UPDATE COMPLETE ===")
            renpy.notify("Room config updated successfully!")
            return True
        except Exception as e:
            print(f"Error updating room config: {str(e)}")
            renpy.notify(f"Error updating file: {str(e)}")
            return False

    # Alias
    def room_update_file():
        return update_room_config_file()
    
    def load_room(room_id):
        if room_id in ROOM_DEFINITIONS:
            store.current_room_id = room_id
            try:
                log_main_event("ROOM", f"enter {room_id}")
            except Exception:
                pass
            import copy
            store.room_objects = copy.deepcopy(ROOM_DEFINITIONS[room_id]["objects"])
            
            # Ensure all objects have z-order properties
            for obj_name in store.room_objects:
                store.room_objects[obj_name] = ensure_object_z_properties(store.room_objects[obj_name], obj_name)
            
            # Preserve any per-object transform objects from definitions (deepcopy may drop/clone improperly)
            try:
                for _oname, _odata in ROOM_DEFINITIONS[room_id]["objects"].items():
                    if "transform" in _odata:
                        store.room_objects.setdefault(_oname, {})["transform"] = _odata["transform"]
            except Exception:
                pass
            store.room_background = ROOM_DEFINITIONS[room_id]["background"]
            
            # Apply persistent overrides including lighting
            if (hasattr(persistent, 'room_overrides') and 
                persistent.room_overrides and 
                room_id in persistent.room_overrides):
                print(f"Applying persistent overrides for room: {room_id}")
                
                # Apply object overrides
                for obj_name, overrides in persistent.room_overrides[room_id].items():
                    if obj_name == "lighting":
                        continue  # Handle lighting separately
                    if obj_name in store.room_objects:
                        print(f"Overriding {obj_name}: x={overrides.get('x')}, y={overrides.get('y')}, z={overrides.get('z')}")
                        store.room_objects[obj_name].update(overrides)
                        ROOM_DEFINITIONS[room_id]["objects"][obj_name].update(overrides)
                
                # Apply lighting overrides
                if "lighting" in persistent.room_overrides[room_id]:
                    lighting_data = persistent.room_overrides[room_id]["lighting"]
                    room_apply_lighting_from_data(lighting_data)
            play_room_audio(room_id)
            if store.room_objects:
                store.selected_object = list(store.room_objects.keys())[0]
            else:
                store.selected_object = None
    
    # Helper: Apply lighting data from persistence
    def room_apply_lighting_from_data(lighting_data):
        """Apply lighting configuration from saved data"""
        try:
            if not lighting_data:
                return False
            
            # Import lighting functions if available
            if not hasattr(store, 'clear_all_lights'):
                print("Warning: Lighting system not available, skipping lighting load")
                return False
            
            # Clear existing lights
            store.clear_all_lights()
            
            # Set quality level
            quality = lighting_data.get("quality", "high")
            if hasattr(store, 'set_lighting_quality'):
                store.set_lighting_quality(quality)
            
            # Load and apply lights
            lights_list = lighting_data.get("lights", [])
            if lights_list:
                print(f"Loading {len(lights_list)} lights from persistence")
                
                for light_dict in lights_list:
                    # Convert dict back to Light object
                    if hasattr(store, 'Light'):
                        light = store.Light.from_dict(light_dict)
                        store.add_light(light)
                    else:
                        # Fallback: add as dict if Light class not available
                        if hasattr(store, 'add_light_from_dict'):
                            store.add_light_from_dict(light_dict)
                
                # Apply lighting to current layers
                if hasattr(store, 'apply_lighting_to_room'):
                    store.apply_lighting_to_room()
                
                print(f"Successfully loaded {len(lights_list)} lights for room")
                return True
            
        except Exception as e:
            print(f"Error loading lighting data: {e}")
            import traceback
            traceback.print_exc()
        
        return False
    
    # YAML Configuration Support
    def export_room_to_yaml(room_id, output_path=None):
        """Export room configuration to YAML file with lighting data"""
        try:
            if room_id not in ROOM_DEFINITIONS:
                print(f"Error: Room '{room_id}' not found")
                return False
            
            # Determine output path
            if not output_path:
                import os
                rooms_dir = os.path.join(renpy.config.gamedir, "rooms", room_id, "config")
                os.makedirs(rooms_dir, exist_ok=True)
                output_path = os.path.join(rooms_dir, f"{room_id}_config.yaml")
            
            # Build room configuration data
            room_data = ROOM_DEFINITIONS[room_id].copy()
            
            # Ensure all objects have z-order properties
            for obj_name, obj_data in room_data.get("objects", {}).items():
                ensure_object_z_properties(obj_data, obj_name)
            
            # Add persistent overrides if available
            if (hasattr(persistent, 'room_overrides') and 
                persistent.room_overrides and 
                room_id in persistent.room_overrides):
                
                overrides = persistent.room_overrides[room_id]
                
                # Apply object overrides
                for obj_name, override_data in overrides.items():
                    if obj_name == "lighting":
                        continue
                    if obj_name in room_data.get("objects", {}):
                        room_data["objects"][obj_name].update(override_data)
                
                # Include lighting configuration
                if "lighting" in overrides:
                    room_data["lighting"] = overrides["lighting"]
            
            # Add current lighting state if available
            if (hasattr(store, 'lights_state') and 
                store.lights_state.get("active") and 
                store.current_room_id == room_id):
                
                lights_data = []
                for light in store.lights_state["active"]:
                    if hasattr(light, 'to_dict'):
                        lights_data.append(light.to_dict())
                    elif isinstance(light, dict):
                        lights_data.append(light)
                
                room_data["lighting"] = {
                    "lights": lights_data,
                    "quality": store.lights_state.get("quality", "high")
                }
            
            # Add metadata
            room_data["_metadata"] = {
                "exported_from": "snatchernauts_framework",
                "version": "1.0",
                "room_id": room_id,
                "export_timestamp": str(renpy.python.time.time()),
                "includes_lighting": "lighting" in room_data
            }
            
            # Save using YAML service
            import sys
            sys.path.append(renpy.config.gamedir + "/api")
            import api_io_yaml
            
            success = api_io_yaml.save_yaml_if_changed(output_path, room_data, force=True)
            
            if success:
                print(f"Room '{room_id}' exported to: {output_path}")
                renpy.notify(f"Room exported to YAML: {room_id}")
                return output_path
            else:
                print(f"Failed to export room '{room_id}' to YAML")
                renpy.notify("Error: Failed to export room to YAML")
                return False
        
        except Exception as e:
            print(f"Error exporting room to YAML: {e}")
            import traceback
            traceback.print_exc()
            renpy.notify(f"Error: Failed to export room: {e}")
            return False
    
    def import_room_from_yaml(yaml_path, room_id=None):
        """Import room configuration from YAML file with lighting data"""
        try:
            import os
            import sys
            sys.path.append(renpy.config.gamedir + "/api")
            import api_io_yaml
            
            if not os.path.exists(yaml_path):
                print(f"Error: YAML file not found: {yaml_path}")
                renpy.notify("Error: YAML file not found")
                return False
            
            # Load YAML data
            room_data = api_io_yaml.load_yaml(yaml_path)
            if not room_data:
                print(f"Error: Could not parse YAML file: {yaml_path}")
                renpy.notify("Error: Could not parse YAML file")
                return False
            
            # Determine room ID
            if not room_id:
                room_id = room_data.get("_metadata", {}).get("room_id")
            if not room_id:
                room_id = os.path.splitext(os.path.basename(yaml_path))[0].replace("_config", "")
            
            print(f"Importing room '{room_id}' from YAML")
            
            # Extract lighting data before updating room definition
            lighting_data = room_data.pop("lighting", None)
            metadata = room_data.pop("_metadata", {})
            
            # Ensure all objects have z-order properties
            for obj_name, obj_data in room_data.get("objects", {}).items():
                ensure_object_z_properties(obj_data, obj_name)
            
            # Update room definition
            ROOM_DEFINITIONS[room_id] = room_data
            
            # If this is the current room, apply changes immediately
            if hasattr(store, 'current_room_id') and store.current_room_id == room_id:
                load_room(room_id)
                
                # Apply lighting if available
                if lighting_data:
                    room_apply_lighting_from_data(lighting_data)
            
            # Store lighting data in persistent overrides for future loads
            if lighting_data:
                if not hasattr(persistent, 'room_overrides') or persistent.room_overrides is None:
                    persistent.room_overrides = {}
                if room_id not in persistent.room_overrides:
                    persistent.room_overrides[room_id] = {}
                persistent.room_overrides[room_id]["lighting"] = lighting_data
            
            lights_count = len(lighting_data.get("lights", [])) if lighting_data else 0
            print(f"Successfully imported room '{room_id}' with {lights_count} lights")
            renpy.notify(f"Room imported: {room_id} ({lights_count} lights)")
            return room_id
        
        except Exception as e:
            print(f"Error importing room from YAML: {e}")
            import traceback
            traceback.print_exc()
            renpy.notify(f"Error: Failed to import room: {e}")
            return False
    
    # Batch operations
    def export_all_rooms_to_yaml(base_dir=None):
        """Export all room definitions to YAML files"""
        try:
            if not base_dir:
                import os
                base_dir = os.path.join(renpy.config.gamedir, "rooms_export")
            
            os.makedirs(base_dir, exist_ok=True)
            exported = []
            failed = []
            
            for room_id in ROOM_DEFINITIONS.keys():
                import os
                output_path = os.path.join(base_dir, f"{room_id}_config.yaml")
                result = export_room_to_yaml(room_id, output_path)
                
                if result:
                    exported.append(room_id)
                else:
                    failed.append(room_id)
            
            total = len(exported) + len(failed)
            print(f"Batch export complete: {len(exported)}/{total} rooms exported")
            
            if failed:
                print(f"Failed exports: {', '.join(failed)}")
                renpy.notify(f"Exported {len(exported)}/{total} rooms (some failed)")
            else:
                renpy.notify(f"Successfully exported all {total} rooms to YAML")
            
            return {"exported": exported, "failed": failed, "base_dir": base_dir}
        
        except Exception as e:
            print(f"Error in batch export: {e}")
            renpy.notify(f"Error: Batch export failed: {e}")
            return False
            
            # Clear gamepad selection and hover so no objects are initially highlighted
            store.gamepad_selected_object = None
            store.current_hover_object = None
            store.previous_hover_object = None

            # Apply per-room breathing settings (if any)
            try:
                apply_room_breathing_settings(room_id)
            except Exception:
                pass
            
            return True
        return False

    # room_load alias removed - use load_room() directly
    
    def play_room_audio(room_id):
        """Play room music using room definition or fallback to audio/<room>.mp3."""
        try:
            music_path = None
            channel = "music"
            if room_id in ROOM_DEFINITIONS:
                rd = ROOM_DEFINITIONS[room_id]
                music_path = rd.get("music") or None
                channel = rd.get("ambient_channel") or channel
            # Fallback if missing or not loadable
            if not music_path or not renpy.loadable(music_path):
                fallback = f"audio/{room_id}.mp3"
                music_path = fallback if renpy.loadable(fallback) else None

            # Stop default channel softly to avoid overlaps
            try:
                renpy.music.stop(channel="music", fadeout=0.4)
            except Exception:
                pass
            if music_path:
                try:
                    log_main_event("AUDIO", f"play {music_path} on {channel}")
                except Exception:
                    pass
                renpy.music.play(music_path, channel=channel, loop=True, fadein=0.4)
            else:
                print(f"[Audio] No playable music for room {room_id}")
        except Exception as e:
            print(f"[Audio] Error playing room audio for {room_id}: {str(e)}")
            pass
    
    def fade_out_room_audio(duration=2.0):
        try:
            try:
                log_main_event("AUDIO", f"fade out audio {duration:.2f}s")
            except Exception:
                pass
            # Stop default music channel
            try:
                renpy.music.stop(channel="music", fadeout=duration)
            except Exception:
                pass
            # Stop room ambient channel if defined
            ch = None
            if store.current_room_id in ROOM_DEFINITIONS:
                ch = ROOM_DEFINITIONS[store.current_room_id].get("ambient_channel")
            if ch:
                try:
                    renpy.music.stop(channel=ch, fadeout=duration)
                except Exception:
                    pass
            print(f"Fading out room audio over {duration} seconds")
        except Exception as e:
            print(f"Error fading out audio: {str(e)}")
            pass

    # Audio aliases removed - use direct functions or new YAML API
    
    def toggle_crt_effect():
        if not hasattr(store, 'crt_enabled'):
            store.crt_enabled = False
        store.crt_enabled = not store.crt_enabled
        store.crt_stable_state = store.crt_enabled
        try:
            log_main_event("VAR", f"crt_enabled={'on' if store.crt_enabled else 'off'}")
        except Exception:
            pass
        renpy.notify(f"CRT effect {'enabled' if store.crt_enabled else 'disabled'}")
        renpy.restart_interaction()

    # Short aliases for CRT controls
    def crt_toggle():
        return toggle_crt_effect()
    
    # YAML Room Configuration Loading
    def load_room_config_yaml(room_id):
        """Load room configuration from YAML file.
        
        Args:
            room_id: Room identifier (e.g., 'room1')
            
        Returns:
            Dict with room configuration or empty dict if failed
        """
        try:
            import yaml
            config_path = "rooms/" + room_id + "/" + room_id + ".yaml"
            if renpy.loadable(config_path):
                config_data = renpy.loader.load(config_path).read().decode('utf-8')
                config = yaml.safe_load(config_data)
                print("[API] Loaded YAML config for " + room_id)
                return config or {}
            else:
                print("[API] YAML config not found: " + config_path)
                return {}
        except Exception as e:
            print("[API] Error loading YAML config for " + room_id + ": " + str(e))
            return {}
    
    def get_room_music_from_config(room_id):
        """Get music file path for a room from its YAML config.
        
        Args:
            room_id: Room identifier
            
        Returns:
            Music file path or None
        """
        config = load_room_config_yaml(room_id)
        if config and "room_info" in config:
            return config["room_info"].get("music")
        return None
    
    def play_room_music_from_config(room_id, channel="music", fadein=2.0):
        """Play room music using YAML configuration.
        
        Args:
            room_id: Room identifier
            channel: Audio channel to use
            fadein: Fade in duration
            
        Returns:
            True if music started, False otherwise
        """
        music_file = get_room_music_from_config(room_id)
        if music_file and renpy.loadable(music_file):
            renpy.music.play(music_file, channel=channel, loop=True, fadein=fadein)
            print("[API] Playing music for " + room_id + ": " + music_file)
            return True
        else:
            print("[API] No music found for room " + room_id)
            return False
    
    # Room Object Configuration APIs
    def get_room_objects_from_config(room_id):
        """Get all objects configuration for a room from YAML.
        
        Args:
            room_id: Room identifier
            
        Returns:
            Dict of objects or empty dict
        """
        config = load_room_config_yaml(room_id)
        return config.get("objects", {})
    
    def get_room_object_config(room_id, object_name):
        """Get specific object configuration from YAML.
        
        Args:
            room_id: Room identifier
            object_name: Object name (e.g., 'detective', 'patreon')
            
        Returns:
            Dict with object config or empty dict
        """
        objects = get_room_objects_from_config(room_id)
        return objects.get(object_name, {})
    
    def get_room_object_interactions(room_id, object_name):
        """Get available interactions for an object.
        
        Args:
            room_id: Room identifier
            object_name: Object name
            
        Returns:
            List of interaction dicts
        """
        obj_config = get_room_object_config(room_id, object_name)
        return obj_config.get("interactions", [])
    
    # Room Environment Configuration APIs
    def get_room_background_from_config(room_id):
        """Get background image path from YAML config.
        
        Args:
            room_id: Room identifier
            
        Returns:
            Background image path or None
        """
        config = load_room_config_yaml(room_id)
        if config and "room_info" in config:
            return config["room_info"].get("background")
        return None
    
    def get_room_lighting_config(room_id):
        """Get lighting configuration from YAML.
        
        Args:
            room_id: Room identifier
            
        Returns:
            Dict with lighting config
        """
        config = load_room_config_yaml(room_id)
        return config.get("lighting", {})
    
    # Atmosphere config removed - was legacy/unused code
    
    # Room Audio Configuration APIs
    def get_room_audio_config(room_id):
        """Get all audio configuration from YAML.
        
        Args:
            room_id: Room identifier
            
        Returns:
            Dict with audio config (music, sfx, speech)
        """
        config = load_room_config_yaml(room_id)
        return config.get("audio", {})
    
    def get_room_sfx_path(room_id, sfx_name):
        """Get path to a specific sound effect.
        
        Args:
            room_id: Room identifier
            sfx_name: Sound effect name (e.g., 'paper_rustle')
            
        Returns:
            SFX file path or None
        """
        audio_config = get_room_audio_config(room_id)
        sfx_config = audio_config.get("sfx", {})
        return sfx_config.get(sfx_name)
    
    def play_room_sfx_from_config(room_id, sfx_name, channel="sound"):
        """Play a sound effect using YAML configuration.
        
        Args:
            room_id: Room identifier
            sfx_name: Sound effect name
            channel: Audio channel
            
        Returns:
            True if played, False otherwise
        """
        sfx_path = get_room_sfx_path(room_id, sfx_name)
        if sfx_path and renpy.loadable(sfx_path):
            renpy.sound.play(sfx_path, channel=channel)
            print("[API] Playing SFX for " + room_id + ": " + sfx_path)
            return True
        else:
            print("[API] SFX not found: " + sfx_name + " for " + room_id)
            return False
    
    # Room Setup Helper APIs
    def apply_room_lighting_from_config(room_id):
        """Apply lighting settings from YAML configuration.
        
        Args:
            room_id: Room identifier
        """
        lighting = get_room_lighting_config(room_id)
        if lighting:
            # Apply lighting settings to store variables
            if "ambient_light" in lighting:
                store.room_ambient_light = lighting["ambient_light"]
            if "shadow_intensity" in lighting:
                store.room_shadow_intensity = lighting["shadow_intensity"]
            if "light_temperature" in lighting:
                store.room_light_temperature = lighting["light_temperature"]
            if "flickering_lights" in lighting and lighting["flickering_lights"]:
                store.crt_animated = True
            # New: apply a declared lighting preset automatically
            try:
                preset_name = str(lighting.get("preset", "")).strip()
                if preset_name:
                    # Prefer direct YAML-based loader integrated with the shader
                    if 'load_lighting' in globals():
                        lights = load_lighting(preset_name)
                        if isinstance(lights, list):
                            # Success path for shader-based lighting
                            if hasattr(store, 'lights_state'):
                                store.lights_state['enabled'] = bool(lights)
                            store.lighting_preview_active = True
                            if getattr(config, 'developer', False):
                                print("[API] Applied lighting preset: {} ({} lights)".format(preset_name, len(lights)))
                        else:
                            # Fallback: use simple helper
                            if 'set_light' in globals():
                                set_light(preset_name)
                                if getattr(config, 'developer', False):
                                    print("[API] Applied simple lighting preset: {}".format(preset_name))
                    elif 'set_light' in globals():
                        set_light(preset_name)
                        if getattr(config, 'developer', False):
                            print("[API] Applied simple lighting preset: {}".format(preset_name))
            except Exception as e:
                print("[API] Lighting preset apply failed: {}".format(e))
            print("[API] Applied lighting config for " + room_id)
    
    # Atmosphere application removed - was legacy/unused code
    
    def convert_yaml_to_room_definition(room_id):
        """Convert YAML room configuration to ROOM_DEFINITIONS format.
        
        Args:
            room_id: Room identifier
            
        Returns:
            Dictionary in ROOM_DEFINITIONS format or None if failed
        """
        try:
            config = load_room_config_yaml(room_id)
            if not config:
                print(f"[API] No YAML config found for room: {room_id}")
                return None
            
            room_info = config.get("room_info", {})
            objects = config.get("objects", {})
            
            # Convert YAML objects to ROOM_DEFINITIONS format
            converted_objects = {}
            for obj_name, obj_data in objects.items():
                # Copy object data and ensure z-order properties
                obj_copy = dict(obj_data)
                converted_objects[obj_name] = ensure_object_z_properties(obj_copy, obj_name)
            
            room_def = {
                "background": room_info.get("background", ""),
                "objects": converted_objects
            }
            
            print(f"[API] Converted YAML to room definition for {room_id}")
            return {room_id: room_def}
            
        except Exception as e:
            print(f"[API] Error converting YAML for room {room_id}: {e}")
            return None
    
    def register_room_from_yaml(room_id):
        """Register room from YAML into global ROOM_DEFINITIONS.
        
        Args:
            room_id: Room identifier
            
        Returns:
            True if successful, False otherwise
        """
        try:
            room_def = convert_yaml_to_room_definition(room_id)
            if room_def:
                # Add to global ROOM_DEFINITIONS
                ROOM_DEFINITIONS.update(room_def)
                print(f"[API] Registered room {room_id} from YAML")
                return True
            return False
            
        except Exception as e:
            print(f"[API] Error registering room {room_id}: {e}")
            return False
    
    def setup_room_from_yaml(room_id):
        """Complete room setup using YAML configuration.
        
        Args:
            room_id: Room identifier
            
        Returns:
            True if setup successful, False otherwise
        """
        try:
            # Ensure room is registered in ROOM_DEFINITIONS
            if room_id not in ROOM_DEFINITIONS:
                register_room_from_yaml(room_id)
            
            # Load and apply all room configuration
            config = load_room_config_yaml(room_id)
            if not config:
                return False
            
            # Note: Objects are already loaded by load_room(), just ensure background is set
            if room_id in ROOM_DEFINITIONS:
                store.room_background = ROOM_DEFINITIONS[room_id]["background"]
                print(f"[API] Room objects already loaded by load_room(): {len(store.room_objects)} objects")
            
            # Apply lighting configuration
            apply_room_lighting_from_config(room_id)
            
            # Play room music
            play_room_music_from_config(room_id)
            
            print("[API] Complete room setup for " + room_id + " from YAML")
            return True
            
        except Exception as e:
            print("[API] Error in room setup for " + room_id + ": " + str(e))
            return False
    
    def set_crt_parameters(warp=0.2, scan=0.5, chroma=0.9, scanline_size=1.0):
        store.crt_warp = warp
        store.crt_scan = scan
        store.crt_chroma = chroma
        store.crt_scanline_size = scanline_size
        try:
            log_main_event("ANIM", f"crt params warp={warp}, scan={scan}, chroma={chroma}, scanline_size={scanline_size}")
        except Exception:
            pass
        renpy.notify(f"CRT parameters updated: warp={warp}, scan={scan}, chroma={chroma}, scanline_size={scanline_size}")
        if hasattr(store, 'crt_enabled') and store.crt_enabled:
            renpy.restart_interaction()

    def crt_params(warp=0.2, scan=0.5, chroma=0.9, scanline_size=1.0):
        return set_crt_parameters(warp, scan, chroma, scanline_size)
    
    # CRT animation toggle removed; animation is controlled via editor presets only.

    def adjust_vignette(delta_strength=0.0, delta_width=0.0, set_strength=None, set_width=None):
        """Adjust or set vignette parameters (now uses colour grading variables).
        - Strength range: 0.0..1.0 (higher = darker edges)
        - Width range: 0.05..0.50 (smaller = narrower, stronger band)
        """
        # Initialize new grading variables if missing
        if not hasattr(store, 'grade_vignette_strength'):
            store.grade_vignette_strength = 0.0
        if not hasattr(store, 'grade_vignette_width'):
            store.grade_vignette_width = 0.25

        strength = store.grade_vignette_strength
        width = store.grade_vignette_width

        if set_strength is not None:
            strength = float(set_strength)
        else:
            strength = float(strength) + float(delta_strength)
        if set_width is not None:
            width = float(set_width)
        else:
            width = float(width) + float(delta_width)

        # Clamp to safe ranges
        strength = max(0.0, min(1.0, strength))
        width = max(0.05, min(0.50, width))

        store.grade_vignette_strength = strength
        store.grade_vignette_width = width
        
        # Enable colour grading if vignette is active
        if strength > 0.0 or width != 0.25:
            store.color_grading_enabled = True
        
        try:
            log_main_event("ANIM", f"vignette strength={strength:.2f}, width={width:.2f} (colour grading)")
        except Exception:
            pass
        renpy.notify(f"Vignette: strength={strength:.2f}, width={width:.2f}")
        renpy.restart_interaction()

    def vignette(delta_strength=0.0, delta_width=0.0, set_strength=None, set_width=None):
        return adjust_vignette(delta_strength, delta_width, set_strength, set_width)
    
    # Console export functions removed - use YAML files for configuration
    
    def get_object_list_for_navigation():
        if not store.room_objects:
            return []
        objects = list(store.room_objects.items())
        objects.sort(key=lambda obj: (obj[1]["y"], obj[1]["x"]))
        return [obj[0] for obj in objects]

    def nav_list():
        return get_object_list_for_navigation()
    
    def find_nearest_object_from_screen_center(direction):
        """Find the nearest object in a specific direction from screen center"""
        if not store.room_objects:
            return None
            
        # Get screen center coordinates
        screen_center_x = config.screen_width // 2
        screen_center_y = config.screen_height // 2
        
        best_obj = None
        best_distance = float('inf')
        
        for obj_name, obj_data in store.room_objects.items():
            obj_center_x = obj_data["x"] + obj_data["width"] // 2
            obj_center_y = obj_data["y"] + obj_data["height"] // 2
            
            valid_direction = False
            if direction == "left" and obj_center_x < screen_center_x:
                valid_direction = True
            elif direction == "right" and obj_center_x > screen_center_x:
                valid_direction = True
            elif direction == "up" and obj_center_y < screen_center_y:
                valid_direction = True
            elif direction == "down" and obj_center_y > screen_center_y:
                valid_direction = True
            
            if valid_direction:
                dx = obj_center_x - screen_center_x
                dy = obj_center_y - screen_center_y
                distance = (dx * dx + dy * dy) ** 0.5
                if distance < best_distance:
                    best_distance = distance
                    best_obj = obj_name
        
        return best_obj
    
    def find_nearest_object(current_obj, direction):
        if not current_obj or current_obj not in store.room_objects:
            return None
        current_data = store.room_objects[current_obj]
        current_center_x = current_data["x"] + current_data["width"] // 2
        current_center_y = current_data["y"] + current_data["height"] // 2
        best_obj = None
        best_distance = float('inf')
        for obj_name, obj_data in store.room_objects.items():
            if obj_name == current_obj:
                continue
            obj_center_x = obj_data["x"] + obj_data["width"] // 2
            obj_center_y = obj_data["y"] + obj_data["height"] // 2
            valid_direction = False
            if direction == "left" and obj_center_x < current_center_x:
                valid_direction = True
            elif direction == "right" and obj_center_x > current_center_x:
                valid_direction = True
            elif direction == "up" and obj_center_y < current_center_y:
                valid_direction = True
            elif direction == "down" and obj_center_y > current_center_y:
                valid_direction = True
            if valid_direction:
                dx = obj_center_x - current_center_x
                dy = obj_center_y - current_center_y
                distance = (dx * dx + dy * dy) ** 0.5
                if distance < best_distance:
                    best_distance = distance
                    best_obj = obj_name
        return best_obj
    
    def gamepad_navigate(direction):
        if not store.gamepad_navigation_enabled:
            return
        obj_list = get_object_list_for_navigation()
        if not obj_list:
            return
        
        # If no object is currently selected, start navigation from screen center
        if not store.gamepad_selected_object or store.gamepad_selected_object not in store.room_objects:
            next_obj = find_nearest_object_from_screen_center(direction)
            if next_obj:
                store.gamepad_selected_object = next_obj
                store.current_hover_object = next_obj
                try:
                    log_main_event("INPUT", f"hover {next_obj} (from screen center)", scope="controller")
                except Exception:
                    pass
                renpy.restart_interaction()
            return
        
        # If an object is already selected, find next object from current position
        next_obj = find_nearest_object(store.gamepad_selected_object, direction)
        if next_obj:
            store.gamepad_selected_object = next_obj
            store.current_hover_object = next_obj
            try:
                log_main_event("INPUT", f"hover {next_obj}", scope="controller")
            except Exception:
                pass
            renpy.restart_interaction()

    def nav_pad(direction):
        return gamepad_navigate(direction)
    
    def gamepad_select_first_object():
        obj_list = get_object_list_for_navigation()
        if obj_list:
            store.gamepad_selected_object = obj_list[0]
            store.current_hover_object = obj_list[0]
            try:
                log_main_event("INPUT", f"hover {obj_list[0]}", scope="controller")
            except Exception:
                pass
            renpy.restart_interaction()

    def nav_first():
        return gamepad_select_first_object()
    
    def toggle_gamepad_navigation():
        store.gamepad_navigation_enabled = not store.gamepad_navigation_enabled
        try:
            log_main_event("VAR", f"gamepad_navigation={'on' if store.gamepad_navigation_enabled else 'off'}")
        except Exception:
            pass
        if not store.gamepad_navigation_enabled:
            store.gamepad_selected_object = None
            if store.current_hover_object == store.gamepad_selected_object:
                store.current_hover_object = None
        renpy.notify(f"Gamepad navigation {'enabled' if store.gamepad_navigation_enabled else 'disabled'}")

    def nav_toggle():
        return toggle_gamepad_navigation()
