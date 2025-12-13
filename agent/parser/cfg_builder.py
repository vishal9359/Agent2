"""Control Flow Graph (CFG) Builder"""

import logging
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Any
from collections import defaultdict
import networkx as nx

logger = logging.getLogger(__name__)


class CFGNode:
    """Represents a node in the Control Flow Graph"""
    
    def __init__(self, node_id: str, node_type: str, label: str, 
                 file_path: Optional[Path] = None, line: Optional[int] = None):
        self.id = node_id
        self.type = node_type  # entry, exit, statement, branch, loop, exception, return
        self.label = label
        self.file_path = file_path
        self.line = line
        self.metadata: Dict[str, Any] = {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "id": self.id,
            "type": self.type,
            "label": self.label,
            "file": str(self.file_path) if self.file_path else None,
            "line": self.line,
            "metadata": self.metadata
        }


class CFGBuilder:
    """Build Control Flow Graph from AST"""
    
    def __init__(self):
        self.node_counter = 0
    
    def build_cfg_from_ast(self, ast: Dict[str, Any], function_name: str, 
                           file_path: Path) -> nx.DiGraph:
        """Build CFG from AST for a specific function"""
        cfg = nx.DiGraph()
        
        # Find function node in AST
        func_node = self._find_function_node(ast, function_name)
        if not func_node:
            logger.warning(f"Function {function_name} not found in AST")
            return cfg
        
        # Create entry and exit nodes
        entry_node = CFGNode(
            node_id=f"{function_name}_entry",
            node_type="entry",
            label=f"Entry: {function_name}",
            file_path=file_path,
            line=func_node.get("start_point", {}).get("row", 0) + 1
        )
        exit_node = CFGNode(
            node_id=f"{function_name}_exit",
            node_type="exit",
            label=f"Exit: {function_name}",
            file_path=file_path
        )
        
        cfg.add_node(entry_node.id, **entry_node.to_dict())
        cfg.add_node(exit_node.id, **exit_node.to_dict())
        
        # Process function body
        body_node = self._find_body_node(func_node)
        if body_node:
            last_node_id = self._process_statement_block(
                body_node, cfg, entry_node.id, exit_node.id, function_name, file_path
            )
            # Connect last node to exit
            if last_node_id and last_node_id != exit_node.id:
                cfg.add_edge(last_node_id, exit_node.id, type="normal")
        else:
            # Empty function body
            cfg.add_edge(entry_node.id, exit_node.id, type="normal")
        
        return cfg
    
    def _find_function_node(self, ast: Dict[str, Any], function_name: str) -> Optional[Dict[str, Any]]:
        """Find function node in AST"""
        if "function" in ast and ast.get("function", {}).get("name") == function_name:
            return ast
        
        for child in ast.get("children", []):
            result = self._find_function_node(child, function_name)
            if result:
                return result
        
        return None
    
    def _find_body_node(self, func_node: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Find function body (compound_statement) in function node"""
        for child in func_node.get("children", []):
            if child.get("type") == "compound_statement":
                return child
            # Recursively search
            result = self._find_body_node(child)
            if result:
                return result
        return None
    
    def _process_statement_block(
        self, 
        block_node: Dict[str, Any],
        cfg: nx.DiGraph,
        entry_id: str,
        exit_id: str,
        function_name: str,
        file_path: Path
    ) -> Optional[str]:
        """Process a statement block and return the last node ID"""
        statements = self._extract_statements(block_node)
        
        if not statements:
            return entry_id
        
        current_node_id = entry_id
        
        for stmt in statements:
            stmt_type = stmt.get("type", "")
            
            if stmt_type == "if_statement":
                current_node_id = self._process_if_statement(
                    stmt, cfg, current_node_id, exit_id, function_name, file_path
                )
            elif stmt_type == "for_statement":
                current_node_id = self._process_for_loop(
                    stmt, cfg, current_node_id, exit_id, function_name, file_path
                )
            elif stmt_type == "while_statement":
                current_node_id = self._process_while_loop(
                    stmt, cfg, current_node_id, exit_id, function_name, file_path
                )
            elif stmt_type == "return_statement":
                return_node = self._create_statement_node(
                    stmt, "return", f"Return", function_name, file_path
                )
                cfg.add_node(return_node.id, **return_node.to_dict())
                cfg.add_edge(current_node_id, return_node.id, type="normal")
                cfg.add_edge(return_node.id, exit_id, type="return")
                return return_node.id
            else:
                # Regular statement
                stmt_node = self._create_statement_node(
                    stmt, "statement", self._get_statement_label(stmt), function_name, file_path
                )
                cfg.add_node(stmt_node.id, **stmt_node.to_dict())
                cfg.add_edge(current_node_id, stmt_node.id, type="normal")
                current_node_id = stmt_node.id
        
        return current_node_id
    
    def _extract_statements(self, block_node: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract statements from a block"""
        statements = []
        
        for child in block_node.get("children", []):
            child_type = child.get("type", "")
            if child_type in ["if_statement", "for_statement", "while_statement", 
                            "return_statement", "expression_statement", "declaration"]:
                statements.append(child)
            elif child_type == "compound_statement":
                # Nested block - extract its statements
                statements.extend(self._extract_statements(child))
        
        return statements
    
    def _process_if_statement(
        self,
        if_node: Dict[str, Any],
        cfg: nx.DiGraph,
        entry_id: str,
        exit_id: str,
        function_name: str,
        file_path: Path
    ) -> str:
        """Process if/else statement"""
        # Create condition node
        condition_text = self._extract_condition(if_node)
        condition_node = self._create_statement_node(
            if_node, "branch", f"If: {condition_text}", function_name, file_path
        )
        cfg.add_node(condition_node.id, **condition_node.to_dict())
        cfg.add_edge(entry_id, condition_node.id, type="normal")
        
        # Find then and else blocks
        then_block = None
        else_block = None
        
        for child in if_node.get("children", []):
            if child.get("type") == "compound_statement":
                if then_block is None:
                    then_block = child
                else:
                    else_block = child
            elif child.get("type") == "if_statement":
                # Nested if
                pass
        
        # Process then block
        then_exit = condition_node.id
        if then_block:
            then_exit = self._process_statement_block(
                then_block, cfg, condition_node.id, exit_id, function_name, file_path
            ) or condition_node.id
        
        # Process else block
        else_exit = condition_node.id
        if else_block:
            else_exit = self._process_statement_block(
                else_block, cfg, condition_node.id, exit_id, function_name, file_path
            ) or condition_node.id
        
        # Merge point
        merge_node = self._create_statement_node(
            if_node, "statement", "Merge", function_name, file_path
        )
        merge_node.id = f"{condition_node.id}_merge"
        cfg.add_node(merge_node.id, **merge_node.to_dict())
        
        if then_exit != condition_node.id:
            cfg.add_edge(then_exit, merge_node.id, type="true")
        if else_exit != condition_node.id:
            cfg.add_edge(else_exit, merge_node.id, type="false")
        else:
            # No else block
            cfg.add_edge(condition_node.id, merge_node.id, type="false")
        
        return merge_node.id
    
    def _process_for_loop(
        self,
        for_node: Dict[str, Any],
        cfg: nx.DiGraph,
        entry_id: str,
        exit_id: str,
        function_name: str,
        file_path: Path
    ) -> str:
        """Process for loop"""
        # Create loop entry node
        loop_entry = self._create_statement_node(
            for_node, "loop", "For Loop Entry", function_name, file_path
        )
        loop_entry.id = f"{function_name}_for_{self.node_counter}"
        self.node_counter += 1
        cfg.add_node(loop_entry.id, **loop_entry.to_dict())
        cfg.add_edge(entry_id, loop_entry.id, type="normal")
        
        # Find loop body
        body_block = None
        for child in for_node.get("children", []):
            if child.get("type") == "compound_statement":
                body_block = child
                break
        
        # Process loop body
        body_exit = loop_entry.id
        if body_block:
            body_exit = self._process_statement_block(
                body_block, cfg, loop_entry.id, exit_id, function_name, file_path
            ) or loop_entry.id
            # Back edge
            cfg.add_edge(body_exit, loop_entry.id, type="back_edge")
        
        # Loop exit
        loop_exit = self._create_statement_node(
            for_node, "statement", "For Loop Exit", function_name, file_path
        )
        loop_exit.id = f"{loop_entry.id}_exit"
        cfg.add_node(loop_exit.id, **loop_exit.to_dict())
        cfg.add_edge(loop_entry.id, loop_exit.id, type="loop_exit")
        
        return loop_exit.id
    
    def _process_while_loop(
        self,
        while_node: Dict[str, Any],
        cfg: nx.DiGraph,
        entry_id: str,
        exit_id: str,
        function_name: str,
        file_path: Path
    ) -> str:
        """Process while loop"""
        # Similar to for loop
        loop_entry = self._create_statement_node(
            while_node, "loop", "While Loop Entry", function_name, file_path
        )
        loop_entry.id = f"{function_name}_while_{self.node_counter}"
        self.node_counter += 1
        cfg.add_node(loop_entry.id, **loop_entry.to_dict())
        cfg.add_edge(entry_id, loop_entry.id, type="normal")
        
        body_block = None
        for child in while_node.get("children", []):
            if child.get("type") == "compound_statement":
                body_block = child
                break
        
        body_exit = loop_entry.id
        if body_block:
            body_exit = self._process_statement_block(
                body_block, cfg, loop_entry.id, exit_id, function_name, file_path
            ) or loop_entry.id
            cfg.add_edge(body_exit, loop_entry.id, type="back_edge")
        
        loop_exit = self._create_statement_node(
            while_node, "statement", "While Loop Exit", function_name, file_path
        )
        loop_exit.id = f"{loop_entry.id}_exit"
        cfg.add_node(loop_exit.id, **loop_exit.to_dict())
        cfg.add_edge(loop_entry.id, loop_exit.id, type="loop_exit")
        
        return loop_exit.id
    
    def _create_statement_node(
        self,
        stmt_node: Dict[str, Any],
        node_type: str,
        label: str,
        function_name: str,
        file_path: Path
    ) -> CFGNode:
        """Create a CFG node from statement"""
        node_id = f"{function_name}_stmt_{self.node_counter}"
        self.node_counter += 1
        
        return CFGNode(
            node_id=node_id,
            node_type=node_type,
            label=label,
            file_path=file_path,
            line=stmt_node.get("start_point", {}).get("row", 0) + 1
        )
    
    def _extract_condition(self, if_node: Dict[str, Any]) -> str:
        """Extract condition text from if statement"""
        for child in if_node.get("children", []):
            if child.get("type") == "parenthesized_expression":
                return child.get("text", "condition")[:50]  # Limit length
        return "condition"
    
    def _get_statement_label(self, stmt_node: Dict[str, Any]) -> str:
        """Get label for a statement node"""
        text = stmt_node.get("text", "")
        # Truncate long statements
        if len(text) > 50:
            return text[:47] + "..."
        return text.strip() or "Statement"
