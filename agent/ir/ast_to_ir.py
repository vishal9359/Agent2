"""AST to IR Transformation"""

import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
import networkx as nx

from agent.ir.ir_schema import FunctionIR, ModuleIR, ProjectIR, ControlBlock
from agent.utils import create_unique_id, format_signature

logger = logging.getLogger(__name__)


class ASTToIRTransformer:
    """Transform AST and CFG to Intermediate Representation"""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.functions: Dict[str, FunctionIR] = {}
        self.modules: Dict[str, ModuleIR] = {}
    
    def transform_function(
        self,
        function_ast: Dict[str, Any],
        cfg: nx.DiGraph,
        file_path: Path,
        namespace: Optional[str] = None,
        class_name: Optional[str] = None
    ) -> FunctionIR:
        """Transform function AST and CFG to FunctionIR"""
        func_info = function_ast.get("function", {})
        func_name = func_info.get("name", "unknown")
        
        # Create function ID
        func_id = create_unique_id("func", 
                                  namespace or "",
                                  class_name or "",
                                  func_name,
                                  str(file_path.stem))
        
        # Extract signature
        return_type = func_info.get("return_type", "void")
        params = func_info.get("parameters", [])
        param_list = [f"{p.get('type', '')} {p.get('name', '')}" for p in params]
        signature = format_signature(return_type, func_name, param_list)
        
        # Extract inputs
        inputs = [{"type": p.get("type", ""), "name": p.get("name", "")} 
                 for p in params]
        
        # Extract outputs
        outputs = [return_type] if return_type != "void" else []
        
        # Transform control blocks from CFG
        control_blocks = self._cfg_to_control_blocks(cfg, func_name)
        
        # Extract calls from CFG nodes
        calls = self._extract_calls_from_cfg(cfg)
        
        # Calculate complexity (simplified: count of decision points)
        complexity = self._calculate_complexity(cfg)
        
        func_ir = FunctionIR(
            id=func_id,
            name=func_name,
            signature=signature,
            file=str(file_path),
            line=function_ast.get("start_point", {}).get("row", 0) + 1,
            namespace=namespace,
            class_name=class_name,
            inputs=inputs,
            outputs=outputs,
            control_blocks=control_blocks,
            calls=calls,
            complexity=complexity,
            metadata={
                "is_virtual": func_info.get("is_virtual", False),
                "is_static": func_info.get("is_static", False),
                "is_const": func_info.get("is_const", False)
            }
        )
        
        self.functions[func_id] = func_ir
        return func_ir
    
    def _cfg_to_control_blocks(self, cfg: nx.DiGraph, function_name: str) -> List[ControlBlock]:
        """Convert CFG to control blocks"""
        control_blocks = []
        
        # Find entry node
        entry_nodes = [n for n in cfg.nodes() if cfg.nodes[n].get("type") == "entry"]
        if not entry_nodes:
            return control_blocks
        
        entry_node = entry_nodes[0]
        
        # Build control blocks by traversing CFG
        visited = set()
        blocks = self._traverse_cfg_for_blocks(cfg, entry_node, visited, function_name)
        
        return blocks
    
    def _traverse_cfg_for_blocks(
        self,
        cfg: nx.DiGraph,
        node_id: str,
        visited: set,
        function_name: str
    ) -> List[ControlBlock]:
        """Traverse CFG and build control blocks"""
        if node_id in visited:
            return []
        
        visited.add(node_id)
        node_data = cfg.nodes[node_id]
        node_type = node_data.get("type", "statement")
        
        blocks = []
        
        if node_type == "branch":
            # If statement
            block = ControlBlock(
                block_id=node_id,
                block_type="if",
                label=node_data.get("label", "If"),
                condition=node_data.get("label", "").replace("If: ", ""),
                children=[],
                metadata={"node_type": node_type}
            )
            
            # Process true and false branches
            successors = list(cfg.successors(node_id))
            for succ in successors:
                edge_data = cfg[node_id][succ]
                edge_type = edge_data.get("type", "normal")
                
                if edge_type == "true":
                    block.children.extend(
                        self._traverse_cfg_for_blocks(cfg, succ, visited, function_name)
                    )
                elif edge_type == "false":
                    # False branch
                    false_block = ControlBlock(
                        block_id=f"{node_id}_else",
                        block_type="else",
                        label="Else",
                        children=self._traverse_cfg_for_blocks(cfg, succ, visited, function_name),
                        metadata={}
                    )
                    block.children.append(false_block)
            
            blocks.append(block)
        
        elif node_type == "loop":
            # Loop statement
            block = ControlBlock(
                block_id=node_id,
                block_type="loop",
                label=node_data.get("label", "Loop"),
                children=[],
                metadata={"node_type": node_type}
            )
            
            # Process loop body
            successors = list(cfg.successors(node_id))
            for succ in successors:
                edge_data = cfg[node_id][succ]
                edge_type = edge_data.get("type", "normal")
                
                if edge_type != "loop_exit":
                    block.children.extend(
                        self._traverse_cfg_for_blocks(cfg, succ, visited, function_name)
                    )
            
            blocks.append(block)
        
        elif node_type in ["statement", "return"]:
            # Regular statement
            block = ControlBlock(
                block_id=node_id,
                block_type="sequence",
                label=node_data.get("label", "Statement"),
                children=[],
                metadata={"node_type": node_type}
            )
            blocks.append(block)
            
            # Continue to next nodes
            successors = list(cfg.successors(node_id))
            for succ in successors:
                if cfg.nodes[succ].get("type") != "exit":
                    blocks.extend(
                        self._traverse_cfg_for_blocks(cfg, succ, visited, function_name)
                    )
        
        return blocks
    
    def _extract_calls_from_cfg(self, cfg: nx.DiGraph) -> List[str]:
        """Extract function calls from CFG nodes"""
        calls = []
        
        for node_id, node_data in cfg.nodes(data=True):
            # Check if node metadata contains call information
            if "calls" in node_data:
                calls.extend(node_data["calls"])
        
        return list(set(calls))  # Remove duplicates
    
    def _calculate_complexity(self, cfg: nx.DiGraph) -> int:
        """Calculate cyclomatic complexity"""
        # Simplified: count decision nodes (branches + loops)
        complexity = 1  # Base complexity
        
        for node_id, node_data in cfg.nodes(data=True):
            node_type = node_data.get("type", "")
            if node_type in ["branch", "loop"]:
                complexity += 1
        
        return complexity
    
    def transform_module(
        self,
        module_name: str,
        module_data: Dict[str, Any],
        function_ids: List[str]
    ) -> ModuleIR:
        """Transform module data to ModuleIR"""
        module_id = create_unique_id("module", module_name)
        
        # Determine entry points (main functions, public APIs)
        entry_points = []
        public_api = []
        private_api = []
        
        for func_id in function_ids:
            if func_id in self.functions:
                func = self.functions[func_id]
                # Heuristic: public if in header file or has public visibility
                if "public" in func.file.lower() or "include" in func.file.lower():
                    public_api.append(func_id)
                else:
                    private_api.append(func_id)
                
                # Entry point if it's main or init function
                if func.name in ["main", "Main", "init", "Init", "start", "Start"]:
                    entry_points.append(func_id)
        
        module_ir = ModuleIR(
            id=module_id,
            name=module_name,
            path=str(module_data.get("path", "")),
            responsibilities=[],  # Will be filled by LLM or analysis
            entry_points=entry_points,
            dependencies=list(module_data.get("dependencies", set())),
            public_api=public_api,
            private_api=private_api,
            functions=function_ids,
            metadata={
                "file_count": len(module_data.get("files", [])),
                "public_headers": [str(f) for f in module_data.get("public_headers", [])],
                "source_files": [str(f) for f in module_data.get("source_files", [])]
            }
        )
        
        self.modules[module_id] = module_ir
        return module_ir
    
    def transform_project(
        self,
        project_name: str,
        module_ids: List[str]
    ) -> ProjectIR:
        """Transform project data to ProjectIR"""
        project_id = create_unique_id("project", project_name)
        
        # Determine main flows (entry points across modules)
        main_flows = []
        startup_sequence = []
        
        for module_id in module_ids:
            if module_id in self.modules:
                module = self.modules[module_id]
                if module.entry_points:
                    main_flows.append({
                        "module": module_id,
                        "entry_points": module.entry_points
                    })
                    startup_sequence.extend(module.entry_points)
        
        project_ir = ProjectIR(
            id=project_id,
            name=project_name,
            root_path=str(self.project_root),
            modules=module_ids,
            main_flows=main_flows,
            startup_sequence=startup_sequence,
            metadata={}
        )
        
        return project_ir
    
    def get_function(self, func_id: str) -> Optional[FunctionIR]:
        """Get function IR by ID"""
        return self.functions.get(func_id)
    
    def get_module(self, module_id: str) -> Optional[ModuleIR]:
        """Get module IR by ID"""
        return self.modules.get(module_id)
    
    def get_all_functions(self) -> Dict[str, FunctionIR]:
        """Get all functions"""
        return self.functions
    
    def get_all_modules(self) -> Dict[str, ModuleIR]:
        """Get all modules"""
        return self.modules
