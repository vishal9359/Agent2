"""LangGraph Agent Nodes"""

import logging
from typing import Dict, Any
import requests
import json

from agent.agent.state import AgentState

logger = logging.getLogger(__name__)


def classify_intent(state: AgentState, llm_model: str = "qwen2.5:latest", 
                   ollama_base_url: str = "http://localhost:11434") -> AgentState:
    """Classify user intent"""
    try:
        url = f"{ollama_base_url.rstrip('/')}/api/generate"
        
        prompt = f"""Classify the user's request into one of these categories:
- project: Generate flowchart for entire project
- module: Generate flowchart for a specific module
- function: Generate flowchart for a specific function
- sequence: Generate sequence diagram showing function calls
- architecture: Generate architecture diagram showing module dependencies

User query: {state['user_query']}
Scope: {state.get('scope', 'None')}

Respond with only the category name (project, module, function, sequence, or architecture)."""

        payload = {
            "model": llm_model,
            "prompt": prompt,
            "stream": False
        }
        response = requests.post(url, json=payload, timeout=60)
        response.raise_for_status()
        data = response.json()
        intent = data.get("response", "").strip().lower()
        
        # Validate intent
        valid_intents = ["project", "module", "function", "sequence", "architecture"]
        if intent not in valid_intents:
            intent = "project"  # Default
        
        state["intent"] = intent
        logger.info(f"Classified intent: {intent}")
        
    except Exception as e:
        logger.error(f"Intent classification failed: {e}")
        state["intent"] = "project"  # Default fallback
        state["error"] = str(e)
    
    return state


def plan_retrieval(state: AgentState, llm_model: str = "qwen2.5:latest",
                  ollama_base_url: str = "http://localhost:11434") -> AgentState:
    """Plan what to retrieve from RAG"""
    try:
        url = f"{ollama_base_url.rstrip('/')}/api/generate"
        
        prompt = f"""Based on the user's intent, plan what information to retrieve:
Intent: {state['intent']}
Query: {state['user_query']}
Scope: {state.get('scope', 'None')}

Generate a search query for retrieving relevant functions/modules from the codebase.
Respond with only the search query text."""

        payload = {
            "model": llm_model,
            "prompt": prompt,
            "stream": False
        }
        response = requests.post(url, json=payload, timeout=60)
        response.raise_for_status()
        data = response.json()
        search_query = data.get("response", state['user_query']).strip()
        
        state["retrieved_context"] = []  # Will be filled by retrieve_context
        state["_search_query"] = search_query  # Temporary storage
        logger.info(f"Planned retrieval query: {search_query}")
        
    except Exception as e:
        logger.error(f"Retrieval planning failed: {e}")
        state["_search_query"] = state['user_query']
        state["error"] = str(e)
    
    return state


def retrieve_context(state: AgentState, retriever) -> AgentState:
    """Retrieve context from RAG"""
    try:
        search_query = state.get("_search_query", state['user_query'])
        intent = state.get("intent", "project")
        
        retrieved = []
        
        if intent in ["function", "module", "project"]:
            # Retrieve functions
            functions = retriever.retrieve_functions(search_query)
            retrieved.extend(functions)
        
        if intent in ["module", "project", "architecture"]:
            # Retrieve modules
            modules = retriever.retrieve_modules(search_query)
            retrieved.extend(modules)
        
        state["retrieved_context"] = retrieved
        logger.info(f"Retrieved {len(retrieved)} context items")
        
    except Exception as e:
        logger.error(f"Context retrieval failed: {e}")
        state["retrieved_context"] = []
        state["error"] = str(e)
    
    return state


def select_graphs(state: AgentState, graph_builder, functions: Dict, modules: Dict) -> AgentState:
    """Select relevant graphs based on retrieved context"""
    try:
        selected_graphs = {}
        selected_functions = []
        selected_modules = []
        
        intent = state.get("intent", "project")
        context = state.get("retrieved_context", [])
        
        # Extract function and module IDs from context
        for item in context:
            metadata = item.get("metadata", {})
            if "graph_node_id" in metadata:
                node_id = metadata["graph_node_id"]
                item_type = metadata.get("type", "")
                
                if item_type == "function" and node_id in functions:
                    selected_functions.append(node_id)
                elif item_type == "module" and node_id in modules:
                    selected_modules.append(node_id)
        
        # Build graphs
        if selected_functions:
            # Build CFG graphs for selected functions
            for func_id in selected_functions:
                func_ir = functions[func_id]
                cfg = graph_builder.build_cfg_graph(func_ir)
                selected_graphs[f"cfg_{func_id}"] = cfg
        
        if intent in ["sequence", "architecture"]:
            # Build call graph or module graph
            if intent == "sequence":
                call_graph = graph_builder.build_call_graph(functions)
                selected_graphs["call_graph"] = call_graph
            elif intent == "architecture":
                module_graph = graph_builder.build_module_graph(modules)
                selected_graphs["module_graph"] = module_graph
        
        state["selected_graphs"] = selected_graphs
        state["selected_functions"] = selected_functions
        state["selected_modules"] = selected_modules
        
        logger.info(f"Selected {len(selected_graphs)} graphs")
        
    except Exception as e:
        logger.error(f"Graph selection failed: {e}")
        state["selected_graphs"] = {}
        state["error"] = str(e)
    
    return state


