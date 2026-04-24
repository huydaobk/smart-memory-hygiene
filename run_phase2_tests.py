#!/usr/bin/env python3
"""
Run Phase 2 Intelligence tests (Week 5-6).
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from datetime import datetime, timedelta
from src.parser.memory_md import MemoryMDParser
from src.intelligence.semantic_analyzer import SemanticAnalyzer, calculate_semantic_similarity
from src.intelligence.topic_extractor import TopicExtractor, extract_topics_from_entries

print("=" * 60)
print("Phase 2: Intelligence Tests (Week 5-6)")
print("=" * 60)

# Test 1: Semantic Analyzer Initialization
print("\n[TEST 1] Semantic Analyzer Initialization...")
try:
    analyzer = SemanticAnalyzer(use_embeddings=False)  # Use fallback for tests
    
    print(f"  Using embeddings: {analyzer.use_embeddings}")
    print(f"  Model name: {analyzer.model_name}")
    
    stats = analyzer.get_cache_stats()
    print(f"  Cache stats: {stats}")
    
    print("  ✓ Semantic analyzer initialized")
except Exception as e:
    print(f"  ✗ FAILED: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 2: Text Similarity (Fallback)
print("\n[TEST 2] Text Similarity (Fallback)...")
try:
    analyzer = SemanticAnalyzer(use_embeddings=False)
    
    text1 = "Use Google Drive for file synchronization"
    text2 = "Use Google Drive to sync files between devices"
    text3 = "Machine learning is a subset of artificial intelligence"
    
    sim_1_2 = analyzer.calculate_similarity(text1, text2)
    sim_1_3 = analyzer.calculate_similarity(text1, text3)
    
    print(f"  Similar texts: {sim_1_2:.4f} (should be >0.5)")
    print(f"  Different texts: {sim_1_3:.4f} (should be <0.3)")
    
    assert sim_1_2 > 0.5, "Similar texts should have high similarity"
    assert sim_1_3 < 0.3, "Different texts should have low similarity"
    
    print("  ✓ Text similarity working")
except Exception as e:
    print(f"  ✗ FAILED: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 3: Semantic Clustering
print("\n[TEST 3] Semantic Clustering...")
try:
    analyzer = SemanticAnalyzer(use_embeddings=False)
    
    entries = [
        {'type': 'workflow', 'content': 'Use rclone for Google Drive sync'},
        {'type': 'workflow', 'content': 'Sync files with rclone to Drive'},
        {'type': 'workflow', 'content': 'Backup with rclone tool'},
        {'type': 'decision', 'content': 'Choose Kimi as AI model'},
        {'type': 'decision', 'content': 'Use Claude for coding tasks'},
    ]
    
    clusters = analyzer.find_semantic_clusters(entries, threshold=0.5)
    print(f"  Found {len(clusters)} clusters")
    
    for i, cluster in enumerate(clusters):
        print(f"    Cluster {i+1}: indices {cluster}")
    
    # Should group rclone entries together
    assert len(clusters) >= 2, "Should find at least 2 clusters"
    
    print("  ✓ Semantic clustering working")
except Exception as e:
    print(f"  ✗ FAILED: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 4: Find Most Similar
print("\n[TEST 4] Find Most Similar...")
try:
    analyzer = SemanticAnalyzer(use_embeddings=False)
    
    entries = [
        {'type': 'workflow', 'content': 'Google Drive sync with rclone'},
        {'type': 'workflow', 'content': 'OneDrive backup solution'},
        {'type': 'decision', 'content': 'Use Dropbox for sharing'},
        {'type': 'workflow', 'content': 'AWS S3 storage sync'},
    ]
    
    query = "How to sync with Google Drive"
    results = analyzer.find_most_similar(query, entries, top_k=3)
    
    print(f"  Query: '{query}'")
    print(f"  Top matches:")
    for idx, score in results:
        print(f"    [{idx}] {score:.4f}: {entries[idx]['content'][:40]}...")
    
    # First result should be Google Drive related
    assert results[0][0] == 0, "First result should be Google Drive entry"
    
    print("  ✓ Similarity search working")
except Exception as e:
    print(f"  ✗ FAILED: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 5: Topic Extraction
print("\n[TEST 5] Topic Extraction...")
try:
    extractor = TopicExtractor()
    
    entries = [
        {'type': 'workflow', 'content': 'Setup Google Drive sync with rclone for backups'},
        {'type': 'workflow', 'content': 'Configure rclone for Google Drive synchronization'},
        {'type': 'decision', 'content': 'Use Kimi K2.5 Turbo as primary model'},
        {'type': 'decision', 'content': 'Fallback to DeepSeek V3 when Kimi unavailable'},
        {'type': 'workflow', 'content': 'Implement neural memory rehearsal daily'},
    ]
    
    topics = extractor.extract_topics(entries, n_topics=3)
    print(f"  Found {len(topics)} topics:")
    
    for topic, indices in topics.items():
        print(f"    '{topic}': entries {indices}")
    
    assert len(topics) >= 1, "Should find at least 1 topic"
    
    print("  ✓ Topic extraction working")
except Exception as e:
    print(f"  ✗ FAILED: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 6: Cluster Labeling
print("\n[TEST 6] Cluster Labeling...")
try:
    extractor = TopicExtractor()
    
    cluster = [
        {'type': 'workflow', 'content': 'Google Drive sync setup'},
        {'type': 'workflow', 'content': 'rclone configuration for Drive'},
        {'type': 'workflow', 'content': 'Backup to Google Drive daily'},
    ]
    
    label = extractor.label_cluster(cluster)
    print(f"  Generated label: '{label}'")
    
    assert 'workflow' in label.lower(), "Label should mention workflow"
    
    print("  ✓ Cluster labeling working")
except Exception as e:
    print(f"  ✗ FAILED: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 7: Integration with Parser
print("\n[TEST 7] Integration with Week 1 Parser...")
try:
    parser = MemoryMDParser(dry_run=True)
    analyzer = SemanticAnalyzer(use_embeddings=False)
    extractor = TopicExtractor()
    
    sample_file = "/mnt/toshiba/projects/smart-memory-hygiene/tests/fixtures/sample-memory.md"
    entries = parser.parse(sample_file)
    
    print(f"  Parsed {len(entries)} entries")
    
    # Extract topics
    topics = extractor.extract_topics(entries, n_topics=5)
    print(f"  Extracted {len(topics)} topics:")
    for topic, indices in list(topics.items())[:3]:
        print(f"    '{topic}': {len(indices)} entries")
    
    # Find clusters
    if len(entries) >= 3:
        clusters = analyzer.find_semantic_clusters(entries[:10], threshold=0.6)
        print(f"  Found {len(clusters)} clusters in first 10 entries")
    
    print("  ✓ Integration working")
except Exception as e:
    print(f"  ✗ FAILED: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "=" * 60)
print("Phase 2: All tests PASSED! ✓")
print("=" * 60)

sys.exit(0)
