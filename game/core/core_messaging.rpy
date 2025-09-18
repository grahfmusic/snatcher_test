# Messaging Helpers
# Centralized functions for user-facing messages and narration.

init python:
    def show_hint(text):
        """Show a brief HUD hint (non-blocking)."""
        try:
            renpy.notify(str(text))
        except Exception:
            pass

    def narrate(text):
        """Show blocking narration using the default narrator."""
        try:
            renpy.say(None, str(text))
        except Exception:
            # As a fallback, show a hint
            show_hint(text)
