"""IR Schema Definitions"""

from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field
from pathlib import Path


class ControlBlock(BaseModel):
    """Represents a control flow block"""
    block_id: str
    block_type: str  # if, loop, try, sequence
    label: str
    condition: Optional[str] = None
    children: List[Any] = Field(default_factory=list)  # List[ControlBlock] - using Any to avoid forward ref
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        arbitrary_types_allowed = True


class FunctionIR(BaseModel):
    """Intermediate Representation of a Function"""
    id: str
    name: str
    signature: str
    file: str
    line: int
    namespace: Optional[str] = None
    class_name: Optional[str] = None
    inputs: List[Dict[str, str]] = Field(default_factory=list)  # [{"type": "...", "name": "..."}]
    outputs: List[str] = Field(default_factory=list)  # Return types
    control_blocks: List[ControlBlock] = Field(default_factory=list)
    calls: List[str] = Field(default_factory=list)  # Function names called
    complexity: int = 0  # Cyclomatic complexity
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ModuleIR(BaseModel):
    """Intermediate Representation of a Module"""
    id: str
    name: str
    path: str
    responsibilities: List[str] = Field(default_factory=list)
    entry_points: List[str] = Field(default_factory=list)  # Function IDs
    dependencies: List[str] = Field(default_factory=list)  # Module names
    public_api: List[str] = Field(default_factory=list)  # Function IDs
    private_api: List[str] = Field(default_factory=list)  # Function IDs
    functions: List[str] = Field(default_factory=list)  # Function IDs
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ProjectIR(BaseModel):
    """Intermediate Representation of a Project"""
    id: str
    name: str
    root_path: str
    modules: List[str] = Field(default_factory=list)  # Module IDs
    main_flows: List[Dict[str, Any]] = Field(default_factory=list)
    startup_sequence: List[str] = Field(default_factory=list)  # Function IDs
    metadata: Dict[str, Any] = Field(default_factory=dict)


