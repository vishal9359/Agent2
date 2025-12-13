"""LangGraph Agent Graph Definition"""

import logging
from typing import Dict, Any
from langgraph.graph import StateGraph, END

from agent.agent.state import AgentState
from agent.agent.nodes import (
    classify_intent,
    plan_retrieval,
    retrieve_context,
    select_graphs,
    plan_diagram,
    generate_diagram,
    validate_output,
    format_output
)

logger = logging.getLogger(__name__)


def create_agent_graph(
    retriever,
    graph_builder,
    functions: Dict[str, Any],
    modules: Dict[str, Any],
    diagram_generator,
    validator,
    llm_model: str = "qwen2.5:latest",
    ollama_base_url: str = "http://localhost:11434"
) -> StateGraph:
    """Create the LangGraph agent workflow"""
    
    # Create node functions with dependencies
    def classify_intent_node(state: AgentState) -> AgentState:
        return classify_intent(state, llm_model, ollama_base_url)
    
    def plan_retrieval_node(state: AgentState) -> AgentState:
        return plan_retrieval(state, llm_model, ollama_base_url)
    
    def retrieve_context_node(state: AgentState) -> AgentState:
        return retrieve_context(state, retriever)
    
    def select_graphs_node(state: AgentState) -> AgentState:
        return select_graphs(state, graph_builder, functions, modules)
    
    def plan_diagram_node(state: AgentState) -> AgentState:
        return plan_diagram(state, llm_model, ollama_base_url)
    
    def generate_diagram_node(state: AgentState) -> AgentState:
        return generate_diagram(state, diagram_generator)
    
    def validate_output_node(state: AgentState) -> AgentState:
        return validate_output(state, validator)
    
    def format_output_node(state: AgentState) -> AgentState:
        return format_output(state)
    
    # Create graph
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("classify_intent", classify_intent_node)
    workflow.add_node("plan_retrieval", plan_retrieval_node)
    workflow.add_node("retrieve_context", retrieve_context_node)
    workflow.add_node("select_graphs", select_graphs_node)
    workflow.add_node("plan_diagram", plan_diagram_node)
    workflow.add_node("generate_diagram", generate_diagram_node)
    workflow.add_node("validate_output", validate_output_node)
    workflow.add_node("format_output", format_output_node)
    
    # Define edges
    workflow.set_entry_point("classify_intent")
    workflow.add_edge("classify_intent", "plan_retrieval")
    workflow.add_edge("plan_retrieval", "retrieve_context")
    workflow.add_edge("retrieve_context", "select_graphs")
    workflow.add_edge("select_graphs", "plan_diagram")
    workflow.add_edge("plan_diagram", "generate_diagram")
    workflow.add_edge("generate_diagram", "validate_output")
    workflow.add_edge("validate_output", "format_output")
    workflow.add_edge("format_output", END)
    
    return workflow.compile()
