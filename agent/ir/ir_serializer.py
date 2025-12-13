"""IR Serialization"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any

from agent.ir.ir_schema import FunctionIR, ModuleIR, ProjectIR
from agent.utils import save_json, load_json

logger = logging.getLogger(__name__)


class IRSerializer:
    """Serialize and deserialize IR objects"""
    
    @staticmethod
    def serialize_function(func_ir: FunctionIR) -> Dict[str, Any]:
        """Serialize FunctionIR to dictionary"""
        return func_ir.model_dump()
    
    @staticmethod
    def deserialize_function(data: Dict[str, Any]) -> FunctionIR:
        """Deserialize dictionary to FunctionIR"""
        return FunctionIR(**data)
    
    @staticmethod
    def serialize_module(module_ir: ModuleIR) -> Dict[str, Any]:
        """Serialize ModuleIR to dictionary"""
        return module_ir.model_dump()
    
    @staticmethod
    def deserialize_module(data: Dict[str, Any]) -> ModuleIR:
        """Deserialize dictionary to ModuleIR"""
        return ModuleIR(**data)
    
    @staticmethod
    def serialize_project(project_ir: ProjectIR) -> Dict[str, Any]:
        """Serialize ProjectIR to dictionary"""
        return project_ir.model_dump()
    
    @staticmethod
    def deserialize_project(data: Dict[str, Any]) -> ProjectIR:
        """Deserialize dictionary to ProjectIR"""
        return ProjectIR(**data)
    
    def save_functions(self, functions: Dict[str, FunctionIR], cache_dir: Path) -> None:
        """Save all functions to cache"""
        cache_dir.mkdir(parents=True, exist_ok=True)
        funcs_file = cache_dir / "functions.json"
        
        data = {
            func_id: self.serialize_function(func_ir)
            for func_id, func_ir in functions.items()
        }
        
        save_json(data, funcs_file)
        logger.info(f"Saved {len(functions)} functions to {funcs_file}")
    
    def load_functions(self, cache_dir: Path) -> Dict[str, FunctionIR]:
        """Load all functions from cache"""
        funcs_file = cache_dir / "functions.json"
        data = load_json(funcs_file)
        
        if not data:
            return {}
        
        functions = {}
        for func_id, func_data in data.items():
            try:
                functions[func_id] = self.deserialize_function(func_data)
            except Exception as e:
                logger.warning(f"Failed to deserialize function {func_id}: {e}")
        
        logger.info(f"Loaded {len(functions)} functions from {funcs_file}")
        return functions
    
    def save_modules(self, modules: Dict[str, ModuleIR], cache_dir: Path) -> None:
        """Save all modules to cache"""
        cache_dir.mkdir(parents=True, exist_ok=True)
        modules_file = cache_dir / "modules.json"
        
        data = {
            module_id: self.serialize_module(module_ir)
            for module_id, module_ir in modules.items()
        }
        
        save_json(data, modules_file)
        logger.info(f"Saved {len(modules)} modules to {modules_file}")
    
    def load_modules(self, cache_dir: Path) -> Dict[str, ModuleIR]:
        """Load all modules from cache"""
        modules_file = cache_dir / "modules.json"
        data = load_json(modules_file)
        
        if not data:
            return {}
        
        modules = {}
        for module_id, module_data in data.items():
            try:
                modules[module_id] = self.deserialize_module(module_data)
            except Exception as e:
                logger.warning(f"Failed to deserialize module {module_id}: {e}")
        
        logger.info(f"Loaded {len(modules)} modules from {modules_file}")
        return modules
    
    def save_project(self, project_ir: ProjectIR, cache_dir: Path) -> None:
        """Save project IR to cache"""
        cache_dir.mkdir(parents=True, exist_ok=True)
        project_file = cache_dir / "project.json"
        
        data = self.serialize_project(project_ir)
        save_json(data, project_file)
        logger.info(f"Saved project IR to {project_file}")
    
    def load_project(self, cache_dir: Path) -> Optional[ProjectIR]:
        """Load project IR from cache"""
        project_file = cache_dir / "project.json"
        data = load_json(project_file)
        
        if not data:
            return None
        
        try:
            return self.deserialize_project(data)
        except Exception as e:
            logger.warning(f"Failed to deserialize project: {e}")
            return None
