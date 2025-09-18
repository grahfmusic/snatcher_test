# Object Factory Utilities
# Functions for creating complete room object configurations
#
# Overview
# - Applies defaults and builders to create normalized object dicts.
# - Computes width/height from original sizes and scale_percent when possible.

init python:
    def create_room_object(x, y, image, description, 
                          scale_percent=100, box_position="auto", float_intensity=0.5,
                          bloom_overrides=None, animation_overrides=None, extra_config=None):
        """Create a complete room object configuration with all settings"""
        # Calculate dimensions if we have the original size info
        if image.split('/')[-1].split('.')[0] in [key for key in ORIGINAL_SIZES.keys()]:
            image_name = image.split('/')[-1].split('.')[0]
            width, height = calc_size(image_name, scale_percent)
        else:
            # Default dimensions if image not in ORIGINAL_SIZES
            width, height = 100, 100
        
        # Base object configuration
        base_config = {
            "x": x, "y": y,
            "scale_percent": scale_percent,
            "width": width,
            "height": height,
            "image": image,
            "description": description,
            "box_position": box_position,
            "float_intensity": float_intensity
        }
        
        # Merge all configurations
        return merge_configs(
            base_config,
            create_bloom_config(bloom_overrides),
            create_animation_config(animation_overrides),
            extra_config or {}
        )
