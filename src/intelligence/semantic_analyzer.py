"""
Semantic Analyzer for Smart Memory Hygiene.

Uses sentence-transformers for embedding-based semantic similarity.
Falls back to text-based similarity if model unavailable.
"""

from typing import List, Tuple, Optional, Dict, Any
from difflib import SequenceMatcher
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SemanticAnalyzer:
    """
    Analyzes semantic similarity between memory entries using embeddings.
    
    Uses sentence-transformers when available, falls back to
    SequenceMatcher for basic text similarity.
    """
    
    DEFAULT_MODEL = 'all-MiniLM-L6-v2'
    DEFAULT_THRESHOLD = 0.7
    
    def __init__(self, model_name: str = DEFAULT_MODEL, use_embeddings: bool = True):
        """
        Initialize semantic analyzer.
        
        Args:
            model_name: Name of sentence-transformer model to use
            use_embeddings: Whether to use embedding-based similarity
        """
        self.model_name = model_name
        self.use_embeddings = use_embeddings
        self.model = None
        self._embedding_cache: Dict[str, Any] = {}
        
        if use_embeddings:
            self._load_model()
    
    def _load_model(self):
        """Load sentence-transformer model."""
        try:
            from sentence_transformers import SentenceTransformer
            logger.info(f"Loading model: {self.model_name}")
            self.model = SentenceTransformer(self.model_name)
            logger.info("Model loaded successfully")
        except ImportError:
            logger.warning("sentence-transformers not available, using fallback")
            self.use_embeddings = False
        except Exception as e:
            logger.warning(f"Failed to load model: {e}, using fallback")
            self.use_embeddings = False
    
    def generate_embedding(self, text: str) -> Optional[Any]:
        """
        Generate embedding vector for text.
        
        Args:
            text: Input text
            
        Returns:
            Embedding vector or None if model unavailable
        """
        if not self.use_embeddings or self.model is None:
            return None
        
        # Check cache
        cache_key = hash(text[:100])  # Use first 100 chars as cache key
        if cache_key in self._embedding_cache:
            return self._embedding_cache[cache_key]
        
        # Generate embedding
        try:
            # Truncate if too long (model limit ~512 tokens)
            words = text.split()
            if len(words) > 100:
                text = ' '.join(words[:100])
            
            embedding = self.model.encode(text, convert_to_numpy=True)
            
            # Cache result
            self._embedding_cache[cache_key] = embedding
            
            return embedding
        except Exception as e:
            logger.error(f"Failed to generate embedding: {e}")
            return None
    
    def calculate_similarity(self, text1: str, text2: str) -> float:
        """
        Calculate semantic similarity between two texts.
        
        Uses cosine similarity of embeddings if available,
        falls back to SequenceMatcher.
        
        Args:
            text1: First text
            text2: Second text
            
        Returns:
            Similarity score from 0.0 to 1.0
        """
        if self.use_embeddings:
            emb1 = self.generate_embedding(text1)
            emb2 = self.generate_embedding(text2)
            
            if emb1 is not None and emb2 is not None:
                return self._cosine_similarity(emb1, emb2)
        
        # Fallback to text-based similarity
        return self._text_similarity(text1, text2)
    
    def _cosine_similarity(self, vec1, vec2) -> float:
        """Calculate cosine similarity between two vectors."""
        # Try numpy first
        try:
            import numpy as np
            dot_product = np.dot(vec1, vec2)
            norm1 = np.linalg.norm(vec1)
            norm2 = np.linalg.norm(vec2)
        except:
            # Fallback for list vectors
            dot_product = sum(a * b for a, b in zip(vec1, vec2))
            norm1 = sum(a * a for a in vec1) ** 0.5
            norm2 = sum(b * b for b in vec2) ** 0.5
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return float(dot_product / (norm1 * norm2))
    
    def _text_similarity(self, text1: str, text2: str) -> float:
        """Calculate text-based similarity using SequenceMatcher."""
        return SequenceMatcher(None, text1.lower(), text2.lower()).ratio()
    
    def find_semantic_clusters(self, entries: List[Any], threshold: float = DEFAULT_THRESHOLD) -> List[List[int]]:
        """
        Find clusters of semantically similar entries.
        
        Args:
            entries: List of entries (objects or dicts with 'content')
            threshold: Minimum similarity to be in same cluster
            
        Returns:
            List of clusters (each cluster is list of entry indices)
        """
        n = len(entries)
        if n < 2:
            return [[i] for i in range(n)] if n > 0 else []
        
        # Extract content
        contents = [self._get_content(e) for e in entries]
        
        # Calculate similarity matrix
        similarity_matrix = []
        for i in range(n):
            row = []
            for j in range(n):
                if i == j:
                    row.append(1.0)
                elif j > i:
                    sim = self.calculate_similarity(contents[i], contents[j])
                    row.append(sim)
                else:
                    row.append(similarity_matrix[j][i])  # Symmetric
            similarity_matrix.append(row)
        
        # Use union-find to cluster
        parent = list(range(n))
        
        def find(x):
            if parent[x] != x:
                parent[x] = find(parent[x])
            return parent[x]
        
        def union(x, y):
            px, py = find(x), find(y)
            if px != py:
                parent[px] = py
        
        # Union entries above threshold
        for i in range(n):
            for j in range(i + 1, n):
                if similarity_matrix[i][j] >= threshold:
                    union(i, j)
        
        # Group by root
        clusters = {}
        for i in range(n):
            root = find(i)
            if root not in clusters:
                clusters[root] = []
            clusters[root].append(i)
        
        return list(clusters.values())
    
    def find_most_similar(self, query: str, entries: List[Any], top_k: int = 5) -> List[Tuple[int, float]]:
        """
        Find most similar entries to a query text.
        
        Args:
            query: Query text
            entries: List of entries to search
            top_k: Number of results to return
            
        Returns:
            List of (entry_index, similarity_score) tuples
        """
        similarities = []
        
        for i, entry in enumerate(entries):
            content = self._get_content(entry)
            sim = self.calculate_similarity(query, content)
            similarities.append((i, sim))
        
        # Sort by similarity (descending)
        similarities.sort(key=lambda x: x[1], reverse=True)
        
        return similarities[:top_k]
    
    def clear_cache(self):
        """Clear embedding cache."""
        self._embedding_cache.clear()
        logger.info("Embedding cache cleared")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        return {
            'cache_size': len(self._embedding_cache),
            'using_embeddings': self.use_embeddings,
            'model_name': self.model_name if self.use_embeddings else None
        }
    
    def _get_content(self, entry) -> str:
        """Extract content from entry."""
        if isinstance(entry, dict):
            return entry.get('content', '')
        return getattr(entry, 'content', '')


# Convenience functions
def calculate_semantic_similarity(text1: str, text2: str, use_embeddings: bool = True) -> float:
    """Calculate semantic similarity between two texts."""
    analyzer = SemanticAnalyzer(use_embeddings=use_embeddings)
    return analyzer.calculate_similarity(text1, text2)


def find_similar_entries(query: str, entries: List[Any], top_k: int = 5) -> List[Tuple[int, float]]:
    """Find entries most similar to query."""
    analyzer = SemanticAnalyzer()
    return analyzer.find_most_similar(query, entries, top_k)
