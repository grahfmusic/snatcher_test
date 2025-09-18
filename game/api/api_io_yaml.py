#!/usr/bin/env python3
"""
YAML IO Service for Snatchernauts Framework
Provides stable YAML I/O with change detection and atomic writes.
"""

import os
import yaml
import hashlib
import tempfile
import shutil
from typing import Any, Dict, Optional

# Use safe loader/dumper for security
from yaml import SafeLoader, SafeDumper

class CustomYAMLDumper(SafeDumper):
    """Custom YAML dumper with stable key ordering and formatting."""
    
    def write_line_break(self, data=None):
        super().write_line_break(data)
        
    def increase_indent(self, flow=False, indentless=False):
        return super().increase_indent(flow, False)

class YAMLIOService:
    """Service for loading and saving YAML files with change detection."""
    
    def __init__(self):
        self._file_hashes = {}  # Track SHA-256 hashes to detect changes
    
    def load_yaml(self, file_path: str) -> Optional[Dict[str, Any]]:
        """
        Load YAML from file path.
        
        Args:
            file_path: Path to YAML file
            
        Returns:
            Parsed YAML data as dict, or None if file doesn't exist or error
        """
        try:
            if not os.path.exists(file_path):
                return None
                
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Cache hash for change detection
            content_hash = hashlib.sha256(content.encode('utf-8')).hexdigest()
            self._file_hashes[file_path] = content_hash
            
            # Parse YAML
            data = yaml.load(content, Loader=SafeLoader)
            return data if data is not None else {}
            
        except Exception as e:
            print(f"YAML load error for {file_path}: {e}")
            return None
    
    def save_yaml_if_changed(self, file_path: str, data: Dict[str, Any], 
                           force: bool = False) -> bool:
        """
        Save YAML data to file, but only if content has changed.
        
        Args:
            file_path: Target file path
            data: Data to save
            force: Force write even if content unchanged
            
        Returns:
            True if file was written, False if no change detected
        """
        try:
            # Generate YAML content with stable formatting
            yaml_content = self._generate_stable_yaml(data)
            content_hash = hashlib.sha256(yaml_content.encode('utf-8')).hexdigest()
            
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
                    tmp_file.write(yaml_content)
                    temp_path = tmp_file.name
                
                # Atomic rename
                shutil.move(temp_path, file_path)
                temp_path = None
                
                # Update hash cache
                self._file_hashes[file_path] = content_hash
                
                print(f"YAML saved: {file_path}")
                return True
                
            finally:
                # Clean up temp file if rename failed
                if temp_path and os.path.exists(temp_path):
                    try:
                        os.unlink(temp_path)
                    except:
                        pass
            
        except Exception as e:
            print(f"YAML save error for {file_path}: {e}")
            return False
    
    def _generate_stable_yaml(self, data: Dict[str, Any]) -> str:
        """
        Generate YAML with stable key ordering and formatting.
        
        Args:
            data: Data to convert to YAML
            
        Returns:
            Formatted YAML string
        """
        # Configure dumper for stable output
        yaml_str = yaml.dump(
            data,
            Dumper=CustomYAMLDumper,
            default_flow_style=False,
            sort_keys=True,
            indent=2,
            width=80,
            allow_unicode=True
        )
        
        # Ensure consistent line endings
        return yaml_str.replace('\r\n', '\n')
    
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
            
            # Check for added/modified keys
            for key, new_value in new_data.items():
                if key not in old_data:
                    changes.append(f"+ {key}")
                elif old_data[key] != new_value:
                    changes.append(f"~ {key}")
            
            # Check for removed keys
            for key in old_data:
                if key not in new_data:
                    changes.append(f"- {key}")
            
            return ", ".join(changes) if changes else "formatting only"
            
        except Exception:
            return "structure changed"

# Global service instance
_yaml_service = None

def get_yaml_service() -> YAMLIOService:
    """Get the global YAML service instance."""
    global _yaml_service
    if _yaml_service is None:
        _yaml_service = YAMLIOService()
    return _yaml_service

# Convenience functions
def load_yaml(file_path: str) -> Optional[Dict[str, Any]]:
    """Load YAML file. Convenience wrapper."""
    return get_yaml_service().load_yaml(file_path)

def save_yaml_if_changed(file_path: str, data: Dict[str, Any], force: bool = False) -> bool:
    """Save YAML file if changed. Convenience wrapper."""
    return get_yaml_service().save_yaml_if_changed(file_path, data, force)
