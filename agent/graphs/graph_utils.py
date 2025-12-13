"""Graph Utilities"""

import logging
from typing import List, Set, Optional
import networkx as nx

logger = logging.getLogger(__name__)


class GraphUtils:
    """Utility functions for graph operations"""
    
    @staticmethod
    def get_entry_nodes(graph: nx.DiGraph) -> List[str]:
        """Get entry nodes (nodes with no incoming edges)"""
        return [node for node in graph.nodes() if graph.in_degree(node) == 0]
    
    @staticmethod
    def get_exit_nodes(graph: nx.DiGraph) -> List[str]:
        """Get exit nodes (nodes with no outgoing edges)"""
        return [node for node in graph.nodes() if graph.out_degree(node) == 0]
    
    @staticmethod
    def get_reachable_nodes(graph: nx.DiGraph, start_node: str) -> Set[str]:
        """Get all nodes reachable from start_node"""
        if start_node not in graph:
            return set()
        
        reachable = set()
        visited = set()
        
        def dfs(node):
            if node in visited:
                return
            visited.add(node)
            reachable.add(node)
            for successor in graph.successors(node):
                dfs(successor)
        
        dfs(start_node)
        return reachable
    
    @staticmethod
    def prune_graph(graph: nx.DiGraph, keep_nodes: Set[str]) -> nx.DiGraph:
        """Prune graph to keep only specified nodes"""
        pruned = graph.subgraph(keep_nodes).copy()
        return pruned
    
    @staticmethod
    def get_subgraph_by_scope(
        graph: nx.DiGraph,
        start_nodes: List[str],
        max_depth: Optional[int] = None
    ) -> nx.DiGraph:
        """Get subgraph starting from given nodes, limited by depth"""
        if max_depth is None:
            max_depth = float('inf')
        
        nodes_to_keep = set()
        
        def collect_nodes(node, depth):
            if depth > max_depth or node in nodes_to_keep:
                return
            nodes_to_keep.add(node)
            if depth < max_depth:
                for successor in graph.successors(node):
                    collect_nodes(successor, depth + 1)
        
        for start_node in start_nodes:
            if start_node in graph:
                collect_nodes(start_node, 0)
        
        return GraphUtils.prune_graph(graph, nodes_to_keep)
    
    @staticmethod
    def validate_graph(graph: nx.DiGraph) -> tuple[bool, List[str]]:
        """Validate graph structure, return (is_valid, errors)"""
        errors = []
        
        # Check for orphan nodes (no connections)
        for node in graph.nodes():
            if graph.in_degree(node) == 0 and graph.out_degree(node) == 0:
                errors.append(f"Orphan node: {node}")
        
        # Check for cycles (warn only, not error)
        try:
            cycles = list(nx.simple_cycles(graph))
            if cycles:
                logger.warning(f"Graph contains {len(cycles)} cycles")
        except Exception as e:
            errors.append(f"Failed to check cycles: {e}")
        
        return len(errors) == 0, errors
