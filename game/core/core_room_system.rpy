# Room System
# Clean room configuration and management
#
# This module handles:
# - Room definitions
# - Object management
# - Room transitions
# - Persistent state

## Room Definitions Registry
# Initialize at the earliest possible time
init -100 python:
    # Initialize room definitions registry
    if not hasattr(store, 'ROOM_DEFINITIONS'):
        store.ROOM_DEFINITIONS = {}
    if not hasattr(store, 'ORIGINAL_SIZES'):
        store.ORIGINAL_SIZES = {}

## Room Configuration Builder
init -10 python:
    def define_room(room_id, background="", music=None, ambient_channel="music", objects=None):
        """Define a room with its configuration.
        
        Args:
            room_id: Unique room identifier
            background: Background image path or color
            music: Background music file path
            ambient_channel: Audio channel for room ambience
            objects: Dict of objects in the room
        """
        ROOM_DEFINITIONS[room_id] = {
            "background": background,
            "music": music,
            "ambient_channel": ambient_channel,
            "objects": objects or {}
        }
        return ROOM_DEFINITIONS[room_id]
    
    def add_room_object(room_id, obj_name, **kwargs):
        """Add an object to a room.
        
        Args:
            room_id: Target room ID
            obj_name: Object identifier
            **kwargs: Object properties (x, y, image, description, etc.)
        """
        if room_id not in ROOM_DEFINITIONS:
            ROOM_DEFINITIONS[room_id] = {
                "background": "",
                "objects": {}
            }
        
        # Build object configuration
        obj_config = build_object_config(**kwargs)
        ROOM_DEFINITIONS[room_id]["objects"][obj_name] = obj_config
        
        return obj_config
    
    def build_object_config(x=0, y=0, image="", description="", 
                           scale_percent=100, width=None, height=None,
                           box_position="auto", actions=None, tags=None,
                           **extra):
        """Build a complete object configuration.
        
        Args:
            x, y: Position coordinates
            image: Image path
            description: Object description text
            scale_percent: Scale percentage (100 = original size)
            width, height: Explicit dimensions (auto-calculated if None)
            box_position: Description box position preference
            actions: List of interaction actions
            tags: List of object tags (e.g., ["character", "interactive"])
            **extra: Additional properties
        """
        # Auto-calculate dimensions if needed
        if width is None or height is None:
            if image:
                calc_width, calc_height = calculate_object_size(image, scale_percent)
                width = width or calc_width
                height = height or calc_height
            else:
                width = width or 100
                height = height or 100
        
        config = {
            "x": x,
            "y": y,
            "image": image,
            "description": description,
            "scale_percent": scale_percent,
            "width": width,
            "height": height,
            "box_position": box_position,
            "actions": actions or [],
            "tags": tags or []
        }
        
        # Merge extra properties
        config.update(extra)
        
        return config
    
    def calculate_object_size(image_path, scale_percent):
        """Calculate object dimensions based on image and scale.
        
        Args:
            image_path: Path to image file
            scale_percent: Scale percentage
            
        Returns:
            Tuple of (width, height)
        """
        # Try to get original size
        if image_path in ORIGINAL_SIZES:
            orig = ORIGINAL_SIZES[image_path]
        else:
            # Load and cache original size
            try:
                if renpy.loadable(image_path):
                    w, h = renpy.image_size(image_path)
                    ORIGINAL_SIZES[image_path] = {"width": w, "height": h}
                    orig = ORIGINAL_SIZES[image_path]
                else:
                    return 100, 100
            except Exception:
                return 100, 100
        
        # Apply scale
        width = int(orig["width"] * scale_percent / 100)
        height = int(orig["height"] * scale_percent / 100)
        
        return width, height
    
    def get_original_size_by_path(image_path):
        """Get cached original size for an image.
        
        Args:
            image_path: Path to image file
            
        Returns:
            Dict with width and height, or defaults
        """
        if image_path in ORIGINAL_SIZES:
            return ORIGINAL_SIZES[image_path]
        
        # Try to load and cache
        try:
            if renpy.loadable(image_path):
                w, h = renpy.image_size(image_path)
                ORIGINAL_SIZES[image_path] = {"width": int(w), "height": int(h)}
                return ORIGINAL_SIZES[image_path]
        except Exception:
            pass
        
        return {"width": 100, "height": 100}

## Room Definitions
# Room-specific definitions should be in their respective room files
# e.g., game/rooms/room1/scripts/room1_config.rpy

