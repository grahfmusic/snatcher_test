# Global Events API
# Generic run-once helpers keyed by a string, independent of rooms.

init python:
    # Session-only run-once flags
    try:
        _run_once_flags
    except NameError:
        _run_once_flags = {}

    def _ensure_persistent_once():
        if not hasattr(persistent, 'run_once_flags') or not isinstance(persistent.run_once_flags, dict):
            persistent.run_once_flags = {}

    def has_run_once(key, persist=False):
        """Return True if `key` has already been executed in this scope."""
        if persist:
            _ensure_persistent_once()
            return bool(persistent.run_once_flags.get(str(key)))
        return bool(_run_once_flags.get(str(key)))

    # Aliases
    def once_ran(key, persist=False):
        return has_run_once(key, persist)

    def mark_run_once(key, persist=False):
        """Mark `key` as executed in this scope."""
        if persist:
            _ensure_persistent_once()
            persistent.run_once_flags[str(key)] = True
        else:
            _run_once_flags[str(key)] = True
        return True

    def once_mark(key, persist=False):
        return mark_run_once(key, persist)

    def run_once(key, func=None, label=None, persist=False, args=None, kwargs=None):
        """Run func/label only once per session or persistently.

        - key: unique string id
        - func: Python callable to call
        - label: Ren'Py label to call in a new context
        - persist: True to persist across playthroughs
        - args/kwargs: optional args
        """
        k = str(key)
        if has_run_once(k, persist=persist):
            return False
        try:
            if func:
                func(*(list(args) if isinstance(args, (list, tuple)) else ([] if args is None else [args])), **(kwargs or {}))
            elif label:
                renpy.call_in_new_context(label, *(list(args) if isinstance(args, (list, tuple)) else ([] if args is None else [args])), **(kwargs or {}))
            mark_run_once(k, persist=persist)
            return True
        except Exception as ex:
            try:
                print(f"[EventsAPI] Error in run_once({k}): {ex}")
            except Exception:
                pass
        return False

    def once(key, func=None, label=None, persist=False, args=None, kwargs=None):
        return run_once(key, func, label, persist, args, kwargs)
