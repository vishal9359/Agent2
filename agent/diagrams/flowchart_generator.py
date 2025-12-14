"""Flowchart Generator"""

import logging
from typing import Dict, Any
import networkx as nx

logger = logging.getLogger(__name__)


class FlowchartGenerator:
    """Generate flowcharts from CFG graphs"""
    
    def generate(self, graphs: Dict[str, nx.DiGraph], format: str = "plantuml") -> str:
        """Generate flowchart from CFG graphs"""
        if format == "plantuml":
            return self._generate_plantuml(graphs)
        elif format == "mermaid":
            return self._generate_mermaid(graphs)
        else:
            return self._generate_plantuml(graphs)
    
    def _generate_plantuml(self, graphs: Dict[str, nx.DiGraph]) -> str:
        """Generate PlantUML flowchart"""
        lines = ["@startuml", "!theme plain", ""]
        
        for graph_name, graph in graphs.items():
            if not graph.nodes():
                continue
            
            # Add title
            lines.append(f"title {graph_name}")
            lines.append("")
            
            # Map nodes to PlantUML shapes
            node_map = {}
            for i, node_id in enumerate(graph.nodes()):
                node_data = graph.nodes[node_id]
                node_type = node_data.get("type", "statement")
                label = node_data.get("label", node_id)
                
                # Escape special characters
                label = label.replace('"', '\\"').replace('\n', ' ')
                
                # Choose shape based on type
                if node_type == "entry":
                    node_map[node_id] = f"start_{i}"
                    lines.append(f"start")
                    lines.append(f":{label};")
                elif node_type == "exit":
                    node_map[node_id] = f"stop_{i}"
                    lines.append(f"stop")
                    lines.append(f":{label};")
                elif node_type == "branch":
                    node_map[node_id] = f"if_{i}"
                    lines.append(f"if ({label}) then (yes)")
                elif node_type == "loop":
                    node_map[node_id] = f"loop_{i}"
                    lines.append(f"while ({label}) is (yes)")
                elif node_type == "return":
                    node_map[node_id] = f"return_{i}"
                    lines.append(f":{label};")
                else:
                    node_map[node_id] = f"node_{i}"
                    lines.append(f":{label};")
            
            lines.append("")
            
            # Add edges
            for source, target, edge_data in graph.edges(data=True):
                source_id = node_map.get(source, source)
                target_id = node_map.get(target, target)
                label = edge_data.get("label", "")
                
                if label:
                    label = label.replace('"', '\\"')
                    lines.append(f"{source_id} --> {target_id} : {label}")
                else:
                    lines.append(f"{source_id} --> {target_id}")
            
            lines.append("")
        
        lines.append("@enduml")
        return "\n".join(lines)
    
    def _generate_mermaid(self, graphs: Dict[str, nx.DiGraph]) -> str:
        """Generate Mermaid flowchart"""
        lines = ["flowchart TD"]
        
        for graph_name, graph in graphs.items():
            if not graph.nodes():
                continue
            
            lines.append(f"    %% {graph_name}")
            
            # Map nodes
            node_map = {}
            for i, node_id in enumerate(graph.nodes()):
                node_data = graph.nodes[node_id]
                node_type = node_data.get("type", "statement")
                label = node_data.get("label", node_id)
                
                # Escape and format label
                label = label.replace('"', '&quot;').replace('\n', ' ')
                node_id_clean = node_id.replace("-", "_").replace(":", "_")
                node_map[node_id] = node_id_clean
                
                # Choose shape
                if node_type == "entry":
                    lines.append(f"    {node_id_clean}([{label}])")
                elif node_type == "exit":
                    lines.append(f"    {node_id_clean}([{label}])")
                elif node_type == "branch":
                    lines.append(f"    {node_id_clean}{{{label}}}")
                elif node_type == "loop":
                    lines.append(f"    {node_id_clean}(({label}))")
                else:
                    lines.append(f"    {node_id_clean}[{label}]")
            
            # Add edges
            for source, target, edge_data in graph.edges(data=True):
                source_id = node_map.get(source, source.replace("-", "_").replace(":", "_"))
                target_id = node_map.get(target, target.replace("-", "_").replace(":", "_"))
                label = edge_data.get("label", "")
                
                if label:
                    label = label.replace('"', '&quot;')
                    lines.append(f"    {source_id} -->|{label}| {target_id}")
                else:
                    lines.append(f"    {source_id} --> {target_id}")
            
            lines.append("")
        
        return "\n".join(lines)
