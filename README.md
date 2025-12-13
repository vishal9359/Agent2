# C++ Flowchart AI Agent

An intelligent AI agent that analyzes C++ projects and generates accurate flowcharts using compiler-grade analysis and open-source LLMs. The agent uses deterministic parsing to extract control flow graphs and leverages RAG (Retrieval-Augmented Generation) for intelligent diagram generation.

## 🎯 Features

- ✅ **Compiler-Grade Parsing**: Accurate AST extraction and control flow analysis using Tree-sitter
- ✅ **RAG-Powered**: Semantic search over project knowledge base using ChromaDB
- ✅ **Multiple Diagram Types**: Flowcharts, sequence diagrams, and architecture diagrams
- ✅ **Open Source Only**: Uses Ollama, ChromaDB, and open-source models
- ✅ **LangGraph Agent**: Intelligent reasoning and planning workflow
- ✅ **Works on Any C++ Project**: No project-specific configuration needed
- ✅ **Deterministic Analysis**: Control flow derived from actual code, not LLM inference

## 📋 Prerequisites

### System Requirements
- **Python**: 3.11.14 or higher
- **Ollama**: Installed and running (see [Ollama Installation](https://ollama.ai))
- **Operating System**: Linux, macOS, or Windows

### Required Ollama Models

Ensure the following models are pulled in Ollama:

```bash
# LLM for reasoning
ollama pull qwen2.5:latest
# Alternative: ollama pull llama3.2:latest

# Embedding model
ollama pull jina/jina-embeddings
```

## 🚀 Installation

### 1. Clone the Repository

```bash
git clone https://github.com/vishal9359/Agent2.git
cd Agent2
```

### 2. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 3. Verify Ollama is Running

```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# If not running, start Ollama
ollama serve
```

### 4. Verify Models are Available

```bash
ollama list
# Should show qwen2.5:latest and jina/jina-embeddings
```

## 📖 Usage

### Command Line Interface (CLI)

#### Generate Flowchart for Entire Project

```bash
python -m agent.cli --project /path/to/cpp/project --type flowchart --output diagram.puml
```

#### Generate Flowchart for Specific Module

```bash
python -m agent.cli --project /path/to/cpp/project --scope src/module_name --type flowchart
```

#### Generate Sequence Diagram

```bash
python -m agent.cli --project /path/to/cpp/project --type sequence --output sequence.puml
```

#### Generate Architecture Diagram

```bash
python -m agent.cli --project /path/to/cpp/project --type architecture --output arch.puml
```

#### CLI Options

```bash
python -m agent.cli --help

Options:
  --project, -p PATH          Path to C++ project (required)
  --type, -t TYPE             Diagram type: flowchart, sequence, architecture
  --scope, -s PATH            Scope (module path or function name)
  --format, -f FORMAT         Diagram format: plantuml, mermaid
  --output, -o FILE           Output file path
  --ollama-url URL            Ollama base URL (default: http://localhost:11434)
  --llm-model MODEL           LLM model name (default: qwen2.5:latest)
  --embedding-model MODEL     Embedding model (default: jina/jina-embeddings)
  --force-rebuild             Force rebuild of analysis cache
```

### Python API

```python
from agent.main import CppFlowchartAgent

# Initialize agent
agent = CppFlowchartAgent(
    project_path="D:/git-project/poseidonos",
    ollama_base_url="http://localhost:11434",
    llm_model="qwen2.5:latest",
    embedding_model="jina/jina-embeddings"
)

# Analyze project (this may take a while for large projects)
agent.analyze_project()

# Generate flowchart for entire project
result = agent.generate_flowchart(
    scope=None,
    diagram_type="flowchart",
    diagram_format="plantuml"
)

print(result["diagram_code"])

# Generate flowchart for specific module
result = agent.generate_flowchart(
    scope="src/module_name",
    diagram_type="flowchart"
)

# Generate sequence diagram
result = agent.generate_flowchart(
    scope="src/module_name",
    diagram_type="sequence"
)
```

## 📊 Diagram Types

### 1. Flowchart
Shows control flow within functions, including:
- Entry and exit points
- Conditional branches (if/else)
- Loops (for/while)
- Function calls
- Return statements

```bash
python -m agent.cli --project <path> --type flowchart
```

### 2. Sequence Diagram
Shows function call sequences and interactions:
- Function call relationships
- Call order
- Caller-callee mappings

```bash
python -m agent.cli --project <path> --type sequence
```

### 3. Architecture Diagram
Shows module dependencies and structure:
- Module relationships
- Dependency graph
- Public vs private APIs

```bash
python -m agent.cli --project <path> --type architecture
```

## 🎨 Diagram Formats

### PlantUML (Default)
- **Format**: `.puml`
- **View Online**: http://www.plantuml.com/plantuml/uml/
- **VS Code**: Install "PlantUML" extension
- **Command Line**: `plantuml diagram.puml`

### Mermaid
- **Format**: `.mmd` or `.mermaid`
- **View Online**: https://mermaid.live/
- **VS Code**: Install "Markdown Preview Mermaid Support"
- **GitHub**: Renders automatically in markdown files

## 🏗️ Architecture

The agent follows a 7-phase architecture:

1. **Phase 1: Compiler-Grade Parsing** - AST extraction, CFG generation, call graph construction
2. **Phase 2: Intermediate Representation** - Language-independent IR transformation
3. **Phase 3: Graph Normalization** - Normalized graph representations
4. **Phase 4: RAG Indexing** - ChromaDB vector storage with semantic search
5. **Phase 5: LangGraph Agent** - Intelligent reasoning and planning
6. **Phase 6: Diagram Generation** - Deterministic graph-to-diagram mapping
7. **Phase 7: Validation** - Diagram correctness and explainability

See [ARCHITECTURE.md](ARCHITECTURE.md) for detailed documentation.

## 📁 Project Structure

```
agent/
├── parser/          # Phase 1: C++ Parsing
├── ir/              # Phase 2: IR Layer
├── graphs/          # Phase 3: Graph Normalization
├── index/           # Phase 4: RAG Indexing
├── agent/           # Phase 5: LangGraph Agent
├── diagrams/        # Phase 6: Diagram Generation
└── validation/      # Phase 7: Validation
```

## 🔧 Configuration

You can customize the agent behavior:

```python
from agent.config import AgentConfig
from pathlib import Path

config = AgentConfig(
    project_path=Path("path/to/project"),
    ollama_base_url="http://localhost:11434",
    llm_model="qwen2.5:latest",
    embedding_model="jina/jina-embeddings",
    cache_dir=Path(".agent_cache"),
    cpp_extensions=[".cpp", ".hpp", ".h", ".cc", ".cxx"],
    exclude_patterns=["**/build/**", "**/test/**"]
)
```

## 🧪 Testing

### Basic Structure Test

```bash
python test_basic.py
```

This verifies:
- All imports work correctly
- Configuration is valid
- IR schema is properly defined

### Example Project Test

```bash
# Test on a sample C++ project
python -m agent.cli --project /path/to/test/project --type flowchart --output test.puml
```

## 🐛 Troubleshooting

### Ollama Connection Issues

**Problem**: Cannot connect to Ollama

**Solution**:
```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# Start Ollama if not running
ollama serve

# Verify models are available
ollama list
```

### Parsing Errors

**Problem**: Some C++ files fail to parse

**Solution**:
- Check logs for specific file errors
- Complex C++ constructs may not parse perfectly
- Try excluding problematic files using `exclude_patterns` in config
- Tree-sitter has limitations with some advanced C++ features

### Memory Issues

**Problem**: Out of memory for large projects

**Solution**:
- Use `--scope` to limit analysis to specific modules
- Increase system memory if possible
- Process modules separately
- Use `--force-rebuild` only when necessary (uses cache by default)

### Diagram Generation Issues

**Problem**: Empty or invalid diagrams

**Solution**:
- Check validation results in output
- Ensure selected graphs are not empty
- Try different diagram types
- Verify project was analyzed successfully

## 📝 Examples

### Example 1: Project Overview

```bash
python -m agent.cli \
  --project /path/to/cpp/project \
  --type architecture \
  --output project_architecture.puml
```

### Example 2: Module Flowchart

```bash
python -m agent.cli \
  --project /path/to/cpp/project \
  --scope src/core \
  --type flowchart \
  --output core_flowchart.puml
```

### Example 3: Function Call Sequence

```bash
python -m agent.cli \
  --project /path/to/cpp/project \
  --scope src/api \
  --type sequence \
  --output api_sequence.puml
```

## 🔍 How It Works

1. **Parsing**: Extracts AST from C++ files using Tree-sitter
2. **CFG Generation**: Builds control flow graphs for each function
3. **Call Graph**: Constructs function call relationships
4. **IR Generation**: Converts AST/CFG to language-independent IR
5. **RAG Indexing**: Indexes IR summaries in ChromaDB for semantic search
6. **Agent Reasoning**: LangGraph agent plans and retrieves relevant context
7. **Diagram Generation**: Generates PlantUML/Mermaid diagrams from graphs
8. **Validation**: Ensures correctness and provides explainability

## 🎓 Key Principles

1. **Deterministic Parsing First**: All control flow comes from AST/CFG, not LLM inference
2. **LLM for Reasoning Only**: LLM used for intent classification, planning, and labeling
3. **Structured IR**: Language-independent intermediate representation
4. **Graph-Based**: All diagrams generated from graphs, not text
5. **Open Source Only**: All dependencies are open source
6. **RAG-Powered**: Semantic search over structured knowledge base

## 📚 Additional Documentation

- [ARCHITECTURE.md](ARCHITECTURE.md) - Complete architecture documentation
- [USAGE.md](USAGE.md) - Detailed usage guide
- [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md) - Implementation details

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

MIT License - see LICENSE file for details

## 🙏 Acknowledgments

- **Tree-sitter**: For C++ AST parsing
- **Ollama**: For open-source LLM access
- **ChromaDB**: For vector database
- **LangGraph**: For agent orchestration
- **PlantUML/Mermaid**: For diagram generation

## 📧 Support

For issues, questions, or contributions, please open an issue on GitHub.

---

**Note**: This agent is designed to work with any C++ project. The first analysis may take time for large projects, but subsequent runs use cached results for faster performance.
