# Room3 Logic - Ren'Py Style
# Dark alley scene with atmospheric tension and mystery

# ============================================================================
# STATE VARIABLES - Using Ren'Py default for persistence
# ============================================================================
default room3_visited = False
default room3_mystery_level = 0
default room3_first_visit = True
default room3_clues_found = []
default room3_danger_level = 0

# ============================================================================
# CHARACTER DEFINITIONS
# ============================================================================
# narrator already defined in room1_logic.rpy
define mysterious_voice = Character("????", color="#9b59b6")

# ============================================================================
# ROOM ENTRY LABEL - Dark alley setup
# ============================================================================
label room3_enter:
    # Set up dark, mysterious visual effects
    $ suppress_room_fade_once = True
    
    # Apply visual effects - midnight chase scene
    $ vignette(1.0, 0.1)  # Heavy vignette for darkness
    $ grade('midnight_chase')
    # Use a dramatic grading preset for this scene
    $ grade('midnight_chase')
    $ grain('subtle')
    
    # Mark as visited
    $ room3_visited = True
    
    # Handle first visit
    if room3_first_visit:
        $ room3_first_visit = False
        narrator "You step into the dark alley. The distant sound of sirens echoes through the night."
        narrator "Shadows dance in the flickering streetlight."
        $ room3_danger_level = 1
    
    # Atmospheric check based on mystery level
    if room3_mystery_level > 3:
        narrator "The air feels heavy with secrets waiting to be uncovered."
    
    return

# ============================================================================
# INTERACTION HANDLERS - Mystery and investigation
# ============================================================================
label room3_search_shadows:
    $ room3_mystery_level += 1
    
    if room3_mystery_level == 1:
        narrator "You peer into the darkness. Something moves in the shadows."
    elif room3_mystery_level == 2:
        narrator "A faint outline becomes visible. Is someone watching you?"
    elif room3_mystery_level == 3:
        mysterious_voice "You shouldn't be here..."
        $ room3_danger_level += 1
    else:
        narrator "The shadows remain silent."
    
    return

label room3_examine_graffiti:
    if "graffiti" not in room3_clues_found:
        $ room3_clues_found.append("graffiti")
        narrator "Strange symbols are spray-painted on the wall."
        narrator "They seem to form a pattern... or perhaps a warning."
        $ room3_mystery_level += 1
    else:
        narrator "The cryptic symbols still make no sense."
    
    return

label room3_check_dumpster:
    if "dumpster" not in room3_clues_found:
        $ room3_clues_found.append("dumpster")
        narrator "You carefully search through the debris."
        narrator "A torn photograph catches your eye. It shows a familiar face..."
        $ room3_mystery_level += 2
    else:
        narrator "Nothing else of interest here."
    
    return

label room3_investigate_door:
    narrator "A heavy metal door stands at the end of the alley."
    
    if room3_mystery_level >= 5:
        narrator "You notice the door is slightly ajar. Light seeps through the crack."
        menu:
            "Enter the door?":
                narrator "You push the door open and step into the unknown..."
                $ room3_danger_level = 5
            "Stay in the alley":
                narrator "Perhaps it's wiser to gather more information first."
    else:
        narrator "The door is locked tight. You'll need to find another way."
    
    return

label room3_flee:
    if room3_danger_level >= 3:
        narrator "Your instincts scream danger. You quickly retreat from the alley."
        # Could trigger room change here
    else:
        narrator "There's still more to investigate here."
    
    return

# ============================================================================
# PYTHON HANDLER - Simplified delegation to labels
# ============================================================================
init -1 python:
    class Room3Logic:
        """Room3 logic - Dark alley with Ren'Py style delegation."""
        
        def on_room_enter(self, room_id):
            """Delegate room entry to Ren'Py label."""
            renpy.call("room3_enter")
            
        def on_object_hover(self, room_id, obj_name):
            """Hover effects - atmospheric for dark alley."""
            # Could add subtle sound effects or visual hints here
            pass
            
        def on_object_interact(self, room_id, obj_name, action_id):
            """Route interactions to appropriate Ren'Py labels."""
            
            # Shadow interactions
            if obj_name == 'shadows' and action_id in ['search', 'examine']:
                renpy.call("room3_search_shadows")
                return True
                
            # Graffiti examination
            elif obj_name == 'graffiti' and action_id in ['examine', 'read']:
                renpy.call("room3_examine_graffiti")
                return True
                
            # Dumpster search
            elif obj_name == 'dumpster' and action_id in ['search', 'check']:
                renpy.call("room3_check_dumpster")
                return True
                
            # Door investigation
            elif obj_name == 'door' and action_id in ['investigate', 'open']:
                renpy.call("room3_investigate_door")
                return True
                
            # Flee action
            elif action_id == 'flee' or action_id == 'leave':
                renpy.call("room3_flee")
                return True
            
            return False
    
    # Register the handler
    register_room_logic('room3', Room3Logic())
