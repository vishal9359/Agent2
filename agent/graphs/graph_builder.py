"""Graph Builder for normalized graph representations"""

import logging
from typing import Dict, List, Optional
import networkx as nx

from agent.ir.ir_schema import FunctionIR, ModuleIR, ProjectIR

logger = logging.getLogger(__name__)


class GraphBuilder:
    """Build normalized graphs from IR"""
    
    def build_cfg_graph(self, func_ir: FunctionIR) -> nx.DiGraph:
        """Build normalized CFG graph from FunctionIR"""
        cfg = nx.DiGraph()
        
        # Add entry node
        entry_id = f"{func_ir.id}_entry"
        cfg.add_node(entry_id, 
                    type="entry",
                    label=f"Entry: {func_ir.name}",
                    function_id=func_ir.id,
                    metadata={})
        
        # Process control blocks
        self._add_control_blocks_to_graph(cfg, func_ir.control_blocks, entry_id, func_ir.id)
        
        # Add exit node
        exit_id = f"{func_ir.id}_exit"
        cfg.add_node(exit_id,
                    type="exit",
                    label=f"Exit: {func_ir.name}",
                    function_id=func_ir.id,
                    metadata={})
        
        # Connect last nodes to exit
        for node_id in cfg.nodes():
            if cfg.out_degree(node_id) == 0 and node_id != exit_id:
                cfg.add_edge(node_id, exit_id, type="normal")
        
        return cfg
    
    def _add_control_blocks_to_graph(
        self,
        graph: nx.DiGraph,
        blocks: List,
        parent_id: str,
        function_id: str
    ) -> str:
        """Add control blocks to graph, return last node ID"""
        current_id = parent_id
        
        for block in blocks:
            block_node_id = f"{function_id}_{block.block_id}"
            
            graph.add_node(block_node_id,
                         type=block.block_type,
                         label=block.label,
                         function_id=function_id,
                         condition=block.condition,
                         metadata=block.metadata)
            
            graph.add_edge(current_id, block_node_id, type="normal")
            
            # Process children
            if block.children:
                last_child_id = self._add_control_blocks_to_graph(
                    graph, block.children, block_node_id, function_id
                )
                current_id = last_child_id
            else:
                current_id = block_node_id
        
        return current_id
    
    def build_call_graph(self, functions: Dict[str, FunctionIR]) -> nx.DiGraph:
        """Build call graph from functions"""
        call_graph = nx.DiGraph()
        
        # Add all functions as nodes
        for func_id, func_ir in functions.items():
            call_graph.add_node(func_id,
                              name=func_ir.name,
                              signature=func_ir.signature,
                              file=func_ir.file,
                              line=func_ir.line,
                              metadata=func_ir.metadata)
        
        # Add call edges
        for func_id, func_ir in functions.items():
            for callee_name in func_ir.calls:
                # Try to find callee function
                callee_id = self._find_function_by_name(callee_name, functions)
                if callee_id:
                    call_graph.add_edge(func_id, callee_id, type="call")
        
        return call_graph
    
    def build_module_graph(self, modules: Dict[str, ModuleIR]) -> nx.DiGraph:
        """Build module dependency graph"""
        module_graph = nx.DiGraph()
        
        # Add all modules as nodes
        for module_id, module_ir in modules.items():
            module_graph.add_node(module_id,
                                name=module_ir.name,
                                path=module_ir.path,
                                metadata=module_ir.metadata)
        
        # Add dependency edges
        for module_id, module_ir in modules.items():
            for dep_name in module_ir.dependencies:
                # Find dependency module
                dep_id = self._find_module_by_name(dep_name, modules)
                if dep_id:
                    module_graph.add_edge(module_id, dep_id, type="depends_on")
        
        return module_graph
    
    def _find_function_by_name(self, name: str, functions: Dict[str, FunctionIR]) -> Optional[str]:
        """Find function ID by name"""
        for func_id, func_ir in functions.items():
            if func_ir.name == name:
                return func_id
        return None
    
    def _find_module_by_name(self, name: str, modules: Dict[str, ModuleIR]) -> Optional[str]:
        """Find module ID by name"""
        for module_id, module_ir in modules.items():
            if module_ir.name == name:
                return module_id
        return None
