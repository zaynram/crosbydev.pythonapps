# PDF Operations with Doculyze

This document explains how to use the PDF splitting and trimming functionality that has been restored from the original implementation.

## PDF Splitting

Split PDF documents at specified page numbers using PyMuPDF.

### Configuration

Create a configuration file or specify parameters for splitting:

```yaml
# config.yaml
preprocessing:
  split_indices: [3, 7, 10]  # Split at pages 3, 7, and 10
```

### Usage Examples

**Using configuration file:**
```bash
python main.py preprocess document.pdf --operation split --config config.yaml
```

**Direct usage (if supported by CLI):**
```bash
# This would split a 10-page PDF into 4 parts:
# - Pages 1-3
# - Pages 3-7  
# - Pages 7-10
# - Pages 10-end
```

### How it Works

The splitting operation:
1. Takes a list of page numbers (1-based indexing)
2. Creates separate PDF files for each section
3. Names output files with the format: `original_name_split_X-Y.pdf`
4. Preserves the original document formatting and structure

## PDF Trimming

Extract specific page ranges from PDF documents.

### Configuration

```yaml
# config.yaml
preprocessing:
  trim_start: 5    # Start from page 5
  trim_end: 15     # End at page 15
```

### Usage Examples

**Extract pages 5-15 from a document:**
```bash
python main.py preprocess document.pdf --operation trim --config config.yaml
```

### How it Works

The trimming operation:
1. Takes start and end page numbers (1-based indexing)  
2. Creates a new PDF with only the specified page range
3. Names output file with the format: `original_name_trim_X-Y.pdf`
4. Handles edge cases (start < 1 becomes 1, end > total_pages becomes total_pages)

## Technical Implementation

Both operations use **PyMuPDF (fitz)** library for robust PDF manipulation:

- **Graceful degradation**: If PyMuPDF is not available, operations return informative error messages
- **Error handling**: Comprehensive error reporting for invalid page ranges or file issues
- **Performance**: Efficient page cloning without full document reprocessing
- **Compatibility**: Works with complex PDF documents including forms, annotations, and images

## Requirements

- PyMuPDF >= 1.26.4 (included in pixi.toml dependencies)
- Input PDF files must be readable and not password-protected

## Examples

### Split a Legal Document

```bash
# Split a 50-page contract at logical sections
python main.py preprocess contract.pdf --operation split
# With configuration: split_indices: [10, 25, 40]
# Creates: contract_split_1-10.pdf, contract_split_10-25.pdf, etc.
```

### Extract Relevant Pages from Medical Records

```bash
# Extract only pages 15-30 from a large medical file
python main.py preprocess medical_record.pdf --operation trim  
# With configuration: trim_start: 15, trim_end: 30
# Creates: medical_record_trim_15-30.pdf
```

## Error Handling

Common scenarios handled:
- **Invalid page numbers**: Automatically adjusted to valid ranges
- **Missing PyMuPDF**: Clear error message with installation instructions
- **Corrupted PDFs**: Detailed error reporting
- **Permission issues**: Informative file access error messages

The implementation maintains full compatibility with the original Doculyze preprocessing functionality while providing enhanced error handling and logging.