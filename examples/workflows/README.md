# Example Workflows

This directory contains example workflows demonstrating how to use Doculyze for different document analysis scenarios.

## Personal Injury Medical Records Analysis

```bash
# 1. Analyze medical records for personal injury case
python main.py analyze examples/documents/medical/ \
  --config configs/medical_records.yaml \
  --context "Motor vehicle accident personal injury case" \
  --document-type "Medical Records"

# 2. Extract specific information for causation analysis
python main.py analyze examples/documents/medical/ \
  --config configs/medical_records.yaml \
  --incident-description "Rear-end collision on Highway 101" \
  --incident-date "2024-03-15" \
  --legal-context "Personal injury lawsuit - Smith v. Jones" \
  --analysis-focus "Establish causation between accident and reported injuries"
```

## Legal Contract Review

```bash
# 1. Analyze contracts for key terms and obligations
python main.py analyze examples/documents/legal/ \
  --config configs/legal_contracts.yaml \
  --context "Contract review for due diligence" \
  --document-type "Service Agreement"

# 2. Batch process multiple contracts
python main.py analyze examples/documents/contracts/ \
  --config configs/legal_contracts.yaml
```

## Multi-format Document Processing

```bash
# 1. Preprocess documents to extract text from various formats
python main.py preprocess examples/documents/sample_docs/ \
  --operation extract \
  --output examples/documents/extracted/

# 2. Analyze document structure for metadata
python main.py preprocess examples/documents/sample_docs/ \
  --operation analyze_structure
```

## Custom Configuration Workflow

```bash
# 1. Create custom configuration for specific use case
python main.py config-create my_real_estate --template legal

# 2. Customize the configuration file (edit configs/my_real_estate.yaml)

# 3. Use custom configuration for analysis
python main.py analyze examples/documents/real_estate/ \
  --config configs/my_real_estate.yaml
```

## GUI Mode Examples

```bash
# Launch GUI for interactive document analysis
python main.py --gui analyze examples/documents/sample_docs/

# GUI preprocessing with visual feedback
python main.py --gui preprocess examples/documents/sample_docs/
```

## Pixi Environment Workflows

```bash
# Use pixi tasks for common operations
pixi run test                                    # Test basic functionality
pixi run cli analyze examples/documents/legal/  # Analyze with pixi environment
pixi run lint                                    # Code quality checks
pixi run format                                  # Code formatting
```