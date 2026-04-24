#!/usr/bin/env python3
"""
Run Week 4 Archive Management tests.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from datetime import datetime, timedelta
from pathlib import Path
import tempfile

from src.archiver.manager import ArchiveManager, archive_low_importance_entries, search_archive

print("=" * 60)
print("Week 4: Archive Management Tests")
print("=" * 60)

# Test 1: Archive Manager Initialization
print("\n[TEST 1] Archive Manager Initialization...")
try:
    with tempfile.TemporaryDirectory() as tmp_dir:
        manager = ArchiveManager(
            archive_dir=tmp_dir,
            importance_threshold=0.3,
            max_age_days=90
        )
        
        print(f"  Archive dir: {manager.archive_dir}")
        print(f"  Index file: {manager.index_file}")
        print(f"  Threshold: {manager.importance_threshold}")
        
        assert manager.archive_dir.exists(), "Archive dir should be created"
        assert manager.index_file.exists(), "Index file should be created"
        
        print("  ✓ Archive manager initialized")
except Exception as e:
    print(f"  ✗ FAILED: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 2: Should Archive Decision
print("\n[TEST 2] Should Archive Decision...")
try:
    with tempfile.TemporaryDirectory() as tmp_dir:
        manager = ArchiveManager(
            archive_dir=tmp_dir,
            importance_threshold=0.3,
            max_age_days=90
        )
        
        # Low importance entry
        low_entry = {
            'type': 'preference',
            'content': 'Old preference about UI color',
            'date': datetime.now() - timedelta(days=10),
            'importance': 0.2,
            'tags': []
        }
        
        should, reason = manager.should_archive(low_entry)
        print(f"  Low importance (0.2): should={should}, reason={reason}")
        assert should is True, "Low importance should be archived"
        
        # High importance entry
        high_entry = {
            'type': 'decision',
            'content': 'Critical architecture decision',
            'date': datetime.now() - timedelta(days=10),
            'importance': 0.9,
            'tags': []
        }
        
        should, reason = manager.should_archive(high_entry)
        print(f"  High importance (0.9): should={should}, reason={reason}")
        assert should is False, "High importance should not be archived"
        
        # Old entry
        old_entry = {
            'type': 'workflow',
            'content': 'Very old workflow',
            'date': datetime.now() - timedelta(days=100),
            'importance': 0.5,
            'tags': []
        }
        
        should, reason = manager.should_archive(old_entry)
        print(f"  Old entry (100 days): should={should}, reason={reason}")
        assert should is True, "Old entries should be archived"
        
        print("  ✓ Archive decisions working")
except Exception as e:
    print(f"  ✗ FAILED: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 3: Archive Entry
print("\n[TEST 3] Archive Entry...")
try:
    with tempfile.TemporaryDirectory() as tmp_dir:
        manager = ArchiveManager(
            archive_dir=tmp_dir,
            importance_threshold=0.3
        )
        
        entry = {
            'type': 'preference',
            'content': 'Test entry for archiving',
            'date': datetime.now() - timedelta(days=5),
            'importance': 0.2,
            'tags': ['test', 'archive']
        }
        
        archive_id = manager.archive_entry(entry)
        print(f"  Archived with ID: {archive_id}")
        
        assert archive_id is not None, "Should return archive ID"
        
        # Check file exists
        archive_file = manager.archive_dir / f"{archive_id}.json"
        assert archive_file.exists(), "Archive file should exist"
        
        print("  ✓ Entry archived successfully")
except Exception as e:
    print(f"  ✗ FAILED: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 4: Retrieve Entry
print("\n[TEST 4] Retrieve Entry...")
try:
    with tempfile.TemporaryDirectory() as tmp_dir:
        manager = ArchiveManager(
            archive_dir=tmp_dir,
            importance_threshold=0.3
        )
        
        # Archive an entry
        entry = {
            'type': 'workflow',
            'content': 'Retrievable workflow entry',
            'date': datetime.now(),
            'importance': 0.2,
            'tags': ['retrieval', 'test']
        }
        
        archive_id = manager.archive_entry(entry)
        
        # Retrieve it
        retrieved = manager.retrieve_entry(archive_id)
        print(f"  Retrieved entry type: {retrieved['type']}")
        print(f"  Retrieved content: {retrieved['content'][:40]}...")
        
        assert retrieved is not None, "Should retrieve entry"
        assert retrieved['type'] == 'workflow', "Type should match"
        
        print("  ✓ Entry retrieval working")
except Exception as e:
    print(f"  ✗ FAILED: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 5: Archive Multiple Entries
print("\n[TEST 5] Archive Multiple Entries...")
try:
    with tempfile.TemporaryDirectory() as tmp_dir:
        entries = [
            {'type': 'preference', 'content': 'Entry 1', 'date': datetime.now(), 'importance': 0.2, 'tags': []},
            {'type': 'preference', 'content': 'Entry 2', 'date': datetime.now(), 'importance': 0.1, 'tags': []},
            {'type': 'decision', 'content': 'Entry 3 (high)', 'date': datetime.now(), 'importance': 0.8, 'tags': []},
        ]
        
        archived_ids = archive_low_importance_entries(entries, tmp_dir, threshold=0.3)
        print(f"  Archived {len(archived_ids)} entries")
        
        assert len(archived_ids) == 2, "Should archive 2 low-importance entries"
        
        print("  ✓ Batch archiving working")
except Exception as e:
    print(f"  ✗ FAILED: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 6: Search Archives
print("\n[TEST 6] Search Archives...")
try:
    with tempfile.TemporaryDirectory() as tmp_dir:
        # Create manager and archive some entries
        manager = ArchiveManager(
            archive_dir=tmp_dir,
            importance_threshold=0.3
        )
        
        entries = [
            {'type': 'workflow', 'content': 'Google Drive sync workflow', 'date': datetime.now(), 'importance': 0.2, 'tags': ['drive']},
            {'type': 'decision', 'content': 'Use Kimi model decision', 'date': datetime.now(), 'importance': 0.1, 'tags': ['model']},
        ]
        
        for entry in entries:
            manager.archive_entry(entry)
        
        # Search
        results = search_archive(tmp_dir, 'drive', limit=5)
        print(f"  Search 'drive': found {len(results)} results")
        
        assert len(results) >= 1, "Should find drive-related entry"
        
        print("  ✓ Archive search working")
except Exception as e:
    print(f"  ✗ FAILED: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 7: Archive Stats
print("\n[TEST 7] Archive Statistics...")
try:
    with tempfile.TemporaryDirectory() as tmp_dir:
        manager = ArchiveManager(
            archive_dir=tmp_dir,
            importance_threshold=0.3
        )
        
        # Archive some entries
        entries = [
            {'type': 'workflow', 'content': 'Workflow 1', 'date': datetime.now(), 'importance': 0.2, 'tags': []},
            {'type': 'workflow', 'content': 'Workflow 2', 'date': datetime.now(), 'importance': 0.1, 'tags': []},
            {'type': 'preference', 'content': 'Preference 1', 'date': datetime.now(), 'importance': 0.15, 'tags': []},
        ]
        
        for entry in entries:
            manager.archive_entry(entry)
        
        stats = manager.get_stats()
        print(f"  Total archived: {stats['total_archived']}")
        print(f"  By type: {stats['by_type']}")
        print(f"  By reason: {stats['by_reason']}")
        
        assert stats['total_archived'] == 3, "Should have 3 archived entries"
        assert 'workflow' in stats['by_type'], "Should track workflow type"
        
        print("  ✓ Archive stats working")
except Exception as e:
    print(f"  ✗ FAILED: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "=" * 60)
print("Week 4: All tests PASSED! ✓")
print("=" * 60)

sys.exit(0)
