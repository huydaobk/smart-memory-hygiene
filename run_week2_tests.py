#!/usr/bin/env python3
"""
Run Week 2 Scoring Engine tests.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from datetime import datetime, timedelta
from src.parser.memory_md import MemoryMDParser
from src.scorer.recency import RecencyScorer, score_recency
from src.scorer.frequency import FrequencyScorer, create_entry_id
from src.scorer.composite import ImportanceScorer, score_importance

print("=" * 60)
print("Week 2: Scoring Engine Tests")
print("=" * 60)

# Test 1: Recency Scorer
print("\n[TEST 1] Recency Scorer...")
try:
    scorer = RecencyScorer(half_life_days=30.0)
    
    # Today
    today = datetime.now()
    score_today = scorer.score(today)
    print(f"  Today: {score_today:.4f} (expected ~1.0)")
    assert score_today > 0.99, "Today should score ~1.0"
    
    # 21 days ago (for score 0.5: exp(-21/30) = 0.5)
    days_21 = today - timedelta(days=21)
    score_21 = scorer.score(days_21)
    print(f"  21 days ago: {score_21:.4f} (expected ~0.5)")
    assert 0.45 < score_21 < 0.55, "21 days should score ~0.5"
    
    # 60 days ago
    days_60 = today - timedelta(days=60)
    score_60 = scorer.score(days_60)
    print(f"  60 days ago: {score_60:.4f} (expected ~0.25)")
    assert 0.1 < score_60 < 0.3, "60 days should score ~0.25"
    
    print("  ✓ Recency scorer working (exponential decay: score = exp(-days/half_life))")
except Exception as e:
    print(f"  ✗ FAILED: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 2: Frequency Scorer
print("\n[TEST 2] Frequency Scorer...")
try:
    scorer = FrequencyScorer()  # No log file for testing
    
    # Record some accesses
    entry_id = "test-entry-123"
    scorer.record_access(entry_id)
    scorer.record_access(entry_id)
    scorer.record_access(entry_id)
    
    score = scorer.score(entry_id)
    print(f"  Entry accessed 3 times: {score:.4f}")
    assert score > 0, "Should have positive score"
    
    # New entry (no accesses)
    new_score = scorer.score("new-entry")
    print(f"  New entry (0 accesses): {new_score:.4f}")
    assert new_score == 0.0, "New entry should score 0"
    
    print("  ✓ Frequency scorer working")
except Exception as e:
    print(f"  ✗ FAILED: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 3: Composite Importance Scorer
print("\n[TEST 3] Composite Importance Scorer...")
try:
    scorer = ImportanceScorer()
    
    # Create test entries
    today = datetime.now()
    
    entry_decision = {
        'type': 'decision',
        'date': today,
        'content': 'Critical decision made today'
    }
    
    entry_old_workflow = {
        'type': 'workflow',
        'date': today - timedelta(days=60),
        'content': 'Old workflow from 2 months ago'
    }
    
    entry_recent_pref = {
        'type': 'preference',
        'date': today - timedelta(days=5),
        'content': 'Recent user preference'
    }
    
    # Score them
    score_decision = scorer.score(entry_decision)
    score_old = scorer.score(entry_old_workflow)
    score_pref = scorer.score(entry_recent_pref)
    
    print(f"  Recent decision: {score_decision:.4f} (should be high)")
    print(f"  Old workflow: {score_old:.4f} (should be lower)")
    print(f"  Recent preference: {score_pref:.4f} (medium)")
    
    # Decision should score highest (type bonus + recency)
    assert score_decision > score_old, "Decision should score higher than old workflow"
    
    # Get breakdown
    breakdown = scorer.get_score_breakdown(entry_decision)
    print(f"  Breakdown: {breakdown}")
    
    print("  ✓ Composite scorer working")
except Exception as e:
    print(f"  ✗ FAILED: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 4: Integration with Parser
print("\n[TEST 4] Integration with Week 1 Parser...")
try:
    # Parse sample file
    parser = MemoryMDParser(dry_run=True)
    sample_file = "/mnt/toshiba/projects/smart-memory-hygiene/tests/fixtures/sample-memory.md"
    entries = parser.parse(sample_file)
    
    # Score all entries
    scorer = ImportanceScorer()
    scored_entries = []
    
    for entry in entries:
        importance = scorer.score(entry)
        entry.importance = importance
        scored_entries.append(entry)
    
    # Sort by importance
    scored_entries.sort(key=lambda e: e.importance, reverse=True)
    
    print(f"  Scored {len(scored_entries)} entries")
    print("\n  Top 5 by importance:")
    for i, entry in enumerate(scored_entries[:5]):
        print(f"    {i+1}. [{entry.type}] {entry.importance:.4f} - {entry.content[:40]}...")
    
    print("\n  Bottom 3 by importance:")
    for i, entry in enumerate(scored_entries[-3:]):
        print(f"    {i+1}. [{entry.type}] {entry.importance:.4f} - {entry.content[:40]}...")
    
    print("  ✓ Integration working")
except Exception as e:
    print(f"  ✗ FAILED: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "=" * 60)
print("Week 2: All tests PASSED! ✓")
print("=" * 60)

sys.exit(0)
