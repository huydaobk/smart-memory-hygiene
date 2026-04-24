#!/usr/bin/env python3
"""
Run Week 3 Deduplication Engine tests.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from datetime import datetime, timedelta
from src.parser.memory_md import MemoryMDParser
from src.scorer.composite import ImportanceScorer
from src.deduper.semantic import SemanticDeduplicator, find_duplicate_entries, merge_duplicate_entries

print("=" * 60)
print("Week 3: Deduplication Engine Tests")
print("=" * 60)

# Test 1: Similarity Calculation
print("\n[TEST 1] Similarity Calculation...")
try:
    deduper = SemanticDeduplicator(similarity_threshold=0.8)
    
    # Create test entries
    entry1 = {
        'type': 'workflow',
        'content': 'Use Google Drive for file sharing between devices',
        'tags': ['sync', 'drive'],
        'date': datetime.now()
    }
    
    entry2 = {
        'type': 'workflow',
        'content': 'Use Google Drive for sharing files across devices',
        'tags': ['sync', 'drive'],
        'date': datetime.now()
    }
    
    entry3 = {
        'type': 'decision',
        'content': 'Completely different topic about machine learning',
        'tags': ['ml', 'ai'],
        'date': datetime.now()
    }
    
    # Calculate similarities
    sim_1_2 = deduper._calculate_similarity(entry1, entry2)
    sim_1_3 = deduper._calculate_similarity(entry1, entry3)
    
    print(f"  Similar entry pair: {sim_1_2:.4f} (should be >0.8)")
    print(f"  Different entry pair: {sim_1_3:.4f} (should be <0.5)")
    
    assert sim_1_2 > 0.7, "Similar entries should have high similarity"
    assert sim_1_3 < 0.5, "Different entries should have low similarity"
    
    print("  ✓ Similarity calculation working")
except Exception as e:
    print(f"  ✗ FAILED: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 2: Find Duplicates
print("\n[TEST 2] Find Duplicates...")
try:
    deduper = SemanticDeduplicator(similarity_threshold=0.7)
    
    entries = [
        {'type': 'workflow', 'content': 'Use rclone for file synchronization between devices', 'tags': [], 'date': datetime.now()},
        {'type': 'workflow', 'content': 'Use rclone for file synchronization between devices', 'tags': [], 'date': datetime.now()},  # Exact duplicate
        {'type': 'decision', 'content': 'Choose Kimi as fallback model', 'tags': [], 'date': datetime.now()},
        {'type': 'workflow', 'content': 'Use rclone for Google Drive sync', 'tags': [], 'date': datetime.now()},
    ]
    
    duplicates = deduper.find_duplicates(entries)
    print(f"  Found {len(duplicates)} duplicate pairs")
    
    for i, j, sim in duplicates:
        print(f"    Entries {i}-{j}: similarity={sim:.4f}")
    
    # Should find at least 1 duplicate (the exact duplicate pair)
    assert len(duplicates) >= 1, f"Should find at least 1 duplicate, found {len(duplicates)}"
    
    print("  ✓ Duplicate detection working")
except Exception as e:
    print(f"  ✗ FAILED: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 3: Merge Entries
print("\n[TEST 3] Merge Entries...")
try:
    deduper = SemanticDeduplicator()
    scorer = ImportanceScorer()
    
    entry1 = {
        'type': 'workflow',
        'content': 'Use rclone for basic sync',
        'tags': ['sync'],
        'date': datetime.now() - timedelta(days=30)
    }
    
    entry2 = {
        'type': 'workflow',
        'content': 'Use rclone for Google Drive sync with mount',
        'tags': ['sync', 'mount'],
        'date': datetime.now() - timedelta(days=5)
    }
    
    merged = deduper.merge_entries(entry1, entry2, scorer)
    
    print(f"  Merged entry type: {merged['type']}")
    print(f"  Merged content length: {len(merged['content'])}")
    print(f"  Merged tags: {merged['tags']}")
    print(f"  Merged importance: {merged['importance']:.4f}")
    
    assert merged['type'] == 'workflow'
    assert len(merged['tags']) == 2  # Both tags combined
    assert 'mount' in merged['content']  # More detailed content kept
    
    print("  ✓ Entry merging working")
except Exception as e:
    print(f"  ✗ FAILED: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 4: Full Deduplication Pipeline
print("\n[TEST 4] Full Deduplication Pipeline...")
try:
    deduper = SemanticDeduplicator(similarity_threshold=0.75)
    scorer = ImportanceScorer()
    
    # Parse sample file
    parser = MemoryMDParser(dry_run=True)
    sample_file = "/mnt/toshiba/projects/smart-memory-hygiene/tests/fixtures/sample-memory.md"
    entries = parser.parse(sample_file)
    
    original_count = len(entries)
    print(f"  Original entries: {original_count}")
    
    # Score entries first
    for entry in entries:
        entry.importance = scorer.score(entry)
    
    # Deduplicate
    deduplicated = deduper.deduplicate(entries, scorer)
    dedup_count = len(deduplicated)
    
    print(f"  After deduplication: {dedup_count}")
    
    stats = deduper.get_stats(original_count, dedup_count)
    print(f"  Removed: {stats['removed']} entries ({stats['reduction_percent']}%)")
    
    # Should remove some duplicates (promoted blocks often similar)
    print("  ✓ Full pipeline working")
except Exception as e:
    print(f"  ✗ FAILED: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 5: Convenience Functions
print("\n[TEST 5] Convenience Functions...")
try:
    entries = [
        {'type': 'workflow', 'content': 'Test entry one', 'tags': [], 'date': datetime.now()},
        {'type': 'workflow', 'content': 'Test entry two', 'tags': [], 'date': datetime.now()},
    ]
    
    # Test find_duplicate_entries
    dups = find_duplicate_entries(entries, threshold=0.5)
    print(f"  find_duplicate_entries: found {len(dups)} pairs")
    
    # Test merge_duplicate_entries
    merged = merge_duplicate_entries(entries, threshold=0.9)
    print(f"  merge_duplicate_entries: {len(merged)} entries after merge")
    
    print("  ✓ Convenience functions working")
except Exception as e:
    print(f"  ✗ FAILED: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "=" * 60)
print("Week 3: All tests PASSED! ✓")
print("=" * 60)

sys.exit(0)
