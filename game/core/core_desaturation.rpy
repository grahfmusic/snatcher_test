# Desaturation Effect Utilities
# Global utilities for desaturation effect calculations and configurations
#
# Overview
# - Computes desaturation parameters and presets for object highlighting.
# - Used for timing, intensity, and animation parameters of desaturation effects.
# - Replaces the old bloom system with a more efficient desaturation approach.
#
# Contracts
# - calculate_desaturation_parameters(obj_config) -> dict
# - should_show_desaturation(obj_config, hover_object, obj_name) -> bool
# - create_desaturation_config_dict(...) -> dict
# - apply_desaturation_preset(obj_config, preset_name) -> obj_config
# - DESATURATION_PRESETS: preset dictionaries for common highlighting styles

init python:
    def calculate_desaturation_parameters(obj_config, scale_factor=None):
        """Calculate desaturation effect parameters for an object"""
        if scale_factor is None:
            scale_factor = obj_config.get("scale_percent", 100) / 100.0
        
        # Get desaturation-specific parameters (with bloom fallbacks for compatibility)
        intensity = obj_config.get("desaturation_intensity", obj_config.get("bloom_intensity", 0.5))
        alpha_min = obj_config.get("desaturation_alpha_min", obj_config.get("bloom_alpha_min", 0.2))
        alpha_max = obj_config.get("desaturation_alpha_max", obj_config.get("bloom_alpha_max", 0.6))
        pulse_speed = obj_config.get("desaturation_pulse_speed", obj_config.get("bloom_pulse_speed", 1.0))
        enabled = obj_config.get("desaturation_enabled", obj_config.get("bloom_enabled", True))
        
        return {
            "desaturation_intensity": intensity,
            "desaturation_alpha_min": alpha_min,
            "desaturation_alpha_max": alpha_max,
            "desaturation_pulse_speed": pulse_speed,
            "desaturation_enabled": enabled
        }
    
    def should_show_desaturation(obj_config, hover_object=None, obj_name=None):
        """Check if desaturation should be displayed for an object"""
        # Check both new and legacy enable flags for compatibility
        if not obj_config.get("desaturation_enabled", obj_config.get("bloom_enabled", True)):
            return False
        
        # If hover_object is provided, check if this object is hovered
        if hover_object is not None and obj_name is not None:
            return hover_object == obj_name
        
        return True
    
    def create_desaturation_config_dict(
        desaturation_intensity=0.5,
        desaturation_alpha_min=0.2, 
        desaturation_alpha_max=0.6, 
        desaturation_pulse_speed=1.0,
        desaturation_fade_duration=0.3,
        desaturation_enabled=True
    ):
        """Create a standardized desaturation configuration dictionary"""
        return {
            "desaturation_intensity": desaturation_intensity,
            "desaturation_alpha_min": desaturation_alpha_min,
            "desaturation_alpha_max": desaturation_alpha_max,
            "desaturation_pulse_speed": desaturation_pulse_speed,
            "desaturation_fade_duration": desaturation_fade_duration,
            "desaturation_enabled": desaturation_enabled
        }

