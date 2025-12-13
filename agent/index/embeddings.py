"""Embedding Generation using Ollama"""

import logging
from typing import List, Optional
import requests
import json

logger = logging.getLogger(__name__)


class EmbeddingGenerator:
    """Generate embeddings using Ollama"""
    
    def __init__(self, model_name: str = "jina/jina-embeddings", base_url: str = "http://localhost:11434"):
        self.model_name = model_name
        self.base_url = base_url.rstrip('/')
    
    def generate_embedding(self, text: str) -> Optional[List[float]]:
        """Generate embedding for a single text"""
        try:
            url = f"{self.base_url}/api/embeddings"
            payload = {
                "model": self.model_name,
                "prompt": text
            }
            response = requests.post(url, json=payload, timeout=30)
            response.raise_for_status()
            data = response.json()
            if data and "embedding" in data:
                return data["embedding"]
            return None
        except Exception as e:
            logger.error(f"Failed to generate embedding: {e}")
            return None
    
    def generate_embeddings(self, texts: List[str]) -> List[Optional[List[float]]]:
        """Generate embeddings for multiple texts"""
        embeddings = []
        for text in texts:
            embedding = self.generate_embedding(text)
            embeddings.append(embedding)
        return embeddings
    
    def get_embedding_dimension(self) -> int:
        """Get embedding dimension (default for jina embeddings)"""
        # jina/jina-embeddings typically returns 1024 dimensions
        # Test with a dummy text to get actual dimension
        test_embedding = self.generate_embedding("test")
        if test_embedding:
            return len(test_embedding)
        return 1024  # Default fallback
