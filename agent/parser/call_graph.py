"""Call Graph Construction"""

import logging
import re
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional, Any
from collections import defaultdict
import networkx as nx

logger = logging.getLogger(__name__)


class CallGraphBuilder:
    """Build call graph from parsed ASTs"""
    
    def __init__(self):
        self.call_graph = nx.DiGraph()
        self.function_locations: Dict[str, Dict[str, Any]] = {}
    
    def add_function(self, function_name: str, file_path: Path, 
                    class_name: Optional[str] = None, 
                    namespace: Optional[str] = None,
                    is_virtual: bool = False,
                    is_static: bool = False) -> None:
        """Add a function to the call graph"""
        # Create fully qualified name
        qualified_name = self._get_qualified_name(function_name, class_name, namespace)
        
        self.call_graph.add_node(qualified_name, 
                                function_name=function_name,
                                class_name=class_name,
                                namespace=namespace,
                                file=str(file_path),
                                is_virtual=is_virtual,
                                is_static=is_static)
        
        self.function_locations[qualified_name] = {
            "file": str(file_path),
            "class": class_name,
            "namespace": namespace,
            "is_virtual": is_virtual,
            "is_static": is_static
        }
    
    def add_call(self, caller: str, callee: str, 
                caller_class: Optional[str] = None,
                caller_namespace: Optional[str] = None,
                call_type: str = "direct") -> None:
        """Add a call relationship"""
        caller_qualified = self._get_qualified_name(caller, caller_class, caller_namespace)
        callee_qualified = callee  # Assume callee is already qualified or will be resolved
        
        if not self.call_graph.has_node(caller_qualified):
            self.call_graph.add_node(caller_qualified)
        
        if not self.call_graph.has_node(callee_qualified):
            self.call_graph.add_node(callee_qualified)
        
        # Add edge if not exists, or update call type
        if self.call_graph.has_edge(caller_qualified, callee_qualified):
            # Update metadata
            edge_data = self.call_graph[caller_qualified][callee_qualified]
            if "call_types" not in edge_data:
                edge_data["call_types"] = []
            if call_type not in edge_data["call_types"]:
                edge_data["call_types"].append(call_type)
        else:
            self.call_graph.add_edge(caller_qualified, callee_qualified, 
                                    call_type=call_type,
                                    call_types=[call_type])
    
    def extract_calls_from_ast(self, ast: Dict[str, Any], 
                               function_name: str,
                               file_path: Path,
                               class_name: Optional[str] = None,
                               namespace: Optional[str] = None) -> None:
        """Extract function calls from AST"""
        caller_qualified = self._get_qualified_name(function_name, class_name, namespace)
        
        # Find function node
        func_node = self._find_function_in_ast(ast, function_name)
        if not func_node:
            return
        
        # Extract calls from function body
        calls = self._extract_calls_from_node(func_node)
        
        for call in calls:
            callee_name = call.get("name")
            call_type = call.get("type", "direct")
            
            if callee_name:
                # Try to resolve callee (simple heuristic)
                resolved_callee = self._resolve_callee(callee_name, file_path, class_name, namespace)
                self.add_call(caller_qualified, resolved_callee, 
                            caller_class=class_name,
                            caller_namespace=namespace,
                            call_type=call_type)
    
    def _find_function_in_ast(self, ast: Dict[str, Any], function_name: str) -> Optional[Dict[str, Any]]:
        """Find function node in AST"""
        if "function" in ast and ast.get("function", {}).get("name") == function_name:
            return ast
        
        for child in ast.get("children", []):
            result = self._find_function_in_ast(child, function_name)
            if result:
                return result
        
        return None
    
    def _extract_calls_from_node(self, node: Dict[str, Any]) -> List[Dict[str, str]]:
        """Extract function calls from a node"""
        calls = []
        
        node_type = node.get("type", "")
        if node_type == "call_expression":
            # Extract function name from call
            func_name = self._extract_function_name_from_call(node)
            if func_name:
                calls.append({"name": func_name, "type": "direct"})
        elif node_type == "field_expression":
            # Method call
            func_name = self._extract_method_name_from_call(node)
            if func_name:
                calls.append({"name": func_name, "type": "method"})
        
        # Recursively search children
        for child in node.get("children", []):
            calls.extend(self._extract_calls_from_node(child))
        
        return calls
    
    def _extract_function_name_from_call(self, call_node: Dict[str, Any]) -> Optional[str]:
        """Extract function name from call expression"""
        # Look for identifier in call expression
        for child in call_node.get("children", []):
            if child.get("type") == "identifier":
                return child.get("text", "").strip()
            elif child.get("type") == "qualified_identifier":
                # Extract from qualified name
                text = child.get("text", "")
                parts = text.split("::")
                return parts[-1] if parts else None
        
        return None
    
    def _extract_method_name_from_call(self, field_node: Dict[str, Any]) -> Optional[str]:
        """Extract method name from field expression"""
        # Field expression: object.method()
        for child in field_node.get("children", []):
            if child.get("type") == "field_identifier":
                return child.get("text", "").strip()
        
        return None
    
    def _resolve_callee(self, callee_name: str, file_path: Path,
                       class_name: Optional[str] = None,
                       namespace: Optional[str] = None) -> str:
        """Resolve callee to qualified name (best-effort)"""
        # Try exact match first
        if class_name:
            qualified = f"{class_name}::{callee_name}"
            if qualified in self.function_locations:
                return qualified
        
        if namespace:
            qualified = f"{namespace}::{callee_name}"
            if qualified in self.function_locations:
                return qualified
        
        # Try simple name
        if callee_name in self.function_locations:
            return callee_name
        
        # Return as-is (will be resolved later or marked as external)
        return callee_name
    
    def _get_qualified_name(self, function_name: str, 
                           class_name: Optional[str] = None,
                           namespace: Optional[str] = None) -> str:
        """Get fully qualified function name"""
        parts = []
        if namespace:
            parts.append(namespace)
        if class_name:
            parts.append(class_name)
        parts.append(function_name)
        return "::".join(parts)
    
    def get_call_graph(self) -> nx.DiGraph:
        """Get the call graph"""
        return self.call_graph
    
    def get_callees(self, function_name: str) -> List[str]:
        """Get all functions called by a function"""
        if function_name in self.call_graph:
            return list(self.call_graph.successors(function_name))
        return []
    
    def get_callers(self, function_name: str) -> List[str]:
        """Get all functions that call a function"""
        if function_name in self.call_graph:
            return list(self.call_graph.predecessors(function_name))
        return []
    
    def get_topological_order(self) -> List[str]:
        """Get functions in topological order (callers before callees)"""
        try:
            return list(nx.topological_sort(self.call_graph))
        except nx.NetworkXError:
            # Graph has cycles
            return list(self.call_graph.nodes())
