# Fade-In Overlay
#
# Overview
# - Modal black fade overlay to block input and reveal scene smoothly.

transform first_room_fade(duration=1.5):
    alpha 1.0
    ease duration alpha 0.0

screen first_room_fade_overlay(duration=1.5):
    modal True
    zorder 1000
    add Solid("#000") at first_room_fade(duration)
    # When the fade completes, clear the first-entry flag and remove overlay
    timer duration action [ SetVariable("first_room_entry", False), Hide("first_room_fade_overlay") ]
