#!/usr/bin/env python3
"""
Run MEMORY.md parser tests (standalone, no pytest required).
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.parser.memory_md import MemoryMDParser

print("=" * 60)
print("MEMORY.md Parser Tests (Standalone)")
print("=" * 60)

# Test 1: Basic parsing
print("\n[TEST 1] Parse sample file...")
try:
    parser = MemoryMDParser(dry_run=True)
    sample_file = "/mnt/toshiba/projects/smart-memory-hygiene/tests/fixtures/sample-memory.md"
    entries = parser.parse(sample_file)
    print(f"✓ Parsed {len(entries)} entries")
    
    # Show breakdown
    stats = parser.get_stats(entries)
    print(f"  - By type: {stats['by_type']}")
    print(f"  - With dates: {stats['with_dates']}")
    print(f"  - With tags: {stats['with_tags']}")
except Exception as e:
    print(f"✗ FAILED: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 2: Entry types
print("\n[TEST 2] Check entry types...")
types_found = set(e.type for e in entries)
expected = {'workflow', 'decision', 'preference', 'instruction', 'error→workflow'}
missing = expected - types_found
if missing:
    print(f"⚠ Missing types: {missing}")
else:
    print(f"✓ All expected types found: {types_found}")

# Test 3: Date extraction
print("\n[TEST 3] Date extraction...")
dated = [e for e in entries if e.date]
print(f"✓ {len(dated)} entries have dates")
if dated:
    print(f"  - Date range: {min(e.date for e in dated)} to {max(e.date for e in dated)}")

# Test 4: Tag extraction
print("\n[TEST 4] Tag extraction...")
tagged = [e for e in entries if e.tags]
print(f"✓ {len(tagged)} entries have tags")
all_tags = set()
for e in tagged:
    all_tags.update(e.tags)
print(f"  - Unique tags: {all_tags}")

# Test 5: Validation
print("\n[TEST 5] Validation...")
is_valid = parser.validate(entries)
print(f"{'✓' if is_valid else '✗'} Validation: {is_valid}")

# Test 6: Show sample entries
print("\n[TEST 6] Sample entries...")
for i, entry in enumerate(entries[:3]):
    print(f"\n  Entry {i+1}:")
    print(f"    Type: {entry.type}")
    print(f"    Date: {entry.date}")
    print(f"    Section: {entry.section}")
    print(f"    Content: {entry.content[:60]}...")
    print(f"    Tags: {entry.tags}")

print("\n" + "=" * 60)
print("All tests completed!")
print("=" * 60)

# Return exit code
sys.exit(0 if is_valid else 1)
