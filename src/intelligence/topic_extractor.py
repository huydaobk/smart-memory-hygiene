"""
Topic Extractor for Smart Memory Hygiene.

Extracts and labels topics from memory content using clustering.
"""

import re
from collections import Counter
from typing import List, Dict, Set, Tuple, Any
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TopicExtractor:
    """
    Extracts topics from memory entries.
    
    Uses keyword extraction and semantic clustering to identify
    main topics in the memory corpus.
    """
    
    # Common stop words to exclude
    STOP_WORDS = {
        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
        'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'be',
        'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would',
        'could', 'should', 'may', 'might', 'must', 'shall', 'can', 'need',
        'this', 'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it',
        'we', 'they', 'me', 'him', 'her', 'us', 'them', 'my', 'your', 'his',
        'her', 'its', 'our', 'their', 'use', 'using', 'used', 'via', 'per'
    }
    
    # Domain-specific keywords for OpenClaw context
    DOMAIN_KEYWORDS = {
        'gateway', 'memory', 'neural', 'nmem', 'openclaw', 'bot', 'agent',
        'telegram', 'discord', 'workflow', 'parser', 'scorer', 'archive',
        'backup', 'sync', 'drive', 'google', 'docs', 'sheets', 'api',
        'crash', 'error', 'fix', 'bug', 'issue', 'debug', 'test',
        'deploy', 'build', 'release', 'version', 'update', 'install'
    }
    
    def __init__(self, min_keyword_length: int = 3):
        """
        Initialize topic extractor.
        
        Args:
            min_keyword_length: Minimum length for extracted keywords
        """
        self.min_keyword_length = min_keyword_length
    
    def extract_keywords(self, text: str, top_n: int = 10) -> List[Tuple[str, int]]:
        """
        Extract keywords from text.
        
        Args:
            text: Input text
            top_n: Number of top keywords to return
            
        Returns:
            List of (keyword, frequency) tuples
        """
        # Normalize text
        text = text.lower()
        
        # Extract words
        words = re.findall(r'\b[a-z][a-z0-9_]+\b', text)
        
        # Filter words
        filtered = [
            w for w in words
            if len(w) >= self.min_keyword_length
            and w not in self.STOP_WORDS
            and not w.isdigit()
        ]
        
        # Count frequencies
        word_counts = Counter(filtered)
        
        # Boost domain keywords
        for word in list(word_counts.keys()):
            if word in self.DOMAIN_KEYWORDS:
                word_counts[word] *= 2
        
        # Return top N
        return word_counts.most_common(top_n)
    
    def extract_topics(self, entries: List[Any], n_topics: int = 5) -> Dict[str, List[int]]:
        """
        Extract topics from a list of entries.
        
        Args:
            entries: List of entries (objects or dicts with 'content' and 'type')
            n_topics: Number of topics to extract
            
        Returns:
            Dict mapping topic names to list of entry indices
        """
        if not entries:
            return {}
        
        # Collect all keywords with their entry indices
        keyword_to_entries: Dict[str, Set[int]] = {}
        
        for i, entry in enumerate(entries):
            content = self._get_content(entry)
            entry_type = self._get_type(entry)
            
            # Extract keywords from content
            keywords = self.extract_keywords(content, top_n=5)
            
            # Add entry type as keyword
            if entry_type:
                keywords.append((entry_type.lower(), 3))
            
            # Map keywords to entries
            for keyword, _ in keywords:
                if keyword not in keyword_to_entries:
                    keyword_to_entries[keyword] = set()
                keyword_to_entries[keyword].add(i)
        
        # Find keywords that appear in multiple entries
        topic_candidates = [
            (kw, entries_set)
            for kw, entries_set in keyword_to_entries.items()
            if len(entries_set) >= 2  # At least 2 entries
        ]
        
        # Sort by number of entries (descending)
        topic_candidates.sort(key=lambda x: len(x[1]), reverse=True)
        
        # Select top N topics, avoiding overlap
        selected_topics: Dict[str, Set[int]] = {}
        used_entries: Set[int] = set()
        
        for keyword, entry_set in topic_candidates:
            # Skip if all entries already covered
            if entry_set <= used_entries:
                continue
            
            # Add this topic
            selected_topics[keyword] = entry_set
            used_entries.update(entry_set)
            
            if len(selected_topics) >= n_topics:
                break
        
        # Convert sets to sorted lists
        return {
            topic: sorted(list(indices))
            for topic, indices in selected_topics.items()
        }
    
    def label_cluster(self, entries: List[Any]) -> str:
        """
        Generate a human-readable label for a cluster of entries.
        
        Args:
            entries: List of entries in cluster
            
        Returns:
            Generated label
        """
        if not entries:
            return "Empty cluster"
        
        # Collect all keywords
        all_keywords: Counter = Counter()
        types: Counter = Counter()
        
        for entry in entries:
            content = self._get_content(entry)
            entry_type = self._get_type(entry)
            
            if entry_type:
                types[entry_type] += 1
            
            keywords = self.extract_keywords(content, top_n=3)
            for kw, count in keywords:
                all_keywords[kw] += count
        
        # Get most common type
        most_common_type = types.most_common(1)
        type_label = most_common_type[0][0] if most_common_type else "mixed"
        
        # Get top keywords
        top_keywords = [kw for kw, _ in all_keywords.most_common(3)]
        
        # Generate label
        if top_keywords:
            keyword_str = " + ".join(top_keywords[:2])
            return f"{type_label}: {keyword_str}"
        else:
            return f"{type_label} entries"
    
    def get_topic_summary(self, topic: str, entries: List[Any]) -> Dict[str, Any]:
        """
        Get summary information about a topic.
        
        Args:
            topic: Topic name
            entries: All entries (topic indices will be extracted)
            
        Returns:
            Summary dict with topic info
        """
        topics = self.extract_topics(entries, n_topics=10)
        
        if topic not in topics:
            return {
                'topic': topic,
                'found': False,
                'entry_count': 0,
                'entries': []
            }
        
        topic_entries = [entries[i] for i in topics[topic]]
        
        # Get date range
        dates = [self._get_date(e) for e in topic_entries if self._get_date(e)]
        
        # Get all keywords for this topic
        all_content = ' '.join(self._get_content(e) for e in topic_entries)
        keywords = self.extract_keywords(all_content, top_n=10)
        
        return {
            'topic': topic,
            'found': True,
            'entry_count': len(topic_entries),
            'entry_indices': topics[topic],
            'date_range': {
                'earliest': min(dates) if dates else None,
                'latest': max(dates) if dates else None
            },
            'keywords': keywords,
            'types': list(set(self._get_type(e) for e in topic_entries))
        }
    
    def _get_content(self, entry) -> str:
        """Extract content from entry."""
        if isinstance(entry, dict):
            return entry.get('content', '')
        return getattr(entry, 'content', '')
    
    def _get_type(self, entry) -> str:
        """Extract type from entry."""
        if isinstance(entry, dict):
            return entry.get('type', '')
        return getattr(entry, 'type', '')
    
    def _get_date(self, entry):
        """Extract date from entry."""
        if isinstance(entry, dict):
            return entry.get('date')
        return getattr(entry, 'date', None)


# Convenience functions
def extract_topics_from_entries(entries: List[Any], n_topics: int = 5) -> Dict[str, List[int]]:
    """Extract topics from entries."""
    extractor = TopicExtractor()
    return extractor.extract_topics(entries, n_topics)


def label_entry_cluster(entries: List[Any]) -> str:
    """Generate label for a cluster of entries."""
    extractor = TopicExtractor()
    return extractor.label_cluster(entries)
