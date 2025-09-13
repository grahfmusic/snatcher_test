# Configuration Builder Utilities
# Functions for creating and merging object configurations
#
# Overview
# - Factory-style helpers to produce normalized configs for objects and traits.
# - Use create_* helpers and merge_configs to keep definitions consistent.

init python:
    def create_object_config(base_config, overrides=None):
        """Create object configuration by merging base config with overrides"""
        config = base_config.copy()
        if overrides:
            config.update(overrides)
        return config
    
    def create_desaturation_config(overrides=None):
        """Create desaturation configuration with optional overrides"""
        return create_object_config(DEFAULT_DESATURATION_CONFIG, overrides)
    
    def create_bloom_config(overrides=None):
        """Create bloom configuration with optional overrides (deprecated - use create_desaturation_config)"""
        return create_object_config(DEFAULT_DESATURATION_CONFIG, overrides)
    
    def create_animation_config(overrides=None):
        """Create animation configuration with optional overrides"""
        return create_object_config(DEFAULT_ANIMATION_CONFIG, overrides)
    
    def merge_configs(*configs):
        """Merge multiple configuration dictionaries"""
        result = {}
        for config in configs:
            if config:
                result.update(config)
        return result
