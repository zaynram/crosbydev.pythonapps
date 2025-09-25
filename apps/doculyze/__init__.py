"""Doculyze - Generic document analysis framework."""

__all__ = [
    "GenericAnalyzer",
    "GenericPreprocessor", 
    "ConfigManager",
    "gui_mode",
]

from .analyzer import GenericAnalyzer
from .preprocessor import GenericPreprocessor
from .config import ConfigManager
from .cli_gui_decorator import gui_mode