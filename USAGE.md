# Usage Guide

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Ensure Ollama is Running

Make sure Ollama is running and you have the required models:

```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# Pull required models if not already available
ollama pull qwen2.5:latest
ollama pull jina/jina-embeddings
```

### 3. Analyze a C++ Project

#### Using Python API

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
```

#### Using CLI

```bash
# Generate flowchart for entire project
python -m agent.cli --project D:/git-project/poseidonos --type flowchart --output diagram.puml

# Generate flowchart for specific module
python -m agent.cli --project D:/git-project/poseidonos --scope src/module_name --type flowchart

# Generate sequence diagram
python -m agent.cli --project D:/git-project/poseidonos --type sequence --output sequence.puml

# Generate architecture diagram
python -m agent.cli --project D:/git-project/poseidonos --type architecture --output arch.puml

# Force rebuild cache
python -m agent.cli --project D:/git-project/poseidonos --type flowchart --force-rebuild
```

## Diagram Types

### Flowchart
Shows control flow within functions:
```bash
python -m agent.cli --project <path> --type flowchart
```

### Sequence Diagram
Shows function call sequences:
```bash
python -m agent.cli --project <path> --type sequence
```

### Architecture Diagram
Shows module dependencies:
```bash
python -m agent.cli --project <path> --type architecture
```

## Diagram Formats

### PlantUML (Default)
```bash
python -m agent.cli --project <path> --format plantuml --output diagram.puml
```

### Mermaid
```bash
python -m agent.cli --project <path> --format mermaid --output diagram.mmd
```

## Viewing Diagrams

### PlantUML
- Online: http://www.plantuml.com/plantuml/uml/
- VS Code: Install "PlantUML" extension
- Command line: Install PlantUML and use `plantuml diagram.puml`

### Mermaid
- Online: https://mermaid.live/
- VS Code: Install "Markdown Preview Mermaid Support" extension
- GitHub: Mermaid diagrams render automatically in markdown files

## Configuration

You can customize the agent behavior:

```python
from agent.main import CppFlowchartAgent

agent = CppFlowchartAgent(
    project_path="path/to/project",
    ollama_base_url="http://localhost:11434",  # Ollama server URL
    llm_model="qwen2.5:latest",  # LLM model for reasoning
    embedding_model="jina/jina-embeddings",  # Embedding model
    cache_dir=".agent_cache"  # Cache directory
)
```

## Troubleshooting

### Ollama Connection Issues
- Ensure Ollama is running: `ollama serve`
- Check if models are available: `ollama list`
- Verify Ollama URL is correct

### Parsing Errors
- Some complex C++ constructs may not parse correctly
- Check logs for specific file errors
- Try excluding problematic files using exclude_patterns in config

### Memory Issues
- For very large projects, consider analyzing specific modules
- Use `--scope` to limit analysis to specific paths
- Increase system memory if needed

### Diagram Generation Issues
- Check validation results in output
- Ensure selected graphs are not empty
- Try different diagram types or formats

## Performance Tips

1. **Use Cache**: The agent caches analysis results. Only use `--force-rebuild` when needed.

2. **Incremental Analysis**: The agent only re-analyzes changed files (based on file hashes).

3. **Scope Limitation**: Use `--scope` to analyze only specific modules for faster results.

4. **Parallel Processing**: For very large projects, consider splitting into modules.

## Examples

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
