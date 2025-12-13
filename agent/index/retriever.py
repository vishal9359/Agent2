"""RAG Retriever"""

import logging
from typing import List, Dict, Any, Optional
import chromadb

from agent.index.embeddings import EmbeddingGenerator

logger = logging.getLogger(__name__)


class Retriever:
    """Retrieve relevant context from ChromaDB"""
    
    def __init__(
        self,
        indexer: "Indexer",
        top_k: int = 10
    ):
        self.indexer = indexer
        self.top_k = top_k
        self.embedding_generator = indexer.embedding_generator
    
    def retrieve(self, query: str, collection_type: str = "functions", 
                filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Retrieve relevant documents"""
        # Get collection
        collection = self._get_collection(collection_type)
        if not collection:
            return []
        
        # Generate query embedding
        query_embedding = self.embedding_generator.generate_embedding(query)
        if not query_embedding:
            logger.warning("Failed to generate query embedding")
            return []
        
        # Build where clause for filters
        where = filters if filters else None
        
        # Query
        try:
            results = collection.query(
                query_embeddings=[query_embedding],
                n_results=self.top_k,
                where=where
            )
            
            # Format results
            retrieved = []
            if results and "ids" in results and results["ids"]:
                for i in range(len(results["ids"][0])):
                    retrieved.append({
                        "id": results["ids"][0][i],
                        "document": results["documents"][0][i] if "documents" in results else "",
                        "metadata": results["metadatas"][0][i] if "metadatas" in results else {},
                        "distance": results["distances"][0][i] if "distances" in results else 0.0
                    })
            
            return retrieved
        except Exception as e:
            logger.error(f"Retrieval failed: {e}")
            return []
    
    def retrieve_functions(self, query: str, 
                          module: Optional[str] = None,
                          file: Optional[str] = None) -> List[Dict[str, Any]]:
        """Retrieve relevant functions"""
        filters = {}
        if module:
            filters["module"] = module
        if file:
            filters["file"] = file
        
        return self.retrieve(query, "functions", filters if filters else None)
    
    def retrieve_modules(self, query: str) -> List[Dict[str, Any]]:
        """Retrieve relevant modules"""
        return self.retrieve(query, "modules")
    
    def retrieve_flows(self, query: str, function: Optional[str] = None) -> List[Dict[str, Any]]:
        """Retrieve relevant flows"""
        filters = {}
        if function:
            filters["function"] = function
        
        return self.retrieve(query, "flows", filters if filters else None)
    
    def _get_collection(self, collection_type: str):
        """Get collection by type"""
        if collection_type == "functions":
            return self.indexer.functions_collection
        elif collection_type == "modules":
            return self.indexer.modules_collection
        elif collection_type == "flows":
            return self.indexer.flows_collection
        elif collection_type == "architecture":
            return self.indexer.architecture_collection
        return None
