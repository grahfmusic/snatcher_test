# Core Error Handling
# Comprehensive error handling for the Snatchernauts framework
#
# Provides decorators and utilities for safe execution with proper debug logging

init -100 python:
    import functools
    import traceback
    
    class FrameworkError(Exception):
        """Base exception for framework errors."""
        pass
    
    class RoomError(FrameworkError):
        """Exception for room-related errors."""
        pass
    
    class ObjectError(FrameworkError):
        """Exception for object-related errors."""
        pass
    
    class ShaderError(FrameworkError):
        """Exception for shader-related errors."""
        pass
    
    class EditorError(FrameworkError):
        """Exception for editor-related errors."""
        pass
    
    def safe_execute(func):
        """Decorator for safe execution with error logging.
        
        Wraps functions to catch and log exceptions properly.
        """
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                # Log error with full context
                func_name = func.__name__
                error_msg = f"Error in {func_name}: {str(e)}"
                
                # Get traceback if in developer mode
                if config.developer:
                    tb = traceback.format_exc()
                    debug_error(error_msg, tb)
                else:
                    debug_error(error_msg)
                
                # Return safe default based on function name patterns
                if "get_" in func_name or "is_" in func_name or "has_" in func_name:
                    return None if "get_" in func_name else False
                elif "load_" in func_name or "save_" in func_name:
                    return False
                
                return None
        return wrapper
    
    def safe_room_operation(func):
        """Decorator for room operations with specific error handling."""
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                debug_perf_start(f"room_{func.__name__}")
                result = func(*args, **kwargs)
                debug_perf_end(f"room_{func.__name__}")
                return result
            except RoomError as e:
                debug_error(f"Room operation failed in {func.__name__}: {e}")
                return False
            except Exception as e:
                debug_error(f"Unexpected error in room operation {func.__name__}: {e}")
                return False
        return wrapper
    
    def safe_object_operation(func):
        """Decorator for object operations with specific error handling."""
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                # Extract object name if available
                obj_name = None
                if args and isinstance(args[0], str):
                    obj_name = args[0]
                elif 'obj_name' in kwargs:
                    obj_name = kwargs['obj_name']
                
                result = func(*args, **kwargs)
                
                if obj_name:
                    debug_object_modify(obj_name, {"operation": func.__name__})
                
                return result
            except ObjectError as e:
                debug_error(f"Object operation failed in {func.__name__}: {e}")
                return False
            except Exception as e:
                debug_error(f"Unexpected error in object operation {func.__name__}: {e}")
                return False
        return wrapper
    
    def safe_shader_operation(func):
        """Decorator for shader operations with specific error handling."""
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                result = func(*args, **kwargs)
                
                # Log shader state changes
                shader_type = kwargs.get('shader_type', 'unknown')
                debug_shader_change(shader_type, {"operation": func.__name__})
                
                return result
            except ShaderError as e:
                debug_error(f"Shader operation failed in {func.__name__}: {e}")
                # Return safe defaults for shader operations
                return None
            except Exception as e:
                debug_error(f"Unexpected error in shader operation {func.__name__}: {e}")
                return None
        return wrapper
    
    def validate_room_id(room_id):
        """Validate room ID before operations.
        
        Args:
            room_id: Room identifier to validate
            
        Raises:
            RoomError: If room_id is invalid
        """
        if not room_id:
            raise RoomError("Room ID cannot be None or empty")
        if not isinstance(room_id, str):
            raise RoomError(f"Room ID must be a string, got {type(room_id)}")
        # Check if room exists
        room_path = f"rooms/{room_id}"
        if not renpy.loadable(f"{room_path}/scripts/{room_id}_config.rpy"):
            debug_warning(f"Room '{room_id}' may not exist (config not found)")
    
    def validate_object_data(obj_data):
        """Validate object data structure.
        
        Args:
            obj_data: Object data dictionary to validate
            
        Raises:
            ObjectError: If object data is invalid
        """
        if not isinstance(obj_data, dict):
            raise ObjectError(f"Object data must be a dictionary, got {type(obj_data)}")
        
        # Required fields
        required_fields = ['x', 'y', 'image']
        for field in required_fields:
            if field not in obj_data:
                raise ObjectError(f"Object data missing required field: {field}")
        
        # Type validation
        if not isinstance(obj_data.get('x'), (int, float)):
            raise ObjectError(f"Object x position must be numeric")
        if not isinstance(obj_data.get('y'), (int, float)):
            raise ObjectError(f"Object y position must be numeric")
    
    def safe_get_store_value(name, default=None):
        """Safely get a value from the store.
        
        Args:
            name: Variable name
            default: Default value if not found
            
        Returns:
            Store value or default
        """
        try:
            return getattr(store, name, default)
        except Exception as e:
            debug_warning(f"Failed to get store value '{name}': {e}")
            return default
    
    def safe_set_store_value(name, value):
        """Safely set a value in the store.
        
        Args:
            name: Variable name
            value: Value to set
            
        Returns:
            True on success, False on failure
        """
        try:
            old_value = getattr(store, name, None)
            setattr(store, name, value)
            debug_var_change(name, old_value, value)
            return True
        except Exception as e:
            debug_error(f"Failed to set store value '{name}': {e}")
            return False
    
    def handle_critical_error(error_msg, exception=None):
        """Handle critical errors that should stop execution.
        
        Args:
            error_msg: Error message to display
            exception: Optional exception object
        """
        debug_error(f"CRITICAL: {error_msg}", exception)
        
        if config.developer:
            # In developer mode, show detailed error
            import traceback
            tb = traceback.format_exc() if exception else ""
            renpy.error(f"{error_msg}\n\n{tb}")
        else:
            # In production, show user-friendly message
            renpy.notify("An error occurred. Please restart the game.")
    
    # Error recovery functions
    def recover_room_state():
        """Attempt to recover from room state errors."""
        debug_system("Attempting room state recovery...")
        
        try:
            # Reset to a safe state
            store.current_room_id = None
            store.room_objects = {}
            store.room_background = None
            store.room_has_faded_in = False
            
            # Try to load the first room as fallback
            if 'load_room' in dir():
                load_room('room1')
                debug_system("Room state recovered - loaded room1")
                return True
        except Exception as e:
            debug_error("Failed to recover room state", e)
            return False
    
    def recover_shader_state():
        """Attempt to recover from shader state errors."""
        debug_system("Attempting shader state recovery...")
        
        try:
            # Reset all shaders to defaults
            store.crt_enabled = False
            store.crt_stable_state = False
            store.crt_animated = False
            
            if 'reset_all_shaders' in dir():
                reset_all_shaders()
                debug_system("Shader state recovered - all shaders reset")
                return True
        except Exception as e:
            debug_error("Failed to recover shader state", e)
            return False
    
    # Context managers for safe operations
    class SafeRoomContext:
        """Context manager for safe room operations."""
        
        def __init__(self, room_id):
            self.room_id = room_id
            self.previous_room = None
        
        def __enter__(self):
            self.previous_room = safe_get_store_value('current_room_id')
            debug_room_enter(self.room_id)
            return self
        
        def __exit__(self, exc_type, exc_val, exc_tb):
            if exc_type:
                debug_error(f"Error in room context for '{self.room_id}': {exc_val}")
                # Attempt recovery
                if self.previous_room:
                    try:
                        if 'load_room' in dir():
                            load_room(self.previous_room)
                    except:
                        pass
            else:
                debug_room_exit(self.room_id)
            return False  # Don't suppress exceptions
    
    class SafeEditorContext:
        """Context manager for safe editor operations."""
        
        def __enter__(self):
            debug_system("Entering editor context")
            # Save current state for potential rollback
            self.saved_state = {
                'crt_enabled': safe_get_store_value('crt_enabled'),
                'room_objects': dict(safe_get_store_value('room_objects', {}))
            }
            return self
        
        def __exit__(self, exc_type, exc_val, exc_tb):
            if exc_type:
                debug_error(f"Error in editor context: {exc_val}")
                # Rollback changes
                for key, value in self.saved_state.items():
                    safe_set_store_value(key, value)
                renpy.notify("Editor operation failed - changes rolled back")
            debug_system("Exiting editor context")
            return True  # Suppress exceptions in editor

# Apply error handling to existing functions
init python:
    # Wrap commonly used functions with error handling
    if 'load_room' in dir():
        load_room = safe_room_operation(load_room)
    
    if 'move_object' in dir():
        move_object = safe_object_operation(move_object)
    
    if 'scale_object' in dir():
        scale_object = safe_object_operation(scale_object)
