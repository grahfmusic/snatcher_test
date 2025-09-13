#!/usr/bin/env python3
"""
Migrate shader preset JSON files from v2.0 to v2.1 format.
This script moves vignette settings from effects.crt to effects.color_grade.

Usage:
    python scripts/migrate-vignette-presets.py [--dry-run] [--backup]

Options:
    --dry-run    Show changes without modifying files
    --backup     Create .bak files before modifying
"""

import json
import os
import sys
import argparse
from pathlib import Path

def migrate_preset_data(data):
    """Migrate a preset from v2.0 to v2.1 format."""
    if not isinstance(data, dict):
        return data, False
    
    # Check version - only migrate if < 2.1 or missing version
    version = data.get("version", "1.0")
    try:
        version_num = float(version)
        if version_num >= 2.1:
            return data, False  # Already migrated
    except (ValueError, TypeError):
        pass  # Treat as old version
    
    effects = data.get("effects", {})
    if not isinstance(effects, dict):
        return data, False
    
    crt = effects.get("crt")
    if not isinstance(crt, dict):
        return data, False
    
    # Check if vignette keys exist in CRT
    vignette_keys = ["vignette", "vignette_width", "vignette_feather"]
    has_vignette = any(key in crt for key in vignette_keys)
    
    if not has_vignette:
        return data, False
    
    # Ensure color_grade section exists
    if "color_grade" not in effects:
        effects["color_grade"] = {}
    elif not isinstance(effects["color_grade"], dict):
        effects["color_grade"] = {}
    
    grade = effects["color_grade"]
    changed = False
    
    # Migrate vignette keys with renaming
    if "vignette" in crt:
        grade["vignette_strength"] = crt.pop("vignette")
        changed = True
    if "vignette_width" in crt:
        grade["vignette_width"] = crt.pop("vignette_width")
        changed = True
    if "vignette_feather" in crt:
        grade["vignette_feather"] = crt.pop("vignette_feather")
        changed = True
    
    if changed:
        # Update version to indicate migration completed
        data["version"] = "2.1"
    
    return data, changed

def process_file(file_path, dry_run=False, backup=False):
    """Process a single JSON file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        migrated_data, changed = migrate_preset_data(data)
        
        if changed:
            print(f"{'[DRY-RUN] ' if dry_run else ''}Migrating: {file_path}")
            
            if not dry_run:
                # Create backup if requested
                if backup:
                    backup_path = file_path.with_suffix('.bak' + file_path.suffix)
                    backup_path.write_bytes(file_path.read_bytes())
                    print(f"  Backup created: {backup_path}")
                
                # Write migrated data
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(migrated_data, f, indent=2)
                    f.write('\n')  # Add final newline
        else:
            print(f"No changes needed: {file_path}")
        
        return changed
    
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description='Migrate shader preset files from v2.0 to v2.1')
    parser.add_argument('--dry-run', action='store_true', help='Show changes without modifying files')
    parser.add_argument('--backup', action='store_true', help='Create .bak files before modifying')
    
    args = parser.parse_args()
    
    # Find script directory and game root
    script_dir = Path(__file__).parent
    game_root = script_dir.parent
    
    # Find all JSON files in the preset directories
    preset_dirs = [
        game_root / "game" / "json" / "presets" / "shaders",
        game_root / "game" / "json" / "custom" / "shaders",
    ]
    
    json_files = []
    for preset_dir in preset_dirs:
        if preset_dir.exists():
            json_files.extend(preset_dir.glob("*.json"))
    
    if not json_files:
        print("No JSON files found in preset directories.")
        return 0
    
    print(f"Found {len(json_files)} JSON files to check...")
    
    changed_count = 0
    for json_file in sorted(json_files):
        if process_file(json_file, args.dry_run, args.backup):
            changed_count += 1
    
    print(f"\nSummary: {changed_count} files {'would be ' if args.dry_run else ''}migrated out of {len(json_files)} total.")
    
    if args.dry_run and changed_count > 0:
        print("Run without --dry-run to apply changes.")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
