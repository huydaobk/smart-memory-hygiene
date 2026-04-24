"""
Recency Scorer for Smart Memory Hygiene.

Calculates recency score based on entry date using exponential decay.
Newer entries get higher scores.
"""

from datetime import datetime, timedelta
from typing import Optional
import math


class RecencyScorer:
    """
    Scores entries based on how recent they are.
    
    Uses exponential decay formula:
    score = exp(-days_ago / half_life)
    
    Where half_life is the number of days for score to drop to 0.5
    """
    
    # Half-life in days for score to decay to 0.5
    DEFAULT_HALF_LIFE = 30.0
    
    def __init__(self, half_life_days: float = DEFAULT_HALF_LIFE):
        """
        Initialize recency scorer.
        
        Args:
            half_life_days: Days for score to decay to 0.5 (default: 30)
        """
        self.half_life = half_life_days
        self.reference_date = datetime.now()
    
    def score(self, entry_date: Optional[datetime]) -> float:
        """
        Calculate recency score for an entry.
        
        Args:
            entry_date: Date of the entry (or None if no date)
            
        Returns:
            Score from 0.0 to 1.0 (1.0 = today, 0.0 = very old)
        """
        if entry_date is None:
            # No date = unknown recency, give neutral score
            return 0.5
        
        # Calculate days ago
        days_ago = (self.reference_date - entry_date).days
        
        if days_ago < 0:
            # Future date (shouldn't happen), treat as today
            return 1.0
        
        # Exponential decay: score = exp(-days_ago / half_life)
        score = math.exp(-days_ago / self.half_life)
        
        # Clamp to [0.0, 1.0]
        return max(0.0, min(1.0, score))
    
    def set_reference_date(self, date: datetime):
        """Set reference date for scoring (useful for testing)."""
        self.reference_date = date
    
    def get_score_breakdown(self, entry_date: Optional[datetime]) -> dict:
        """
        Get detailed scoring information.
        
        Returns:
            Dict with days_ago, half_life, raw_score
        """
        if entry_date is None:
            return {
                'days_ago': None,
                'half_life': self.half_life,
                'raw_score': 0.5,
                'note': 'No date available'
            }
        
        days_ago = (self.reference_date - entry_date).days
        score = self.score(entry_date)
        
        return {
            'days_ago': max(0, days_ago),
            'half_life': self.half_life,
            'raw_score': score,
            'note': 'Exponential decay scoring'
        }


# Convenience functions
def score_recency(entry_date: Optional[datetime], half_life_days: float = 30.0) -> float:
    """Convenience function to score a single date."""
    scorer = RecencyScorer(half_life_days=half_life_days)
    return scorer.score(entry_date)


def get_recency_tiers() -> dict:
    """
    Get score tiers for interpretation.
    
    Returns:
        Dict mapping tier names to score ranges
    """
    return {
        'very_recent': (0.8, 1.0),    # Last ~7 days
        'recent': (0.5, 0.8),         # Last ~30 days
        'moderate': (0.2, 0.5),       # Last ~60 days
        'old': (0.0, 0.2),            # Older than ~60 days
    }
