#!/usr/bin/env python3
"""
JSON IO Service for Snatchernauts Framework
Provides stable JSON I/O with change detection and atomic writes.
"""

import os
import json
import hashlib
import tempfile
import shutil
from typing import Any, Dict, Optional

class JSONIOService:
    """Service for loading and saving JSON files with change detection."""
    
    def __init__(self):
        self._file_hashes = {}  # Track SHA-256 hashes to detect changes
    
    def load_json(self, file_path: str) -> Optional[Dict[str, Any]]:
        """
        Load JSON from file path.
        
        Args:
            file_path: Path to JSON file
            
        Returns:
            Parsed JSON data as dict, or None if file doesn't exist or error
        """
        try:
            if not os.path.exists(file_path):
                return None
                
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Cache hash for change detection
            content_hash = hashlib.sha256(content.encode('utf-8')).hexdigest()
            self._file_hashes[file_path] = content_hash
            
            # Parse JSON
            data = json.loads(content)
            return data if data is not None else {}
            
        except Exception as e:
            print(f"JSON load error for {file_path}: {e}")
            return None
    
    def save_json_if_changed(self, file_path: str, data: Dict[str, Any], 
                           force: bool = False) -> bool:
        """
        Save JSON data to file, but only if content has changed.
        
        Args:
            file_path: Target file path
            data: Data to save
            force: Force write even if content unchanged
            
        Returns:
            True if file was written, False if no change detected
        """
        try:
            # Generate JSON content with stable formatting
            json_content = self._generate_stable_json(data)
            content_hash = hashlib.sha256(json_content.encode('utf-8')).hexdigest()
            
            # Check if content changed
            cached_hash = self._file_hashes.get(file_path)
            if not force and cached_hash == content_hash:
                return False  # No change, skip write
            
            # Ensure directory exists
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            # Atomic write using temporary file
            temp_path = None
            try:
                with tempfile.NamedTemporaryFile(
                    mode='w', 
                    encoding='utf-8', 
                    suffix='.tmp',
                    dir=os.path.dirname(file_path),
                    delete=False
                ) as tmp_file:
                    tmp_file.write(json_content)
                    temp_path = tmp_file.name
                
                # Atomic rename
                shutil.move(temp_path, file_path)
                temp_path = None
                
                # Update hash cache
                self._file_hashes[file_path] = content_hash
                
                print(f"JSON saved: {file_path}")
                return True
                
            finally:
                # Clean up temp file if rename failed
                if temp_path and os.path.exists(temp_path):
                    try:
                        os.unlink(temp_path)
                    except:
                        pass
            
        except Exception as e:
            print(f"JSON save error for {file_path}: {e}")
            return False
    
    def _generate_stable_json(self, data: Dict[str, Any]) -> str:
        """
        Generate JSON with stable key ordering and formatting.
        
        Args:
            data: Data to convert to JSON
            
        Returns:
            Formatted JSON string
        """
        # Configure JSON encoder for stable output
        json_str = json.dumps(
            data,
            indent=2,
            sort_keys=True,
            ensure_ascii=False,
            separators=(',', ': ')
        )
        
        # Ensure consistent line endings and add final newline
        return json_str.replace('\r\n', '\n') + '\n'
    
    def compute_diff(self, old_data: Dict[str, Any], new_data: Dict[str, Any]) -> str:
        """
        Compute a simple diff description between two data structures.
        
        Args:
            old_data: Previous data
            new_data: New data
            
        Returns:
            Human-readable diff description
        """
        try:
            changes = []
            
            # Check for added/modified keys (recursively for nested objects)
            self._diff_recursive(old_data, new_data, [], changes)
            
            return ", ".join(changes) if changes else "formatting only"
            
        except Exception:
            return "structure changed"
    
    def _diff_recursive(self, old_data: Any, new_data: Any, path: list, changes: list):
        """Recursively compute differences between data structures."""
        if isinstance(old_data, dict) and isinstance(new_data, dict):
            # Compare dictionaries
            for key, new_value in new_data.items():
                current_path = path + [str(key)]
                if key not in old_data:
                    changes.append(f"+ {'.'.join(current_path)}")
                else:
                    self._diff_recursive(old_data[key], new_value, current_path, changes)
            
            # Check for removed keys
            for key in old_data:
                if key not in new_data:
                    current_path = path + [str(key)]
                    changes.append(f"- {'.'.join(current_path)}")
                    
        elif isinstance(old_data, list) and isinstance(new_data, list):
            # Compare lists (simplified - just check length)
            if len(old_data) != len(new_data):
                changes.append(f"~ {'.'.join(path)} (length changed)")
            else:
                # Compare each element
                for i, (old_item, new_item) in enumerate(zip(old_data, new_data)):
                    current_path = path + [f"[{i}]"]
                    self._diff_recursive(old_item, new_item, current_path, changes)
                    
        elif old_data != new_data:
            # Values differ
            changes.append(f"~ {'.'.join(path) if path else 'root'}")

# Global service instance
_json_service = None

def get_json_service() -> JSONIOService:
    """Get the global JSON service instance."""
    global _json_service
    if _json_service is None:
        _json_service = JSONIOService()
    return _json_service

# Convenience functions
def load_json(file_path: str) -> Optional[Dict[str, Any]]:
    """Load JSON file. Convenience wrapper."""
    return get_json_service().load_json(file_path)

def save_json_if_changed(file_path: str, data: Dict[str, Any], force: bool = False) -> bool:
    """Save JSON file if changed. Convenience wrapper."""
    return get_json_service().save_json_if_changed(file_path, data, force)
