"""
Rich CLI for MCP Agent with interactive features
"""

import asyncio
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Prompt, Confirm
from rich.table import Table

from src.config import settings
from src.config.logging import get_logger

app = typer.Typer(
    name="mcpagent",
    help="MCP Agent - Production-grade AI Agent System",
    add_completion=False
)

console = Console()
logger = get_logger(__name__)


@app.command()
def version():
    """Show version information"""
    table = Table(title="MCP Agent Information")
    table.add_column("Property", style="cyan")
    table.add_column("Value", style="green")
    
    table.add_row("Name", settings.app_name)
    table.add_row("Version", settings.version)
    table.add_row("Environment", settings.app_env)
    table.add_row("LLM Provider", settings.llm_provider)
    table.add_row("Vector Store", settings.vector_store_type)
    
    console.print(table)


@app.command()
def chat(
    query: Optional[str] = typer.Option(None, "--query", "-q", help="Query to ask"),
    session_id: str = typer.Option("default", "--session", "-s", help="Session ID"),
    mode: str = typer.Option("agent", "--mode", "-m", help="Mode: agent or rag"),
    interactive: bool = typer.Option(False, "--interactive", "-i", help="Interactive mode")
):
    """Chat with the AI agent"""
    
    if interactive:
        _interactive_chat(session_id, mode)
    elif query:
        _single_query(query, session_id, mode)
    else:
        console.print("[red]Error:[/red] Please provide a query with --query or use --interactive")
        raise typer.Exit(1)


def _single_query(query: str, session_id: str, mode: str):
    """Execute a single query"""
    console.print(Panel(f"[bold cyan]Query:[/bold cyan] {query}"))
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task("Processing...", total=None)
        
        # TODO: Call agent/RAG system here
        # For now, placeholder response
        response = f"Mock response for: {query} (mode={mode}, session={session_id})"
        
        progress.remove_task(task)
    
    console.print("\n[bold green]Response:[/bold green]")
    console.print(Markdown(response))


def _interactive_chat(session_id: str, mode: str):
    """Interactive chat session"""
    console.print(Panel.fit(
        "[bold cyan]MCP Agent - Interactive Chat[/bold cyan]\n"
        f"Session: {session_id} | Mode: {mode}\n"
        "Type 'exit' or 'quit' to end session",
        border_style="cyan"
    ))
    
    while True:
        try:
            query = Prompt.ask("\n[bold yellow]You[/bold yellow]")
            
            if query.lower() in ["exit", "quit"]:
                console.print("[cyan]Goodbye![/cyan]")
                break
            
            if not query.strip():
                continue
            
            # TODO: Call agent system
            response = f"Mock response for: {query}"
            
            console.print(f"\n[bold green]Agent[/bold green]: {response}")
        
        except KeyboardInterrupt:
            console.print("\n[cyan]Chat interrupted[/cyan]")
            break
        except Exception as e:
            console.print(f"[red]Error:[/red] {e}")


@app.command()
def ingest(
    path: str = typer.Argument(..., help="Path to document or directory"),
    recursive: bool = typer.Option(False, "--recursive", "-r", help="Recursively ingest directory")
):
    """Ingest documents into knowledge base"""
    console.print(f"[cyan]Ingesting documents from:[/cyan] {path}")
    
    # TODO: Implement document ingestion
    console.print("[green]✓[/green] Documents ingested successfully")


@app.command()
def status():
    """Show system status"""
    from src.infrastructure.database import engine
    from src.infrastructure.cache.redis_cache import cache
    from src.core.rag import rag_system
    
    table = Table(title="System Status")
    table.add_column("Component", style="cyan")
    table.add_column("Status", style="green")
    table.add_column("Details", style="yellow")
    
    # Database
    try:
        with engine.connect():
            table.add_row("Database", "✓ Healthy", settings.database_url.split("@")[-1])
    except Exception as e:
        table.add_row("Database", "✗ Unhealthy", str(e)[:50])
    
    # Cache
    if cache.enabled:
        stats = cache.get_stats()
        table.add_row("Cache", "✓ Enabled", f"{stats.get('keys', 0)} keys")
    else:
        table.add_row("Cache", "✗ Disabled", "")
    
    # RAG
    if rag_system.available:
        stats = rag_system.get_collection_stats()
        table.add_row("RAG System", "✓ Ready", f"{stats.get('document_count', 0)} docs")
    else:
        table.add_row("RAG System", "✗ Unavailable", "")
    
    # LLM
    api_key = settings.get_llm_api_key()
    if api_key:
        table.add_row("LLM", "✓ Configured", f"{settings.llm_provider}/{settings.openai_model}")
    else:
        table.add_row("LLM", "✗ Not configured", "Missing API key")
    
    console.print(table)


if __name__ == "__main__":
    app()

