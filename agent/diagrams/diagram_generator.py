"""Unified Diagram Generator"""

import logging
from typing import Dict, Any
import networkx as nx

from agent.diagrams.flowchart_generator import FlowchartGenerator
from agent.diagrams.sequence_generator import SequenceGenerator
from agent.diagrams.architecture_generator import ArchitectureGenerator

logger = logging.getLogger(__name__)


class DiagramGenerator:
    """Unified diagram generator"""
    
    def __init__(self):
        self.flowchart_gen = FlowchartGenerator()
        self.sequence_gen = SequenceGenerator()
        self.architecture_gen = ArchitectureGenerator()
    
    def generate_flowchart(self, graphs: Dict[str, nx.DiGraph], format: str = "plantuml") -> str:
        """Generate flowchart diagram"""
        return self.flowchart_gen.generate(graphs, format)
    
    def generate_sequence_diagram(self, graphs: Dict[str, nx.DiGraph], format: str = "plantuml") -> str:
        """Generate sequence diagram"""
        return self.sequence_gen.generate(graphs, format)
    
    def generate_architecture_diagram(self, graphs: Dict[str, nx.DiGraph], format: str = "plantuml") -> str:
        """Generate architecture diagram"""
        return self.architecture_gen.generate(graphs, format)
