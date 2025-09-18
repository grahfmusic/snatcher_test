# Room1 Configuration
# Register room from YAML using simple API

init python:
    # Load and register room1 from YAML configuration
    ROOM1_CONFIG = load_yaml_config("room1")
    yaml_room("room1")
