# Main game script - clean entry point to room1

# Main entry point - fade out, then pixelate into room1
label start:
    # Developer-only hooks removed; start game directly
    
    # Global game start hook
    $ on_game_start()
    
    # Prepare background (no fade). We'll transition with Pixellate only.
    scene black
    
    # Register room1 from YAML first, then load
    $ register_yaml_room("room1")
    $ load_room("room1")
    $ on_room_enter("room1")
    
    # Music is started by load_room() via play_room_audio
    
    # Skip per-object/background fade-in on first entry
    $ room_has_faded_in = True

    # Transition into the exploration screen (pixelate only), then enter loop
    python:
        renpy.transition(Pixellate(1.2, 14))
    jump room_loop

label room_loop:
    call screen room_exploration
    jump room_loop
