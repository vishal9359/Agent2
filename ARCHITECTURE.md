# C++ Flowchart AI Agent - Complete Architecture & Approach

## Executive Summary

This document outlines the complete architecture, technology stack, and implementation approach for an AI agent that can analyze any C++ project and generate accurate flowcharts using only open-source tools and models.

**Core Principle**: *"Deterministic compiler analysis first, LLM only for reasoning & visualization."*

---

## 1. Technology Stack

### 1.1 Core Frameworks
- **LangGraph**: For agent orchestration and state management
- **LangChain**: For LLM integration and RAG pipeline
- **ChromaDB**: For vector storage and semantic search
- **Tree-sitter**: For C++ AST parsing (fast, incremental)
- **Clang Python Bindings**: For accurate C++ parsing (when available)
- **NetworkX**: For graph operations and algorithms
- **PlantUML**: For diagram generation (primary)
- **Mermaid**: For alternative diagram format

### 1.2 LLM & Embeddings (Open Source via Ollama)
- **LLM Models**: 
  - Primary: `qwen2.5:latest` or `llama3.2:latest` (for reasoning)
  - Fallback: `gemma:7b` or `gemma:2b`
- **Embedding Model**: 
  - `jina/jina-embeddings` (via Ollama)
  - Alternative: `nomic-embed-text` (if available)

### 1.3 Python Environment
- **Python**: 3.11.14
- **Key Libraries**:
  - `langchain-core`: 1.1.3
  - `langchain-community`: 0.4.1
  - `langchain-classic`: 1.0.0
  - `langgraph`: Latest
  - `chromadb`: Latest
  - `tree-sitter`: 0.25.2
  - `tree-sitter-cpp`: Latest
  - `networkx`: Latest
  - `ollama`: Latest (for model access)

---

## 2. System Architecture

### 2.1 High-Level Flow

```
C++ Project Path
    ↓
[Phase 1: Compiler-Grade Parsing]
    ├── AST Extraction (Tree-sitter/Clang)
    ├── Control Flow Graph (CFG) Generation
    ├── Call Graph Construction
    └── Module Dependency Analysis
    ↓
[Phase 2: Intermediate Representation]
    ├── AST → IR Transformation
    ├── Function IR
    ├── Module IR
    └── Project IR
    ↓
[Phase 3: Graph Normalization]
    ├── CFG → Normalized Graph
    ├── Call Graph → Normalized Graph
    └── Module Graph → Normalized Graph
    ↓
[Phase 4: RAG Indexing]
    ├── IR Summaries → Embeddings
    ├── Store in ChromaDB
    └── Metadata Tagging
    ↓
[Phase 5: Agent Reasoning]
    ├── Intent Classification
    ├── Retrieval Planning
    └── Diagram Planning
    ↓
[Phase 6: Diagram Generation]
    ├── Graph → PlantUML/Mermaid
    ├── LLM-Assisted Labeling
    └── Output Generation
    ↓
[Phase 7: Validation]
    ├── Structural Validation
    ├── Diagram Syntax Check
    └── Explainability Output
```

### 2.2 Component Architecture

```
agent/
├── parser/          # Phase 1: C++ Parsing
│   ├── ast_extractor.py
│   ├── cfg_builder.py
│   ├── call_graph.py
│   └── module_analyzer.py
├── ir/              # Phase 2: IR Layer
│   ├── ir_schema.py
│   ├── ast_to_ir.py
│   └── ir_serializer.py
├── graphs/          # Phase 3: Graph Normalization
│   ├── graph_builder.py
│   ├── graph_persistence.py
│   └── graph_utils.py
├── index/           # Phase 4: RAG Indexing
│   ├── indexer.py
│   ├── retriever.py
│   └── embeddings.py
├── agent/           # Phase 5: LangGraph Agent
│   ├── agent_graph.py
│   ├── nodes.py
│   └── state.py
├── diagrams/        # Phase 6: Diagram Generation
│   ├── flowchart_generator.py
│   ├── sequence_generator.py
│   └── architecture_generator.py
└── validation/      # Phase 7: Validation
    ├── validator.py
    └── explainer.py
```

