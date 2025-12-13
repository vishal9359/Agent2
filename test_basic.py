"""Basic test to verify imports and structure"""

def test_imports():
    """Test that all modules can be imported"""
    try:
        from agent.config import AgentConfig
        from agent.utils import find_cpp_files, compute_file_hash
        from agent.parser import ASTExtractor, CFGBuilder, CallGraphBuilder, ModuleAnalyzer
        from agent.ir import FunctionIR, ModuleIR, ProjectIR, ASTToIRTransformer, IRSerializer
        from agent.graphs import GraphBuilder, GraphPersistence, GraphUtils
        from agent.index import Indexer, Retriever, EmbeddingGenerator
        from agent.agent import create_agent_graph, AgentState
        from agent.diagrams import DiagramGenerator, FlowchartGenerator
        from agent.validation import Validator, Explainer
        from agent.main import CppFlowchartAgent
        print("✅ All imports successful!")
        return True
    except Exception as e:
        print(f"❌ Import error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_config():
    """Test configuration"""
    try:
        from agent.config import AgentConfig
        from pathlib import Path
        
        config = AgentConfig(project_path=Path("/test"))
        assert config.project_path == Path("/test")
        assert config.ollama_base_url == "http://localhost:11434"
        print("✅ Configuration test passed!")
        return True
    except Exception as e:
        print(f"❌ Config test error: {e}")
        return False

def test_ir_schema():
    """Test IR schema"""
    try:
        from agent.ir.ir_schema import FunctionIR, ModuleIR, ProjectIR, ControlBlock
        
        # Test ControlBlock
        block = ControlBlock(
            block_id="test",
            block_type="if",
            label="Test Block"
        )
        assert block.block_id == "test"
        
        # Test FunctionIR
        func_ir = FunctionIR(
            id="func1",
            name="test_func",
            signature="void test_func()",
            file="test.cpp",
            line=1
        )
        assert func_ir.name == "test_func"
        
        print("✅ IR schema test passed!")
        return True
    except Exception as e:
        print(f"❌ IR schema test error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Running basic tests...")
    print()
    
    results = []
    results.append(("Imports", test_imports()))
    print()
    results.append(("Config", test_config()))
    print()
    results.append(("IR Schema", test_ir_schema()))
    print()
    
    print("="*50)
    print("Test Results:")
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {name}: {status}")
    
    all_passed = all(result for _, result in results)
    if all_passed:
        print("\n🎉 All basic tests passed!")
    else:
        print("\n⚠️  Some tests failed. Check errors above.")
