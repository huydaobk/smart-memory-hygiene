"""
Composite Importance Scorer for Smart Memory Hygiene.

Combines multiple scoring factors into a single importance score:
- Recency (40%): How recent is the entry
- Frequency (30%): How often is it accessed
- Type bonus (30%): Entry type importance
"""

from typing import Optional, List
from datetime import datetime

from .recency import RecencyScorer
from .frequency import FrequencyScorer, create_entry_id


class ImportanceScorer:
    """
    Calculates composite importance score for memory entries.
    
    Formula:
    importance = (recency * 0.4) + (frequency * 0.3) + (type_bonus * 0.3)
    
    Type bonus weights:
    - decision: 1.0 (highest - strategic decisions)
    - error→workflow: 0.9 (high - lessons learned)
    - instruction: 0.8 (high - operating procedures)
    - workflow: 0.6 (medium - processes)
    - preference: 0.4 (lower - user preferences)
    """
    
    TYPE_WEIGHTS = {
        'decision': 1.0,
        'error→workflow': 0.9,
        'instruction': 0.8,
        'workflow': 0.6,
        'preference': 0.4,
    }
    
    # Score component weights
    RECENCY_WEIGHT = 0.4
    FREQUENCY_WEIGHT = 0.3
    TYPE_WEIGHT = 0.3
    
    def __init__(self, 
                 recency_half_life: float = 30.0,
                 frequency_log_file: Optional[str] = None):
        """
        Initialize composite scorer.
        
        Args:
            recency_half_life: Days for recency score to halve
            frequency_log_file: Path to frequency log file
        """
        self.recency_scorer = RecencyScorer(half_life_days=recency_half_life)
        self.frequency_scorer = FrequencyScorer(log_file=frequency_log_file)
    
    def score(self, entry) -> float:
        """
        Calculate composite importance score for an entry.
        
        Args:
            entry: MemoryEntry object (or dict with type, date, content)
            
        Returns:
            Importance score from 0.0 to 1.0
        """
        # Extract entry attributes (handle both object and dict)
        if hasattr(entry, 'get'):  # dict-like
            entry_type = entry.get('type', 'unknown')
            entry_date = entry.get('date', None)
            entry_content = entry.get('content', '')
        else:  # object-like (MemoryEntry)
            entry_type = getattr(entry, 'type', 'unknown')
            entry_date = getattr(entry, 'date', None)
            entry_content = getattr(entry, 'content', '')
        
        # Calculate component scores
        recency_score = self.recency_scorer.score(entry_date)
        
        # Frequency score
        entry_id = create_entry_id(entry_content, str(entry_date) if entry_date else "")
        frequency_score = self.frequency_scorer.score(entry_id)
        
        # Type bonus
        type_bonus = self.TYPE_WEIGHTS.get(entry_type, 0.5)
        
        # Composite score
        importance = (
            recency_score * self.RECENCY_WEIGHT +
            frequency_score * self.FREQUENCY_WEIGHT +
            type_bonus * self.TYPE_WEIGHT
        )
        
        return round(importance, 4)
    
    def score_batch(self, entries: List) -> List[float]:
        """
        Score multiple entries at once.
        
        Args:
            entries: List of MemoryEntry objects
            
        Returns:
            List of importance scores
        """
        return [self.score(entry) for entry in entries]
    
    def get_score_breakdown(self, entry) -> dict:
        """
        Get detailed score breakdown for an entry.
        
        Returns:
            Dict with component scores and final importance
        """
        # Extract entry attributes (handle both object and dict)
        if hasattr(entry, 'get'):  # dict-like
            entry_type = entry.get('type', 'unknown')
            entry_date = entry.get('date', None)
            entry_content = entry.get('content', '')
        else:  # object-like (MemoryEntry)
            entry_type = getattr(entry, 'type', 'unknown')
            entry_date = getattr(entry, 'date', None)
            entry_content = getattr(entry, 'content', '')
        
        recency_score = self.recency_scorer.score(entry_date)
        
        entry_id = create_entry_id(entry_content, str(entry_date) if entry_date else "")
        frequency_score = self.frequency_scorer.score(entry_id)
        type_bonus = self.TYPE_WEIGHTS.get(entry_type, 0.5)
        
        importance = (
            recency_score * self.RECENCY_WEIGHT +
            frequency_score * self.FREQUENCY_WEIGHT +
            type_bonus * self.TYPE_WEIGHT
        )
        
        return {
            'recency': {
                'score': round(recency_score, 4),
                'weight': self.RECENCY_WEIGHT,
                'weighted': round(recency_score * self.RECENCY_WEIGHT, 4)
            },
            'frequency': {
                'score': round(frequency_score, 4),
                'weight': self.FREQUENCY_WEIGHT,
                'weighted': round(frequency_score * self.FREQUENCY_WEIGHT, 4)
            },
            'type_bonus': {
                'score': type_bonus,
                'weight': self.TYPE_WEIGHT,
                'weighted': round(type_bonus * self.TYPE_WEIGHT, 4)
            },
            'final_importance': round(importance, 4)
        }
    
    def record_access(self, entry):
        """Record an access to an entry for frequency tracking."""
        # Extract entry attributes (handle both object and dict)
        if hasattr(entry, 'get'):  # dict-like
            entry_content = entry.get('content', '')
            entry_date = entry.get('date', None)
        else:  # object-like (MemoryEntry)
            entry_content = getattr(entry, 'content', '')
            entry_date = getattr(entry, 'date', None)
        
        entry_id = create_entry_id(entry_content, str(entry_date) if entry_date else "")
        self.frequency_scorer.record_access(entry_id)


# Convenience functions
def score_importance(entry, 
                    recency_half_life: float = 30.0,
                    frequency_log_file: Optional[str] = None) -> float:
    """Convenience function to score a single entry."""
    scorer = ImportanceScorer(
        recency_half_life=recency_half_life,
        frequency_log_file=frequency_log_file
    )
    return scorer.score(entry)


def get_importance_tiers() -> dict:
    """
    Get importance score tiers for interpretation.
    
    Returns:
        Dict mapping tier names to score ranges
    """
    return {
        'critical': (0.8, 1.0),      # Must keep
        'high': (0.6, 0.8),          # Important
        'medium': (0.4, 0.6),      # Moderate
        'low': (0.2, 0.4),          # Consider archive
        'archive': (0.0, 0.2),       # Safe to archive
    }
