"""
Unit tests for MEMORY.md parser.
Run with: python3 -m pytest tests/test_parser_memory_md.py -v
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime
from pathlib import Path
from src.parser.memory_md import MemoryMDParser, MemoryEntry, parse_memory_md, get_memory_stats


class TestMemoryEntry:
    """Tests for MemoryEntry dataclass."""
    
    def test_basic_creation(self):
        entry = MemoryEntry(
            type="workflow",
            date=datetime(2026, 4, 13),
            content="Test content",
            tags=["REL:test"]
        )
        assert entry.type == "workflow"
        assert entry.date.year == 2026
        assert entry.content == "Test content"
        assert entry.tags == ["REL:test"]


class TestMemoryMDParser:
    """Tests for MemoryMDParser class."""
    
    def setup_method(self):
        """Setup for each test method."""
        self.parser = MemoryMDParser(dry_run=True)
        self.sample_file = "/mnt/toshiba/projects/smart-memory-hygiene/tests/fixtures/sample-memory.md"
    
    def test_parse_file_exists(self):
        """Test parsing existing file."""
        entries = self.parser.parse(self.sample_file)
        assert len(entries) > 0
    
    def test_parse_file_not_found(self):
        """Test parsing non-existent file raises error."""
        try:
            self.parser.parse("/nonexistent/path/MEMORY.md")
            assert False, "Should have raised FileNotFoundError"
        except FileNotFoundError:
            pass
    
    def test_workflow_entry_parsing(self):
        """Test parsing workflow entries."""
        entries = self.parser.parse(self.sample_file)
        workflow_entries = [e for e in entries if e.type == "workflow"]
        assert len(workflow_entries) > 0
        
        # Check first workflow entry
        entry = workflow_entries[0]
        assert "Google Drive" in entry.content or "Blocker" in entry.content
    
    def test_decision_entry_parsing(self):
        """Test parsing decision entries."""
        entries = self.parser.parse(self.sample_file)
        decision_entries = [e for e in entries if e.type == "decision"]
        assert len(decision_entries) > 0
        
        # Check decision content
        entry = decision_entries[0]
        assert "NotebookLM" in entry.content or "Fireworks" in entry.content
    
    def test_error_workflow_entry_parsing(self):
        """Test parsing error→workflow entries."""
        entries = self.parser.parse(self.sample_file)
        error_entries = [e for e in entries if e.type == "error→workflow"]
        assert len(error_entries) > 0
    
    def test_preference_entry_parsing(self):
        """Test parsing preference entries."""
        entries = self.parser.parse(self.sample_file)
        pref_entries = [e for e in entries if e.type == "preference"]
        assert len(pref_entries) > 0
    
    def test_instruction_entry_parsing(self):
        """Test parsing instruction entries."""
        entries = self.parser.parse(self.sample_file)
        inst_entries = [e for e in entries if e.type == "instruction"]
        assert len(inst_entries) > 0
    
    def test_date_extraction(self):
        """Test date extraction from entries."""
        entries = self.parser.parse(self.sample_file)
        dated_entries = [e for e in entries if e.date is not None]
        assert len(dated_entries) > 0
        
        # Check date range
        for entry in dated_entries:
            assert entry.date.year >= 2026
    
    def test_tag_extraction(self):
        """Test tag extraction (REL, CAUSED_BY, synced)."""
        entries = self.parser.parse(self.sample_file)
        tagged_entries = [e for e in entries if e.tags]
        assert len(tagged_entries) > 0
        
        # Check specific tags
        for entry in tagged_entries:
            for tag in entry.tags:
                assert tag.startswith("REL:") or tag.startswith("CAUSED_BY:") or tag == "synced"
    
    def test_section_detection(self):
        """Test section header detection."""
        entries = self.parser.parse(self.sample_file)
        
        # All entries should have a section
        for entry in entries:
            assert entry.section is not None
            assert len(entry.section) > 0
    
    def test_validate_entries(self):
        """Test entry validation."""
        entries = self.parser.parse(self.sample_file)
        is_valid = self.parser.validate(entries)
        assert is_valid is True
    
    def test_get_stats(self):
        """Test statistics generation."""
        entries = self.parser.parse(self.sample_file)
        stats = self.parser.get_stats(entries)
        
        assert stats['total_entries'] > 0
        assert 'by_type' in stats
        assert 'by_section' in stats
        assert stats['with_dates'] >= 0
        assert stats['with_tags'] >= 0
    
    def test_write_dry_run(self):
        """Test write operation in dry-run mode."""
        import tempfile
        entries = self.parser.parse(self.sample_file)
        
        with tempfile.TemporaryDirectory() as tmp_dir:
            output_file = Path(tmp_dir) / "output.md"
            result = self.parser.write(entries, str(output_file))
            assert result is True
            assert not output_file.exists()  # Should not create file in dry-run


class TestConvenienceFunctions:
    """Tests for convenience functions."""
    
    def test_parse_memory_md(self):
        """Test parse_memory_md convenience function."""
        sample_file = "/mnt/toshiba/projects/smart-memory-hygiene/tests/fixtures/sample-memory.md"
        entries = parse_memory_md(sample_file, dry_run=True)
        assert len(entries) > 0
    
    def test_get_memory_stats(self):
        """Test get_memory_stats convenience function."""
        sample_file = "/mnt/toshiba/projects/smart-memory-hygiene/tests/fixtures/sample-memory.md"
        stats = get_memory_stats(sample_file)
        
        assert 'total_entries' in stats
        assert stats['total_entries'] > 0


class TestEdgeCases:
    """Tests for edge cases and error handling."""
    
    def setup_method(self):
        self.parser = MemoryMDParser(dry_run=True)
    
    def test_empty_content(self):
        """Test parsing empty content."""
        entries = self.parser.parse_content("")
        assert len(entries) == 0
    
    def test_malformed_entries(self):
        """Test handling malformed entries."""
        content = """
## Test Section
- [invalidtype] This should not parse
- [workflow Missing bracket content
- Normal text without tag
- [workflow] Valid entry [synced]
"""
        entries = self.parser.parse_content(content)
        # Should only parse valid entries
        assert len(entries) >= 1
        assert entries[0].type == "workflow"
    
    def test_promoted_block_skip(self):
        """Test that promoted block markers are skipped."""
        content = """
## Section
<!-- openclaw-memory-promotion:memory:2026-04-24.md:1:4 -->
- [workflow] Real entry [synced]
"""
        entries = self.parser.parse_content(content)
        assert len(entries) == 1
        assert "openclaw-memory-promotion" not in entries[0].content


if __name__ == "__main__":
    # Run tests without pytest
    import sys
    
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
    
    print("\n" + "=" * 60)
    print("All tests completed!")
    print("=" * 60)