---

## 3. Detailed Implementation Phases

### Phase 1: Compiler-Grade Parsing Layer

#### 1.1 AST Extraction
**Technology**: Tree-sitter (primary) with Clang fallback

**Responsibilities**:
- Parse all `.cpp`, `.hpp`, `.h`, `.cc`, `.cxx` files
- Extract complete AST per translation unit
- Handle includes, macros, templates (best-effort)
- Persist ASTs in JSON format

**Key Extractions**:
- Functions (name, parameters, return type, body)
- Classes (name, methods, inheritance)
- Namespaces
- Control structures (if/else, loops, switches)
- Exception blocks (try/catch)

#### 1.2 Control Flow Graph (CFG) Generation
**Algorithm**: Standard CFG construction from AST

**Nodes**:
- Entry node
- Exit node
- Statement nodes
- Branch nodes (if/else, switch)
- Loop nodes (for, while, do-while)
- Exception nodes (try/catch)
- Return nodes

**Edges**:
- Sequential flow
- Conditional branches
- Loop back-edges
- Exception paths

#### 1.3 Call Graph Construction
**Approach**: Static analysis + heuristics

**Resolution Strategy**:
1. Direct function calls (exact match)
2. Virtual dispatch (class hierarchy analysis)
3. Function pointers (best-effort tracking)
4. Template instantiations

**Storage**: Directed graph with caller → callee edges

#### 1.4 Module & Dependency Analysis
**Module Definition**: Directory-based + include analysis

**Process**:
- Group files by directory structure
- Analyze `#include` statements
- Identify public vs private APIs
- Build inter-module dependency graph

---

### Phase 2: Intermediate Representation (IR)

#### 2.1 IR Schema Design

**Function IR**:
```python
{
    "id": "unique_id",
    "name": "function_name",
    "signature": "return_type name(params)",
    "file": "path/to/file.cpp",
    "line": 42,
    "inputs": [...],
    "outputs": [...],
    "control_blocks": [...],
    "calls": [...],
    "complexity": "metric"
}
```

**Module IR**:
```python
{
    "id": "module_id",
    "name": "module_name",
    "path": "path/to/module",
    "responsibilities": [...],
    "entry_points": [...],
    "dependencies": [...],
    "public_api": [...],
    "private_api": [...]
}
```

**Project IR**:
```python
{
    "id": "project_id",
    "name": "project_name",
    "root_path": "...",
    "modules": [...],
    "main_flows": [...],
    "startup_sequence": [...]
}
```

#### 2.2 AST → IR Transformation
**Process**:
1. Traverse AST nodes
2. Map to IR schema
3. Simplify control flow
4. Resolve references
5. Extract semantic meaning

**Output**: Language-independent IR representation

---

### Phase 3: Graph Normalization

#### 3.1 Graph Models
**CFG Graph**: NetworkX DiGraph
- Nodes: IR function blocks
- Edges: Control flow

**Call Graph**: NetworkX DiGraph
- Nodes: Functions
- Edges: Call relationships

**Module Graph**: NetworkX DiGraph
- Nodes: Modules
- Edges: Dependencies

#### 3.2 Graph Persistence
**Format**: JSON (GraphML for large projects)

**Metadata**:
- Node IDs (stable across runs)
- Labels
- File/line references
- Timestamps

**Benefits**:
- Incremental updates
- Cache reuse
- CI/CD integration

---

### Phase 4: RAG Indexing (Knowledge Base)

#### 4.1 What to Index
**DO Index**:
- Function IR summaries (semantic descriptions)
- Flow block descriptions
- Call relationship descriptions
- Module responsibility descriptions
- Architecture patterns

