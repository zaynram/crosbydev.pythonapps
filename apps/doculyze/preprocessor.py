"""
Generic document preprocessor that handles multiple file formats and operations.
Enhanced from the original PDF-only preprocessor.
"""
from __future__ import annotations

import shutil
from pathlib import Path
from typing import Dict, Any, List, Optional, Union, Generator
import datetime as dt

import sys
from pathlib import Path

# Add parent directories to path to find modules
sys.path.insert(0, str(Path(__file__).parent.parent))
from common_simple import console, track, timings
from file_processor import FileProcessor

# Import PyMuPDF for PDF operations
try:
    import fitz
    PYMUPDF_AVAILABLE = True
except ImportError:
    PYMUPDF_AVAILABLE = False


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
    
    def _get_split_path(self, file_path: Path, suffix: str = "") -> Path:
        """Generate output path for split documents."""
        suffix_with_ext = suffix if f"{file_path.suffix}" in suffix else f"{suffix}{file_path.suffix}"
        return self.output_dir / f"{file_path.stem}{suffix_with_ext}"
    
    def _clone_pdf_pages(
        self,
        src_path: Path,
        from_page: int,
        to_page: int,
        output_path: Path,
        start_at: int = -1,
    ) -> bool:
        """Clone specific pages from a PDF document using PyMuPDF."""
        if not PYMUPDF_AVAILABLE:
            console.log("PyMuPDF not available for PDF operations")
            return False
            
        try:
            src = fitz.open(src_path)
            out = fitz.open()
            out.insert_pdf(src, from_page=from_page, to_page=to_page, start_at=start_at)
            out.save(output_path)
            src.close()
            out.close()
            return True
        except Exception as e:
            console.error(f"Failed to clone PDF pages: {e}")
            return False
    
    def _split_pdf(self, file_path: Path, split_indices: List[int]) -> List[Dict[str, Any]]:
        """Split PDF file at specified page indices using PyMuPDF."""
        results = []
        
        if not PYMUPDF_AVAILABLE:
            return [{
                "operation": "split",
                "input_file": str(file_path),
                "success": False,
                "error": "PyMuPDF not available. Install with: pip install pymupdf",
                "timestamp": dt.datetime.now().isoformat()
            }]
        
        try:
            # Open PDF to get total page count
            doc = fitz.open(file_path)
            total_pages = len(doc)
            doc.close()
            
            # Sort split indices and add boundaries
            indices = sorted(set(split_indices))
            if indices and indices[0] != 1:
                indices.insert(0, 1)
            if indices and indices[-1] != total_pages:
                indices.append(total_pages)
            
            # Create splits
            for i in range(len(indices) - 1):
                from_page = indices[i] - 1  # Convert to 0-based indexing
                to_page = indices[i + 1] - 1
                
                suffix = f"_split_{indices[i]}-{indices[i + 1]}"
                output_path = self._get_split_path(file_path, suffix)
                
                success = self._clone_pdf_pages(
                    file_path, from_page, to_page, output_path, start_at=0
                )
                
                results.append({
                    "operation": "split",
                    "input_file": str(file_path),
                    "output_file": str(output_path),
                    "pages": f"{indices[i]}-{indices[i + 1]}",
                    "success": success,
                    "timestamp": dt.datetime.now().isoformat()
                })
                
                if success:
                    console.log(f"Split PDF pages {indices[i]}-{indices[i + 1]} -> {output_path.name}")
                else:
                    console.error(f"Failed to split PDF pages {indices[i]}-{indices[i + 1]}")
                    
            return results
            
        except Exception as e:
            console.error(f"Failed to split PDF {file_path.name}: {e}")
            return [{
                "operation": "split",
                "input_file": str(file_path),
                "success": False,
                "error": str(e),
                "timestamp": dt.datetime.now().isoformat()
            }]
    
    def _trim_pdf(self, file_path: Path, start_page: int, end_page: int) -> Dict[str, Any]:
        """Trim PDF to specific page range using PyMuPDF."""
        if not PYMUPDF_AVAILABLE:
            return {
                "operation": "trim",
                "input_file": str(file_path),
                "success": False,
                "error": "PyMuPDF not available. Install with: pip install pymupdf",
                "timestamp": dt.datetime.now().isoformat()
            }
        
        try:
            # Open PDF to get total page count
            doc = fitz.open(file_path)
            total_pages = len(doc)
            doc.close()
            
            # Validate page range
            start_page = max(1, start_page)
            end_page = min(total_pages, end_page) if end_page > 0 else total_pages
            
            suffix = f"_trim_{start_page}-{end_page}"
            output_path = self._get_split_path(file_path, suffix)
            
            # Convert to 0-based indexing for PyMuPDF
            from_page = start_page - 1
            to_page = end_page - 1
            
            success = self._clone_pdf_pages(file_path, from_page, to_page, output_path)
            
            result = {
                "operation": "trim",
                "input_file": str(file_path),
                "output_file": str(output_path),
                "pages": f"{start_page}-{end_page}",
                "success": success,
                "timestamp": dt.datetime.now().isoformat()
            }
            
            if success:
                console.log(f"Trimmed PDF to pages {start_page}-{end_page} -> {output_path.name}")
            else:
                console.error(f"Failed to trim PDF to pages {start_page}-{end_page}")
                result["error"] = "Failed to clone PDF pages"
                
            return result
            
        except Exception as e:
            console.error(f"Failed to trim PDF {file_path.name}: {e}")
            return {
                "operation": "trim",
                "input_file": str(file_path),
                "success": False,
                "error": str(e),
                "timestamp": dt.datetime.now().isoformat()
            }
    
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