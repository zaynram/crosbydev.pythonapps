"""
Generic document analyzer that can be configured for different document types.
Replaces the medical-specific analyzer with a configurable approach.
"""
from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
import datetime as dt

# Optional imports for different backends
try:
    import ollama
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False

import sys
from pathlib import Path

# Add parent directories to path to find modules
sys.path.insert(0, str(Path(__file__).parent.parent))
from common_simple import console, track, retry, timings
from file_processor import FileProcessor
from validator import FlexibleValidator


class GenericAnalyzer:
    """Generic document analyzer using configurable prompts and LLM models."""
    
    def __init__(
        self,
        path: Path,
        output_dir: Optional[Path] = None,
        config: Optional[Dict[str, Any]] = None,
        gui_mode: bool = False
    ):
        self.path = Path(path).resolve()
        
        # Handle output directory for single files vs directories
        if output_dir:
            self.output_dir = Path(output_dir)
        elif self.path.is_file():
            self.output_dir = self.path.parent / "analysis"
        else:
            self.output_dir = self.path / "analysis"
            
        self.output_dir.mkdir(exist_ok=True)
        
        self.gui_mode = gui_mode
        self.config = config or {}
        
        # Extract configuration parameters
        self.system_prompt = self.config.get("system_prompt", "")
        self.prompt_template = self.config.get("prompt_template", "")
        self.response_schema = self.config.get("response_schema", {})
        self.model_id = self.config.get("model_id", "gemma3n:e4b")
        self.max_tokens = self.config.get("max_tokens", 16000)
        self.temperature = self.config.get("temperature", 0.2)
        
        # Initialize file processor
        self.file_processor = FileProcessor()
        
        # Initialize validator with flexible configuration
        validation_config = self.config.get("validation", {})
        self.validator = FlexibleValidator(validation_config)
    
    @property
    def _options(self) -> Optional[Any]:
        """Get LLM options based on available backend."""
        if OLLAMA_AVAILABLE:
            return ollama.Options(
                temperature=self.temperature,
                num_ctx=self.max_tokens,
                num_predict=4096,
                use_mlock=True,
                low_vram=True,
            )
        return None
    
    @retry(max_retries=3)
    def _pull_model(self) -> None:
        """Pull the specified model if using Ollama."""
        if not OLLAMA_AVAILABLE:
            console.log("Ollama not available, skipping model pull")
            return
            
        try:
            models = {m.model for m in ollama.list().models}
            if self.model_id not in models:
                console.log(f"Pulling model: {self.model_id}")
                ollama.pull(self.model_id)
        except Exception as e:
            console.error(f"Failed to pull model {self.model_id}: {e}")
            raise
    
    def _format_prompt(self, document_text: str, **context) -> str:
        """Format the prompt template with document text and context."""
        format_args = {
            'document_text': document_text,
            **context
        }
        
        try:
            return self.prompt_template.format(**format_args)
        except KeyError as e:
            console.error(f"Missing template variable: {e}")
            # Return a simple fallback
            return f"Analyze the following document:\n\n{document_text}"
    
    def _query_llm(self, prompt: str) -> Dict[str, Any]:
        """Query the LLM with the formatted prompt."""
        if not OLLAMA_AVAILABLE:
            # Return mock data for testing when Ollama is not available
            console.log("Ollama not available, returning mock results")
            return {
                "entities": ["Mock Entity 1", "Mock Entity 2"],
                "key_clauses": ["Mock Clause 1"],
                "dates": ["2024-01-01"],
                "obligations": ["Mock Obligation"]
            }
        
        try:
            response = ollama.generate(
                model=self.model_id,
                prompt=f"System: {self.system_prompt}\n\nUser: {prompt}",
                format='json',
                options=self._options,
            )
            
            result = json.loads(response.response)
            return result
            
        except json.JSONDecodeError as e:
            console.error(f"Failed to parse LLM response as JSON: {e}")
            raise
        except Exception as e:
            console.error(f"LLM query failed: {e}")
            raise
    
    def _analyze_document(self, file_path: Path, **context) -> Dict[str, Any]:
        """Analyze a single document."""
        console.log(f"Analyzing: {file_path.name}")
        
        # Extract text from document
        document_text = self.file_processor.extract_text(file_path)
        
        if not document_text.strip():
            console.log(f"No text extracted from {file_path.name}")
            return {}
        
        # Format prompt
        prompt = self._format_prompt(document_text, **context)
        
        # Query LLM
        analysis_results = self._query_llm(prompt)
        
        # Validate results
        validated_results, match_counts = self.validator.validate(
            document_text, analysis_results
        )
        
        return {
            "file": file_path.name,
            "analysis": analysis_results,
            "validation": validated_results,
            "match_counts": match_counts,
            "metadata": {
                "timestamp": dt.datetime.now().isoformat(),
                "model_id": self.model_id,
                "text_length": len(document_text)
            }
        }
    
    def analyze(self, **context) -> List[Dict[str, Any]]:
        """Analyze documents in the specified path."""
        console.log(f"Starting analysis of documents in: {self.path}")
        
        # Pull model if needed
        self._pull_model()
        
        # Get list of supported files
        supported_extensions = self.config.get("preprocessing", {}).get(
            "supported_formats", [".pdf", ".docx", ".doc", ".txt"]
        )
        
        if self.path.is_file():
            files = [self.path] if self.path.suffix.lower() in supported_extensions else []
        else:
            files = [
                f for f in self.path.iterdir() 
                if f.is_file() and f.suffix.lower() in supported_extensions
            ]
        
        if not files:
            console.log("No supported files found for analysis")
            return []
        
        console.log(f"Found {len(files)} files to analyze")
        
        # Analyze each file
        results = []
        for file_path in track(files, "Analyzing documents"):
            try:
                result = self._analyze_document(file_path, **context)
                if result:
                    results.append(result)
            except Exception as e:
                console.error(f"Failed to analyze {file_path.name}: {e}")
                continue
        
        # Save results
        self._save_results(results)
        
        console.log(f"Analysis completed. {len(results)} files processed.")
        return results
    
    def _save_results(self, results: List[Dict[str, Any]]) -> None:
        """Save analysis results to output directory."""
        if not results:
            return
        
        # Save individual results
        for result in results:
            filename = f"{Path(result['file']).stem}_analysis.json"
            output_file = self.output_dir / filename
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
        
        # Save summary
        summary = {
            "total_files": len(results),
            "timestamp": dt.datetime.now().isoformat(),
            "configuration": self.config,
            "results_summary": [
                {
                    "file": r["file"],
                    "analysis_keys": list(r.get("analysis", {}).keys()),
                    "match_counts": r.get("match_counts", {})
                }
                for r in results
            ]
        }
        
        summary_file = self.output_dir / "analysis_summary.json"
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        
        console.log(f"Results saved to: {self.output_dir}")
    
    @property
    def analysis_config(self) -> Dict[str, Any]:
        """Get the current analysis configuration."""
        return {
            "model_id": self.model_id,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "system_prompt": self.system_prompt,
            "prompt_template": self.prompt_template,
            "response_schema": self.response_schema,
            "output_directory": str(self.output_dir),
        }