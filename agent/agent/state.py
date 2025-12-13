"""Agent State Schema"""

from typing import TypedDict, List, Dict, Optional, Any
from pathlib import Path


class AgentState(TypedDict):
    """State schema for the LangGraph agent"""
    # User input
    user_query: str
    project_path: Path
    scope: Optional[str]  # Path to specific module/file
    
    # Intent classification
    intent: Optional[str]  # project, module, function, sequence, architecture
    
    # Retrieval
    retrieved_context: List[Dict[str, Any]]
    
    # Graph selection
    selected_graphs: Dict[str, Any]  # {graph_type: graph}
    selected_functions: List[str]  # Function IDs
    selected_modules: List[str]  # Module IDs
    
    # Diagram planning
    diagram_plan: Dict[str, Any]
    diagram_type: Optional[str]  # flowchart, sequence, architecture
    diagram_format: Optional[str]  # plantuml, mermaid
    
    # Output
    diagram_output: Optional[str]
    validation_results: Dict[str, Any]
    explanation: Optional[str]
    
    # Error handling
    error: Optional[str]
    retry_count: int
