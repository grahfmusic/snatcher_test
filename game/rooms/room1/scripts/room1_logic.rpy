# Room1 Logic (enhanced) - Ren'Py Style
# Demonstrates detective interaction system with dialogue cutscenes

# ============================================================================
# STATE VARIABLES - Using Ren'Py default for persistence
# ============================================================================
default detective_talked_to = False
default detective_ask_about_available = False
default detective_conversation_stage = 0
default room1_patreon_taken = False
default room1_first_visit = True

# ============================================================================
# CHARACTER DEFINITIONS - Standard Ren'Py characters
# ============================================================================
define detective_char = Character("Detective Blake", color="#4a90e2")
define player_char = Character("You", color="#e2a04a")
define narrator = Character(None, what_italic=True)

# ============================================================================
# ROOM ENTRY LABEL - Main entry point using Ren'Py style
# ============================================================================
label room1_enter:
    # Set current room for editor
    $ current_room_id = "room1"
    $ suppress_room_fade_once = True
    
    # Complete room setup from YAML configuration
    $ setup_room_from_yaml("room1")
    
    # Note: room_objects already loaded by load_room(), don't overwrite them

    # Ensure a visible lighting setup is active for this demo room.
    # Loads a shipped YAML preset so lights render without using the editor.
    python:
        try:
            if 'load_lighting' in globals():
                # Pick a clear, high-contrast starter preset
                _lights = load_lighting('streetlamp')  # matches light_streetlamp.yaml
                if isinstance(_lights, list):
                    if hasattr(store, 'lights_state'):
                        store.lights_state['enabled'] = bool(_lights)
                        store.lighting_preview_active = True
                    try:
                        renpy.restart_interaction()
                    except Exception:
                        pass
                elif 'set_light' in globals():
                    set_light('streetlamp')
        except Exception:
            pass
    
    # Apply default visual effects if no profiles loaded
    if not hasattr(store, 'room1_profiles_loaded'):
        # Apply default CRT preset (off by default)
        if hasattr(store, 'apply_crt_preset'):
            $ apply_crt_preset("Off")
        
        # Apply default lighting - Documentary/Natural Sunlight for visibility
        if hasattr(store, 'current_lighting_genre'):
            $ current_lighting_genre = "Documentary"
            $ current_lighting_style = "Natural Sunlight"
            $ lighting_intensity = 0.8
    
    # Handle first visit
    if room1_first_visit:
        $ room1_first_visit = False
        $ renpy.notify('Tip: Press F8 for Editor, F11 for Debug')
        
        # Apply default breathing preset
        if hasattr(store, 'apply_breathing_preset'):
            $ apply_breathing_preset("Emotional States", "Relaxed")
    
    # Hide taken items
    if persistent.room1_patreon_taken and "patreon" in room_objects:
        $ room_objects["patreon"]["visible"] = False
    
    return

# ============================================================================
# INTERACTION HANDLERS - Ren'Py style labels for interactions
# ============================================================================
label room1_detective_talk:
    # Clear interaction UI
    $ renpy.scene(layer="transient")
    hide screen interaction_menu
    $ interaction_menu_active = False
    $ interaction_target_object = None
    $ current_hover_object = None
    
    # Jump to detective dialogue
    call detective_talk_scene
    return

label room1_detective_ask_about:
    if detective_ask_about_available:
        call detective_ask_about_scene
    else:
        narrator "You should talk to the detective first."
    return

label room1_patreon_take:
    $ persistent.room1_patreon_taken = True
    $ room1_patreon_taken = True
    $ obj_hide('patreon')
    
    narrator "You take the flyer and slip it into your coat."
    
    # Show notification
    $ show_hint("room1: took 'patreon'")
    $ renpy.restart_interaction()
    return