# Desaturation presets for common object highlighting styles
define DESATURATION_PRESETS = {
    # Basic presets
    "subtle": {
        "desaturation_intensity": 0.3,
        "desaturation_alpha_min": 0.2,
        "desaturation_alpha_max": 0.5,
        "desaturation_pulse_speed": 0.8,
        "desaturation_fade_duration": 0.4
    },
    "moderate": {
        "desaturation_intensity": 0.5,
        "desaturation_alpha_min": 0.3,
        "desaturation_alpha_max": 0.7,
        "desaturation_pulse_speed": 1.0,
        "desaturation_fade_duration": 0.3
    },
    "intense": {
        "desaturation_intensity": 0.8,
        "desaturation_alpha_min": 0.4,
        "desaturation_alpha_max": 0.9,
        "desaturation_pulse_speed": 1.2,
        "desaturation_fade_duration": 0.2
    },
    "gentle": {
        "desaturation_intensity": 0.2,
        "desaturation_alpha_min": 0.1,
        "desaturation_alpha_max": 0.4,
        "desaturation_pulse_speed": 0.6,
        "desaturation_fade_duration": 0.8
    },
    
    # EXPLOSIVE variants - fast, high-contrast highlighting
    "explosive_subtle": {
        "desaturation_intensity": 0.7,
        "desaturation_alpha_min": 0.3,
        "desaturation_alpha_max": 0.7,
        "desaturation_pulse_speed": 1.2,
        "desaturation_fade_duration": 0.15
    },
    "explosive_normal": {
        "desaturation_intensity": 1.0,
        "desaturation_alpha_min": 0.5,
        "desaturation_alpha_max": 1.0,
        "desaturation_pulse_speed": 1.5,
        "desaturation_fade_duration": 0.1
    },
    "explosive_intense": {
        "desaturation_intensity": 1.2,
        "desaturation_alpha_min": 0.7,
        "desaturation_alpha_max": 1.0,
        "desaturation_pulse_speed": 2.0,
        "desaturation_fade_duration": 0.05
    },
    
    # WHISPER variants - very subtle, slow highlighting
    "whisper_subtle": {
        "desaturation_intensity": 0.1,
        "desaturation_alpha_min": 0.02,
        "desaturation_alpha_max": 0.15,
        "desaturation_pulse_speed": 0.3,
        "desaturation_fade_duration": 1.2
    },
    "whisper_normal": {
        "desaturation_intensity": 0.15,
        "desaturation_alpha_min": 0.05,
        "desaturation_alpha_max": 0.25,
        "desaturation_pulse_speed": 0.4,
        "desaturation_fade_duration": 1.0
    },
    "whisper_intense": {
        "desaturation_intensity": 0.25,
        "desaturation_alpha_min": 0.1,
        "desaturation_alpha_max": 0.4,
        "desaturation_pulse_speed": 0.6,
        "desaturation_fade_duration": 0.8
    },
    
    # HEARTBEAT variants - rhythmic pulsing
    "heartbeat_subtle": {
        "desaturation_intensity": 0.4,
        "desaturation_alpha_min": 0.05,
        "desaturation_alpha_max": 0.6,
        "desaturation_pulse_speed": 1.5
    },
    "heartbeat_normal": {
        "desaturation_intensity": 0.6,
        "desaturation_alpha_min": 0.1,
        "desaturation_alpha_max": 0.8,
        "desaturation_pulse_speed": 1.8
    },
    "heartbeat_intense": {
        "desaturation_intensity": 0.8,
        "desaturation_alpha_min": 0.2,
        "desaturation_alpha_max": 1.0,
        "desaturation_pulse_speed": 2.2
    },
    
    # FLICKER variants - rapid, erratic highlighting
    "flicker_subtle": {
        "desaturation_intensity": 0.5,
        "desaturation_alpha_min": 0.1,
        "desaturation_alpha_max": 0.7,
        "desaturation_pulse_speed": 2.0
    },
    "flicker_normal": {
        "desaturation_intensity": 0.7,
        "desaturation_alpha_min": 0.2,
        "desaturation_alpha_max": 0.9,
        "desaturation_pulse_speed": 2.5
    },
    "flicker_intense": {
        "desaturation_intensity": 0.9,
        "desaturation_alpha_min": 0.3,
        "desaturation_alpha_max": 1.0,
        "desaturation_pulse_speed": 3.0
    },
    
    # ETHEREAL variants - dreamy, floating feel
    "ethereal_subtle": {
        "desaturation_intensity": 0.25,
        "desaturation_alpha_min": 0.1,
        "desaturation_alpha_max": 0.4,
        "desaturation_pulse_speed": 0.5
    },
    "ethereal_normal": {
        "desaturation_intensity": 0.4,
        "desaturation_alpha_min": 0.15,
        "desaturation_alpha_max": 0.6,
        "desaturation_pulse_speed": 0.7
    },
    "ethereal_intense": {
        "desaturation_intensity": 0.6,
        "desaturation_alpha_min": 0.25,
        "desaturation_alpha_max": 0.8,
        "desaturation_pulse_speed": 0.9
    },
    
    # LIGHTNING variants - sharp, electric highlighting
    "lightning_subtle": {
        "desaturation_intensity": 0.7,
        "desaturation_alpha_min": 0.4,
        "desaturation_alpha_max": 0.8,
        "desaturation_pulse_speed": 2.5
    },
    "lightning_normal": {
        "desaturation_intensity": 0.9,
        "desaturation_alpha_min": 0.6,
        "desaturation_alpha_max": 1.0,
        "desaturation_pulse_speed": 3.0
    },
    "lightning_intense": {
        "desaturation_intensity": 1.1,
        "desaturation_alpha_min": 0.8,
        "desaturation_alpha_max": 1.0,
        "desaturation_pulse_speed": 3.5
    },
    
    # DREAM variants - soft, mysterious
    "dream_subtle": {
        "desaturation_intensity": 0.2,
        "desaturation_alpha_min": 0.05,
        "desaturation_alpha_max": 0.3,
        "desaturation_pulse_speed": 0.4
    },
    "dream_normal": {
        "desaturation_intensity": 0.3,
        "desaturation_alpha_min": 0.1,
        "desaturation_alpha_max": 0.5,
        "desaturation_pulse_speed": 0.5
    },
    "dream_intense": {
        "desaturation_intensity": 0.5,
        "desaturation_alpha_min": 0.2,
        "desaturation_alpha_max": 0.7,
        "desaturation_pulse_speed": 0.7
    },
    
    # NEON variants - bright, attention-grabbing
    "neon_subtle": {
        "desaturation_intensity": 0.6,
        "desaturation_alpha_min": 0.3,
        "desaturation_alpha_max": 0.7,
        "desaturation_pulse_speed": 1.2
    },
    "neon_normal": {
        "desaturation_intensity": 0.8,
        "desaturation_alpha_min": 0.5,
        "desaturation_alpha_max": 0.9,
        "desaturation_pulse_speed": 1.4
    },
    "neon_intense": {
        "desaturation_intensity": 1.0,
        "desaturation_alpha_min": 0.7,
        "desaturation_alpha_max": 1.0,
        "desaturation_pulse_speed": 1.6
    }
}

init python:
    def apply_desaturation_preset(obj_config, preset_name):
        """Apply a desaturation preset to an object configuration"""
        if preset_name in DESATURATION_PRESETS:
            preset = DESATURATION_PRESETS[preset_name]
            for key, value in preset.items():
                obj_config[key] = value
        return obj_config
