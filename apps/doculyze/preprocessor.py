"""
Generic document preprocessor that handles multiple file formats and operations.
Enhanced from the original PDF-only preprocessor.
"""
from __future__ import annotations

import shutil
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
import datetime as dt

import sys
from pathlib import Path

# Add parent directories to path to find modules
sys.path.insert(0, str(Path(__file__).parent.parent))
from common_simple import console, track, timings
from file_processor import FileProcessor


class GenericPreprocessor:
    """Generic document preprocessor with enhanced functionality."""
    
    def __init__(
        self,
        path: Path,
        output_dir: Optional[Path] = None,
        operation: str = "extract",
        config: Optional[Dict[str, Any]] = None,
        gui_mode: bool = False
    ):
        self.path = Path(path).resolve()
        
        # Handle output directory for single files vs directories
        if output_dir:
            self.output_dir = Path(output_dir)
        elif self.path.is_file():
            self.output_dir = self.path.parent / "preprocessed"
        else:
            self.output_dir = self.path / "preprocessed"
            
        self.operation = operation
        self.gui_mode = gui_mode
        self.config = config or {}
        
        # Initialize file processor
        self.file_processor = FileProcessor(self.config)
        
        # Configuration parameters
        self.supported_formats = self.config.get("supported_formats", [".pdf", ".docx", ".doc", ".txt"])
        self.extract_text = self.config.get("extract_text", True)
        self.clean_text = self.config.get("clean_text", True)
        self.keep_original = self.config.get("keep_original", True)
        
        # Create output directory
        self.output_dir.mkdir(exist_ok=True)
    
    def process(self) -> List[Dict[str, Any]]:
        """Process documents based on the specified operation."""
        console.log(f"Starting preprocessing with operation: {self.operation}")
        
        # Get list of files to process
        files_to_process = self._get_files_to_process()
        
        if not files_to_process:
            console.log("No supported files found for preprocessing")
            return []
        
        console.log(f"Found {len(files_to_process)} files to process")
        
        results = []
        
        if self.operation == "extract":
            results = self._extract_text_operation(files_to_process)
        elif self.operation == "split":
            results = self._split_operation(files_to_process)
        elif self.operation == "trim":
            results = self._trim_operation(files_to_process)
        elif self.operation == "convert":
            results = self._convert_operation(files_to_process)
        elif self.operation == "analyze_structure":
            results = self._analyze_structure_operation(files_to_process)
        else:
            console.error(f"Unknown operation: {self.operation}")
            return []
        
        # Save processing summary
        self._save_processing_summary(results)
        
        console.log(f"Preprocessing completed. {len(results)} files processed.")
        return results
    
    def _get_files_to_process(self) -> List[Path]:
        """Get list of files to process based on path and supported formats."""
        if self.path.is_file():
            if self.path.suffix.lower() in self.supported_formats:
                return [self.path]
            else:
                console.log(f"File format not supported: {self.path.suffix}")
                return []
        else:
            return [
                f for f in self.path.iterdir()
                if f.is_file() and f.suffix.lower() in self.supported_formats
            ]
    
    def _extract_text_operation(self, files: List[Path]) -> List[Dict[str, Any]]:
        """Extract text from documents and save as .txt files."""
        results = []
        
        for file_path in track(files, "Extracting text"):
            try:
                # Extract text
                text = self.file_processor.extract_text(file_path)
                
                if not text.strip():
                    console.log(f"No text extracted from {file_path.name}")
                    continue
                
                # Save extracted text
                output_file = self.output_dir / f"{file_path.stem}_extracted.txt"
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(text)
                
                result = {
                    "operation": "extract",
                    "input_file": str(file_path),
                    "output_file": str(output_file),
                    "text_length": len(text),
                    "success": True,
                    "timestamp": dt.datetime.now().isoformat()
                }
                
                results.append(result)
                console.log(f"Extracted text from {file_path.name} -> {output_file.name}")
                
            except Exception as e:
                console.error(f"Failed to extract text from {file_path.name}: {e}")
                results.append({
                    "operation": "extract",
                    "input_file": str(file_path),
                    "success": False,
                    "error": str(e),
                    "timestamp": dt.datetime.now().isoformat()
                })
        
        return results
    
    def _split_operation(self, files: List[Path]) -> List[Dict[str, Any]]:
        """Split documents based on configuration."""
        results = []
        split_indices = self.config.get("split_indices", [])
        
        if not split_indices:
            console.log("No split indices specified, skipping split operation")
            return results
        
        for file_path in track(files, "Splitting documents"):
            try:
                if file_path.suffix.lower() == ".pdf":
                    result = self._split_pdf(file_path, split_indices)
                elif file_path.suffix.lower() in [".docx", ".doc"]:
                    result = self._split_word_document(file_path, split_indices)
                elif file_path.suffix.lower() == ".txt":
                    result = self._split_text_file(file_path, split_indices)
                else:
                    continue
                
                results.extend(result)
                
            except Exception as e:
                console.error(f"Failed to split {file_path.name}: {e}")
                results.append({
                    "operation": "split",
                    "input_file": str(file_path),
                    "success": False,
                    "error": str(e),
                    "timestamp": dt.datetime.now().isoformat()
                })
        
        return results
    
    def _trim_operation(self, files: List[Path]) -> List[Dict[str, Any]]:
        """Trim documents to specified page ranges."""
        results = []
        trim_start = self.config.get("trim_start", 0)
        trim_end = self.config.get("trim_end", -1)
        
        for file_path in track(files, "Trimming documents"):
            try:
                if file_path.suffix.lower() == ".pdf":
                    result = self._trim_pdf(file_path, trim_start, trim_end)
                else:
                    # For non-PDF files, trim by extracting text and splitting by paragraphs
                    result = self._trim_text_content(file_path, trim_start, trim_end)
                
                if result:
                    results.append(result)
                
            except Exception as e:
                console.error(f"Failed to trim {file_path.name}: {e}")
                results.append({
                    "operation": "trim",
                    "input_file": str(file_path),
                    "success": False,
                    "error": str(e),
                    "timestamp": dt.datetime.now().isoformat()
                })
        
        return results
    
    def _convert_operation(self, files: List[Path]) -> List[Dict[str, Any]]:
        """Convert documents between formats."""
        results = []
        target_format = self.config.get("target_format", ".txt")
        
        for file_path in track(files, "Converting documents"):
            try:
                if file_path.suffix.lower() == target_format:
                    console.log(f"Skipping {file_path.name} - already in target format")
                    continue
                
                # Extract text and save in target format
                text = self.file_processor.extract_text(file_path)
                
                if target_format == ".txt":
                    output_file = self.output_dir / f"{file_path.stem}_converted.txt"
                    with open(output_file, 'w', encoding='utf-8') as f:
                        f.write(text)
                else:
                    console.log(f"Conversion to {target_format} not yet supported")
                    continue
                
                result = {
                    "operation": "convert",
                    "input_file": str(file_path),
                    "output_file": str(output_file),
                    "source_format": file_path.suffix.lower(),
                    "target_format": target_format,
                    "success": True,
                    "timestamp": dt.datetime.now().isoformat()
                }
                
                results.append(result)
                console.log(f"Converted {file_path.name} -> {output_file.name}")
                
            except Exception as e:
                console.error(f"Failed to convert {file_path.name}: {e}")
                results.append({
                    "operation": "convert",
                    "input_file": str(file_path),
                    "success": False,
                    "error": str(e),
                    "timestamp": dt.datetime.now().isoformat()
                })
        
        return results
    
    def _analyze_structure_operation(self, files: List[Path]) -> List[Dict[str, Any]]:
        """Analyze document structure and metadata."""
        results = []
        
        for file_path in track(files, "Analyzing structure"):
            try:
                file_info = self.file_processor.get_file_info(file_path)
                
                # Add additional analysis
                text = self.file_processor.extract_text(file_path)
                
                analysis = {
                    "word_count": len(text.split()) if text else 0,
                    "character_count": len(text) if text else 0,
                    "paragraph_count": len([p for p in text.split('\n\n') if p.strip()]) if text else 0,
                    "has_text": bool(text and text.strip())
                }
                
                result = {
                    "operation": "analyze_structure",
                    "input_file": str(file_path),
                    "file_info": file_info,
                    "text_analysis": analysis,
                    "success": True,
                    "timestamp": dt.datetime.now().isoformat()
                }
                
                results.append(result)
                console.log(f"Analyzed {file_path.name}")
                
            except Exception as e:
                console.error(f"Failed to analyze {file_path.name}: {e}")
                results.append({
                    "operation": "analyze_structure",
                    "input_file": str(file_path),
                    "success": False,
                    "error": str(e),
                    "timestamp": dt.datetime.now().isoformat()
                })
        
        return results
    
    def _split_pdf(self, file_path: Path, split_indices: List[int]) -> List[Dict[str, Any]]:
        """Split PDF file at specified page indices."""
        # This would require PyMuPDF implementation
        # For now, return placeholder
        return [{
            "operation": "split",
            "input_file": str(file_path),
            "success": False,
            "error": "PDF splitting not yet implemented",
            "timestamp": dt.datetime.now().isoformat()
        }]
    
    def _split_word_document(self, file_path: Path, split_indices: List[int]) -> List[Dict[str, Any]]:
        """Split Word document at specified positions."""
        # This would require more complex document handling
        # For now, return placeholder
        return [{
            "operation": "split",
            "input_file": str(file_path),
            "success": False,
            "error": "Word document splitting not yet implemented",
            "timestamp": dt.datetime.now().isoformat()
        }]
    
    def _split_text_file(self, file_path: Path, split_indices: List[int]) -> List[Dict[str, Any]]:
        """Split text file at specified line numbers."""
        results = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # Split at specified line indices
            current_start = 0
            for i, split_index in enumerate(split_indices):
                if split_index > len(lines):
                    break
                
                chunk_lines = lines[current_start:split_index]
                if chunk_lines:
                    output_file = self.output_dir / f"{file_path.stem}_part_{i+1}.txt"
                    with open(output_file, 'w', encoding='utf-8') as f:
                        f.writelines(chunk_lines)
                    
                    results.append({
                        "operation": "split",
                        "input_file": str(file_path),
                        "output_file": str(output_file),
                        "part_number": i + 1,
                        "line_range": [current_start, split_index],
                        "success": True,
                        "timestamp": dt.datetime.now().isoformat()
                    })
                
                current_start = split_index
            
            # Handle remaining lines
            if current_start < len(lines):
                chunk_lines = lines[current_start:]
                output_file = self.output_dir / f"{file_path.stem}_part_{len(split_indices)+1}.txt"
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.writelines(chunk_lines)
                
                results.append({
                    "operation": "split",
                    "input_file": str(file_path),
                    "output_file": str(output_file),
                    "part_number": len(split_indices) + 1,
                    "line_range": [current_start, len(lines)],
                    "success": True,
                    "timestamp": dt.datetime.now().isoformat()
                })
        
        except Exception as e:
            results.append({
                "operation": "split",
                "input_file": str(file_path),
                "success": False,
                "error": str(e),
                "timestamp": dt.datetime.now().isoformat()
            })
        
        return results
    
    def _trim_pdf(self, file_path: Path, start: int, end: int) -> Dict[str, Any]:
        """Trim PDF to specified page range."""
        # This would require PyMuPDF implementation
        return {
            "operation": "trim",
            "input_file": str(file_path),
            "success": False,
            "error": "PDF trimming not yet implemented",
            "timestamp": dt.datetime.now().isoformat()
        }
    
    def _trim_text_content(self, file_path: Path, start: int, end: int) -> Dict[str, Any]:
        """Trim text content to specified range."""
        try:
            text = self.file_processor.extract_text(file_path)
            paragraphs = [p for p in text.split('\n\n') if p.strip()]
            
            if end == -1:
                end = len(paragraphs)
            
            trimmed_paragraphs = paragraphs[start:end]
            trimmed_text = '\n\n'.join(trimmed_paragraphs)
            
            output_file = self.output_dir / f"{file_path.stem}_trimmed{file_path.suffix}"
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(trimmed_text)
            
            return {
                "operation": "trim",
                "input_file": str(file_path),
                "output_file": str(output_file),
                "paragraph_range": [start, end],
                "success": True,
                "timestamp": dt.datetime.now().isoformat()
            }
        
        except Exception as e:
            return {
                "operation": "trim",
                "input_file": str(file_path),
                "success": False,
                "error": str(e),
                "timestamp": dt.datetime.now().isoformat()
            }
    
    def _save_processing_summary(self, results: List[Dict[str, Any]]) -> None:
        """Save processing summary to output directory."""
        if not results:
            return
        
        summary = {
            "operation": self.operation,
            "total_files": len(results),
            "successful": len([r for r in results if r.get("success", False)]),
            "failed": len([r for r in results if not r.get("success", False)]),
            "timestamp": dt.datetime.now().isoformat(),
            "configuration": self.config,
            "results": results
        }
        
        import json
        summary_file = self.output_dir / f"preprocessing_summary_{self.operation}.json"
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        
        console.log(f"Processing summary saved to: {summary_file}")