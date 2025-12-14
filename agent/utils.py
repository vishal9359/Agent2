"""Utility functions for the C++ Flowchart Agent"""

import hashlib
import json
from pathlib import Path
from typing import Any, Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


def compute_file_hash(file_path: Path) -> str:
    """Compute SHA256 hash of a file"""
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()


def compute_string_hash(content: str) -> str:
    """Compute SHA256 hash of a string"""
    return hashlib.sha256(content.encode()).hexdigest()


def ensure_dir(path: Path) -> Path:
    """Ensure directory exists, create if not"""
    path.mkdir(parents=True, exist_ok=True)
    return path


def load_json(file_path: Path) -> Optional[Dict[str, Any]]:
    """Load JSON file, return None if file doesn't exist"""
    try:
        if file_path.exists():
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception as e:
        logger.warning(f"Failed to load JSON from {file_path}: {e}")
    return None


def save_json(data: Dict[str, Any], file_path: Path) -> None:
    """Save data to JSON file"""
    ensure_dir(file_path.parent)
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def find_cpp_files(root_path: Path, extensions: List[str], exclude_patterns: List[str]) -> List[Path]:
    """Find all C++ files in a directory tree"""
    cpp_files = []
    
    # Normalize extensions (ensure they start with .)
    normalized_extensions = [ext if ext.startswith('.') else f'.{ext}' for ext in extensions]
    
    for file_path in root_path.rglob("*"):
        if not file_path.is_file():
            continue
        
        # Strictly check file extension
        if file_path.suffix.lower() not in normalized_extensions:
            continue
        
        # Check exclude patterns
        should_exclude = False
        file_str = str(file_path)
        for pattern in exclude_patterns:
            # Simple pattern matching (can be enhanced with fnmatch)
            if pattern.replace("**", "").replace("*", "") in file_str:
                should_exclude = True
                break
        
        if not should_exclude:
            cpp_files.append(file_path)
    
    return sorted(cpp_files)


def normalize_path(path: Path) -> str:
    """Normalize path to a consistent string representation"""
    return str(path.resolve())


def get_module_name(file_path: Path, project_root: Path) -> str:
    """Extract module name from file path relative to project root"""
    try:
        rel_path = file_path.relative_to(project_root)
        # Use parent directory as module name
        if len(rel_path.parts) > 1:
            return rel_path.parts[0]
        return "root"
    except ValueError:
        return "unknown"


def sanitize_name(name: str) -> str:
    """Sanitize name for use in IDs and labels"""
    # Replace invalid characters
    sanitized = "".join(c if c.isalnum() or c in ("_", "-") else "_" for c in name)
    return sanitized


def create_unique_id(prefix: str, *parts: str) -> str:
    """Create a unique ID from prefix and parts"""
    combined = "_".join([prefix] + [sanitize_name(str(p)) for p in parts])
    return combined


def format_signature(return_type: str, name: str, params: List[str]) -> str:
    """Format function signature"""
    params_str = ", ".join(params) if params else "void"
    return f"{return_type} {name}({params_str})"
