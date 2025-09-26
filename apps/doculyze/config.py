"""
Configuration management for Doculyze.
Supports YAML, JSON, and TOML configuration files.
"""
from __future__ import annotations

import json
import yaml
from pathlib import Path
from typing import Dict, Any, Optional, List
import toml

# Default configuration templates
DEFAULT_CONFIGS = {
    "legal": {
        "analysis": {
            "system_prompt": """You are a legal document analyst tasked with extracting information from legal documents.

Instructions:
1. Review the provided document text and context information.
2. Extract relevant legal entities, clauses, dates, and key information based on the specified extraction targets.
3. Focus only on information directly relevant to the specified context.
4. If no relevant information is found, return empty arrays.
5. Do not include any text, notes, or explanations outside of the JSON object.
6. Disregard any artifacts from document parsing.""",
            "prompt_template": """Use the following information to extract the relevant legal information.

Context: {context}
Document Type: {document_type}
Analysis Target: {analysis_target}

Document Text:
{document_text}""",
            "response_schema": {
                "type": "object",
                "properties": {
                    "entities": {
                        "type": "array",
                        "items": {"type": "string"}
                    },
                    "key_clauses": {
                        "type": "array", 
                        "items": {"type": "string"}
                    },
                    "dates": {
                        "type": "array",
                        "items": {"type": "string"}
                    },
                    "obligations": {
                        "type": "array",
                        "items": {"type": "string"}
                    }
                }
            },
            "model_id": "gemma3n:e4b",
            "max_tokens": 16000,
            "temperature": 0.2
        },
        "validation": {
            "threshold": 0.4,
            "algorithm": "ngram_bonus",
            "bonus_factor": 0.5,
            "strictness": "moderate"
        },
        "preprocessing": {
            "supported_formats": [".pdf", ".docx", ".doc", ".txt"],
            "extract_text": True,
            "ocr_enabled": True,
            "clean_text": True
        }
    },
    
    "medical": {
        "analysis": {
            "system_prompt": """You are a medical data analyst tasked with extracting information from medical documents.

Instructions:
1. Review the provided medical document text and context information.
2. Identify relevant medical information based on the specified context and analysis target.
3. Only include information directly relevant to the specified context.
4. If no relevant information is found, return empty arrays.
5. Do not include any text, notes, or explanations outside of the JSON object.
6. Disregard any artifacts from document parsing.""",
            "prompt_template": """Use the following information to extract relevant medical information.

Context: {context}
Analysis Target: {analysis_target}
Date of Interest: {date}

Medical Document Text:
{document_text}""",
            "response_schema": {
                "type": "object",
                "properties": {
                    "injuries": {
                        "type": "array",
                        "items": {"type": "string"}
                    },
                    "treatments": {
                        "type": "array",
                        "items": {"type": "string"}
                    },
                    "medications": {
                        "type": "array",
                        "items": {"type": "string"}
                    },
                    "diagnoses": {
                        "type": "array",
                        "items": {"type": "string"}
                    }
                }
            },
            "model_id": "gemma3n:e4b",
            "max_tokens": 16000,
            "temperature": 0.2
        },
        "validation": {
            "threshold": 0.5,
            "algorithm": "ngram_bonus",
            "bonus_factor": 0.5,
            "strictness": "strict"
        },
        "preprocessing": {
            "supported_formats": [".pdf", ".docx", ".doc", ".txt"],
            "extract_text": True,
            "ocr_enabled": True,
            "clean_text": True
        }
    },
    
    "contracts": {
        "analysis": {
            "system_prompt": """You are a contract analyst tasked with extracting key information from contract documents.

Instructions:
1. Review the provided contract text and context information.
2. Extract contract terms, parties, obligations, dates, and financial information.
3. Focus only on information directly relevant to the contract analysis.
4. If no relevant information is found, return empty arrays.
5. Do not include any text, notes, or explanations outside of the JSON object.
6. Disregard any artifacts from document parsing.""",
            "prompt_template": """Use the following information to extract relevant contract information.

Contract Type: {contract_type}
Analysis Focus: {analysis_focus}
Context: {context}

Contract Text:
{document_text}""",
            "response_schema": {
                "type": "object",
                "properties": {
                    "parties": {
                        "type": "array",
                        "items": {"type": "string"}
                    },
                    "terms": {
                        "type": "array",
                        "items": {"type": "string"}
                    },
                    "obligations": {
                        "type": "array",
                        "items": {"type": "string"}
                    },
                    "dates": {
                        "type": "array",
                        "items": {"type": "string"}
                    },
                    "financial_terms": {
                        "type": "array",
                        "items": {"type": "string"}
                    }
                }
            },
            "model_id": "gemma3n:e4b",
            "max_tokens": 16000,
            "temperature": 0.2
        },
        "validation": {
            "threshold": 0.4,
            "algorithm": "ngram_bonus",
            "bonus_factor": 0.5,
            "strictness": "moderate"
        },
        "preprocessing": {
            "supported_formats": [".pdf", ".docx", ".doc", ".txt"],
            "extract_text": True,
            "ocr_enabled": True,
            "clean_text": True
        }
    }
}


