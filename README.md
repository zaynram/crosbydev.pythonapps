# Doculyze - Flexible Document Analysis Tool

A powerful, configurable document analysis system that can analyze various types of legal, medical, and business documents using LLM-powered extraction and validation.

## Features

### ✅ Multi-Format Support
- **PDF**: OCR-enabled text extraction
- **DOCX**: Microsoft Word documents with table support
- **DOC**: Legacy Word document support
- **TXT**: Plain text with encoding detection

### ✅ CLI & GUI Interfaces
- **CLI**: Full-featured Typer-based command line interface
- **GUI**: Gooey-powered graphical interface (use `--gui` flag)
- Seamless switching between interfaces

### ✅ Configurable Analysis
- Template-based configuration system (YAML/JSON/TOML)
- Domain-specific prompt templates
- Flexible validation parameters
- Custom response schemas

### ✅ Built-in Document Types
- Legal contracts and agreements
- Litigation documents and court filings
- Medical records and reports
- Real estate transactions
- Custom document types via configuration

## Quick Start

### Installation

**Using Pixi (Recommended):**

Pixi provides reproducible environments and dependency management for this project.

```bash
# Option 1: Use the provided pixi.sh wrapper script
./pixi.sh install     # Install dependencies
./pixi.sh cli --help  # Show CLI help
./pixi.sh test        # Run basic tests

# Option 2: Use pixi directly
# Install pixi if not already installed
curl -fsSL https://pixi.sh/install.sh | bash

# Navigate to the project directory
cd doculyze

# Install dependencies and activate environment
pixi install

# Use pixi to run commands
pixi run cli --help                    # Show CLI help
pixi run analyze documents/            # Run document analysis
pixi run preprocess files/             # Run preprocessing

# Or activate the shell and run commands directly
pixi shell
python main.py --help
```

**Manual Installation:**
```bash
pip install typer[all] python-docx docx2txt pyyaml toml rich
# Optional: pip install gooey  # For GUI interface
# Optional: pip install ollama  # For LLM integration
```

### Basic Usage

```bash
# Show help
python main.py --help

# List available configurations
python main.py list-configs

# Test text extraction
python main.py test-extract document.pdf

# Analyze a document
python main.py --config configs/legal_contracts.yaml analyze contracts/agreement.docx

# Preprocess documents
python main.py preprocess documents/ --operation extract

# Create custom configuration
python main.py config-create my_config --template legal
```

## Pixi Tasks

The project includes several predefined pixi tasks for common operations:

```bash
# Show CLI help
pixi run cli --help

# Run document analysis
pixi run analyze document.pdf --context "Legal review"

# Run preprocessing  
pixi run preprocess documents/ --operation extract

# Run legacy application (for backwards compatibility)
pixi run app medscan
```

## Commands

### Analysis
```bash
# Single document
python main.py analyze document.pdf --context "Contract review"

# Batch analysis
python main.py analyze documents/ --config configs/legal_contracts.yaml

# With custom parameters
python main.py analyze contract.docx --context "M&A Due Diligence" --document-type "Purchase Agreement"
```

### Preprocessing
```bash
# Extract text from documents
python main.py preprocess documents/ --operation extract

# Analyze document structure
python main.py preprocess documents/ --operation analyze_structure

# Convert formats
python main.py preprocess document.docx --operation convert

# Split documents (configuration-based)
python main.py preprocess document.pdf --operation split

# Trim documents to specific ranges
python main.py preprocess document.pdf --operation trim
```

### Configuration Management
```bash
# Show current configuration
python main.py config-show

# Show specific section
python main.py --config myconfig.yaml config-show

# Create from template
python main.py config-create litigation --template legal

# List available templates and configs
python main.py list-configs
```

## Configuration System

### Sample Configuration Structure
```yaml
analysis:
  system_prompt: |
    You are a document analyst...
  prompt_template: |
    Analyze the following {document_type}:
    {document_text}
  response_schema:
    type: object
    properties:
      entities: { type: array, items: { type: string } }
      key_terms: { type: array, items: { type: string } }
  model_id: "gemma3n:e4b"
  max_tokens: 16000
  temperature: 0.2

validation:
  threshold: 0.4
  algorithm: "ngram_bonus"
  strictness: "moderate"

preprocessing:
  supported_formats: [".pdf", ".docx", ".doc", ".txt"]
  extract_text: true
  ocr_enabled: true
  clean_text: true
```

### Available Templates
- **legal**: General legal document analysis
- **medical**: Medical record processing
- **contracts**: Contract-specific analysis
- Custom templates can be created and shared

## Advanced Usage

### GUI Mode
```bash
# Launch GUI interface for any command
python main.py --gui analyze documents/
python main.py --gui preprocess files/
```

### Batch Processing with Custom Validation
```bash
python main.py --config configs/advanced_legal.yaml analyze \
  documents/ \
  --context "Due diligence review" \
  --document-type "Corporate contracts"
```

### Multi-Step Workflow
```bash
# 1. Analyze document structure
python main.py preprocess contracts/ --operation analyze_structure

# 2. Extract and clean text
python main.py preprocess contracts/ --operation extract

# 3. Perform analysis
python main.py --config configs/legal_contracts.yaml analyze contracts/
```

## Integration

### With LLM Backends
- **Ollama**: Local LLM inference (recommended)
- **API-based models**: Easily configurable
- **Mock responses**: For testing without LLM backend

### Output Formats
- **JSON**: Structured analysis results
- **Summary reports**: Human-readable summaries
- **Validation reports**: Match confidence and verification

## File Structure
```
doculyze/
├── main.py                 # CLI entry point
├── apps/doculyze/         # Core modules
│   ├── analyzer.py        # Document analysis engine
│   ├── preprocessor.py    # Document preprocessing
│   ├── file_processor.py  # Multi-format text extraction
│   ├── validator.py       # Flexible validation system
│   └── config.py          # Configuration management
├── configs/               # Configuration templates
│   ├── legal_contracts.yaml
│   ├── medical_records.yaml
│   ├── litigation_documents.yaml
│   └── real_estate.yaml
└── sample_docs/           # Example documents
```

## Contributing

The system is designed to be easily extensible:

1. **New document types**: Add configuration templates
2. **New file formats**: Extend `FileProcessor` class
3. **New validation algorithms**: Add to `FlexibleValidator`
4. **New preprocessing operations**: Extend `GenericPreprocessor`

## Migration from Legacy System

If migrating from the original medical-specific system:

1. Medical configurations are preserved in `configs/medical_records.yaml`
2. All original functionality is available through the new CLI
3. GUI compatibility is maintained through the `--gui` flag
4. Batch processing is enhanced with better progress tracking

## License

See LICENSE file for details.