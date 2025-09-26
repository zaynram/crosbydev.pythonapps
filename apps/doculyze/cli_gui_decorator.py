"""
Decorators for handling CLI/GUI mode switching with Typer and Gooey integration.
"""
from __future__ import annotations

import functools
import sys
from typing import Callable, Any, Dict, Optional
import typer

# Import gooey components - make them optional in case not available
try:
    from gooey import Gooey, GooeyParser
    GOOEY_AVAILABLE = True
except ImportError:
    GOOEY_AVAILABLE = False
    # Mock classes if gooey is not available
    class Gooey:
        def __init__(self, *args, **kwargs):
            pass
        def __call__(self, func):
            return func
    
    class GooeyParser:
        def __init__(self, *args, **kwargs):
            pass


def needs_gui_support(func: Callable) -> Callable:
    """Decorator to mark functions that need GUI support."""
    func._needs_gui = True
    return func


def gui_mode(func: Callable) -> Callable:
    """
    Decorator that enables GUI mode for Typer commands when --gui flag is used.
    
    This decorator detects if the --gui flag is present and launches the GUI version
    using Gooey, otherwise runs the normal CLI version.
    """
    
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Get context from args
        ctx = None
        for arg in args:
            if isinstance(arg, typer.Context):
                ctx = arg
                break
        
        # Check if GUI mode is requested
        if ctx and ctx.obj and ctx.obj.get("gui", False):
            if not GOOEY_AVAILABLE:
                typer.echo("Error: GUI mode requested but Gooey is not available.", err=True)
                typer.echo("Install with: pip install gooey", err=True)
                raise typer.Exit(1)
            
            # Launch GUI version
            return _launch_gui_mode(func, *args, **kwargs)
        else:
            # Run normal CLI version
            return func(*args, **kwargs)
    
    return wrapper


def _launch_gui_mode(func: Callable, *args, **kwargs) -> Any:
    """Launch the GUI version of a command using Gooey."""
    
    # Get the command name from the function
    command_name = getattr(func, '__name__', 'Command')
    
    # Create a Gooey wrapper
    @Gooey(
        program_name=f"Doculyze - {command_name.title()}",
        program_description=f"GUI interface for {command_name} command",
        default_size=(800, 600),
        show_help_button=True,
        show_config_button=True,
        menu=[{
            'name': 'File',
            'items': [{
                'type': 'AboutDialog',
                'menuTitle': 'About',
                'name': 'Doculyze',
                'description': 'Document analysis tool with LLM integration',
                'version': '1.0.0'
            }]
        }]
    )
    def gui_wrapper():
        # Create argument parser that mimics Typer structure
        parser = GooeyParser(description=f"GUI for {command_name} command")
        
        # Add arguments based on the function signature
        _add_arguments_from_function(parser, func)
        
        # Parse arguments
        args = parser.parse_args()
        
        # Convert args to the format expected by the original function
        converted_args, converted_kwargs = _convert_gui_args(args)
        
        # Call the original function
        return func(*converted_args, **converted_kwargs)
    
    # Execute the GUI wrapper
    return gui_wrapper()


def _add_arguments_from_function(parser: GooeyParser, func: Callable) -> None:
    """Add arguments to GooeyParser based on Typer function signature."""
    import inspect
    
    sig = inspect.signature(func)
    
    for param_name, param in sig.parameters.items():
        if param_name == 'ctx':  # Skip context parameter
            continue
            
        # Get type annotation
        param_type = param.annotation if param.annotation != inspect.Parameter.empty else str
        
        # Determine if it's required
        required = param.default == inspect.Parameter.empty
        
        # Add argument
        if param_type == typer.FileText or param_type == 'Path':
            parser.add_argument(
                f'--{param_name}',
                required=required,
                widget='FileChooser',
                help=f'{param_name.replace("_", " ").title()}'
            )
        elif param_type == bool:
            parser.add_argument(
                f'--{param_name}',
                action='store_true',
                help=f'{param_name.replace("_", " ").title()}'
            )
        else:
            parser.add_argument(
                f'--{param_name}',
                required=required,
                type=str,
                help=f'{param_name.replace("_", " ").title()}'
            )


def _convert_gui_args(args: Any) -> tuple[list, dict]:
    """Convert GUI parsed arguments to format expected by Typer function."""
    # Create a mock context object
    class MockContext:
        def __init__(self):
            self.obj = {"gui": True}
    
    converted_args = [MockContext()]
    converted_kwargs = {}
    
    # Convert all parsed arguments to kwargs
    for key, value in vars(args).items():
        if value is not None:
            converted_kwargs[key] = value
    
    return converted_args, converted_kwargs