def plan_diagram(state: AgentState, llm_model: str = "qwen2.5:latest",
                ollama_base_url: str = "http://localhost:11434") -> AgentState:
    """Plan diagram structure"""
    try:
        url = f"{ollama_base_url.rstrip('/')}/api/generate"
        
        intent = state.get("intent", "project")
        selected_count = len(state.get("selected_graphs", {}))
        
        prompt = f"""Plan the diagram structure:
Intent: {intent}
Number of selected graphs: {selected_count}

Determine:
1. Diagram type (flowchart, sequence, architecture)
2. Diagram format (plantuml or mermaid)
3. Level of detail (high, medium, low)
4. Key nodes to highlight

Respond in JSON format:
{{"diagram_type": "...", "format": "...", "detail_level": "...", "highlight_nodes": [...]}}"""

        payload = {
            "model": llm_model,
            "prompt": prompt,
            "stream": False
        }
        response = requests.post(url, json=payload, timeout=60)
        response.raise_for_status()
        data = response.json()
        response_text = data.get("response", "").strip()
        
        # Parse JSON (simple extraction)
        import json
        try:
            # Try to extract JSON from response
            if "{" in response_text:
                json_start = response_text.find("{")
                json_end = response_text.rfind("}") + 1
                json_str = response_text[json_start:json_end]
                plan = json.loads(json_str)
            else:
                plan = {"diagram_type": intent, "format": "plantuml", "detail_level": "medium"}
        except:
            plan = {"diagram_type": intent, "format": "plantuml", "detail_level": "medium"}
        
        state["diagram_plan"] = plan
        state["diagram_type"] = plan.get("diagram_type", intent)
        state["diagram_format"] = plan.get("format", "plantuml")
        
        logger.info(f"Planned diagram: {plan}")
        
    except Exception as e:
        logger.error(f"Diagram planning failed: {e}")
        state["diagram_plan"] = {"diagram_type": intent, "format": "plantuml"}
        state["diagram_type"] = intent
        state["diagram_format"] = "plantuml"
        state["error"] = str(e)
    
    return state


def generate_diagram(state: AgentState, diagram_generator) -> AgentState:
    """Generate diagram from graphs"""
    try:
        diagram_type = state.get("diagram_type", "flowchart")
        diagram_format = state.get("diagram_format", "plantuml")
        selected_graphs = state.get("selected_graphs", {})
        
        if not selected_graphs:
            state["diagram_output"] = ""
            state["error"] = "No graphs selected"
            return state
        
        # Generate diagram based on type
        if diagram_type == "flowchart":
            diagram_code = diagram_generator.generate_flowchart(
                selected_graphs, format=diagram_format
            )
        elif diagram_type == "sequence":
            diagram_code = diagram_generator.generate_sequence_diagram(
                selected_graphs, format=diagram_format
            )
        elif diagram_type == "architecture":
            diagram_code = diagram_generator.generate_architecture_diagram(
                selected_graphs, format=diagram_format
            )
        else:
            diagram_code = diagram_generator.generate_flowchart(
                selected_graphs, format=diagram_format
            )
        
        state["diagram_output"] = diagram_code
        logger.info(f"Generated {diagram_type} diagram in {diagram_format} format")
        
    except Exception as e:
        logger.error(f"Diagram generation failed: {e}")
        state["diagram_output"] = ""
        state["error"] = str(e)
    
    return state


def validate_output(state: AgentState, validator) -> AgentState:
    """Validate diagram output"""
    try:
        diagram_output = state.get("diagram_output", "")
        selected_graphs = state.get("selected_graphs", {})
        
        if not diagram_output:
            state["validation_results"] = {"valid": False, "errors": ["Empty diagram"]}
            return state
        
        # Validate diagram syntax
        validation = validator.validate_diagram(diagram_output, state.get("diagram_format", "plantuml"))
        
        # Validate structure
        structure_validation = validator.validate_structure(selected_graphs, diagram_output)
        
        state["validation_results"] = {
            "valid": validation.get("valid", False) and structure_validation.get("valid", False),
            "syntax_errors": validation.get("errors", []),
            "structure_errors": structure_validation.get("errors", [])
        }
        
        logger.info(f"Validation result: {state['validation_results']['valid']}")
        
    except Exception as e:
        logger.error(f"Validation failed: {e}")
        state["validation_results"] = {"valid": False, "errors": [str(e)]}
        state["error"] = str(e)
    
    return state


def format_output(state: AgentState) -> AgentState:
    """Format final output"""
    try:
        diagram_output = state.get("diagram_output", "")
        validation = state.get("validation_results", {})
        
        if validation.get("valid", False):
            state["explanation"] = f"Generated {state.get('diagram_type', 'flowchart')} diagram successfully."
        else:
            errors = validation.get("errors", [])
            state["explanation"] = f"Diagram generated with warnings: {', '.join(errors)}"
        
        logger.info("Output formatted")
        
    except Exception as e:
        logger.error(f"Output formatting failed: {e}")
        state["error"] = str(e)
    
    return state
