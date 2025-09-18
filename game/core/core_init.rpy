# Early init to disable engine-level reload/reset keys and set safe logging defaults
init -999 python:
    try:
        # Remove R-based reload/reset to avoid accidental exits
        renpy.config.keymap["reload_game"] = []
        renpy.config.keymap["utter_restart"] = []
    except Exception:
        pass

    # Provide safe defaults for logging flags very early
    try:
        if not hasattr(renpy.store, 'sn_log_enabled'):
            renpy.store.sn_log_enabled = True
        if not hasattr(renpy.store, 'sn_log_color'):
            renpy.store.sn_log_color = True
        if not hasattr(renpy.store, 'sn_log_intercept_prints'):
            renpy.store.sn_log_intercept_prints = True
        if not hasattr(renpy.store, 'sn_log_main_logic_only'):
            renpy.store.sn_log_main_logic_only = True
    except Exception:
        pass
