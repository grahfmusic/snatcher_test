# Interactions API
# Object color, gradient backgrounds, and interaction/menu routines
#
# Overview
# - Builds and shows object interaction menus; executes selected actions.
# - Provides color extraction and gradient backgrounds for UI styling.
#
# Contracts
# - show_interaction_menu(obj_name)
# - hide_interaction_menu(...)
# - navigate_interaction_menu(direction)
# - execute_selected_action() -> calls execute_object_action
# - execute_object_action(obj_name, action_type)
#
# Integration
# - Before executing built-in side effects, emits on_object_interact(room,obj,action)

init python:
    def get_object_main_color(obj_name):
        """Extract a representative color for an object with caching.

        Attempts dominant color extraction from the object's image using Pillow.
        Falls back to a type-based color when unavailable.
        """
        try:
            if obj_name not in store.room_objects:
                return "#ffffff"
            obj = store.room_objects[obj_name]
            image_path = obj.get("image", "")
            if image_path:
                cache = getattr(store, 'DOMINANT_COLOR_CACHE', None)
                if cache is None:
                    cache = {}
                    store.DOMINANT_COLOR_CACHE = cache
                if image_path in cache:
                    return cache[image_path]

                try:
                    from PIL import Image
                    if renpy.loadable(image_path):
                        with renpy.file(image_path) as f:
                            im = Image.open(f).convert('RGBA')
                            im = im.resize((64, 64), Image.BILINEAR)
                            colors = im.getcolors(64*64)
                            if colors:
                                colors = [c for c in colors if c[1][3] > 16]
                                if colors:
                                    colors.sort(key=lambda x: x[0], reverse=True)
                                    _, (r, g, b, a) = colors[0]
                                    hexcol = "#{:02x}{:02x}{:02x}".format(r, g, b)
                                    cache[image_path] = hexcol
                                    return hexcol
                except Exception:
                    pass

                obj_type = obj.get("object_type", "item")
                fallback = "#4a90e2" if obj_type == 'character' else ("#e2a04a" if obj_type == 'item' else "#ffffff")
                cache[image_path] = fallback
                return fallback
        except Exception:
            pass
        return "#ffffff"

    def _hex_to_rgb(h):
        h = h.lstrip('#')
        if len(h) >= 6:
            return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))
        return (255, 255, 255)

    def _rgb_to_hex(r, g, b):
        return "#{:02x}{:02x}{:02x}".format(max(0, min(255, r)), max(0, min(255, g)), max(0, min(255, b)))

    def _brighten_hex_color(hex_color, min_v=0.92, sat_boost=1.25):
        """Boost brightness and saturation while keeping hue."""
        try:
            import colorsys
            r, g, b = _hex_to_rgb(hex_color)
            r1, g1, b1 = r/255.0, g/255.0, b/255.0
            h, s, v = colorsys.rgb_to_hsv(r1, g1, b1)
            v = max(v, float(min_v))
            s = min(1.0, s * float(sat_boost))
            rr, gg, bb = colorsys.hsv_to_rgb(h, s, v)
            return _rgb_to_hex(int(rr*255), int(gg*255), int(bb*255))
        except Exception:
            return hex_color

    def get_highlight_tint_for_object(obj_name):
        base = get_object_main_color(obj_name)
        return _brighten_hex_color(base)
    
    def create_gradient_background(base_color, alpha=0.7):
        """Create a gradient background using the base color"""
        try:
            base_color = base_color.lstrip('#')
            if len(base_color) == 6:
                r, g, b = tuple(int(base_color[i:i+2], 16) for i in (0, 2, 4))
            else:
                r, g, b = 255, 255, 255
            lighter_r = min(255, int(r * 1.3))
            lighter_g = min(255, int(g * 1.3))
            lighter_b = min(255, int(b * 1.3))
            darker_r = max(0, int(r * 0.7))
            darker_g = max(0, int(g * 0.7))
            darker_b = max(0, int(b * 0.7))
            from renpy.display.im import LinearGradient
            top_color = "#{:02x}{:02x}{:02x}{:02x}".format(lighter_r, lighter_g, lighter_b, int(255 * alpha))
            bottom_color = "#{:02x}{:02x}{:02x}{:02x}".format(darker_r, darker_g, darker_b, int(255 * alpha))
            return LinearGradient(top_color, bottom_color, 0, 0, 0, INTERACTION_BUTTON_CONFIG["height"])
        except:
            return base_color + "{:02x}".format(int(255 * alpha))

