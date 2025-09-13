#!/usr/bin/env python3
"""
Ensure all shader preset JSON files have vignette settings in color_grade
and are version 2.1.

This script adds default vignette settings to files that are missing them
and updates version numbers from 2.0 to 2.1.
"""

import json
import sys
import pathlib
from pathlib import Path

DEFAULTS = {
    "vignette_strength": 0.25,
    "vignette_width": 0.8,
    "vignette_feather": 0.2,
}

def patch_file(path):
    """Add missing vignette settings and update version."""
    p = pathlib.Path(path)
    
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
        changed = False
        
        # Ensure effects section exists
        if "effects" not in data:
            data["effects"] = {}
            changed = True
        
        # Ensure color_grade section exists
        effects = data["effects"]
        if "color_grade" not in effects:
            effects["color_grade"] = {}
            changed = True
        
        cg = effects["color_grade"]
        
        # Add missing vignette settings
        for key, default_value in DEFAULTS.items():
            if key not in cg:
                cg[key] = default_value
                changed = True
                print(f"  Added {key}: {default_value}")
        
        # Update version to 2.1 if it's 2.0
        if data.get("version") == "2.0":
            data["version"] = "2.1"
            changed = True
            print(f"  Updated version: 2.0 -> 2.1")
        
        if changed:
            print(f"Patching: {path}")
            # Write back with consistent formatting
            p.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
            return True
        else:
            print(f"No changes needed: {path}")
            return False
            
    except Exception as e:
        print(f"Error processing {path}: {e}")
        return False

def main():
    if len(sys.argv) < 2:
        print("Usage: python ensure-grade-vignette.py <file1.json> [file2.json] ...")
        print("   or: python ensure-grade-vignette.py --all")
        sys.exit(1)
    
    if sys.argv[1] == "--all":
        # Process all JSON files in the shader directories
        base_dir = Path(__file__).parent.parent
        dirs = [
            base_dir / "game" / "json" / "presets" / "shaders",
            base_dir / "game" / "json" / "custom" / "shaders",
        ]
        
        json_files = []
        for preset_dir in dirs:
            if preset_dir.exists():
                json_files.extend(preset_dir.glob("*.json"))
        
        if not json_files:
            print("No JSON files found in shader directories.")
            return 0
        
        print(f"Found {len(json_files)} JSON files to check...")
        changed_count = 0
        for json_file in sorted(json_files):
            if patch_file(json_file):
                changed_count += 1
        
        print(f"\nSummary: {changed_count} files patched out of {len(json_files)} total.")
    else:
        # Process individual files
        changed_count = 0
        for file_path in sys.argv[1:]:
            if patch_file(file_path):
                changed_count += 1
        
        print(f"\nSummary: {changed_count} files patched.")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
