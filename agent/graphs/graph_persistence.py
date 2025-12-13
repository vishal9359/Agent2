"""Graph Persistence"""

import json
import logging
from pathlib import Path
from typing import Dict, Optional
import networkx as nx

from agent.utils import save_json, load_json, ensure_dir

logger = logging.getLogger(__name__)


class GraphPersistence:
    """Persist and load graphs"""
    
    def save_graph(self, graph: nx.DiGraph, file_path: Path) -> None:
        """Save graph to JSON file"""
        ensure_dir(file_path.parent)
        
        # Convert to JSON-serializable format
        data = {
            "nodes": [
                {
                    "id": node_id,
                    **node_data
                }
                for node_id, node_data in graph.nodes(data=True)
            ],
            "edges": [
                {
                    "source": source,
                    "target": target,
                    **edge_data
                }
                for source, target, edge_data in graph.edges(data=True)
            ]
        }
        
        save_json(data, file_path)
        logger.info(f"Saved graph with {len(data['nodes'])} nodes and {len(data['edges'])} edges to {file_path}")
    
    def load_graph(self, file_path: Path) -> Optional[nx.DiGraph]:
        """Load graph from JSON file"""
        data = load_json(file_path)
        
        if not data:
            return None
        
        graph = nx.DiGraph()
        
        # Add nodes
        for node_data in data.get("nodes", []):
            node_id = node_data.pop("id")
            graph.add_node(node_id, **node_data)
        
        # Add edges
        for edge_data in data.get("edges", []):
            source = edge_data.pop("source")
            target = edge_data.pop("target")
            graph.add_edge(source, target, **edge_data)
        
        logger.info(f"Loaded graph with {len(graph.nodes())} nodes and {len(graph.edges())} edges from {file_path}")
        return graph
    
    def save_graphs(self, graphs: Dict[str, nx.DiGraph], cache_dir: Path) -> None:
        """Save multiple graphs to cache"""
        ensure_dir(cache_dir)
        
        for graph_name, graph in graphs.items():
            graph_file = cache_dir / f"{graph_name}.json"
            self.save_graph(graph, graph_file)
    
    def load_graphs(self, cache_dir: Path) -> Dict[str, nx.DiGraph]:
        """Load multiple graphs from cache"""
        graphs = {}
        
        if not cache_dir.exists():
            return graphs
        
        for graph_file in cache_dir.glob("*.json"):
            graph_name = graph_file.stem
            graph = self.load_graph(graph_file)
            if graph:
                graphs[graph_name] = graph
        
        return graphs
