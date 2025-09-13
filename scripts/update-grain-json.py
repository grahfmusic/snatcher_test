#!/usr/bin/env python3

import json
import os
import glob
import shutil
from datetime import datetime

def update_grain_json_files():
    """Add downscale parameter to existing grain JSON preset files."""
    
    # Define directories to scan
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    json_dirs = [
        os.path.join(base_dir, "game", "json", "presets", "shaders"),
        os.path.join(base_dir, "game", "json", "custom", "shaders")
    ]
    
    updated_files = []
    errors = []
    
    print("=== Grain JSON Downscale Parameter Update ===")
    print(f"Scan time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    for json_dir in json_dirs:
        if not os.path.exists(json_dir):
            print(f"Directory not found: {json_dir}")
            continue
            
        print(f"Scanning: {json_dir}")
        
        # Find grain JSON files
        pattern = os.path.join(json_dir, "grain_*.json")
        grain_files = glob.glob(pattern)
        
        for file_path in sorted(grain_files):
            try:
                # Read existing file
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Check if it has a grain effect block
                effects = data.get("effects", {})
                grain_block = effects.get("grain")
                
                if grain_block and isinstance(grain_block, dict):
                    # Check if downscale already exists
                    if "downscale" not in grain_block:
                        # Add downscale parameter with default value
                        grain_block["downscale"] = 2.0
                        
                        # Create backup
                        backup_path = f"{file_path}.bak"
                        shutil.copy2(file_path, backup_path)
                        
                        # Write updated file
                        with open(file_path, 'w', encoding='utf-8') as f:
                            json.dump(data, f, indent=2)
                        
                        updated_files.append(file_path)
                        print(f"  ✓ Updated: {os.path.basename(file_path)}")
                    else:
                        print(f"  - Skipped: {os.path.basename(file_path)} (already has downscale)")
                else:
                    print(f"  - Skipped: {os.path.basename(file_path)} (no grain block)")
                    
            except Exception as e:
                errors.append(f"{file_path}: {e}")
                print(f"  ✗ Error: {os.path.basename(file_path)} - {e}")
    
    print()
    print("=== Summary ===")
    print(f"Updated files: {len(updated_files)}")
    print(f"Errors: {len(errors)}")
    
    if updated_files:
        print("\nUpdated files:")
        for f in updated_files:
            print(f"  - {os.path.basename(f)}")
    
    if errors:
        print("\nErrors:")
        for e in errors:
            print(f"  - {e}")
    
    return len(updated_files) > 0

if __name__ == "__main__":
    update_grain_json_files()
