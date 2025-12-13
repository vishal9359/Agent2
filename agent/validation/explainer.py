"""Explainability Output Generator"""

import logging
from typing import Dict, List, Any
import networkx as nx

logger = logging.getLogger(__name__)


class Explainer:
    """Generate explainability output"""
    
    def explain_diagram(
        self,
        diagram_code: str,
        selected_graphs: Dict[str, nx.DiGraph],
        selected_functions: List[str],
        selected_modules: List[str]
    ) -> str:
        """Generate explanation of how diagram was derived"""
        lines = []
        
        lines.append("## Diagram Generation Explanation")
        lines.append("")
        
        # Source information
        lines.append("### Source Information")
        lines.append(f"- Functions analyzed: {len(selected_functions)}")
        lines.append(f"- Modules analyzed: {len(selected_modules)}")
        lines.append(f"- Graphs used: {len(selected_graphs)}")
        lines.append("")
        
        # Graph details
        lines.append("### Graph Details")
        for graph_name, graph in selected_graphs.items():
            lines.append(f"- **{graph_name}**: {len(graph.nodes())} nodes, {len(graph.edges())} edges")
        lines.append("")
        
        # Functions
        if selected_functions:
            lines.append("### Functions")
            for func_id in selected_functions[:10]:  # Limit to first 10
                lines.append(f"- {func_id}")
            if len(selected_functions) > 10:
                lines.append(f"- ... and {len(selected_functions) - 10} more")
            lines.append("")
        
        # Modules
        if selected_modules:
            lines.append("### Modules")
            for module_id in selected_modules:
                lines.append(f"- {module_id}")
            lines.append("")
        
        # Diagram info
        lines.append("### Diagram Information")
        lines.append(f"- Diagram code length: {len(diagram_code)} characters")
        lines.append(f"- Format: {'PlantUML' if '@startuml' in diagram_code else 'Mermaid'}")
        lines.append("")
        
        lines.append("### Generation Method")
        lines.append("This diagram was generated using:")
        lines.append("1. Compiler-grade AST parsing to extract control flow")
        lines.append("2. Control Flow Graph (CFG) construction")
        lines.append("3. Deterministic graph-to-diagram mapping")
        lines.append("4. LLM-assisted labeling for readability")
        lines.append("")
        lines.append("**Note**: All control flow paths are derived from actual code analysis, not inferred by LLM.")
        
        return "\n".join(lines)
