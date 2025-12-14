"""AST Extraction using Tree-sitter"""

import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
import tree_sitter
from tree_sitter import Language, Parser

logger = logging.getLogger(__name__)


class ASTExtractor:
    """Extract Abstract Syntax Tree from C++ files using Tree-sitter"""
    
    def __init__(self):
        """Initialize Tree-sitter parser for C++"""
        try:
            # Try to load the C++ language
            # tree-sitter-cpp provides the language function
            try:
                import tree_sitter_cpp
                self.language = Language(tree_sitter_cpp.language())
            except ImportError:
                # This is a fallback - user should install tree-sitter-cpp
                raise ImportError(
                    "tree-sitter-cpp not found. Install with: pip install tree-sitter-cpp"
                )
            
            self.parser = Parser(self.language)
            logger.info("Tree-sitter C++ parser initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Tree-sitter parser: {e}")
            raise
    
    def parse_file(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """Parse a C++ file and extract AST"""
        try:
            with open(file_path, "rb") as f:
                source_code = f.read()
            
            tree = self.parser.parse(source_code)
            root_node = tree.root_node
            
            return self._extract_ast_structure(root_node, source_code, file_path)
        except Exception as e:
            logger.warning(f"Failed to parse {file_path}: {e}")
            return None
    
    def _extract_ast_structure(
        self, 
        node: tree_sitter.Node, 
        source_code: bytes,
        file_path: Path
    ) -> Dict[str, Any]:
        """Extract structured information from AST node"""
        result = {
            "type": node.type,
            "start_byte": node.start_byte,
            "end_byte": node.end_byte,
            "start_point": {"row": node.start_point[0], "column": node.start_point[1]},
            "end_point": {"row": node.end_point[0], "column": node.end_point[1]},
            "text": source_code[node.start_byte:node.end_byte].decode("utf-8", errors="ignore"),
            "children": []
        }
        
        # Extract specific node types
        if node.type == "function_definition":
            result["function"] = self._extract_function(node, source_code)
        elif node.type == "class_specifier":
            result["class"] = self._extract_class(node, source_code)
        elif node.type == "namespace_definition":
            result["namespace"] = self._extract_namespace(node, source_code)
        elif node.type == "declaration":
            result["declaration"] = self._extract_declaration(node, source_code)
        
        # Recursively process children
        for child in node.children:
            child_result = self._extract_ast_structure(child, source_code, file_path)
            if child_result:
                result["children"].append(child_result)
        
        return result
    
    def _extract_function(self, node: tree_sitter.Node, source_code: bytes) -> Dict[str, Any]:
        """Extract function information"""
        func_info = {
            "name": None,
            "return_type": None,
            "parameters": [],
            "body": None,
            "is_virtual": False,
            "is_static": False,
            "is_const": False
        }
        
        # Extract function name
        for child in node.children:
            if child.type == "function_declarator":
                declarator = child
                for subchild in declarator.children:
                    if subchild.type == "identifier":
                        func_info["name"] = source_code[subchild.start_byte:subchild.end_byte].decode("utf-8", errors="ignore")
                    elif subchild.type == "parameter_list":
                        func_info["parameters"] = self._extract_parameters(subchild, source_code)
            elif child.type == "primitive_type" or child.type == "type_identifier":
                func_info["return_type"] = source_code[child.start_byte:child.end_byte].decode("utf-8", errors="ignore")
            elif child.type == "compound_statement":
                func_info["body"] = source_code[child.start_byte:child.end_byte].decode("utf-8", errors="ignore")
            elif child.type == "virtual_specifier":
                func_info["is_virtual"] = True
            elif child.type == "storage_class_specifier":
                text = source_code[child.start_byte:child.end_byte].decode("utf-8", errors="ignore")
                if "static" in text:
                    func_info["is_static"] = True
        
        return func_info
    
    def _extract_class(self, node: tree_sitter.Node, source_code: bytes) -> Dict[str, Any]:
        """Extract class information"""
        class_info = {
            "name": None,
            "base_classes": [],
            "methods": [],
            "fields": []
        }
        
        for child in node.children:
            if child.type == "type_identifier":
                class_info["name"] = source_code[child.start_byte:child.end_byte].decode("utf-8", errors="ignore")
            elif child.type == "base_class_clause":
                # Extract base classes
                for base in child.children:
                    if base.type == "base_class_specifier":
                        base_text = source_code[base.start_byte:base.end_byte].decode("utf-8", errors="ignore")
                        class_info["base_classes"].append(base_text)
            elif child.type == "field_declaration_list":
                # Extract fields and methods
                for member in child.children:
                    if member.type == "function_definition":
                        class_info["methods"].append(self._extract_function(member, source_code))
                    elif member.type == "field_declaration":
                        field_text = source_code[member.start_byte:member.end_byte].decode("utf-8", errors="ignore")
                        class_info["fields"].append(field_text)
        
        return class_info
    
    def _extract_namespace(self, node: tree_sitter.Node, source_code: bytes) -> Dict[str, Any]:
        """Extract namespace information"""
        namespace_info = {
            "name": None,
            "content": []
        }
        
        for child in node.children:
            if child.type == "namespace_identifier":
                namespace_info["name"] = source_code[child.start_byte:child.end_byte].decode("utf-8", errors="ignore")
            elif child.type == "declaration_list":
                # Extract declarations in namespace
                for decl in child.children:
                    decl_text = source_code[decl.start_byte:decl.end_byte].decode("utf-8", errors="ignore")
                    namespace_info["content"].append(decl_text)
        
        return namespace_info
    
    def _extract_declaration(self, node: tree_sitter.Node, source_code: bytes) -> Dict[str, Any]:
        """Extract declaration information"""
        return {
            "text": source_code[node.start_byte:node.end_byte].decode("utf-8", errors="ignore")
        }
    
    def _extract_parameters(self, node: tree_sitter.Node, source_code: bytes) -> List[Dict[str, str]]:
        """Extract function parameters"""
        parameters = []
        
        for child in node.children:
            if child.type == "parameter_declaration":
                param_text = source_code[child.start_byte:child.end_byte].decode("utf-8", errors="ignore")
                # Try to extract type and name
                param_parts = param_text.split()
                if len(param_parts) >= 2:
                    param_type = param_parts[0]
                    param_name = param_parts[-1].rstrip(",")
                    parameters.append({"type": param_type, "name": param_name})
                else:
                    parameters.append({"type": param_text, "name": ""})
        
        return parameters
    
    def extract_functions(self, file_path: Path) -> List[Dict[str, Any]]:
        """Extract all functions from a file"""
        ast = self.parse_file(file_path)
        if not ast:
            return []
        
        functions = []
        self._collect_functions(ast, functions)
        return functions
    
    def _collect_functions(self, node: Dict[str, Any], functions: List[Dict[str, Any]]) -> None:
        """Recursively collect all functions from AST"""
        if "function" in node and node["function"]:
            func = node["function"].copy()
            func["location"] = {
                "file": str(node.get("file_path", "")),
                "line": node["start_point"]["row"] + 1,
                "column": node["start_point"]["column"]
            }
            functions.append(func)
        
        for child in node.get("children", []):
            self._collect_functions(child, functions)
    
    def extract_classes(self, file_path: Path) -> List[Dict[str, Any]]:
        """Extract all classes from a file"""
        ast = self.parse_file(file_path)
        if not ast:
            return []
        
        classes = []
        self._collect_classes(ast, classes)
        return classes
    
    def _collect_classes(self, node: Dict[str, Any], classes: List[Dict[str, Any]]) -> None:
        """Recursively collect all classes from AST"""
        if "class" in node and node["class"]:
            cls = node["class"].copy()
            cls["location"] = {
                "file": str(node.get("file_path", "")),
                "line": node["start_point"]["row"] + 1
            }
            classes.append(cls)
        
        for child in node.get("children", []):
            self._collect_classes(child, classes)
