# Doculyze Examples

This directory contains examples and sample files to help you get started with Doculyze.

## Directory Structure

### `/documents/`
Contains sample documents and processed outputs for testing and demonstration:

- **`sample_docs/`** - Sample documents in various formats (TXT, DOCX)
- **`converted_docs/`** - Example converted documents showing format transformation

### `/configurations/`
Contains configuration examples and usage documentation:

- **`medical_records_usage_example.md`** - Detailed guide for using medical records configuration in personal injury cases

### `/scripts/`
Contains utility scripts for creating sample content:

- **`create_sample_docx.py`** - Script to generate sample DOCX files for testing

## Quick Start

1. **Test text extraction:**
   ```bash
   python main.py test-extract examples/documents/sample_docs/sample_contract.txt
   ```

2. **Analyze sample documents:**
   ```bash
   python main.py analyze examples/documents/sample_docs/ --config configs/legal_contracts.yaml
   ```

3. **Preprocess documents:**
   ```bash
   python main.py preprocess examples/documents/sample_docs/ --operation extract
   ```

4. **Create additional sample documents:**
   ```bash
   python examples/scripts/create_sample_docx.py
   ```

## Configuration Examples

The configurations in the main `/configs/` directory provide templates for different document types:

- `legal_contracts.yaml` - For analyzing legal contracts and agreements
- `litigation_documents.yaml` - For court filings and legal proceedings  
- `medical_records.yaml` - For personal injury medical record analysis
- `real_estate.yaml` - For property documents and transactions
- `advanced_legal.yaml` - For complex legal analysis with risk assessment

See `/examples/configurations/` for detailed usage guides and examples.

## Using Pixi

All examples work with the Pixi environment management:

```bash
# Install and activate environment
pixi install
pixi shell

# Run examples
python main.py analyze examples/documents/sample_docs/
```

Or use pixi tasks directly:

```bash
pixi run test
pixi run cli analyze examples/documents/sample_docs/
```