#!/usr/bin/env python3
"""
Doculyze - A flexible document analysis tool.

This tool can analyze various types of documents using LLMs and provides both
CLI and GUI interfaces.
"""
from __future__ import annotations

import sys
import os
from pathlib import Path
from typing import Optional, Dict, Any
import json
import yaml
import typer
from rich.console import Console
from rich.table import Table

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

# Direct imports to avoid triggering apps.__init__.py
sys.path.insert(0, str(Path(__file__).parent / "apps" / "doculyze"))

try:
    from config import ConfigManager
    from analyzer import GenericAnalyzer  
    from preprocessor import GenericPreprocessor
    # Optional GUI support
    try:
        from cli_gui_decorator import gui_mode, needs_gui_support
        GUI_AVAILABLE = True
    except ImportError:
        GUI_AVAILABLE = False
        # Create dummy decorator if GUI not available
        def gui_mode(func):
            return func
except ImportError as e:
    print(f"Import error: {e}")
    print("Make sure all dependencies are installed and paths are correct")
    sys.exit(1)

# Initialize Typer app
app = typer.Typer(
    name="doculyze",
    help="Analyze documents using configurable LLM prompts and extraction methods.",
    add_completion=False,
)

console = Console()
config_manager = ConfigManager()


@app.callback()
def main(
    ctx: typer.Context,
    gui: bool = typer.Option(False, "--gui", help="Launch GUI interface instead of CLI"),
    config: Optional[Path] = typer.Option(None, "--config", help="Configuration file path"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose output"),
):
    """Doculyze - Flexible document analysis tool."""
    ctx.ensure_object(dict)
    ctx.obj["gui"] = gui
    ctx.obj["config"] = config
    ctx.obj["verbose"] = verbose
    
    if gui and not GUI_AVAILABLE:
        console.print("[red]GUI mode requested but GUI components are not available.[/red]")
        console.print("Install GUI dependencies with: pip install gooey wxpython")
        raise typer.Exit(1)
    
    if config:
        try:
            config_manager.load_config(config)
            if verbose:
                console.print(f"[green]Loaded configuration:[/green] {config}")
        except Exception as e:
            console.print(f"[red]Failed to load config {config}: {e}[/red]")
            raise typer.Exit(1)
    
    if verbose:
        console.print(f"[green]Configuration:[/green] {config or 'default templates'}")


@app.command()
@gui_mode
def analyze(
    ctx: typer.Context,
    path: Path = typer.Argument(..., help="Path to documents or folder containing documents"),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Output directory for results"),
    config_key: Optional[str] = typer.Option(None, "--config-key", help="Override config section to use"),
    context: Optional[str] = typer.Option(None, "--context", help="Analysis context"),
    document_type: Optional[str] = typer.Option(None, "--document-type", help="Type of document being analyzed"),
):
    """Analyze documents using LLM inference."""
    try:
        config = config_manager.get_analysis_config(config_key)
        
        analyzer = GenericAnalyzer(
            path=path,
            output_dir=output,
            config=config,
            gui_mode=ctx.obj.get("gui", False)
        )
        
        if ctx.obj.get("verbose"):
            console.print("[green]Analysis configuration:[/green]")
            console.print_json(data=config)
        
        # Prepare context for analysis
        analysis_context = {}
        if context:
            analysis_context["context"] = context
        if document_type:
            analysis_context["document_type"] = document_type
            
        results = analyzer.analyze(**analysis_context)
        
        if not ctx.obj.get("gui", False):
            console.print("[green]Analysis completed![/green]")
            console.print(f"Results saved to: {analyzer.output_dir}")
            console.print(f"Processed {len(results)} files")
        
    except Exception as e:
        console.print(f"[red]Analysis failed: {e}[/red]")
        raise typer.Exit(1)


@app.command()
@gui_mode
def preprocess(
    ctx: typer.Context,
    path: Path = typer.Argument(..., help="Path to document or folder containing documents"),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Output directory"),
    operation: str = typer.Option("extract", "--operation", help="Preprocessing operation: extract, split, trim, convert, analyze_structure"),
    config_key: Optional[str] = typer.Option(None, "--config-key", help="Override config section to use"),
):
    """Preprocess documents (extract text, split, trim, etc.)."""
    try:
        config = config_manager.get_preprocessing_config(config_key)
        
        preprocessor = GenericPreprocessor(
            path=path,
            output_dir=output,
            operation=operation,
            config=config,
            gui_mode=ctx.obj.get("gui", False)
        )
        
        if ctx.obj.get("verbose"):
            console.print("[green]Preprocessing configuration:[/green]")
            console.print_json(data=config)
        
        results = preprocessor.process()
        
        if not ctx.obj.get("gui", False):
            console.print("[green]Preprocessing completed![/green]")
            console.print(f"Results saved to: {preprocessor.output_dir}")
            console.print(f"Processed {len(results)} files")
        
    except Exception as e:
        console.print(f"[red]Preprocessing failed: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def config_show(
    section: Optional[str] = typer.Argument(None, help="Configuration section to show"),
):
    """Show current configuration."""
    try:
        if section:
            config = config_manager.get_section(section)
            if config:
                console.print(f"[green]Configuration section '{section}':[/green]")
                console.print_json(data=config)
            else:
                console.print(f"[red]Section '{section}' not found[/red]")
        else:
            config = config_manager.get_all_config()
            if config:
                console.print("[green]Full configuration:[/green]")
                console.print_json(data=config)
            else:
                console.print("[yellow]No configuration loaded. Available templates:[/yellow]")
                templates = config_manager.list_templates()
                for template in templates:
                    console.print(f"  • {template}")
    except Exception as e:
        console.print(f"[red]Failed to show config: {e}[/red]")


@app.command()
def config_create(
    name: str = typer.Argument(..., help="Configuration file name"),
    template: str = typer.Option("legal", "--template", help="Template type: legal, medical, contracts, etc."),
):
    """Create a new configuration file from template."""
    try:
        config_path = config_manager.create_config_from_template(name, template)
        console.print(f"[green]Created configuration file:[/green] {config_path}")
        console.print("Edit this file to customize your analysis parameters.")
    except Exception as e:
        console.print(f"[red]Failed to create config: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def list_configs():
    """List available configuration templates and files."""
    try:
        templates = config_manager.list_templates()
        configs = config_manager.list_configs()
        
        if templates:
            console.print("[green]Available templates:[/green]")
            for template in templates:
                console.print(f"  • {template}")
        
        if configs:
            console.print("\n[green]Available configuration files:[/green]")
            for config in configs:
                console.print(f"  • {config}")
        
        if not templates and not configs:
            console.print("[yellow]No templates or configurations found[/yellow]")
    except Exception as e:
        console.print(f"[red]Failed to list configs: {e}[/red]")


@app.command()
def test_extract(
    file_path: Path = typer.Argument(..., help="Path to test file"),
):
    """Test text extraction from a single file."""
    try:
        sys.path.insert(0, str(Path(__file__).parent / "apps" / "doculyze"))
        from file_processor import FileProcessor
        
        processor = FileProcessor()
        
        if not file_path.exists():
            console.print(f"[red]File not found: {file_path}[/red]")
            raise typer.Exit(1)
        
        console.print(f"[blue]Testing extraction from:[/blue] {file_path}")
        
        # Get file info
        info = processor.get_file_info(file_path)
        console.print("[green]File info:[/green]")
        console.print_json(data=info)
        
        # Extract text
        text = processor.extract_text(file_path)
        
        console.print(f"[green]Extracted text length:[/green] {len(text)} characters")
        
        # Show first 500 characters
        if text:
            preview = text[:500] + "..." if len(text) > 500 else text
            console.print("[green]Text preview:[/green]")
            console.print(preview)
        else:
            console.print("[yellow]No text extracted[/yellow]")
            
    except Exception as e:
        console.print(f"[red]Extraction test failed: {e}[/red]")
        raise typer.Exit(1)


if __name__ == "__main__":
    app()