**DON'T Index**:
- Raw source code
- AST nodes directly
- Low-level implementation details

#### 4.2 Vector Index Strategy
**ChromaDB Collections**:
- `functions`: Function-level summaries
- `modules`: Module-level descriptions
- `flows`: Control flow descriptions
- `architecture`: High-level patterns

**Metadata Schema**:
```python
{
    "project": "project_name",
    "module": "module_name",
    "file": "file_path",
    "function": "function_name",
    "graph_node_id": "node_id",
    "type": "function|module|flow|architecture"
}
```

#### 4.3 Embedding Generation
**Model**: `jina/jina-embeddings` via Ollama

**Process**:
1. Generate IR summaries (text descriptions)
2. Create embeddings
3. Store in ChromaDB with metadata
4. Enable semantic search

#### 4.4 Incremental Reindexing
**Strategy**:
- Hash-based change detection (file content hash)
- Re-index only modified files/functions
- Update graphs incrementally

---

### Phase 5: Agent Reasoning & Planning (LangGraph)

#### 5.1 Agent State Schema
```python
{
    "user_query": "string",
    "project_path": "string",
    "intent": "project|module|function|sequence|architecture",
    "scope": "path or None",
    "retrieved_context": [...],
    "selected_graphs": {...},
    "diagram_plan": {...},
    "diagram_output": "string",
    "validation_results": {...}
}
```

#### 5.2 LangGraph Workflow

**Nodes**:
1. **Classify Intent**: Determine diagram type needed
2. **Plan Retrieval**: Decide what to retrieve from RAG
3. **Retrieve Context**: Query ChromaDB
4. **Select Graphs**: Choose relevant CFG/Call/Module graphs
5. **Plan Diagram**: Decide diagram structure and abstraction
6. **Generate Diagram**: Create PlantUML/Mermaid code
7. **Validate**: Check correctness
8. **Format Output**: Return final result

**Edges**: Conditional routing based on state

#### 5.3 LLM Usage Guidelines
**LLM Responsibilities**:
- ✅ Intent classification
- ✅ Natural language understanding
- ✅ Diagram planning
- ✅ Node labeling (readability)
- ✅ Annotations and comments

**LLM Prohibitions**:
- ❌ Inferring control flow (use CFG)
- ❌ Creating new nodes/edges
- ❌ Guessing function logic
- ❌ Inventing call relationships

---

### Phase 6: Diagram Generation

#### 6.1 Deterministic Diagram Builder

**CFG → Flowchart**:
- Map CFG nodes to flowchart shapes
- Map CFG edges to flowchart arrows
- Preserve all paths (no simplification without user request)

**Call Graph → Sequence Diagram**:
- Map callers/callees to participants
- Map calls to messages
- Preserve call order

**Module Graph → Architecture Diagram**:
- Map modules to components
- Map dependencies to connections
- Show public vs private APIs

#### 6.2 LLM-Assisted Labeling
**Process**:
1. Generate diagram structure from graphs (deterministic)
2. Send to LLM for:
   - Renaming nodes for readability
   - Adding helpful annotations
   - Adding comments
3. Validate LLM output (no structural changes)

#### 6.3 Output Formats

**PlantUML** (Primary):
- Flowcharts: `@startuml ... @enduml`
- Sequence: `@startuml sequence ... @enduml`
- Component: `@startuml component ... @enduml`

**Mermaid** (Alternative):
- Flowcharts: `flowchart TD ...`
- Sequence: `sequenceDiagram ...`
- Architecture: `graph TD ...`

**Validation**: Syntax check before output

---

### Phase 7: Validation & Guardrails

#### 7.1 Structural Validation
**Checks**:
- All CFG paths represented in diagram
- No orphan nodes
- No hallucinated edges
- All referenced functions exist

#### 7.2 Diagram Validation
**Process**:
- Parse PlantUML/Mermaid syntax
- Render headlessly (if possible)
- Fail fast on syntax errors

