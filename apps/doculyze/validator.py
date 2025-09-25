"""
Flexible validation system that can be configured for different analysis types and strictness levels.
Replaces the rigid medical-specific validation with a configurable approach.
"""
from __future__ import annotations

import re
import typing as ty
from typing import Dict, Any, List, Tuple, Optional, Union

import sys
from pathlib import Path

# Add parent directories to path to find modules
sys.path.insert(0, str(Path(__file__).parent.parent))
from common_simple import timings


class FlexibleValidator:
    """
    Configurable validation system that can adapt to different document types and analysis requirements.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        
        # Configuration parameters
        self.threshold = self.config.get("threshold", 0.5)
        self.algorithm = self.config.get("algorithm", "ngram_bonus")
        self.bonus_factor = self.config.get("bonus_factor", 0.5)
        self.strictness = self.config.get("strictness", "moderate")
        
        # Strictness-based adjustments
        self._apply_strictness_settings()
    
    def _apply_strictness_settings(self) -> None:
        """Apply strictness-based adjustments to validation parameters."""
        strictness_configs = {
            "lenient": {
                "threshold_multiplier": 0.7,
                "bonus_factor_multiplier": 1.3,
                "min_match_length": 2
            },
            "moderate": {
                "threshold_multiplier": 1.0,
                "bonus_factor_multiplier": 1.0,
                "min_match_length": 3
            },
            "strict": {
                "threshold_multiplier": 1.3,
                "bonus_factor_multiplier": 0.8,
                "min_match_length": 4
            }
        }
        
        strictness_config = strictness_configs.get(self.strictness, strictness_configs["moderate"])
        
        self.threshold = min(1.0, self.threshold * strictness_config["threshold_multiplier"])
        self.bonus_factor = self.bonus_factor * strictness_config["bonus_factor_multiplier"]
        self.min_match_length = strictness_config["min_match_length"]
    
    def validate(self, document_text: str, analysis_results: Dict[str, Any]) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """
        Validate analysis results against document text.
        
        Returns:
            Tuple of (validated_results, match_counts)
        """
        if self.algorithm == "ngram_bonus":
            return self._validate_ngram_bonus(document_text, analysis_results)
        elif self.algorithm == "fuzzy_match":
            return self._validate_fuzzy_match(document_text, analysis_results)
        elif self.algorithm == "semantic_similarity":
            return self._validate_semantic_similarity(document_text, analysis_results)
        else:
            # Default to ngram_bonus
            return self._validate_ngram_bonus(document_text, analysis_results)
    
    @timings()
    def _validate_ngram_bonus(self, document_text: str, analysis_results: Dict[str, Any]) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """Validate using n-gram matching with consecutive bonus."""
        validated_results = {}
        match_counts = {}
        
        document_text_lower = document_text.lower()
        
        for category, items in analysis_results.items():
            if not isinstance(items, list):
                continue
            
            validated_results[category] = {
                "verified": {},
                "unverified": {}
            }
            
            match_counts[category] = {
                "verified": 0,
                "unverified": 0
            }
            
            for item in items:
                item_str = str(item)
                confidence, matches = self._score_item_ngram(item_str, document_text_lower)
                
                if confidence >= self.threshold and matches:
                    validated_results[category]["verified"][item_str] = (confidence, matches)
                    match_counts[category]["verified"] += 1
                else:
                    validated_results[category]["unverified"][item_str] = (confidence, matches)
                    match_counts[category]["unverified"] += 1
        
        return validated_results, match_counts
    
    def _score_item_ngram(self, item_str: str, document_text: str) -> Tuple[float, List[str]]:
        """Score an item using n-gram matching with consecutive bonus."""
        token_re = re.compile(r'\w+', re.UNICODE)
        words = token_re.findall(item_str.lower())
        
        if not words:
            return 0.0, []
        
        i = 0
        runs: List[int] = []
        matched_phrases: List[str] = []
        n = len(words)
        
        while i < n:
            found_len = 0
            # Try longest n-gram first (greedy)
            for L in range(n - i, 0, -1):
                if L < self.min_match_length and L < n:
                    continue
                    
                phrase = " ".join(words[i:i + L])
                if phrase in document_text:
                    found_len = L
                    matched_phrases.append(phrase)
                    break
            
            if found_len > 0:
                runs.append(found_len)
                i += found_len
            else:
                i += 1
        
        base_matches = sum(runs)
        # Triangular bonus to favor longer consecutive runs
        bonus = sum((r * (r - 1) / 2) * self.bonus_factor for r in runs)
        raw_score = base_matches + bonus
        
        # Theoretical maximum: all tokens matched in a single run
        max_score = n + ((n * (n - 1) / 2) * self.bonus_factor)
        confidence = float(raw_score / max_score) if max_score > 0 else 0.0
        
        # Clamp for safety
        confidence = max(0.0, min(1.0, confidence))
        
        return confidence, matched_phrases
    
    def _validate_fuzzy_match(self, document_text: str, analysis_results: Dict[str, Any]) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """Validate using fuzzy string matching (approximate matching)."""
        # This would require additional libraries like rapidfuzz or fuzzywuzzy
        # For now, fall back to ngram method
        return self._validate_ngram_bonus(document_text, analysis_results)
    
    def _validate_semantic_similarity(self, document_text: str, analysis_results: Dict[str, Any]) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """Validate using semantic similarity (would require embeddings)."""
        # This would require embedding models and similarity computation
        # For now, fall back to ngram method
        return self._validate_ngram_bonus(document_text, analysis_results)
    
    def get_validation_summary(self, match_counts: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a summary of validation results."""
        summary = {
            "total_categories": len(match_counts),
            "categories": {},
            "overall": {
                "verified": 0,
                "unverified": 0,
                "total": 0
            }
        }
        
        for category, counts in match_counts.items():
            verified = counts.get("verified", 0)
            unverified = counts.get("unverified", 0)
            total = verified + unverified
            
            summary["categories"][category] = {
                "verified": verified,
                "unverified": unverified,
                "total": total,
                "verification_rate": (verified / total) if total > 0 else 0.0
            }
            
            summary["overall"]["verified"] += verified
            summary["overall"]["unverified"] += unverified
            summary["overall"]["total"] += total
        
        if summary["overall"]["total"] > 0:
            summary["overall"]["verification_rate"] = (
                summary["overall"]["verified"] / summary["overall"]["total"]
            )
        else:
            summary["overall"]["verification_rate"] = 0.0
        
        return summary
    
    def adjust_threshold(self, new_threshold: float) -> None:
        """Dynamically adjust the validation threshold."""
        self.threshold = max(0.0, min(1.0, new_threshold))
    
    def adjust_strictness(self, new_strictness: str) -> None:
        """Dynamically adjust the validation strictness."""
        if new_strictness in ["lenient", "moderate", "strict"]:
            self.strictness = new_strictness
            self._apply_strictness_settings()
    
    def get_config(self) -> Dict[str, Any]:
        """Get current validation configuration."""
        return {
            "threshold": self.threshold,
            "algorithm": self.algorithm,
            "bonus_factor": self.bonus_factor,
            "strictness": self.strictness,
            "min_match_length": getattr(self, "min_match_length", 3)
        }