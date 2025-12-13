# Quick Start Guide

## 🚀 Get Started in 5 Minutes

### Step 1: Install Ollama

```bash
# Visit https://ollama.ai and install Ollama
# Or use:
curl -fsSL https://ollama.ai/install.sh | sh
```

### Step 2: Pull Required Models

```bash
ollama pull qwen2.5:latest
ollama pull jina/jina-embeddings
```

### Step 3: Install Python Dependencies

```bash
cd Agent2
pip install -r requirements.txt
```

### Step 4: Test Basic Setup

```bash
python test_basic.py
```

Expected output:
```
✅ All imports successful!
✅ Configuration test passed!
✅ IR schema test passed!
🎉 All basic tests passed!
```

### Step 5: Run on Your C++ Project

```bash
# Replace with your C++ project path
python -m agent.cli --project /path/to/your/cpp/project --type flowchart --output diagram.puml
```

## 📝 Example: Analyzing a C++ Project

```bash
# Example: Analyze poseidonos project
python -m agent.cli \
  --project D:/git-project/poseidonos \
  --type flowchart \
  --output poseidonos_flowchart.puml
```

## 🔍 View Generated Diagrams

### PlantUML Diagrams

1. **Online**: Copy content to http://www.plantuml.com/plantuml/uml/
2. **VS Code**: Install "PlantUML" extension, open `.puml` file
3. **Command Line**: `plantuml diagram.puml` (requires Java)

### Mermaid Diagrams

1. **Online**: Copy content to https://mermaid.live/
2. **VS Code**: Install "Markdown Preview Mermaid Support"
3. **GitHub**: Add to markdown file, GitHub renders automatically

## ⚡ Common Commands

```bash
# Generate flowchart
python -m agent.cli -p /path/to/project -t flowchart -o output.puml

# Generate sequence diagram
python -m agent.cli -p /path/to/project -t sequence -o sequence.puml

# Generate architecture diagram
python -m agent.cli -p /path/to/project -t architecture -o arch.puml

# Analyze specific module
python -m agent.cli -p /path/to/project -s src/module_name -t flowchart

# Force rebuild cache
python -m agent.cli -p /path/to/project -t flowchart --force-rebuild
```

## 🐛 Troubleshooting

### Issue: "Cannot connect to Ollama"

**Solution**:
```bash
# Start Ollama
ollama serve

# Verify it's running
curl http://localhost:11434/api/tags
```

### Issue: "Model not found"

**Solution**:
```bash
# List available models
ollama list

# Pull missing models
ollama pull qwen2.5:latest
ollama pull jina/jina-embeddings
```

### Issue: "Import errors"

**Solution**:
```bash
# Reinstall dependencies
pip install -r requirements.txt --upgrade

# Verify Python version (needs 3.11+)
python --version
```

## 📚 Next Steps

- Read [README.md](README.md) for detailed documentation
- Check [ARCHITECTURE.md](ARCHITECTURE.md) for system design
- See [USAGE.md](USAGE.md) for advanced usage

## 💡 Tips

1. **First Run**: May take time for large projects - be patient!
2. **Cache**: Subsequent runs are faster (uses cached analysis)
3. **Scope**: Use `--scope` to analyze specific modules for faster results
4. **Memory**: Large projects may need more RAM

---

**Ready to go!** Start analyzing your C++ projects now! 🎉
