"""Main Entry Point for C++ Flowchart Agent"""

import logging
from pathlib import Path
from typing import Optional, Dict, Any
from tqdm import tqdm

from agent.config import AgentConfig
from agent.utils import find_cpp_files, ensure_dir, compute_file_hash
from agent.parser import ASTExtractor, CFGBuilder, CallGraphBuilder, ModuleAnalyzer
from agent.ir import ASTToIRTransformer, IRSerializer
from agent.graphs import GraphBuilder, GraphPersistence
from agent.index import Indexer, Retriever
from agent.agent import create_agent_graph
from agent.diagrams import DiagramGenerator
from agent.validation import Validator, Explainer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CppFlowchartAgent:
    """Main agent class for C++ flowchart generation"""
    
    def __init__(
        self,
        project_path: str | Path,
        ollama_base_url: str = "http://localhost:11434",
        llm_model: str = "qwen2.5:latest",
        embedding_model: str = "jina/jina-embeddings",
        cache_dir: Optional[str | Path] = None
    ):
        """Initialize the agent"""
        self.config = AgentConfig(
            project_path=Path(project_path),
            ollama_base_url=ollama_base_url,
            llm_model=llm_model,
            embedding_model=embedding_model
        )
        
        if cache_dir:
            self.config.cache_dir = Path(cache_dir)
        else:
            self.config.cache_dir = self.config.project_path / ".agent_cache"
        
        ensure_dir(self.config.cache_dir)
        
        # Initialize components
        logger.info("Initializing components...")
        self.ast_extractor = ASTExtractor()
        self.cfg_builder = CFGBuilder()
        self.call_graph_builder = CallGraphBuilder()
        self.module_analyzer = ModuleAnalyzer(self.config.project_path)
        
        self.ir_transformer = ASTToIRTransformer(self.config.project_path)
        self.ir_serializer = IRSerializer()
        
        self.graph_builder = GraphBuilder()
        self.graph_persistence = GraphPersistence()
        
        # Initialize indexer and retriever
        db_path = self.config.cache_dir / "chroma_db"
        self.indexer = Indexer(
            db_path=db_path,
            collection_prefix=self.config.chroma_collection_prefix,
            embedding_model=self.config.embedding_model,
            ollama_base_url=self.config.ollama_base_url
        )
        self.retriever = Retriever(self.indexer, top_k=self.config.top_k_retrieval)
        
        self.diagram_generator = DiagramGenerator()
        self.validator = Validator()
        self.explainer = Explainer()
        
        # Cached data
        self.functions: Dict[str, Any] = {}
        self.modules: Dict[str, Any] = {}
        self.project_ir = None
        
        logger.info("Agent initialized successfully")
    
    def analyze_project(self, force_rebuild: bool = False) -> None:
        """Analyze the C++ project"""
        logger.info(f"Analyzing project: {self.config.project_path}")
        
        # Check cache
        if not force_rebuild:
            self.functions = self.ir_serializer.load_functions(self.config.cache_dir)
            self.modules = self.ir_serializer.load_modules(self.config.cache_dir)
            self.project_ir = self.ir_serializer.load_project(self.config.cache_dir)
            
            if self.functions and self.modules:
                logger.info("Loaded cached analysis results")
                return
        
        # Find C++ files
        logger.info("Finding C++ files...")
        cpp_files = find_cpp_files(
            self.config.project_path,
            self.config.cpp_extensions,
            self.config.exclude_patterns
        )
        logger.info(f"Found {len(cpp_files)} C++ files")
        
        # Analyze modules
        logger.info("Analyzing modules...")
        self.module_analyzer.analyze_project(cpp_files)
        
        # Parse files and extract ASTs
        logger.info("Parsing files and extracting ASTs...")
        for file_path in tqdm(cpp_files, desc="Parsing files"):
            try:
                # Double-check file extension to ensure it's a C++ file
                if file_path.suffix.lower() not in [ext.lower() for ext in self.config.cpp_extensions]:
                    logger.debug(f"Skipping non-C++ file: {file_path}")
                    continue
                
                # Extract functions
                functions = self.ast_extractor.extract_functions(file_path)
                
                if not functions:
                    # No functions found, skip this file
                    continue
                
                for func_info in functions:
                    func_name = func_info.get("name")
                    if not func_name:
                        continue
                    
                    try:
                        # Get module
                        module_name = self.module_analyzer.get_module_for_file(file_path)
                        
                        # Add to call graph
                        self.call_graph_builder.add_function(
                            func_name,
                            file_path,
                            class_name=func_info.get("class_name"),
                            namespace=func_info.get("namespace"),
                            is_virtual=func_info.get("is_virtual", False),
                            is_static=func_info.get("is_static", False)
                        )
                        
                        # Parse AST for this function
                        ast = self.ast_extractor.parse_file(file_path)
                        if ast:
                            # Build CFG
                            cfg = self.cfg_builder.build_cfg_from_ast(
                                ast, func_name, file_path
                            )
                            
                            # Transform to IR
                            func_ir = self.ir_transformer.transform_function(
                                {"function": func_info, **ast},
                                cfg,
                                file_path,
                                namespace=func_info.get("namespace"),
                                class_name=func_info.get("class_name")
                            )
                            
                            # Extract calls
                            self.call_graph_builder.extract_calls_from_ast(
                                ast, func_name, file_path
                            )
                    except Exception as func_error:
                        # Log but continue with other functions
                        logger.debug(f"Failed to process function {func_name} in {file_path}: {func_error}")
                        continue
            except Exception as e:
                logger.warning(f"Failed to process {file_path}: {e}")
        
        # Transform modules to IR
        logger.info("Transforming modules to IR...")
        module_data = self.module_analyzer.get_all_modules()
        function_ids = list(self.ir_transformer.get_all_functions().keys())
        
        for module_name, mod_data in module_data.items():
            module_func_ids = [
                fid for fid in function_ids
                if self.ir_transformer.get_function(fid) and
                self.module_analyzer.get_module_for_file(
                    Path(self.ir_transformer.get_function(fid).file)
                ) == module_name
            ]
            
            module_ir = self.ir_transformer.transform_module(
                module_name, mod_data, module_func_ids
            )
        
        # Transform project
        logger.info("Creating project IR...")
        module_ids = list(self.ir_transformer.get_all_modules().keys())
        project_name = self.config.project_path.name
        self.project_ir = self.ir_transformer.transform_project(project_name, module_ids)
        
        # Save to cache
        logger.info("Saving to cache...")
        self.functions = self.ir_transformer.get_all_functions()
        self.modules = self.ir_transformer.get_all_modules()
        
        self.ir_serializer.save_functions(self.functions, self.config.cache_dir)
        self.ir_serializer.save_modules(self.modules, self.config.cache_dir)
        self.ir_serializer.save_project(self.project_ir, self.config.cache_dir)
        
        # Index in RAG
        logger.info("Indexing in RAG...")
        self.indexer.index_all(self.functions, self.modules)
        
        logger.info("Project analysis complete!")
    
    def generate_flowchart(
        self,
        scope: Optional[str] = None,
        diagram_type: str = "flowchart",
        diagram_format: str = "plantuml"
    ) -> Dict[str, Any]:
        """Generate flowchart diagram"""
        # Ensure project is analyzed
        if not self.functions:
            logger.info("Project not analyzed yet, analyzing now...")
            self.analyze_project()
        
        # Create agent graph
        agent_graph = create_agent_graph(
            self.retriever,
            self.graph_builder,
            self.functions,
            self.modules,
            self.diagram_generator,
            self.validator,
            llm_model=self.config.llm_model,
            ollama_base_url=self.config.ollama_base_url
        )
        
        # Prepare initial state
        from agent.agent.state import AgentState
        
        initial_state: AgentState = {
            "user_query": f"Generate {diagram_type} diagram" + (f" for {scope}" if scope else ""),
            "project_path": self.config.project_path,
            "scope": scope,
            "intent": None,
            "retrieved_context": [],
            "selected_graphs": {},
            "selected_functions": [],
            "selected_modules": [],
            "diagram_plan": {},
            "diagram_type": diagram_type,
            "diagram_format": diagram_format,
            "diagram_output": None,
            "validation_results": {},
            "explanation": None,
            "error": None,
            "retry_count": 0
        }
        
        # Run agent
        logger.info("Running agent workflow...")
        final_state = agent_graph.invoke(initial_state)
        
        # Generate explanation
        explanation = self.explainer.explain_diagram(
            final_state.get("diagram_output", ""),
            final_state.get("selected_graphs", {}),
            final_state.get("selected_functions", []),
            final_state.get("selected_modules", [])
        )
        
        return {
            "diagram_code": final_state.get("diagram_output", ""),
            "diagram_type": final_state.get("diagram_type", diagram_type),
            "diagram_format": final_state.get("diagram_format", diagram_format),
            "validation": final_state.get("validation_results", {}),
            "explanation": explanation,
            "error": final_state.get("error")
        }
