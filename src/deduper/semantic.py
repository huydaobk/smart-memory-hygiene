"""
Semantic Deduplicator for Smart Memory Hygiene.

Identifies and merges semantically similar memory entries.
Uses simple text similarity (no ML required for MVP).
"""

import re
from typing import List, Tuple, Optional, Dict, Any
from difflib import SequenceMatcher



class SemanticDeduplicator:
    """
    Finds and merges duplicate or similar memory entries.
    
    Similarity methods:
    - Exact match: Same content
    - Near match: >80% text similarity
    - Topic match: Same keywords/tags
    """
    
    DEFAULT_THRESHOLD = 0.8  # 80% similarity for merging
    
    def __init__(self, similarity_threshold: float = DEFAULT_THRESHOLD):
        """
        Initialize deduplicator.
        
        Args:
            similarity_threshold: Minimum similarity to consider duplicate (0.0-1.0)
        """
        self.threshold = similarity_threshold
    
    def find_duplicates(self, entries: List) -> List[Tuple[int, int, float]]:
        """
        Find pairs of similar entries.
        
        Args:
            entries: List of MemoryEntry objects
            
        Returns:
            List of (index1, index2, similarity_score) tuples
        """
        duplicates = []
        n = len(entries)
        
        for i in range(n):
            for j in range(i + 1, n):
                sim = self._calculate_similarity(entries[i], entries[j])
                if sim >= self.threshold:
                    duplicates.append((i, j, sim))
        
        return duplicates
    
    def _calculate_similarity(self, entry1, entry2) -> float:
        """
        Calculate similarity between two entries.
        
        Uses multiple signals:
        1. Content text similarity (60%)
        2. Type match (20%)
        3. Tag overlap (20%)
        """
        # Extract content
        content1 = self._normalize_text(self._get_content(entry1))
        content2 = self._normalize_text(self._get_content(entry2))
        
        # Text similarity using SequenceMatcher
        text_sim = SequenceMatcher(None, content1, content2).ratio()
        
        # Type match
        type1 = self._get_type(entry1)
        type2 = self._get_type(entry2)
        type_sim = 1.0 if type1 == type2 else 0.0
        
        # Tag overlap
        tags1 = set(self._get_tags(entry1))
        tags2 = set(self._get_tags(entry2))
        if tags1 and tags2:
            tag_sim = len(tags1 & tags2) / len(tags1 | tags2)
        else:
            tag_sim = 0.0
        
        # Weighted combination
        similarity = (
            text_sim * 0.6 +
            type_sim * 0.2 +
            tag_sim * 0.2
        )
        
        return similarity
    
    def _normalize_text(self, text: str) -> str:
        """Normalize text for comparison."""
        # Lowercase
        text = text.lower()
        # Remove extra whitespace
        text = ' '.join(text.split())
        # Remove special chars but keep meaning
        text = re.sub(r'[^\w\s]', ' ', text)
        return text.strip()
    
    def _get_content(self, entry) -> str:
        """Extract content from entry (object or dict)."""
        if hasattr(entry, 'content'):
            return entry.content
        return entry.get('content', '')
    
    def _get_type(self, entry) -> str:
        """Extract type from entry."""
        if hasattr(entry, 'type'):
            return entry.type
        return entry.get('type', 'unknown')
    
    def _get_tags(self, entry) -> List[str]:
        """Extract tags from entry."""
        if hasattr(entry, 'tags'):
            return entry.tags if entry.tags else []
        return entry.get('tags', [])
    
    def merge_entries(self, entry1, entry2, importance_scorer=None) -> dict:
        """
        Merge two similar entries into one consolidated entry.
        
        Strategy:
        - Keep more recent date
        - Combine unique tags
        - Merge content intelligently
        - Use higher importance score
        """
        # Get dates
        date1 = self._get_date(entry1)
        date2 = self._get_date(entry2)
        
        # Use more recent date
        merged_date = max(date1, date2) if date1 and date2 else (date1 or date2)
        
        # Combine tags (unique)
        tags1 = set(self._get_tags(entry1))
        tags2 = set(self._get_tags(entry2))
        merged_tags = list(tags1 | tags2)
        
        # Merge content (keep longer/more detailed)
        content1 = self._get_content(entry1)
        content2 = self._get_content(entry2)
        merged_content = content1 if len(content1) > len(content2) else content2
        
        # Use type from entry1 (should be same)
        merged_type = self._get_type(entry1)
        
        # Calculate merged importance if scorer provided
        merged_importance = 0.0
        if importance_scorer:
            temp_entry = {
                'type': merged_type,
                'date': merged_date,
                'content': merged_content
            }
            merged_importance = importance_scorer.score(temp_entry)
        
        return {
            'type': merged_type,
            'date': merged_date,
            'content': merged_content,
            'tags': merged_tags,
            'importance': merged_importance,
            'merged_from': 2,
            'note': 'Auto-merged duplicate entries'
        }
    
    def _get_date(self, entry):
        """Extract date from entry."""
        if hasattr(entry, 'date'):
            return entry.date
        return entry.get('date', None)
    
    def deduplicate(self, entries: List, importance_scorer=None) -> List[Dict[str, Any]]:
        """
        Main deduplication pipeline.
        
        Args:
            entries: List of entries to deduplicate
            importance_scorer: Optional scorer for merged entries
            
        Returns:
            List of deduplicated entries
        """
        if len(entries) < 2:
            return entries
        
        # Find all duplicate pairs
        duplicates = self.find_duplicates(entries)
        
        if not duplicates:
            return entries
        
        # Group duplicates into clusters
        clusters = self._group_duplicates(duplicates, len(entries))
        
        # Build result
        result = []
        merged_indices = set()
        
        for cluster in clusters:
            if len(cluster) == 1:
                # Single entry, keep as-is
                result.append(entries[cluster[0]])
            else:
                # Merge cluster
                merged = self._merge_cluster(
                    [entries[i] for i in cluster],
                    importance_scorer
                )
                result.append(merged)
                merged_indices.update(cluster)
        
        # Add non-merged entries
        for i, entry in enumerate(entries):
            if i not in merged_indices:
                result.append(entry)
        
        return result
    
    def _group_duplicates(self, duplicates: List[Tuple[int, int, float]], 
                          n_entries: int) -> List[List[int]]:
        """Group duplicate pairs into clusters."""
        # Union-Find data structure
        parent = list(range(n_entries))
        
        def find(x):
            if parent[x] != x:
                parent[x] = find(parent[x])
            return parent[x]
        
        def union(x, y):
            px, py = find(x), find(y)
            if px != py:
                parent[px] = py
        
        # Union all duplicate pairs
        for i, j, _ in duplicates:
            union(i, j)
        
        # Group by root
        clusters = {}
        for i in range(n_entries):
            root = find(i)
            if root not in clusters:
                clusters[root] = []
            clusters[root].append(i)
        
        return list(clusters.values())
    
    def _merge_cluster(self, cluster_entries: List, importance_scorer=None) -> dict:
        """Merge a cluster of similar entries."""
        if len(cluster_entries) == 1:
            return cluster_entries[0]
        
        # Start with first entry
        merged = cluster_entries[0]
        
        # Iteratively merge with others
        for entry in cluster_entries[1:]:
            merged = self.merge_entries(merged, entry, importance_scorer)
        
        return merged
    
    def get_stats(self, original_count: int, deduplicated_count: int) -> dict:
        """Get deduplication statistics."""
        removed = original_count - deduplicated_count
        reduction_pct = (removed / original_count * 100) if original_count > 0 else 0
        
        return {
            'original_count': original_count,
            'deduplicated_count': deduplicated_count,
            'removed': removed,
            'reduction_percent': round(reduction_pct, 2)
        }


# Convenience functions
def find_duplicate_entries(entries: List, threshold: float = 0.8) -> List[Tuple[int, int, float]]:
    """Convenience function to find duplicates."""
    deduper = SemanticDeduplicator(similarity_threshold=threshold)
    return deduper.find_duplicates(entries)


def merge_duplicate_entries(entries: List, threshold: float = 0.8, importance_scorer=None) -> List:
    """Convenience function to merge duplicates."""
    deduper = SemanticDeduplicator(similarity_threshold=threshold)
    return deduper.deduplicate(entries, importance_scorer)
