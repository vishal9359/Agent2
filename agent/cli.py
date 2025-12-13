"""CLI Interface for C++ Flowchart Agent"""

import click
import sys
from pathlib import Path

from agent.main import CppFlowchartAgent


@click.command()
@click.option("--project", "-p", required=True, help="Path to C++ project")
@click.option("--type", "-t", default="flowchart", 
              type=click.Choice(["flowchart", "sequence", "architecture"]),
              help="Diagram type")
@click.option("--scope", "-s", default=None, help="Scope (module path or function name)")
@click.option("--format", "-f", default="plantuml",
              type=click.Choice(["plantuml", "mermaid"]),
              help="Diagram format")
@click.option("--output", "-o", default=None, help="Output file path")
@click.option("--ollama-url", default="http://localhost:11434", help="Ollama base URL")
@click.option("--llm-model", default="qwen2.5:latest", help="LLM model name")
@click.option("--embedding-model", default="jina/jina-embeddings", help="Embedding model name")
@click.option("--force-rebuild", is_flag=True, help="Force rebuild of analysis cache")
def main(project, type, scope, format, output, ollama_url, llm_model, 
         embedding_model, force_rebuild):
    """Generate flowcharts for C++ projects"""
    
    try:
        # Initialize agent
        click.echo(f"Initializing agent for project: {project}")
        agent = CppFlowchartAgent(
            project_path=project,
            ollama_base_url=ollama_url,
            llm_model=llm_model,
            embedding_model=embedding_model
        )
        
        # Analyze project
        click.echo("Analyzing project...")
        agent.analyze_project(force_rebuild=force_rebuild)
        
        # Generate diagram
        click.echo(f"Generating {type} diagram...")
        result = agent.generate_flowchart(
            scope=scope,
            diagram_type=type,
            diagram_format=format
        )
        
        if result.get("error"):
            click.echo(f"Error: {result['error']}", err=True)
            sys.exit(1)
        
        # Output result
        diagram_code = result.get("diagram_code", "")
        
        if output:
            output_path = Path(output)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(diagram_code)
            click.echo(f"Diagram saved to: {output_path}")
        else:
            click.echo("\n" + "="*80)
            click.echo("DIAGRAM CODE:")
            click.echo("="*80)
            click.echo(diagram_code)
            click.echo("="*80)
        
        # Show validation results
        validation = result.get("validation", {})
        if validation.get("valid"):
            click.echo("\n✓ Diagram validation passed")
        else:
            errors = validation.get("errors", [])
            if errors:
                click.echo(f"\n✗ Diagram validation failed: {errors}", err=True)
        
        # Show explanation
        explanation = result.get("explanation", "")
        if explanation:
            click.echo("\n" + explanation)
        
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
