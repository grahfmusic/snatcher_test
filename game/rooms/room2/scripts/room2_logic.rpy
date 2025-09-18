# Room2 Logic - Ren'Py Style
# Evidence room logic

# ============================================================================
# STATE VARIABLES - Using Ren'Py default for persistence
# ============================================================================
default room2_visited = False
default room2_objects_discovered = 0
default room2_puzzle_solved = False
default room2_first_visit = True
default room2_evidence_examined = []

# ============================================================================
# CHARACTER DEFINITIONS
# ============================================================================
# narrator already defined in room1_logic.rpy

# ============================================================================
# ROOM ENTRY LABEL - Evidence room setup
# ============================================================================
label room2_enter:
    # Set up evidence room visual effects
    $ suppress_room_fade_once = True
    
    # Apply visual effects - evidence room with window blinds
    $ vignette(0.8, 0.2)
    $ grade('evidence_room')
    # Apply a neutral cinematic look suitable for evidence inspection
    $ grade('detective_office')
    $ grain('subtle')
    
    # Mark as visited
    $ room2_visited = True
    
    # Handle first visit
    if room2_first_visit:
        $ room2_first_visit = False
        narrator "You enter the evidence room. Dust particles float in the light streaming through the blinds."
    
    # Set up room audio if available
    python:
        if hasattr(store, 'setup_room2_audio'):
            setup_room2_audio()
    
    return

# ============================================================================
# INTERACTION HANDLERS - Investigation mechanics
# ============================================================================
label room2_investigate_object:
    $ room2_objects_discovered += 1
    
    narrator "You carefully examine the evidence..."
    
    if room2_objects_discovered == 1:
        narrator "This could be important to the case."
    elif room2_objects_discovered == 3:
        narrator "The pieces are starting to come together."
    elif room2_objects_discovered >= 5:
        narrator "You've gathered substantial evidence."
        $ room2_puzzle_solved = True
    
    return

label room2_examine_files:
    if "files" not in room2_evidence_examined:
        $ room2_evidence_examined.append("files")
        narrator "The case files are spread across the desk. Red string connects various photographs and documents."
        narrator "One name keeps appearing: 'Project Snatcher'."
    else:
        narrator "You've already thoroughly examined the files."
    return

label room2_check_computer:
    if "computer" not in room2_evidence_examined:
        $ room2_evidence_examined.append("computer")
        narrator "The computer terminal displays encrypted data streams."
        narrator "You'll need proper clearance to access this information."
    else:
        narrator "The terminal is still locked."
    return

label room2_inspect_board:
    narrator "The evidence board shows a complex web of connections."
    
    if room2_objects_discovered >= 3:
        narrator "With what you've discovered, the pattern is becoming clearer."
    else:
        narrator "You need more evidence to understand the full picture."
    
    return

# ============================================================================
# PYTHON HANDLER - Simplified delegation to labels
# ============================================================================
init -1 python:
    class Room2Logic:
        """Room2 logic - Evidence room with Ren'Py style delegation."""
        
        def on_room_enter(self, room_id):
            """Delegate room entry to Ren'Py label."""
            renpy.call("room2_enter")
            
        def on_object_hover(self, room_id, obj_name):
            """Hover effects - kept minimal."""
            pass
            
        def on_object_interact(self, room_id, obj_name, action_id):
            """Route interactions to appropriate Ren'Py labels."""
            
            # Investigation interactions
            if action_id == 'investigate':
                renpy.call("room2_investigate_object")
                return True
            
            # Specific object interactions
            elif obj_name == 'files' and action_id in ['examine', 'look']:
                renpy.call("room2_examine_files")
                return True
                
            elif obj_name == 'computer' and action_id in ['use', 'check']:
                renpy.call("room2_check_computer")
                return True
                
            elif obj_name == 'board' and action_id in ['inspect', 'examine']:
                renpy.call("room2_inspect_board")
                return True
            
            return False
    
    # Register the handler
    register_room_logic('room2', Room2Logic())