# ============================================================================
# PYTHON HANDLER - Simplified to delegate to labels
# ============================================================================
init -1 python:
    class Room1Logic:
        """Room-specific logic for room1 - Ren'Py style delegation."""
        
        def on_room_enter(self, room_id):
            """Handle room entry - setup without calling labels."""
            # Set current room for editor
            store.current_room_id = room_id
            store.suppress_room_fade_once = True
            
            # Complete room setup from YAML configuration
            setup_room_from_yaml(room_id)

            # Ensure visible lighting is present in the scene
            try:
                # Turn on verbose lighting debug
                if 'lights_debug' in globals():
                    lights_debug(True)
                # Only auto-load if no lights are currently active
                if 'load_lighting' in globals():
                    _lights = load_lighting('streetlamp')
                    # If scan failed to find preset, craft a visible fallback
                    if (not _lights) and 'Light' in globals():
                            try:
                                sw = getattr(config, 'screen_width', 1280)
                                sh = getattr(config, 'screen_height', 720)
                                _lights = [
                                    Light(id='fallback_ambient', kind='ambient', x=sw/2.0, y=sh/2.0, radius=max(sw, sh), intensity=0.25, color=[0.10, 0.15, 0.30, 1.0], target='both'),
                                    Light(id='fallback_spot', kind='spot', x=sw*0.8, y=sh*0.2, radius=380, intensity=1.4, color=[0.90, 0.95, 1.00, 1.0], dir=[-0.6, 1.0], softness=0.3, target='objects')
                                ]
                            except Exception:
                                _lights = []
                    if isinstance(_lights, list):
                        if hasattr(store, 'lights_state'):
                            store.lights_state['enabled'] = bool(_lights)
                            store.lighting_preview_active = True
                        try:
                            renpy.restart_interaction()
                        except Exception:
                            pass
                    elif 'set_light' in globals():
                        set_light('streetlamp')
                elif 'set_light' in globals():
                    set_light('streetlamp')
            except Exception:
                pass
            
            # Available YAML API functions for room logic:
            # - get_room_object_config(room_id, "detective") - Get object config
            # - get_room_object_interactions(room_id, "detective") - Get available interactions
            # - play_room_sfx_from_config(room_id, "paper_rustle") - Play sound effects
            # - get_room_lighting_config(room_id) - Get lighting settings
            # - get_room_audio_config(room_id) - Get all audio configuration
            
            # Note: room_objects already loaded by load_room(), don't overwrite them
            print(f"[Room1Logic] Objects already loaded: {len(store.room_objects)} objects")
            
            # Apply room-specific profiles if they exist
            self.load_room_profiles(room_id)
            
            # If no room profiles, apply defaults
            if not hasattr(store, 'room1_profiles_loaded'):
                # Default lighting for visibility
                if hasattr(store, 'current_lighting_genre'):
                    store.current_lighting_genre = "Documentary"
                    store.current_lighting_style = "Natural Sunlight"
                    store.lighting_intensity = 0.8
                
                # CRT state left unchanged; presets and user controls manage it
                if hasattr(store, 'current_crt_preset'):
                    store.current_crt_preset = "Off"
            
            # Handle first visit
            if store.room1_first_visit:
                store.room1_first_visit = False
                # Use editor message system
                if hasattr(store, 'add_editor_message'):
                    add_editor_message('Tip: Press F8 for Editor, F11 for Debug')
                
                # Apply default breathing if available
                if hasattr(store, 'apply_breathing_preset'):
                    apply_breathing_preset("Emotional States", "Relaxed")
            
            # Hide taken items
            if persistent.room1_patreon_taken and "patreon" in store.room_objects:
                store.room_objects["patreon"]["visible"] = False
            
        def on_object_hover(self, room_id, obj_name):
            """Hover effects - kept minimal."""
            pass
            
        def on_object_interact(self, room_id, obj_name, action_id):
            """Route interactions to appropriate Ren'Py labels."""
            
            # Detective interactions
            if obj_name == 'detective':
                if action_id == 'talk':
                    renpy.call_in_new_context("room1_detective_talk")
                    return True
                elif action_id == 'ask_about':
                    renpy.call("room1_detective_ask_about")
                    return True
            
            # Patreon flyer interaction
            elif obj_name == 'patreon' and action_id == 'take':
                renpy.call("room1_patreon_take")
                return True
            
            return False
    
        def load_room_profiles(self, room_id):
            """Load room-specific presets if available (YAML-based)."""
            try:
                # Prefer custom presets named like room id
                candidates = []
                if 'shader_preset_list' in globals():
                    for rel in shader_preset_list('custom'):
                        base = rel.split('/')[-1].lower()
                        name_no_ext = base.rsplit('.', 1)[0]
                        if name_no_ext == f"{room_id}" or name_no_ext.startswith(f"{room_id}_"):
                            candidates.append(rel)
                # Fallback: shipped example matching color grade or scene
                if not candidates:
                    for rel in shader_preset_list('shipped'):
                        base = rel.split('/')[-1].lower()
                        name_no_ext = base.rsplit('.', 1)[0]
                        if name_no_ext in ("evidence_room", "noir"):
                            candidates.append(rel)
                if candidates:
                    shader_preset_apply_file(candidates[0])
                    store.room1_profiles_loaded = True
            except Exception:
                pass
    
    # Register the handler
    register_room_logic('room1', Room1Logic())
