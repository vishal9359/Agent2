"""Architecture Diagram Generator"""

import logging
from typing import Dict, Any
import networkx as nx

logger = logging.getLogger(__name__)


class ArchitectureGenerator:
    """Generate architecture diagrams from module graphs"""
    
    def generate(self, graphs: Dict[str, nx.DiGraph], format: str = "plantuml") -> str:
        """Generate architecture diagram from module graph"""
        module_graph = graphs.get("module_graph")
        if not module_graph:
            return ""
        
        if format == "plantuml":
            return self._generate_plantuml(module_graph)
        elif format == "mermaid":
            return self._generate_mermaid(module_graph)
        else:
            return self._generate_plantuml(module_graph)
    
    def _generate_plantuml(self, module_graph: nx.DiGraph) -> str:
        """Generate PlantUML component diagram"""
        lines = ["@startuml", "!theme plain", ""]
        
        # Add components (modules)
        for node_id in module_graph.nodes():
            node_data = module_graph.nodes[node_id]
            module_name = node_data.get("name", node_id)
            lines.append(f"component \"{module_name}\" as {node_id.replace('-', '_')}")
        
        lines.append("")
        
        # Add dependencies
        for source, target, edge_data in module_graph.edges(data=True):
            source_clean = source.replace("-", "_")
            target_clean = target.replace("-", "_")
            lines.append(f"{source_clean} --> {target_clean}")
        
        lines.append("@enduml")
        return "\n".join(lines)
    
    def _generate_mermaid(self, module_graph: nx.DiGraph) -> str:
        """Generate Mermaid architecture diagram"""
        lines = ["graph TD"]
        
        # Add nodes (modules)
        for node_id in module_graph.nodes():
            node_data = module_graph.nodes[node_id]
            module_name = node_data.get("name", node_id)
            node_id_clean = node_id.replace("-", "_").replace(":", "_")
            lines.append(f"    {node_id_clean}[\"{module_name}\"]")
        
        # Add edges (dependencies)
        for source, target, edge_data in module_graph.edges(data=True):
            source_clean = source.replace("-", "_").replace(":", "_")
            target_clean = target.replace("-", "_").replace(":", "_")
            lines.append(f"    {source_clean} --> {target_clean}")
        
        return "\n".join(lines)