#### 7.3 Explainability
**Output**:
- Source functions/modules used
- Graph nodes mapped
- Abstraction level applied
- Any simplifications made

---

## 4. Scalability Considerations

### 4.1 Large Project Handling
- **Batch Parsing**: Process files in parallel
- **Incremental Updates**: Only re-parse changed files
- **Memory Management**: Stream large ASTs
- **Caching**: Cache ASTs, IRs, graphs, embeddings

### 4.2 Performance Optimization
- **Lazy Loading**: Load graphs on-demand
- **Graph Pruning**: Filter irrelevant nodes early
- **Embedding Caching**: Reuse embeddings for unchanged text

### 4.3 CI/CD Integration
- **CLI Interface**: Command-line tool
- **JSON Output**: Machine-readable results
- **Exit Codes**: Success/failure indicators

---

## 5. Error Handling & Robustness

### 5.1 Parsing Failures
- **Graceful Degradation**: Continue with partial AST
- **Error Reporting**: Log parsing errors
- **Fallback Strategies**: Use simpler parsing if needed

### 5.2 LLM Failures
- **Retry Logic**: Retry with exponential backoff
- **Fallback Models**: Switch to alternative LLM
- **Deterministic Fallback**: Use default labels if LLM fails

### 5.3 Graph Generation Failures
- **Validation**: Check graph integrity
- **Repair**: Attempt to fix common issues
- **Error Messages**: Clear failure explanations

---

## 6. Testing Strategy

### 6.1 Unit Tests
- Parser correctness
- IR transformation accuracy
- Graph generation validity
- Diagram syntax correctness

### 6.2 Integration Tests
- End-to-end pipeline
- RAG retrieval accuracy
- Agent workflow correctness

### 6.3 Validation Tests
- Test on known C++ projects
- Compare generated diagrams with ground truth
- Performance benchmarks

---

## 7. Deployment & Usage

### 7.1 Installation
```bash
pip install -r requirements.txt
# Ensure Ollama is running with required models
```

### 7.2 Usage
```python
from agent.main import CppFlowchartAgent

agent = CppFlowchartAgent(
    project_path="D:/git-project/poseidonos",
    ollama_base_url="http://localhost:11434"
)

# Generate project-level flowchart
result = agent.generate_flowchart(
    scope=None,  # Entire project
    diagram_type="flowchart"
)

# Generate module-level flowchart
result = agent.generate_flowchart(
    scope="src/module_name",
    diagram_type="flowchart"
)
```

### 7.3 CLI Usage
```bash
python -m agent.cli --project D:/git-project/poseidonos --type flowchart --output diagram.puml
```

---

## 8. Future Enhancements

- **Multi-language Support**: Extend to other languages
- **Interactive Diagrams**: Clickable, explorable diagrams
- **Diff Visualization**: Show changes between versions
- **Performance Analysis**: Add timing information
- **Documentation Generation**: Auto-generate docs from diagrams

---

## 9. Key Success Criteria

✅ Works on any C++ project (no project-specific code)  
✅ Produces correct flowcharts (no hallucinated logic)  
✅ Never infers control flow from text (uses CFG)  
✅ LLM-replaceable (deterministic core)  
✅ CI/CD friendly (automated, reliable)  
✅ Open-source only (no proprietary dependencies)  

---

## 10. Implementation Priority

1. **Phase 1** (Critical): Parsing & CFG generation
2. **Phase 2** (Critical): IR layer
3. **Phase 3** (Critical): Graph normalization
4. **Phase 4** (Important): RAG indexing
5. **Phase 5** (Important): Agent reasoning
6. **Phase 6** (Important): Diagram generation
7. **Phase 7** (Nice-to-have): Validation & explainability

---

**Document Version**: 1.0  
**Last Updated**: 2024  
**Author**: AI Agent Development Team