class ConfigManager:
    """Manages configuration files and templates for Doculyze."""
    
    def __init__(self, config_dir: Optional[Path] = None):
        self.config_dir = config_dir or Path.cwd() / "configs"
        self.config_dir.mkdir(exist_ok=True)
        self.current_config: Dict[str, Any] = {}
        self.templates = DEFAULT_CONFIGS
    
    def load_config(self, config_path: Path) -> Dict[str, Any]:
        """Load configuration from file."""
        if not config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
        
        suffix = config_path.suffix.lower()
        
        with open(config_path, 'r', encoding='utf-8') as f:
            if suffix == '.yaml' or suffix == '.yml':
                self.current_config = yaml.safe_load(f)
            elif suffix == '.json':
                self.current_config = json.load(f)
            elif suffix == '.toml':
                self.current_config = toml.load(f)
            else:
                raise ValueError(f"Unsupported configuration format: {suffix}")
        
        return self.current_config
    
    def save_config(self, config: Dict[str, Any], config_path: Path) -> None:
        """Save configuration to file."""
        config_path.parent.mkdir(parents=True, exist_ok=True)
        suffix = config_path.suffix.lower()
        
        with open(config_path, 'w', encoding='utf-8') as f:
            if suffix == '.yaml' or suffix == '.yml':
                yaml.dump(config, f, default_flow_style=False, indent=2)
            elif suffix == '.json':
                json.dump(config, f, indent=2)
            elif suffix == '.toml':
                toml.dump(config, f)
            else:
                raise ValueError(f"Unsupported configuration format: {suffix}")
    
    def get_analysis_config(self, section: Optional[str] = None) -> Dict[str, Any]:
        """Get analysis configuration section."""
        if section and section in self.current_config:
            return self.current_config[section].get('analysis', {})
        elif 'analysis' in self.current_config:
            return self.current_config['analysis']
        else:
            # Return default legal config
            return self.templates['legal']['analysis']
    
    def get_preprocessing_config(self, section: Optional[str] = None) -> Dict[str, Any]:
        """Get preprocessing configuration section."""
        if section and section in self.current_config:
            return self.current_config[section].get('preprocessing', {})
        elif 'preprocessing' in self.current_config:
            return self.current_config['preprocessing']
        else:
            # Return default legal config
            return self.templates['legal']['preprocessing']
    
    def get_validation_config(self, section: Optional[str] = None) -> Dict[str, Any]:
        """Get validation configuration section."""
        if section and section in self.current_config:
            return self.current_config[section].get('validation', {})
        elif 'validation' in self.current_config:
            return self.current_config['validation']
        else:
            # Return default legal config
            return self.templates['legal']['validation']
    
    def get_section(self, section: str) -> Optional[Dict[str, Any]]:
        """Get a specific configuration section."""
        return self.current_config.get(section)
    
    def get_all_config(self) -> Dict[str, Any]:
        """Get the full current configuration."""
        return self.current_config
    
    def create_config_from_template(self, name: str, template: str) -> Path:
        """Create a new configuration file from a template."""
        if template not in self.templates:
            raise ValueError(f"Unknown template: {template}. Available: {list(self.templates.keys())}")
        
        config_path = self.config_dir / f"{name}.yaml"
        self.save_config(self.templates[template], config_path)
        return config_path
    
    def list_templates(self) -> List[str]:
        """List available configuration templates."""
        return list(self.templates.keys())
    
    def list_configs(self) -> List[str]:
        """List available configuration files."""
        configs = []
        for ext in ['.yaml', '.yml', '.json', '.toml']:
            configs.extend([f.stem for f in self.config_dir.glob(f"*{ext}")])
        return configs