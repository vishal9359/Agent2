"""Module and Dependency Analysis"""

import logging
import re
from pathlib import Path
from typing import Dict, List, Set, Optional, Tuple, Any
from collections import defaultdict
import networkx as nx

from agent.utils import get_module_name

logger = logging.getLogger(__name__)


class ModuleAnalyzer:
    """Analyze modules and dependencies in a C++ project"""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.modules: Dict[str, Dict[str, Any]] = {}
        self.module_dependencies = nx.DiGraph()
        self.file_to_module: Dict[str, str] = {}
    
    def analyze_project(self, cpp_files: List[Path]) -> None:
        """Analyze the entire project structure"""
        # Group files by module (directory-based)
        for file_path in cpp_files:
            module_name = get_module_name(file_path, self.project_root)
            
            if module_name not in self.modules:
                self.modules[module_name] = {
                    "name": module_name,
                    "path": self.project_root / module_name if module_name != "root" else self.project_root,
                    "files": [],
                    "public_headers": [],
                    "private_headers": [],
                    "source_files": [],
                    "dependencies": set(),
                    "public_api": [],
                    "private_api": []
                }
            
            self.modules[module_name]["files"].append(file_path)
            self.file_to_module[str(file_path)] = module_name
            
            # Categorize files
            if file_path.suffix in [".h", ".hpp"]:
                if "include" in str(file_path) or "public" in str(file_path):
                    self.modules[module_name]["public_headers"].append(file_path)
                else:
                    self.modules[module_name]["private_headers"].append(file_path)
            else:
                self.modules[module_name]["source_files"].append(file_path)
        
        # Analyze dependencies from includes
        for module_name, module_data in self.modules.items():
            self._analyze_module_dependencies(module_name, module_data)
    
    def _analyze_module_dependencies(self, module_name: str, module_data: Dict[str, Any]) -> None:
        """Analyze dependencies for a module"""
        includes = set()
        
        # Extract includes from all files in module
        for file_path in module_data["files"]:
            file_includes = self._extract_includes(file_path)
            includes.update(file_includes)
        
        # Map includes to modules
        for include in includes:
            dep_module = self._resolve_include_to_module(include)
            if dep_module and dep_module != module_name:
                module_data["dependencies"].add(dep_module)
                self.module_dependencies.add_edge(module_name, dep_module)
    
    def _extract_includes(self, file_path: Path) -> List[str]:
        """Extract #include statements from a file"""
        includes = []
        
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
            
            # Match #include patterns
            include_pattern = r'#include\s+[<"]([^>"]+)[>"]'
            matches = re.findall(include_pattern, content)
            includes.extend(matches)
        except Exception as e:
            logger.warning(f"Failed to read {file_path}: {e}")
        
        return includes
    
    def _resolve_include_to_module(self, include_path: str) -> Optional[str]:
        """Resolve include path to module name"""
        # Remove file extension
        include_base = Path(include_path).stem
        
        # Try to find matching file in project
        for module_name, module_data in self.modules.items():
            for file_path in module_data["files"]:
                if file_path.stem == include_base or file_path.name == include_path:
                    return module_name
        
        # Check if it's a system include (skip)
        if include_path.startswith(("<", "/")):
            return None
        
        # Unknown dependency
        return None
    
    def get_module(self, module_name: str) -> Optional[Dict[str, Any]]:
        """Get module information"""
        return self.modules.get(module_name)
    
    def get_module_for_file(self, file_path: Path) -> Optional[str]:
        """Get module name for a file"""
        return self.file_to_module.get(str(file_path))
    
    def get_dependencies(self, module_name: str) -> List[str]:
        """Get dependencies of a module"""
        if module_name in self.module_dependencies:
            return list(self.module_dependencies.successors(module_name))
        return []
    
    def get_dependents(self, module_name: str) -> List[str]:
        """Get modules that depend on this module"""
        if module_name in self.module_dependencies:
            return list(self.module_dependencies.predecessors(module_name))
        return []
    
    def get_module_graph(self) -> nx.DiGraph:
        """Get module dependency graph"""
        return self.module_dependencies
    
    def get_all_modules(self) -> Dict[str, Dict[str, Any]]:
        """Get all modules"""
        return self.modules
    
    def add_function_to_module(self, module_name: str, function_name: str, 
                              is_public: bool = False) -> None:
        """Add a function to module's API"""
        if module_name in self.modules:
            if is_public:
                if function_name not in self.modules[module_name]["public_api"]:
                    self.modules[module_name]["public_api"].append(function_name)
            else:
                if function_name not in self.modules[module_name]["private_api"]:
                    self.modules[module_name]["private_api"].append(function_name)
