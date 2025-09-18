# Room Events API
# Helpers to run room-specific callbacks on first enter (session or persistent).

init python:
    # Session-scoped visited flags: cleared on new game/run.
    try:
        room_visit_flags
    except NameError:
        room_visit_flags = {}

    # Registry of room events. Structure:
    # room_event_registry['first_enter'][room_id] = [ { func, label, persist, args, kwargs, priority } ]
    try:
        room_event_registry
    except NameError:
        room_event_registry = { 'first_enter': {} }

    def _ensure_persistent_flags():
        """Ensure persistent map exists for persistent first-enter tracking."""
        if not hasattr(persistent, 'room_visit_flags') or not isinstance(persistent.room_visit_flags, dict):
            persistent.room_visit_flags = {}

    def room_has_visited(room_id, persist=False):
        """Return True if the room was marked visited.

        - persist=False: checks per-session flags
        - persist=True: checks persistent storage across sessions
        """
        if persist:
            _ensure_persistent_flags()
            return bool(persistent.room_visit_flags.get(room_id))
        return bool(room_visit_flags.get(room_id))

    # Alias
    def room_visited(room_id, persist=False):
        return room_has_visited(room_id, persist)

    def mark_room_visited(room_id, persist=False):
        """Mark a room as visited in session or persistent scope."""
        if persist:
            _ensure_persistent_flags()
            persistent.room_visit_flags[room_id] = True
        else:
            room_visit_flags[room_id] = True
        return True

    def room_visited_mark(room_id, persist=False):
        return mark_room_visited(room_id, persist)

    def register_on_first_enter(room_id, func=None, label=None, persist=False, args=None, kwargs=None, priority=0):
        """Register a callback or label to run once on first enter of room_id.

        - func: Python callable to execute
        - label: Ren'Py label name to call in a new context
        - persist: when True, only runs once across all playthroughs (persistent)
        - args/kwargs: optional args for func/label
        - priority: lower numbers run earlier
        """
        events = room_event_registry.setdefault('first_enter', {}).setdefault(room_id, [])
        events.append({
            'func': func,
            'label': label,
            'persist': bool(persist),
            'args': list(args) if isinstance(args, (list, tuple)) else ([] if args is None else [args]),
            'kwargs': dict(kwargs) if isinstance(kwargs, dict) else {},
            'priority': int(priority),
        })
        return True

    def on_first_enter(room_id, func=None, label=None, persist=False, args=None, kwargs=None, priority=0):
        return register_on_first_enter(room_id, func, label, persist, args, kwargs, priority)

    def process_first_enter_events(room_id):
        """Run any registered first-enter events for room_id if not yet visited.

        Executes all events regardless of which one marks visited; then marks visited.
        Uses per-event 'persist' to decide whether to skip if already globally visited.
        """
        events_map = room_event_registry.get('first_enter', {})
        events = list(events_map.get(room_id, []))
        if not events:
            return False

        # Sort by priority
        events.sort(key=lambda e: e.get('priority', 0))

        # Determine scopes to run
        for e in events:
            use_persist = bool(e.get('persist'))
            if room_has_visited(room_id, persist=use_persist):
                # Already ran in this scope; skip this event
                continue
            # Run
            try:
                if e.get('func'):
                    e['func'](*(e.get('args') or []), **(e.get('kwargs') or {}))
                elif e.get('label'):
                    try:
                        renpy.call_in_new_context(e['label'], *(e.get('args') or []), **(e.get('kwargs') or {}))
                    except Exception:
                        # Fallback to notify if label missing
                        renpy.notify(f"Missing label: {e['label']}")
                # Mark visited for this event's scope
                mark_room_visited(room_id, persist=use_persist)
            except Exception as ex:
                try:
                    print(f"[RoomEvents] Error running first-enter event for {room_id}: {ex}")
                except Exception:
                    pass
        return True

    def first_enter_run(room_id):
        return process_first_enter_events(room_id)

    def run_on_first_enter(room_id, func=None, label=None, persist=False, args=None, kwargs=None):
        """Immediate runner: execute now if first time; otherwise no-op.

        This does not register; it simply checks and runs once per scope.
        """
        use_persist = bool(persist)
        if room_has_visited(room_id, persist=use_persist):
            return False
        try:
            if func:
                func(*(list(args) if isinstance(args, (list, tuple)) else ([] if args is None else [args])), **(kwargs or {}))
            elif label:
                renpy.call_in_new_context(label, *(list(args) if isinstance(args, (list, tuple)) else ([] if args is None else [args])), **(kwargs or {}))
            mark_room_visited(room_id, persist=use_persist)
            return True
        except Exception as ex:
            try:
                print(f"[RoomEvents] Error in run_on_first_enter for {room_id}: {ex}")
            except Exception:
                pass
        return False

    def first_enter_once(room_id, func=None, label=None, persist=False, args=None, kwargs=None):
        return run_on_first_enter(room_id, func, label, persist, args, kwargs)
