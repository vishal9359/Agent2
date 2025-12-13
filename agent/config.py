"""Configuration management for the C++ Flowchart Agent"""

from pathlib import Path
from typing import Optional
from pydantic import BaseModel, Field


class AgentConfig(BaseModel):
    """Configuration for the C++ Flowchart Agent"""
    
    # Project settings
    project_path: Path
    cache_dir: Path = Field(default_factory=lambda: Path(".agent_cache"))
    
    # Ollama settings
    ollama_base_url: str = "http://localhost:11434"
    llm_model: str = "qwen2.5:latest"
    embedding_model: str = "jina/jina-embeddings"
    
    # ChromaDB settings
    chroma_db_path: Optional[Path] = None
    chroma_collection_prefix: str = "cpp_agent"
    
    # Parsing settings
    cpp_extensions: list[str] = Field(default_factory=lambda: [".cpp", ".hpp", ".h", ".cc", ".cxx"])
    exclude_patterns: list[str] = Field(default_factory=lambda: [
        "**/build/**",
        "**/cmake-build/**",
        "**/.git/**",
        "**/node_modules/**",
        "**/test/**",
        "**/tests/**"
    ])
    
    # Graph settings
    max_graph_nodes: int = 10000
    graph_cache_enabled: bool = True
    
    # Diagram settings
    default_diagram_format: str = "plantuml"  # plantuml or mermaid
    diagram_max_nodes: int = 500
    
    # RAG settings
    embedding_dimension: int = 1024  # jina embeddings dimension
    top_k_retrieval: int = 10
    
    # Validation settings
    validate_diagrams: bool = True
    strict_mode: bool = False
    
    class Config:
        arbitrary_types_allowed = True
