# Bloom Color Extraction System
# Global utilities for extracting and caching dominant colors from images
#
# Overview
# - Extracts a representative color from an image for bloom tinting.
# - Caches results to avoid repeated processing.

init python:
    def extract_dominant_color(image_path):
        """Extract the most prominent color from an image"""
        try:
            import pygame
            import colorsys
            import os
            
            # Try to get the full path to the image
            full_path = renpy.loader.get_path(image_path)
            if not full_path or not os.path.exists(full_path):
                return "#ffffff"  # File not found
            
            # Load image with pygame
            surface = pygame.image.load(full_path).convert_alpha()
            width, height = surface.get_size()
            
            # Sample colors from the image
            color_count = {}
            sample_step = max(1, min(width, height) // 10)  # Sample every N pixels
            
            for x in range(0, width, sample_step):
                for y in range(0, height, sample_step):
                    try:
                        pixel = surface.get_at((x, y))
                        # Skip transparent pixels
                        if len(pixel) >= 4 and pixel[3] < 100:
                            continue
                        
                        # Get RGB values
                        r, g, b = pixel[0], pixel[1], pixel[2]
                        
                        # Skip very dark pixels
                        if r + g + b < 150:  # Total RGB less than 150
                            continue
                        
                        # Group similar colors (reduce precision to group similar ones)
                        color_key = (r // 32, g // 32, b // 32)  # 8 levels per channel
                        color_count[color_key] = color_count.get(color_key, 0) + 1
                    except:
                        continue
            
            if not color_count:
                return "#ffffff"  # No colors found
            
            # Find the most common color
            dominant_key = max(color_count.keys(), key=color_count.get)
            r, g, b = dominant_key[0] * 32, dominant_key[1] * 32, dominant_key[2] * 32
            
            # Enhance the color for bloom effect
            # Convert to HSV for better control
            h, s, v = colorsys.rgb_to_hsv(r/255.0, g/255.0, b/255.0)
            
            # Create a highlighting color that contrasts nicely with the object
            # Keep similar hue but adjust saturation and brightness for visibility
            
            # For edge highlighting, we want similar but brighter/more saturated colors
            if v < 0.5:  # Dark objects - make highlight brighter
                v = min(1.0, v + 0.4)  # Significant brightness increase
                s = min(1.0, s * 1.3)  # Boost saturation for visibility
            else:  # Light objects - adjust for contrast
                if s < 0.3:  # Desaturated objects - add some color
                    s = min(1.0, s + 0.3)
                    v = min(1.0, v * 1.1)  # Slight brightness boost
                else:  # Saturated objects - enhance existing color
                    s = min(1.0, s * 1.1)  # Slight saturation boost
                    v = min(0.95, max(0.7, v))  # Ensure good visibility range
            
            # Subtle hue shift for better edge definition (complementary-ish colors)
            h = (h + 0.08) % 1.0  # Small hue shift for distinction
            
            # Convert back to RGB
            r, g, b = colorsys.hsv_to_rgb(h, s, v)
            hex_color = "#{:02x}{:02x}{:02x}".format(int(r * 255), int(g * 255), int(b * 255))
            
            return hex_color
            
        except Exception as e:
            # Silent fallback to white
            return "#ffffff"
    
    def get_bloom_color(image_path, fallback_color="#ffcc88"):
        """Get bloom color for an image, with caching"""
        # Cache colors to avoid recalculating
        if not hasattr(store, '_bloom_color_cache'):
            store._bloom_color_cache = {}
        
        if image_path not in store._bloom_color_cache:
            store._bloom_color_cache[image_path] = extract_dominant_color(image_path)
        
        extracted_color = store._bloom_color_cache[image_path]
        # Use warm golden fallback color if extraction failed
        return extracted_color if extracted_color != "#ffffff" else fallback_color

# Initialize bloom color cache globally
init -1 python:
    # Ensure the bloom color cache is available globally
    store._bloom_color_cache = {}

# Utility function to clear bloom color cache (useful for reloading)
init python:
    def clear_bloom_color_cache():
        """Clear the bloom color cache to force re-extraction"""
        if hasattr(store, '_bloom_color_cache'):
            store._bloom_color_cache.clear()
    
    def preload_bloom_colors(image_paths):
        """Preload bloom colors for a list of image paths"""
        for image_path in image_paths:
            get_bloom_color(image_path)