# Framework dialogue system - handles scene transitions from interaction hooks
default pending_dialogue_scene = None
default pending_dialogue_args = None
default interaction_overrides = {}
# These are referenced in the interaction functions
default interaction_target_object = None
default interaction_selected_action = 0
default previous_hover_action = 0

init python:
    # ----- Action list helpers -----
    def get_interaction_actions(obj_type):
        """Return the action list for a given object type."""
        return (INTERACTION_ACTIONS.get(obj_type, []) or []).copy()

    # Aliases
    def act_get(obj_type):
        return get_interaction_actions(obj_type)

    def set_interaction_actions(obj_type, actions):
        """Replace the action list for an object type (list of {label, action})."""
        INTERACTION_ACTIONS[obj_type] = list(actions or [])
        try:
            renpy.restart_interaction()
        except Exception:
            pass
        return True

    def act_set(obj_type, actions):
        return set_interaction_actions(obj_type, actions)

    def add_interaction_action(obj_type, label, action, index=None):
        """Add a single action to an object type. If index is None, append."""
        lst = INTERACTION_ACTIONS.setdefault(obj_type, [])
        entry = {"label": str(label), "action": str(action)}
        if isinstance(index, int) and 0 <= index <= len(lst):
            lst.insert(index, entry)
        else:
            lst.append(entry)
        try:
            renpy.restart_interaction()
        except Exception:
            pass
        return True

    def act_add(obj_type, label, action, index=None):
        return add_interaction_action(obj_type, label, action, index)

    def remove_interaction_action(obj_type, action):
        """Remove the first action entry matching 'action' for a type."""
        lst = INTERACTION_ACTIONS.get(obj_type, [])
        for i, a in enumerate(list(lst)):
            if a.get("action") == action:
                del lst[i]
                try:
                    renpy.restart_interaction()
                except Exception:
                    pass
                return True
        return False

    def act_remove(obj_type, action):
        return remove_interaction_action(obj_type, action)

    # ----- Per-object overrides -----
    def set_object_actions(obj_name, actions):
        """Override the action list for a specific object (list of {label, action})."""
        store.interaction_overrides[obj_name] = list(actions or [])
        try:
            renpy.restart_interaction()
        except Exception:
            pass
        return True

    def obj_act_set(obj_name, actions):
        return set_object_actions(obj_name, actions)

    def clear_object_actions(obj_name):
        """Clear any per-object action override."""
        if obj_name in store.interaction_overrides:
            del store.interaction_overrides[obj_name]
            try:
                renpy.restart_interaction()
            except Exception:
                pass
            return True
        return False

    def obj_act_clear(obj_name):
        return clear_object_actions(obj_name)

    def get_actions_for_object(obj_name):
        """Return effective actions for an object, honoring per-object overrides."""
        if obj_name in store.interaction_overrides:
            return store.interaction_overrides[obj_name]
        obj = store.room_objects.get(obj_name) if hasattr(store, 'room_objects') else None
        if isinstance(obj, dict):
            # Inline per-object interactions defined in object config
            inline = obj.get("interactions")
            if isinstance(inline, list) and inline:
                return inline
            obj_type = obj.get("object_type", "item")
        else:
            obj_type = "item"
        return get_interaction_actions(obj_type)

    # Alias
    def obj_actions(obj_name):
        return get_actions_for_object(obj_name)
    def trigger_dialogue_scene(scene_label, args=None):
        """Framework function to safely trigger dialogue scenes from interaction hooks.
        
        This handles the complexity of transitioning from Python interaction context
        to Ren'Py script context for developers.
        
        Args:
            scene_label: The label name to call (e.g. "detective_talk_scene")
            args: Optional arguments to pass to the scene
        """
        store.pending_dialogue_scene = scene_label
        store.pending_dialogue_args = args
        log_debug("InteractionAPI", f"Dialogue scene '{scene_label}' queued for execution")
    
    def show_interaction_menu(obj_name):
        """Show interaction menu for the specified object"""
        global interaction_menu_active, interaction_target_object, interaction_selected_action
        
        if obj_name not in store.room_objects:
            renpy.notify(f"Object {obj_name} not found")
            return
        
        obj = store.room_objects[obj_name]
        actions = get_actions_for_object(obj_name)
        
        if not actions:
            renpy.notify("No interactions defined for this object")
            return
        
        interaction_menu_active = True
        interaction_target_object = obj_name
        store.interaction_target = obj_name  # Also set interaction_target for the menu screen
        interaction_selected_action = 0
        store.current_hover_object = obj_name
        try:
            labels = ", ".join(a.get("label", "?") for a in actions)
            obj_type = obj.get("object_type", "item")
            log_main_event("INTERACTION", f"show defs for {obj_name} type={obj_type} actions=[{labels}]", scope="global")
        except Exception:
            pass
        renpy.restart_interaction()

    def interact_show(obj_name):
        return show_interaction_menu(obj_name)
    
    def hide_interaction_menu(keep_object_selected=False, target_object=None):
        """Hide the interaction menu and optionally keep object selected"""
        global interaction_menu_active, interaction_target_object, interaction_selected_action
        obj_to_keep = target_object or interaction_target_object
        interaction_menu_active = False
        interaction_target_object = None
        interaction_selected_action = 0
        if keep_object_selected and obj_to_keep:
            store.current_hover_object = obj_to_keep
            store.gamepad_selected_object = obj_to_keep
        else:
            store.current_hover_object = None
            store.gamepad_selected_object = None
        renpy.restart_interaction()

    def interact_hide(keep_object_selected=False, target_object=None):
        return hide_interaction_menu(keep_object_selected, target_object)
    
    def navigate_interaction_menu(direction):
        """Navigate through interaction menu options with gamepad"""
        global interaction_selected_action
        if not interaction_menu_active or not interaction_target_object:
            return
        actions = get_actions_for_object(interaction_target_object)
        if direction == "up":
            renpy.sound.play("audio/ui/up.wav", channel="menu_nav")
            interaction_selected_action = (interaction_selected_action - 1) % len(actions)
        elif direction == "down":
            renpy.sound.play("audio/ui/down.wav", channel="menu_nav")
            interaction_selected_action = (interaction_selected_action + 1) % len(actions)
        renpy.restart_interaction()

    def interact_nav(direction):
        return navigate_interaction_menu(direction)
    
    def execute_selected_action():
        """Execute the currently selected action"""
        if not interaction_menu_active or not interaction_target_object:
            return
        obj = store.room_objects[interaction_target_object]
        actions = get_actions_for_object(interaction_target_object)
        if interaction_selected_action < len(actions):
            action = actions[interaction_selected_action]
            try:
                log_main_event("INPUT", f"execute action {action['action']} on {interaction_target_object}", scope="keyboard")
            except Exception:
                pass
            execute_object_action(interaction_target_object, action["action"])

    def interact_execute():
        return execute_selected_action()
    def execute_object_action(obj_name, action_type):
        """Execute a specific action on an object"""
        previous_object = obj_name
        
        # For the "leave" action, keep object selected to maintain description box
        # For other actions, clear the hover object to hide description box after execution
        if action_type == "leave":
            hide_interaction_menu(keep_object_selected=True, target_object=obj_name)
        else:
            hide_interaction_menu(keep_object_selected=False, target_object=None)
        
        obj = store.room_objects[obj_name]
        obj_type = obj.get("object_type", "item") 
        # Notify game logic hooks before executing side effects
        handled = False
        try:
            result = on_object_interact(store.current_room_id, obj_name, action_type)
            handled = bool(result)
        except Exception:
            handled = False
        if handled:
            try:
                log_main_event("INTERACT", f"{action_type} on {obj_name} handled by room logic", scope="local")
            except Exception:
                pass
            return
        if action_type == "talk":
            handle_talk_action(obj_name)
        elif action_type == "ask_about":
            handle_ask_about_action(obj_name)
        elif action_type == "take":
            handle_take_action(obj_name)
        elif action_type == "investigate":
            handle_investigate_action(obj_name)
        elif action_type == "open":
            handle_open_action(obj_name)
        elif action_type == "knock":
            handle_knock_action(obj_name)
        elif action_type == "search":
            handle_search_action(obj_name)
        elif action_type == "leave":
            renpy.sound.play("audio/ui/cancel.wav", channel="menu_nav")
            try:
                log_main_event("INTERACT", f"leave menu on {obj_name}")
            except Exception:
                pass
        else:
            renpy.notify(f"Unknown action: {action_type}")

    def interact_do(obj_name, action_type):
        return execute_object_action(obj_name, action_type)
    
    def handle_talk_action(obj_name):
        obj = store.room_objects[obj_name]
        character_name = obj_name.replace("_", " ").title()
        narrate(f"You strike up a conversation with {character_name}.")
    
    def handle_ask_about_action(obj_name):
        obj = store.room_objects[obj_name]
        character_name = obj_name.replace("_", " ").title()
        narrate(f"What would you like to ask {character_name} about?")
    
    def handle_take_action(obj_name):
        narrate(f"You take the {obj_name.replace('_', ' ')}")
    
    def handle_investigate_action(obj_name):
        obj = store.room_objects[obj_name]
        narrate(f"You carefully investigate the {obj_name.replace('_', ' ')}: {obj.get('description', 'Nothing of interest.')}")
    
    def handle_open_action(obj_name):
        narrate(f"You open the {obj_name.replace('_', ' ')}")
    
    def handle_knock_action(obj_name):
        narrate(f"You knock on the {obj_name.replace('_', ' ')}")
    
    def handle_search_action(obj_name):
        narrate(f"You search the {obj_name.replace('_', ' ')}")
    
    def get_menu_base_position(obj_name):
        if obj_name not in store.room_objects:
            return 0, 0
        obj = store.room_objects[obj_name]
        menu_x = obj["x"] + obj["width"] - INTERACTION_BUTTON_CONFIG["width"] - 10
        menu_y = obj["y"] + (obj["height"] // 3)
        if menu_x < 10:
            menu_x = 10
        elif menu_x > config.screen_width - INTERACTION_BUTTON_CONFIG["width"] - 10:
            menu_x = config.screen_width - INTERACTION_BUTTON_CONFIG["width"] - 10
        if menu_y < 10:
            menu_y = 10
        return menu_x, menu_y

init python:
    def gamepad_activate_object():
        """Activate interaction menu for currently selected object (A button)"""
        if store.gamepad_selected_object and store.gamepad_selected_object in store.room_objects:
            show_interaction_menu(store.gamepad_selected_object)

    def pad_activate():
        return gamepad_activate_object()
    
    def gamepad_confirm_action():
        """Confirm selected action (A button when menu is active)"""
        if interaction_menu_active:
            renpy.sound.play("audio/ui/select.wav", channel="menu_nav")
            try:
                if interaction_target_object:
                    actions = INTERACTION_ACTIONS.get(store.room_objects[interaction_target_object].get("object_type", "item"), [])
                    if actions and 0 <= interaction_selected_action < len(actions):
                        log_main_event("INPUT", f"execute action {actions[interaction_selected_action]['action']} on {interaction_target_object}", scope="controller")
            except Exception:
                pass
            execute_selected_action()
        else:
            renpy.sound.play("audio/ui/select.wav", channel="menu_nav")
            try:
                if store.gamepad_selected_object:
                    log_main_event("INPUT", f"select {store.gamepad_selected_object}", scope="controller")
            except Exception:
                pass
            gamepad_activate_object()

    def pad_confirm():
        return gamepad_confirm_action()
    
    def gamepad_cancel_action():
        """Cancel current action (B button)"""
        if interaction_menu_active:
            renpy.sound.play("audio/ui/cancel.wav", channel="menu_nav")
            hide_interaction_menu(keep_object_selected=True, target_object=interaction_target_object)

    def pad_cancel():
        return gamepad_cancel_action()
    
    def keyboard_cancel_action():
        """Cancel current action (Escape key)"""
        if interaction_menu_active:
            renpy.sound.play("audio/ui/cancel.wav", channel="menu_nav")
            hide_interaction_menu(keep_object_selected=True, target_object=interaction_target_object)
    
    def mouse_leave_action(obj_name, action_type):
        """Handle Leave button click"""
        previous_object = obj_name
        hide_interaction_menu(keep_object_selected=True, target_object=obj_name)
        renpy.sound.play("audio/ui/cancel.wav", channel="menu_nav")
        try:
            log_main_event("INTERACT", f"leave menu on {obj_name}", scope="mouse")
        except Exception:
            pass
    
    def execute_object_action_from_mouse(obj_name, action_type):
        """Mouse-initiated action execution wrapper to tag input source"""
        try:
            log_main_event("INPUT", f"execute action {action_type} on {obj_name}", scope="mouse")
        except Exception:
            pass
        execute_object_action(obj_name, action_type)

    def get_button_action(obj_name, action_data):
        """Get the appropriate action function for a button based on action type"""
        if action_data["action"] == "leave":
            return Function(mouse_leave_action, obj_name, action_data["action"])
        else:
            return Function(execute_object_action_from_mouse, obj_name, action_data["action"])