## Room Management Functions
init python:
    def load_room(room_id):
        """Load a room and set it as current.
        
        Args:
            room_id: Room identifier to load
            
        Returns:
            True if successful, False otherwise
        """
        if room_id not in ROOM_DEFINITIONS:
            print(f"[Room] Error: Room '{room_id}' not defined")
            return False
        
        # Store current room ID
        store.current_room_id = room_id
        
        # Deep copy room objects to allow runtime modifications
        import copy
        room_def = ROOM_DEFINITIONS[room_id]
        store.room_objects = copy.deepcopy(room_def["objects"])
        store.room_background = room_def["background"]
        
        # Debug: Show what was loaded
        for obj_name, obj_data in store.room_objects.items():
            print(f"[Room] Loaded object {obj_name}: image={obj_data.get('image')}, x={obj_data.get('x')}, has_z={obj_data.get('z') is not None}")
        
        # Apply persistent overrides if any
        apply_persistent_room_state(room_id)
        
        # Room audio is handled by individual room logic using standard Ren'Py commands
        
        # Select first object for navigation
        if store.room_objects:
            store.selected_object = list(store.room_objects.keys())[0]
        else:
            store.selected_object = None
        
        # Clear hover states
        store.current_hover_object = None
        store.previous_hover_object = None
        store.gamepad_selected_object = None
        
        # Apply room-specific settings (breathing, etc.)
        try:
            apply_room_breathing_settings(room_id)
        except Exception:
            pass
        
        print(f"[Room] Loaded room '{room_id}' with {len(store.room_objects)} objects")
        return True
    
    def apply_persistent_room_state(room_id):
        """Apply any persistent modifications to room objects.
        
        Args:
            room_id: Room identifier
        """
        if not hasattr(persistent, 'room_overrides') or persistent.room_overrides is None:
            persistent.room_overrides = {}
        
        if room_id in persistent.room_overrides:
            overrides = persistent.room_overrides[room_id]
            for obj_name, obj_overrides in overrides.items():
                if obj_name in store.room_objects:
                    store.room_objects[obj_name].update(obj_overrides)
                    print(f"[Room] Applied overrides to {obj_name}")
    
    def save_room_state(room_id=None):
        """Save current room state to persistent storage.
        
        Args:
            room_id: Room to save (defaults to current)
        """
        if room_id is None:
            room_id = store.current_room_id
        
        if not room_id:
            return False
        
        if not hasattr(persistent, 'room_overrides'):
            persistent.room_overrides = {}
        
        # Store current object states
        persistent.room_overrides[room_id] = {}
        for obj_name, obj_data in store.room_objects.items():
            # Only save position and scale changes
            persistent.room_overrides[room_id][obj_name] = {
                "x": obj_data["x"],
                "y": obj_data["y"],
                "scale_percent": obj_data["scale_percent"],
                "width": obj_data["width"],
                "height": obj_data["height"]
            }
        
        print(f"[Room] Saved state for room '{room_id}'")
        renpy.notify("Room state saved!")
        return True
    
    def reset_room_state(room_id=None):
        """Reset room to original configuration.
        
        Args:
            room_id: Room to reset (defaults to current)
        """
        if room_id is None:
            room_id = store.current_room_id
        
        if not room_id:
            return False
        
        # Clear persistent overrides
        if hasattr(persistent, 'room_overrides') and room_id in persistent.room_overrides:
            del persistent.room_overrides[room_id]
        
        # Reload room
        load_room(room_id)
        
        print(f"[Room] Reset room '{room_id}' to defaults")
        renpy.notify("Room reset to original state!")
        return True
    
    # Audio functions moved to api_room.rpy - rooms handle their own audio
    # def play_room_audio(room_id):
    #     """DEPRECATED: Rooms now handle their own audio using standard Ren'Py commands."""
    #     pass
    
    def transition_to_room(room_id, transition=None):
        """Transition to a new room with optional effect.
        
        Args:
            room_id: Target room ID
            transition: Ren'Py transition to use (e.g., Fade, Dissolve)
        """
        # Default transition
        if transition is None:
            transition = Fade(0.5, 0.3, 0.5)
        
        # Hide current screen
        renpy.hide_screen("room_exploration")
        
        # Load new room
        if load_room(room_id):
            # Trigger room enter logic
            try:
                on_room_enter(room_id)
            except Exception:
                pass
            
            # Show new room with transition
            renpy.show_screen("room_exploration")
            renpy.with_statement(transition)
            
            return True
        return False
