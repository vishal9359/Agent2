"""Sequence Diagram Generator"""

import logging
from typing import Dict, Any
import networkx as nx

logger = logging.getLogger(__name__)


class SequenceGenerator:
    """Generate sequence diagrams from call graphs"""
    
    def generate(self, graphs: Dict[str, nx.DiGraph], format: str = "plantuml") -> str:
        """Generate sequence diagram from call graph"""
        call_graph = graphs.get("call_graph")
        if not call_graph:
            return ""
        
        if format == "plantuml":
            return self._generate_plantuml(call_graph)
        elif format == "mermaid":
            return self._generate_mermaid(call_graph)
        else:
            return self._generate_plantuml(call_graph)
    
    def _generate_plantuml(self, call_graph: nx.DiGraph) -> str:
        """Generate PlantUML sequence diagram"""
        lines = ["@startuml", "!theme plain", ""]
        
        # Get all participants (functions)
        participants = set()
        for node_id in call_graph.nodes():
            node_data = call_graph.nodes[node_id]
            func_name = node_data.get("name", node_id)
            participants.add(func_name)
        
        # Add participants
        for participant in sorted(participants):
            lines.append(f"participant \"{participant}\"")
        
        lines.append("")
        
        # Add messages (calls)
        for source, target, edge_data in call_graph.edges(data=True):
            source_data = call_graph.nodes[source]
            target_data = call_graph.nodes[target]
            
            source_name = source_data.get("name", source)
            target_name = target_data.get("name", target)
            
            lines.append(f"\"{source_name}\" -> \"{target_name}\": call")
        
        lines.append("@enduml")
        return "\n".join(lines)
    
    def _generate_mermaid(self, call_graph: nx.DiGraph) -> str:
        """Generate Mermaid sequence diagram"""
        lines = ["sequenceDiagram"]
        
        # Get participants
        participants = set()
        for node_id in call_graph.nodes():
            node_data = call_graph.nodes[node_id]
            func_name = node_data.get("name", node_id)
            participants.add(func_name)
        
        # Add participants
        for i, participant in enumerate(sorted(participants)):
            lines.append(f"    participant P{i} as {participant}")
        
        # Create mapping
        participant_map = {name: f"P{i}" for i, name in enumerate(sorted(participants))}
        
        # Add messages
        for source, target, edge_data in call_graph.edges(data=True):
            source_data = call_graph.nodes[source]
            target_data = call_graph.nodes[target]
            
            source_name = source_data.get("name", source)
            target_name = target_data.get("name", target)
            
            source_id = participant_map.get(source_name, source_name)
            target_id = participant_map.get(target_name, target_name)
            
            lines.append(f"    {source_id}->>{target_id}: call")
        
        return "\n".join(lines)
