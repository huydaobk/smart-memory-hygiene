"""
Frequency Scorer for Smart Memory Hygiene.

Tracks and scores entries based on access frequency.
More frequently accessed entries get higher scores.
"""

import json
from pathlib import Path
from typing import Dict, Optional
from datetime import datetime


class FrequencyScorer:
    """
    Scores entries based on access frequency.
    
    Uses a simple access log approach:
    - Each access increments counter
    - Score normalized by max observed frequency
    """
    
    def __init__(self, log_file: Optional[str] = None):
        """
        Initialize frequency scorer.
        
        Args:
            log_file: Path to access log file (optional)
        """
        self.log_file = log_file
        self.access_counts: Dict[str, int] = {}
        self.max_count = 1  # Avoid division by zero
        
        if log_file and Path(log_file).exists():
            self._load_log()
    
    def _load_log(self):
        """Load access counts from log file."""
        try:
            with open(self.log_file, 'r') as f:
                self.access_counts = json.load(f)
                if self.access_counts:
                    self.max_count = max(self.access_counts.values())
        except (json.JSONDecodeError, IOError):
            self.access_counts = {}
    
    def _save_log(self):
        """Save access counts to log file."""
        if self.log_file:
            Path(self.log_file).parent.mkdir(parents=True, exist_ok=True)
            with open(self.log_file, 'w') as f:
                json.dump(self.access_counts, f, indent=2)
    
    def record_access(self, entry_id: str):
        """
        Record an access to an entry.
        
        Args:
            entry_id: Unique identifier for the entry
        """
        self.access_counts[entry_id] = self.access_counts.get(entry_id, 0) + 1
        self.max_count = max(self.max_count, self.access_counts[entry_id])
        self._save_log()
    
    def score(self, entry_id: str) -> float:
        """
        Calculate frequency score for an entry.
        
        Args:
            entry_id: Unique identifier for the entry
            
        Returns:
            Score from 0.0 to 1.0
        """
        count = self.access_counts.get(entry_id, 0)
        
        if count == 0:
            return 0.0
        
        # Normalize by max count, with log scaling for better distribution
        import math
        score = math.log1p(count) / math.log1p(self.max_count)
        
        return max(0.0, min(1.0, score))
    
    def get_access_count(self, entry_id: str) -> int:
        """Get raw access count for an entry."""
        return self.access_counts.get(entry_id, 0)
    
    def get_stats(self) -> dict:
        """Get frequency statistics."""
        if not self.access_counts:
            return {
                'total_entries': 0,
                'total_accesses': 0,
                'max_count': 0,
                'avg_count': 0.0
            }
        
        total_accesses = sum(self.access_counts.values())
        
        return {
            'total_entries': len(self.access_counts),
            'total_accesses': total_accesses,
            'max_count': self.max_count,
            'avg_count': total_accesses / len(self.access_counts)
        }


# Convenience functions
def create_entry_id(content: str, date_str: str = "") -> str:
    """
    Create a unique entry ID from content and date.
    
    Args:
        content: Entry content
        date_str: Date string (optional)
        
    Returns:
        Unique identifier
    """
    import hashlib
    text = f"{date_str}:{content[:50]}"
    return hashlib.md5(text.encode()).hexdigest()[:12]
