"""RAG Indexing with ChromaDB"""

import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
import chromadb
from chromadb.config import Settings

from agent.ir.ir_schema import FunctionIR, ModuleIR, ProjectIR
from agent.index.embeddings import EmbeddingGenerator
from agent.utils import compute_string_hash

logger = logging.getLogger(__name__)


class Indexer:
    """Index IR summaries in ChromaDB"""
    
    def __init__(
        self,
        db_path: Optional[Path] = None,
        collection_prefix: str = "cpp_agent",
        embedding_model: str = "jina/jina-embeddings",
        ollama_base_url: str = "http://localhost:11434"
    ):
        self.collection_prefix = collection_prefix
        self.embedding_generator = EmbeddingGenerator(embedding_model, ollama_base_url)
        
        # Initialize ChromaDB
        if db_path:
            self.client = chromadb.PersistentClient(path=str(db_path))
        else:
            self.client = chromadb.Client(Settings(anonymized_telemetry=False))
        
        # Create collections
        self.functions_collection = self._get_or_create_collection("functions")
        self.modules_collection = self._get_or_create_collection("modules")
        self.flows_collection = self._get_or_create_collection("flows")
        self.architecture_collection = self._get_or_create_collection("architecture")
    
    def _get_or_create_collection(self, name: str):
        """Get or create a ChromaDB collection"""
        collection_name = f"{self.collection_prefix}_{name}"
        try:
            return self.client.get_collection(collection_name)
        except:
            return self.client.create_collection(collection_name)
    
    def index_function(self, func_ir: FunctionIR) -> None:
        """Index a function IR"""
        # Generate summary text
        summary = self._generate_function_summary(func_ir)
        
        # Generate embedding
        embedding = self.embedding_generator.generate_embedding(summary)
        if not embedding:
            logger.warning(f"Failed to generate embedding for function {func_ir.id}")
            return
        
        # Prepare metadata
        metadata = {
            "project": func_ir.file.split("/")[0] if "/" in func_ir.file else "unknown",
            "module": func_ir.file.split("/")[1] if "/" in func_ir.file else "unknown",
            "file": func_ir.file,
            "function": func_ir.name,
            "graph_node_id": func_ir.id,
            "type": "function",
            "signature": func_ir.signature,
            "complexity": str(func_ir.complexity),
            "namespace": func_ir.namespace or "",
            "class": func_ir.class_name or ""
        }
        
        # Add to collection
        self.functions_collection.add(
            ids=[func_ir.id],
            embeddings=[embedding],
            documents=[summary],
            metadatas=[metadata]
        )
        
        logger.debug(f"Indexed function {func_ir.name} ({func_ir.id})")
    
    def index_module(self, module_ir: ModuleIR) -> None:
        """Index a module IR"""
        summary = self._generate_module_summary(module_ir)
        
        embedding = self.embedding_generator.generate_embedding(summary)
        if not embedding:
            logger.warning(f"Failed to generate embedding for module {module_ir.id}")
            return
        
        metadata = {
            "project": module_ir.path.split("/")[0] if "/" in module_ir.path else "unknown",
            "module": module_ir.name,
            "file": "",
            "function": "",
            "graph_node_id": module_ir.id,
            "type": "module",
            "path": module_ir.path,
            "function_count": str(len(module_ir.functions))
        }
        
        self.modules_collection.add(
            ids=[module_ir.id],
            embeddings=[embedding],
            documents=[summary],
            metadatas=[metadata]
        )
        
        logger.debug(f"Indexed module {module_ir.name} ({module_ir.id})")
    
    def index_flow(self, func_ir: FunctionIR, flow_description: str) -> None:
        """Index a control flow description"""
        embedding = self.embedding_generator.generate_embedding(flow_description)
        if not embedding:
            return
        
        flow_id = f"{func_ir.id}_flow"
        metadata = {
            "project": func_ir.file.split("/")[0] if "/" in func_ir.file else "unknown",
            "module": func_ir.file.split("/")[1] if "/" in func_ir.file else "unknown",
            "file": func_ir.file,
            "function": func_ir.name,
            "graph_node_id": func_ir.id,
            "type": "flow"
        }
        
        self.flows_collection.add(
            ids=[flow_id],
            embeddings=[embedding],
            documents=[flow_description],
            metadatas=[metadata]
        )
    
    def index_all(self, functions: Dict[str, FunctionIR], 
                  modules: Dict[str, ModuleIR]) -> None:
        """Index all functions and modules"""
        logger.info(f"Indexing {len(functions)} functions and {len(modules)} modules")
        
        for func_ir in functions.values():
            self.index_function(func_ir)
        
        for module_ir in modules.values():
            self.index_module(module_ir)
        
        logger.info("Indexing complete")
    
    def _generate_function_summary(self, func_ir: FunctionIR) -> str:
        """Generate text summary for function"""
        parts = []
        
        # Signature
        parts.append(f"Function: {func_ir.signature}")
        
        # Location
        parts.append(f"Location: {func_ir.file}:{func_ir.line}")
        
        # Inputs/Outputs
        if func_ir.inputs:
            inputs_str = ", ".join([f"{inp['type']} {inp['name']}" for inp in func_ir.inputs])
            parts.append(f"Inputs: {inputs_str}")
        
        if func_ir.outputs:
            parts.append(f"Outputs: {', '.join(func_ir.outputs)}")
        
        # Control flow description
        if func_ir.control_blocks:
            flow_desc = self._describe_control_blocks(func_ir.control_blocks)
            parts.append(f"Flow: {flow_desc}")
        
        # Calls
        if func_ir.calls:
            parts.append(f"Calls: {', '.join(func_ir.calls)}")
        
        # Complexity
        parts.append(f"Complexity: {func_ir.complexity}")
        
        return " | ".join(parts)
    
    def _generate_module_summary(self, module_ir: ModuleIR) -> str:
        """Generate text summary for module"""
        parts = []
        
        parts.append(f"Module: {module_ir.name}")
        parts.append(f"Path: {module_ir.path}")
        
        if module_ir.responsibilities:
            parts.append(f"Responsibilities: {', '.join(module_ir.responsibilities)}")
        
        if module_ir.entry_points:
            parts.append(f"Entry points: {len(module_ir.entry_points)}")
        
        if module_ir.dependencies:
            parts.append(f"Dependencies: {', '.join(module_ir.dependencies)}")
        
        parts.append(f"Functions: {len(module_ir.functions)}")
        
        return " | ".join(parts)
    
    def _describe_control_blocks(self, blocks: List) -> str:
        """Describe control blocks in text"""
        descriptions = []
        for block in blocks:
            if block.block_type == "if":
                desc = f"if({block.condition or 'condition'})"
            elif block.block_type == "loop":
                desc = "loop"
            elif block.block_type == "sequence":
                desc = block.label
            else:
                desc = block.block_type
            
            if block.children:
                child_desc = self._describe_control_blocks(block.children)
                desc = f"{desc}[{child_desc}]"
            
            descriptions.append(desc)
        
        return "; ".join(descriptions)
