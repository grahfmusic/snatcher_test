# Import/Export Services
# Professional import/export system for editor configurations, room data, and game states
#
# Features:
# - Export editor configurations to JSON
# - Import saved configurations
# - Room data export/import
# - Game state snapshots
# - Workspace save/load

init -10 python:
    import json
    import os
    import time
    from datetime import datetime
    
    # Export directory configuration
    EXPORT_BASE_DIR = "game/exports"
    EXPORT_CONFIGS_DIR = os.path.join(EXPORT_BASE_DIR, "configs")
    EXPORT_ROOMS_DIR = os.path.join(EXPORT_BASE_DIR, "rooms")
    EXPORT_STATES_DIR = os.path.join(EXPORT_BASE_DIR, "states")
    EXPORT_WORKSPACES_DIR = os.path.join(EXPORT_BASE_DIR, "workspaces")
    
    def ensure_export_directories():
        """Ensure all export directories exist."""
        for directory in [EXPORT_BASE_DIR, EXPORT_CONFIGS_DIR, EXPORT_ROOMS_DIR, 
                         EXPORT_STATES_DIR, EXPORT_WORKSPACES_DIR]:
            if not os.path.exists(directory):
                try:
                    os.makedirs(directory)
                except Exception as e:
                    debug_error(f"Failed to create directory {directory}", e)
    
    # ==================== CONFIGURATION EXPORT/IMPORT ====================
    
    def export_editor_config(config_name=None):
        """Export current editor configuration to JSON.
        
        Args:
            config_name: Optional name for the config (defaults to timestamp)
            
        Returns:
            Path to exported file or None on failure
        """
        ensure_export_directories()
        
        if not config_name:
            config_name = datetime.now().strftime("editor_config_%Y%m%d_%H%M%S")
        
        config_data = {
            "version": "2.0.0",
            "timestamp": time.time(),
            "name": config_name,
            
            # Shader settings
            "shaders": {
                "crt": {
                    "enabled": getattr(store, 'crt_enabled', False),
                    "animated": getattr(store, 'crt_animated', False),
                    "warp": getattr(store, 'crt_warp', 0.2),
                    "scan": getattr(store, 'crt_scan', 0.5),
                    "chroma": getattr(store, 'crt_chroma', 0.9),
                    "scanline_size": getattr(store, 'crt_scanline_size', 1.0),
                    "vignette_strength": getattr(store, 'crt_vignette_strength', 0.35),
                    "vignette_width": getattr(store, 'crt_vignette_width', 0.25)
                },
                "film_grain": {
                    "state": shader_states.get("film_grain", {}).get("current", 0) if 'shader_states' in dir() else 0,
                    "downscale": getattr(store, 'film_grain_downscale', 2.0)
                },
                "color_grading": {
                    "state": shader_states.get("color_grading", {}).get("current", 0) if 'shader_states' in dir() else 0
                },
                "lighting": {
                    "state": shader_states.get("lighting", {}).get("current", 0) if 'shader_states' in dir() else 0,
                    "strength": getattr(store, 'lighting_strength', 1.0),
                    "animated": getattr(store, 'lighting_animated', False),
                    "anim_speed": getattr(store, 'lighting_anim_speed', 0.5)
                }
            },
            
            # Breathing settings
            "breathing": {
                "enabled": getattr(store, 'breath_enabled', False),
                "components": {
                    "chest": getattr(store, 'breath_use_chest', True),
                    "shoulder_left": getattr(store, 'breath_use_shoulder_left', True),
                    "shoulder_right": getattr(store, 'breath_use_shoulder_right', True),
                    "head": getattr(store, 'breath_use_head', True)
                },
                "parameters": {
                    "chest_amp": getattr(store, 'chest_breathe_amp', 0.04),
                    "chest_period": getattr(store, 'chest_breathe_period', 5.2),
                    "chest_center_u": getattr(store, 'chest_breathe_center_u', 0.5),
                    "chest_center_v": getattr(store, 'chest_breathe_center_v', 0.58),
                    "chest_half_u": getattr(store, 'chest_breathe_half_u', 0.12),
                    "chest_half_v": getattr(store, 'chest_breathe_half_v', 0.13)
                }
            },
            
            # UI settings
            "ui": {
                "show_info_overlay": getattr(store, 'show_info_overlay', True),
                "show_debug_overlay": getattr(store, 'show_debug_overlay', False),
                "show_description_boxes": getattr(store, 'show_description_boxes', True)
            }
        }
        
        # Save to file
        filename = f"{config_name}.json"
        filepath = os.path.join(EXPORT_CONFIGS_DIR, filename)
        
        try:
            with open(filepath, 'w') as f:
                json.dump(config_data, f, indent=2)
            debug_system(f"Exported editor config to {filepath}")
            return filepath
        except Exception as e:
            debug_error(f"Failed to export editor config", e)
            return None
    
    def import_editor_config(filepath):
        """Import editor configuration from JSON file.
        
        Args:
            filepath: Path to the config file
            
        Returns:
            True on success, False on failure
        """
        try:
            with open(filepath, 'r') as f:
                config_data = json.load(f)
            
            # Validate version
            version = config_data.get("version", "1.0.0")
            if not version.startswith("2."):
                debug_warning(f"Config version {version} may not be fully compatible")
            
            # Apply shader settings
            shaders = config_data.get("shaders", {})
            if "crt" in shaders:
                crt = shaders["crt"]
                store.crt_enabled = crt.get("enabled", False)
                store.crt_animated = crt.get("animated", False)
                store.crt_warp = crt.get("warp", 0.2)
                store.crt_scan = crt.get("scan", 0.5)
                store.crt_chroma = crt.get("chroma", 0.9)
                store.crt_scanline_size = crt.get("scanline_size", 1.0)
                store.crt_vignette_strength = crt.get("vignette_strength", 0.35)
                store.crt_vignette_width = crt.get("vignette_width", 0.25)
            
            # Apply breathing settings
            breathing = config_data.get("breathing", {})
            if breathing:
                store.breath_enabled = breathing.get("enabled", False)
                components = breathing.get("components", {})
                store.breath_use_chest = components.get("chest", True)
                store.breath_use_shoulder_left = components.get("shoulder_left", True)
                store.breath_use_shoulder_right = components.get("shoulder_right", True)
                store.breath_use_head = components.get("head", True)
                
                params = breathing.get("parameters", {})
                store.chest_breathe_amp = params.get("chest_amp", 0.04)
                store.chest_breathe_period = params.get("chest_period", 5.2)
                store.chest_breathe_center_u = params.get("chest_center_u", 0.5)
                store.chest_breathe_center_v = params.get("chest_center_v", 0.58)
            
            # Apply UI settings
            ui = config_data.get("ui", {})
            if ui:
                store.show_info_overlay = ui.get("show_info_overlay", True)
                store.show_debug_overlay = ui.get("show_debug_overlay", False)
                store.show_description_boxes = ui.get("show_description_boxes", True)
            
            debug_system(f"Imported editor config from {filepath}")
            renpy.restart_interaction()
            return True
            
        except Exception as e:
            debug_error(f"Failed to import editor config from {filepath}", e)
            return False
    
    # ==================== ROOM DATA EXPORT/IMPORT ====================
    
    def export_room_data(room_id=None):
        """Export room data to JSON.
        
        Args:
            room_id: Room to export (defaults to current room)
            
        Returns:
            Path to exported file or None on failure
        """
        ensure_export_directories()
        
        if not room_id:
            room_id = getattr(store, 'current_room_id', 'unknown')
        
        room_data = {
            "version": "2.0.0",
            "timestamp": time.time(),
            "room_id": room_id,
            "background": getattr(store, 'room_background', None),
            "objects": {}
        }
        
        # Export object data
        if hasattr(store, 'room_objects'):
            for obj_name, obj_data in store.room_objects.items():
                room_data["objects"][obj_name] = {
                    "x": obj_data.get("x", 0),
                    "y": obj_data.get("y", 0),
                    "scale": obj_data.get("scale", 100),
                    "visible": obj_data.get("visible", True),
                    "image": obj_data.get("image", ""),
                    "description": obj_data.get("description", ""),
                    "interactions": obj_data.get("interactions", [])
                }
        
        # Save to file
        filename = f"room_{room_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = os.path.join(EXPORT_ROOMS_DIR, filename)
        
        try:
            with open(filepath, 'w') as f:
                json.dump(room_data, f, indent=2)
            debug_system(f"Exported room data to {filepath}")
            return filepath
        except Exception as e:
            debug_error(f"Failed to export room data", e)
            return None
    
    def import_room_data(filepath):
        """Import room data from JSON file.
        
        Args:
            filepath: Path to the room data file
            
        Returns:
            True on success, False on failure
        """
        try:
            with open(filepath, 'r') as f:
                room_data = json.load(f)
            
            # Apply room data
            room_id = room_data.get("room_id")
            if room_id:
                # Load the room first
                if 'load_room' in dir():
                    load_room(room_id)
                
                # Apply object positions and properties
                objects = room_data.get("objects", {})
                for obj_name, obj_data in objects.items():
                    if obj_name in store.room_objects:
                        store.room_objects[obj_name].update(obj_data)
                
                debug_system(f"Imported room data from {filepath}")
                renpy.restart_interaction()
                return True
            else:
                debug_warning("No room_id in imported data")
                return False
                
        except Exception as e:
            debug_error(f"Failed to import room data from {filepath}", e)
            return False
    
    # ==================== WORKSPACE SAVE/LOAD ====================
    
    def save_workspace(workspace_name=None):
        """Save complete workspace state.
        
        Args:
            workspace_name: Name for the workspace (defaults to timestamp)
            
        Returns:
            Path to workspace directory or None on failure
        """
        ensure_export_directories()
        
        if not workspace_name:
            workspace_name = datetime.now().strftime("workspace_%Y%m%d_%H%M%S")
        
        workspace_dir = os.path.join(EXPORT_WORKSPACES_DIR, workspace_name)
        
        try:
            if not os.path.exists(workspace_dir):
                os.makedirs(workspace_dir)
            
            # Save workspace metadata
            metadata = {
                "version": "2.0.0",
                "name": workspace_name,
                "timestamp": time.time(),
                "current_room": getattr(store, 'current_room_id', None)
            }
            
            with open(os.path.join(workspace_dir, "metadata.json"), 'w') as f:
                json.dump(metadata, f, indent=2)
            
            # Export editor config
            config_path = export_editor_config("editor_config")
            if config_path:
                import shutil
                shutil.move(config_path, os.path.join(workspace_dir, "editor_config.json"))
            
            # Export current room data
            room_path = export_room_data()
            if room_path:
                import shutil
                shutil.move(room_path, os.path.join(workspace_dir, "room_data.json"))
            
            # Save game state
            game_state = {
                "game_flags": getattr(store, 'game_flags', {}),
                "player_inventory": getattr(store, 'player_inventory', []),
                "current_chapter": getattr(store, 'current_chapter', 1)
            }
            
            with open(os.path.join(workspace_dir, "game_state.json"), 'w') as f:
                json.dump(game_state, f, indent=2)
            
            debug_system(f"Saved workspace to {workspace_dir}")
            return workspace_dir
            
        except Exception as e:
            debug_error(f"Failed to save workspace", e)
            return None
    
    def load_workspace(workspace_dir):
        """Load complete workspace state.
        
        Args:
            workspace_dir: Path to workspace directory
            
        Returns:
            True on success, False on failure
        """
        try:
            # Load metadata
            with open(os.path.join(workspace_dir, "metadata.json"), 'r') as f:
                metadata = json.load(f)
            
            debug_system(f"Loading workspace '{metadata.get('name', 'unknown')}'")
            
            # Load editor config
            config_path = os.path.join(workspace_dir, "editor_config.json")
            if os.path.exists(config_path):
                import_editor_config(config_path)
            
            # Load room data
            room_path = os.path.join(workspace_dir, "room_data.json")
            if os.path.exists(room_path):
                import_room_data(room_path)
            
            # Load game state
            state_path = os.path.join(workspace_dir, "game_state.json")
            if os.path.exists(state_path):
                with open(state_path, 'r') as f:
                    game_state = json.load(f)
                
                store.game_flags = game_state.get("game_flags", {})
                store.player_inventory = game_state.get("player_inventory", [])
                store.current_chapter = game_state.get("current_chapter", 1)
            
            debug_system(f"Loaded workspace from {workspace_dir}")
            renpy.restart_interaction()
            return True
            
        except Exception as e:
            debug_error(f"Failed to load workspace from {workspace_dir}", e)
            return False
    
    def list_workspaces():
        """List available workspaces.
        
        Returns:
            List of workspace names
        """
        ensure_export_directories()
        
        try:
            workspaces = []
            for item in os.listdir(EXPORT_WORKSPACES_DIR):
                item_path = os.path.join(EXPORT_WORKSPACES_DIR, item)
                if os.path.isdir(item_path):
                    metadata_path = os.path.join(item_path, "metadata.json")
                    if os.path.exists(metadata_path):
                        workspaces.append(item)
            return sorted(workspaces)
        except Exception as e:
            debug_error("Failed to list workspaces", e)
            return []
    
    # ==================== QUICK EXPORT/IMPORT FUNCTIONS ====================
    
    def quick_export_all():
        """Quick export of everything to a timestamped workspace."""
        workspace_name = save_workspace()
        if workspace_name:
            renpy.notify(f"Exported workspace: {os.path.basename(workspace_name)}")
        else:
            renpy.notify("Export failed!")
    
    def quick_import_latest():
        """Quick import of the most recent workspace."""
        workspaces = list_workspaces()
        if workspaces:
            latest = workspaces[-1]  # Assuming they're sorted by name/timestamp
            workspace_dir = os.path.join(EXPORT_WORKSPACES_DIR, latest)
            if load_workspace(workspace_dir):
                renpy.notify(f"Imported workspace: {latest}")
            else:
                renpy.notify("Import failed!")
        else:
            renpy.notify("No workspaces found!")

# Console commands for import/export
init python:
    config.console_commands["export_config"] = export_editor_config
    config.console_commands["export_room"] = export_room_data
    config.console_commands["save_workspace"] = save_workspace
    config.console_commands["list_workspaces"] = list_workspaces
    config.console_commands["quick_export"] = quick_export_all
    config.console_commands["quick_import"] = quick_import_latest
