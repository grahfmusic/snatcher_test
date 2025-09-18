# Detective Dialogue Scenes
# Contains all dialogue sequences for the detective character in room1

# Detective talk scene - initial conversation
label detective_talk_scene:
    # Activate cinematic letterbox via shader for detective conversations
    $ letterbox_on()
    scene black with dissolve
    
    # First time talking to detective
    if not detective_talked_to:
        "Detective Blake looks up from his notes."
        "Well, well. Another curious soul wandering into this case."
        
        "Case? What kind of case are you working on?"
        
        "The kind that keeps me up at night. Missing persons, strange disappearances."
        "Name's Blake. Detective Blake. Been on the force for fifteen years."
        
        "I'm just passing through. Didn't mean to intrude."
        
        "Everyone's 'just passing through' until they're not."
        "Tell you what - stick around if you want. Might need an extra pair of eyes."
        
        # Update conversation state
        $ detective_talked_to = True
        $ detective_ask_about_available = True
        $ detective_conversation_stage = 1
        
    # Subsequent conversations
    elif detective_conversation_stage == 1:
        "Back again? Good. I was hoping you'd reconsider my offer."
        
        "What exactly would you need me to do?"
        
        "Just keep your eyes open. Notice things others might miss."
        "In my experience, fresh perspectives can crack cases wide open."
        
        $ detective_conversation_stage = 2
        
    elif detective_conversation_stage >= 2:
        "Any new observations? Sometimes the smallest detail matters most."
        
        menu:
            "I noticed something strange about the patreon flyer.":
                "That flyer over there - it seems out of place."
                "Good eye. Everything's a potential clue in this business."
                "Keep thinking like that and you'll make a fine detective yourself."
                
            "Nothing new to report.":
                "Still looking around. Nothing jumps out at me yet."
                "Patience is key. The truth reveals itself to those who wait."
    
    scene black with dissolve
    
    # Deactivate letterbox after conversation ends
    $ letterbox_off()
    return

# Detective ask about scene - unlocked after first conversation
label detective_ask_about_scene:
    # Hide interaction menu during dialogue
    $ interact_hide()
    
    # Show letterbox with smooth animation
    $ letterbox_on()
    
    detective_char "What would you like to know? I've got fifteen years of stories."
    
    menu:
        "Tell me about the missing persons case.":
            detective_char "Three people in the last month. All vanished without a trace."
            detective_char "No signs of struggle, no notes, no witnesses. Just... gone."
            player_char "Any connection between them?"
            detective_char "That's what I'm trying to figure out. Different ages, backgrounds, lifestyles."
            detective_char "But they all frequented the same areas downtown."
            
        "How did you become a detective?":
            detective_char "Started as a beat cop. Saw too many cases go cold."
            detective_char "Decided if I was going to make a difference, I needed to be the one asking questions."
            player_char "Any regrets?"
            detective_char "Only that I didn't start sooner. Every day counts in this line of work."
            
        "What's this place got to do with your investigation?":
            detective_char "Good question. This location keeps coming up in witness statements."
            detective_char "Nothing concrete, but enough mentions to make it worth investigating."
            player_char "And have you found anything?"
            detective_char "Still working on it. That's where you come in - fresh eyes, new perspective."
            
        "Never mind.":
            detective_char "No problem. Door's always open if you change your mind."
    
    # Hide letterbox with smooth animation
    $ letterbox_off()
    
    return

# Helper label to get room logic instance
label get_room_logic_label(room_id):
    python:
        try:
            room1_logic = get_room_logic(room_id)
            # Store result in a variable that can be accessed outside the python block
            store.temp_room_logic = room1_logic
        except:
            store.temp_room_logic = None
    return
