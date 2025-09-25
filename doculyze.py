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

# Add apps to path
sys.path.insert(0, str(Path(__file__).parent))

try:
    from apps.common_simple import console as app_console
    from apps.doculyze.cli_gui_decorator import gui_mode, needs_gui_support
    from apps.doculyze.config import ConfigManager
    from apps.doculyze.analyzer import GenericAnalyzer
    from apps.doculyze.preprocessor import GenericPreprocessor
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
    
    if config:
        config_manager.load_config(config)
    
    if verbose:
        console.print(f"[green]Using configuration:[/green] {config or 'default'}")


@app.command()
@gui_mode
def analyze(
    ctx: typer.Context,
    path: Path = typer.Argument(..., help="Path to documents or folder containing documents"),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Output directory for results"),
    config_override: Optional[str] = typer.Option(None, "--config-key", help="Override config section to use"),
):
    """Analyze documents using LLM inference."""
    config = config_manager.get_analysis_config(config_override)
    
    analyzer = GenericAnalyzer(
        path=path,
        output_dir=output,
        config=config,
        gui_mode=ctx.obj.get("gui", False)
    )
    
    if ctx.obj.get("verbose"):
        console.print("[green]Analysis configuration:[/green]")
        console.print_json(data=config)
    
    results = analyzer.analyze()
    
    if not ctx.obj.get("gui", False):
        console.print("[green]Analysis completed![/green]")
        console.print(f"Results saved to: {analyzer.output_dir}")


@app.command()
@gui_mode
def preprocess(
    ctx: typer.Context,
    path: Path = typer.Argument(..., help="Path to document or folder containing documents"),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Output directory"),
    operation: str = typer.Option("extract", "--operation", help="Preprocessing operation: extract, split, trim"),
    config_override: Optional[str] = typer.Option(None, "--config-key", help="Override config section to use"),
):
    """Preprocess documents (extract text, split, trim, etc.)."""
    config = config_manager.get_preprocessing_config(config_override)
    
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


@app.command()
def config_show(
    section: Optional[str] = typer.Argument(None, help="Configuration section to show"),
):
    """Show current configuration."""
    if section:
        config = config_manager.get_section(section)
        if config:
            console.print(f"[green]Configuration section '{section}':[/green]")
            console.print_json(data=config)
        else:
            console.print(f"[red]Section '{section}' not found[/red]")
    else:
        config = config_manager.get_all_config()
        console.print("[green]Full configuration:[/green]")
        console.print_json(data=config)


@app.command()
def config_create(
    name: str = typer.Argument(..., help="Configuration file name"),
    template: str = typer.Option("legal", "--template", help="Template type: legal, medical, contracts, etc."),
):
    """Create a new configuration file from template."""
    config_path = config_manager.create_config_from_template(name, template)
    console.print(f"[green]Created configuration file:[/green] {config_path}")
    console.print("Edit this file to customize your analysis parameters.")


@app.command()
def list_configs():
    """List available configuration templates and files."""
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


if __name__ == "__main__":
    app()