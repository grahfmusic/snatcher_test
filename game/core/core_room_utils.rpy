# Room and Image Utilities
# General utilities for room management and image processing
#
# Overview
# - Keeps a small registry of original image sizes and helpers to compute
#   scaled dimensions and infer scale percentages.
# - Used by room editors and display helpers.

# Original image dimensions cache (object or base image name -> size)
define ORIGINAL_SIZES = {
}

init python:
    def calc_size(image_name, scale_percent):
        """Calculate width and height from percentage of original size"""
        if image_name in ORIGINAL_SIZES:
            orig = ORIGINAL_SIZES[image_name]
            width = int(orig["width"] * scale_percent / 100)
            height = int(orig["height"] * scale_percent / 100)
            return width, height
        return 100, 100  # fallback
    
    def add_original_size(image_name, width, height):
        """Add a new image to the original sizes dictionary"""
        ORIGINAL_SIZES[image_name] = {"width": width, "height": height}
    
    def get_original_size(image_name):
        """Get cached original dimensions by name, or a safe default."""
        return ORIGINAL_SIZES.get(image_name, {"width": 100, "height": 100})

    def get_original_size_by_path(image_path):
        """Get original dimensions for a given image path, caching by base name.

        Falls back to 100x100 if the file is not loadable. The cache key uses
        the base filename without extension so it works with object IDs that
        match the image base name (common pattern in this project).
        """
        try:
            base = image_path.split('/')[-1].split('.')[0]
            if base in ORIGINAL_SIZES:
                return ORIGINAL_SIZES[base]
            if renpy.loadable(image_path):
                w, h = renpy.image_size(image_path)
                ORIGINAL_SIZES[base] = {"width": int(w), "height": int(h)}
                return ORIGINAL_SIZES[base]
        except Exception:
            pass
        return {"width": 100, "height": 100}
    
    def calculate_scale_from_dimensions(image_name, target_width, target_height):
        """Calculate what scale percentage would give the target dimensions"""
        if image_name in ORIGINAL_SIZES:
            orig = ORIGINAL_SIZES[image_name]
            scale_x = (target_width / orig["width"]) * 100
            scale_y = (target_height / orig["height"]) * 100
            # Return the average scale or the smaller one to maintain aspect ratio
            return min(scale_x, scale_y)
        return 100.0
