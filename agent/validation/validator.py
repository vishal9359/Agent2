"""Diagram Validator"""

import logging
import re
from typing import Dict, List, Any
import networkx as nx

logger = logging.getLogger(__name__)


class Validator:
    """Validate diagrams and structures"""
    
    def validate_diagram(self, diagram_code: str, format: str = "plantuml") -> Dict[str, Any]:
        """Validate diagram syntax"""
        errors = []
        
        if format == "plantuml":
            errors = self._validate_plantuml(diagram_code)
        elif format == "mermaid":
            errors = self._validate_mermaid(diagram_code)
        
        return {
            "valid": len(errors) == 0,
            "errors": errors
        }
    
    def _validate_plantuml(self, diagram_code: str) -> List[str]:
        """Validate PlantUML syntax"""
        errors = []
        
        # Check for start/end tags
        if "@startuml" not in diagram_code:
            errors.append("Missing @startuml tag")
        if "@enduml" not in diagram_code:
            errors.append("Missing @enduml tag")
        
        # Check for balanced parentheses in if statements
        if_count = diagram_code.count("if (")
        endif_count = diagram_code.count("endif")
        if if_count != endif_count:
            errors.append(f"Unbalanced if/endif: {if_count} if, {endif_count} endif")
        
        # Check for balanced while/endwhile
        while_count = diagram_code.count("while (")
        endwhile_count = diagram_code.count("endwhile")
        if while_count != endwhile_count:
            errors.append(f"Unbalanced while/endwhile: {while_count} while, {endwhile_count} endwhile")
        
        return errors
    
    def _validate_mermaid(self, diagram_code: str) -> List[str]:
        """Validate Mermaid syntax"""
        errors = []
        
        # Check for flowchart/sequence/graph declaration
        if not any(keyword in diagram_code for keyword in ["flowchart", "sequenceDiagram", "graph"]):
            errors.append("Missing diagram type declaration")
        
        # Check for balanced brackets
        open_brackets = diagram_code.count("[")
        close_brackets = diagram_code.count("]")
        if open_brackets != close_brackets:
            errors.append(f"Unbalanced brackets: {open_brackets} open, {close_brackets} close")
        
        return errors
    
    def validate_structure(self, graphs: Dict[str, nx.DiGraph], diagram_code: str) -> Dict[str, Any]:
        """Validate that diagram represents graphs correctly"""
        errors = []
        warnings = []
        
        # Check that all graphs have nodes
        for graph_name, graph in graphs.items():
            if not graph.nodes():
                warnings.append(f"Graph {graph_name} is empty")
        
        # Check for orphan nodes
        for graph_name, graph in graphs.items():
            for node_id in graph.nodes():
                if graph.in_degree(node_id) == 0 and graph.out_degree(node_id) == 0:
                    warnings.append(f"Orphan node {node_id} in graph {graph_name}")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings
        }
    
    def validate_graph_integrity(self, graph: nx.DiGraph) -> Dict[str, Any]:
        """Validate graph integrity"""
        errors = []
        
        # Check for cycles (warn only)
        try:
            cycles = list(nx.simple_cycles(graph))
            if cycles:
                logger.warning(f"Graph contains {len(cycles)} cycles")
        except Exception as e:
            errors.append(f"Failed to check cycles: {e}")
        
        # Check for disconnected components
        if not nx.is_weakly_connected(graph):
            components = list(nx.weakly_connected_components(graph))
            if len(components) > 1:
                warnings = [f"Graph has {len(components)} disconnected components"]
            else:
                warnings = []
        else:
            warnings = []
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings
        }
