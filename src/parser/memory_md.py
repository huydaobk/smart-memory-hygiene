"""
MEMORY.md Parser for Smart Memory Hygiene Framework.

Parses OpenClaw MEMORY.md files into structured MemoryEntry objects.
Supports roundtrip parsing: file -> entries -> file (lossless or improved).
"""

import re
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict, Any
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class MemoryEntry:
    """Represents a single memory entry from MEMORY.md."""
    
    type: str  # workflow, decision, error, preference, instruction, etc.
    date: Optional[datetime]  # Extracted date
    content: str  # Clean content
    tags: List[str] = field(default_factory=list)  # REL, CAUSED_BY, etc.
    metadata: Dict[str, Any] = field(default_factory=dict)  # Extra info
    raw_text: str = ""  # Original text for reconstruction
    section: str = ""  # Parent section (e.g., "Workflow", "Critical Rules")
    
    # Scoring (populated later)
    importance: float = 0.0
    recency_score: float = 0.0
    frequency_score: float = 0.0


class MemoryMDParser:
    """Parser for OpenClaw MEMORY.md files."""
    
    # Entry type patterns
    ENTRY_PATTERNS = {
        'workflow': r'^\s*-\s*\[workflow\]\s*(.+?)(?:\s*\[synced\])?$',
        'decision': r'^\s*-\s*\[decision\]\s*(.+)$',
        'error': r'^\s*-\s*\[error\]\s*(.+)$',
        'error_workflow': r'^\s*-\s*\[error→workflow\]\s*(.+)$',
        'preference': r'^\s*-\s*\[preference\]\s*(.+)$',
        'instruction': r'^\s*-\s*\[instruction\]\s*(.+)$',
        'workflow_error': r'^\s*-\s*\[workflow\]\s*\[error\]\s*(.+)$',
    }
    
    # Date patterns
    DATE_PATTERNS = [
        r'\((\d{4}-\d{2}-\d{2})\)',  # (2026-04-13)
        r'(\d{4}-\d{2}-\d{2})',  # 2026-04-13
    ]
    
    # Tag patterns
    TAG_PATTERNS = {
        'REL': r'REL:\s*(\S+)',
        'CAUSED_BY': r'CAUSED_BY\s+(\S+)',
        'synced': r'\[synced\]',
    }
    
    def __init__(self, dry_run: bool = True):
        """
        Initialize parser.
        
        Args:
            dry_run: If True, never modifies original files (default: True)
        """
        self.dry_run = dry_run
        self.errors: List[str] = []
    
    def parse(self, file_path: str) -> List[MemoryEntry]:
        """
        Parse MEMORY.md file into list of MemoryEntry objects.
        
        Args:
            file_path: Path to MEMORY.md file
            
        Returns:
            List of MemoryEntry objects
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        content = path.read_text(encoding='utf-8')
        return self.parse_content(content)
    
    def parse_content(self, content: str) -> List[MemoryEntry]:
        """Parse raw content string."""
        entries = []
        lines = content.split('\n')
        
        current_section = ""
        i = 0
        while i < len(lines):
            line = lines[i]
            
            # Detect sections (## or ### headers)
            if line.startswith('## ') or line.startswith('### '):
                current_section = line.lstrip('#').strip()
                i += 1
                continue
            
            # Skip promoted block markers
            if '<!-- openclaw-memory-promotion:' in line:
                i += 1
                continue
            
            # Try to parse entry
            entry = self._parse_line(line, current_section)
            if entry:
                entry.raw_text = line
                entries.append(entry)
            
            i += 1
        
        logger.info(f"Parsed {len(entries)} entries from content")
        return entries
    
    def _parse_line(self, line: str, section: str) -> Optional[MemoryEntry]:
        """Parse a single line into MemoryEntry if it matches patterns."""
        
        for entry_type, pattern in self.ENTRY_PATTERNS.items():
            match = re.match(pattern, line, re.IGNORECASE)
            if match:
                content = match.group(1).strip()
                
                # Extract date
                date = self._extract_date(content) or self._extract_date(section)
                
                # Extract tags
                tags = self._extract_tags(line)
                
                # Normalize type
                normalized_type = entry_type.replace('_', '→')
                
                return MemoryEntry(
                    type=normalized_type,
                    date=date,
                    content=content,
                    tags=tags,
                    section=section,
                    raw_text=line
                )
        
        return None
    
    def _extract_date(self, text: str) -> Optional[datetime]:
        """Extract date from text."""
        for pattern in self.DATE_PATTERNS:
            match = re.search(pattern, text)
            if match:
                date_str = match.group(1)
                try:
                    return datetime.strptime(date_str, '%Y-%m-%d')
                except ValueError:
                    continue
        return None
    
    def _extract_tags(self, text: str) -> List[str]:
        """Extract tags like REL, CAUSED_BY from text."""
        tags = []
        
        for tag_name, pattern in self.TAG_PATTERNS.items():
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                if tag_name == 'synced':
                    tags.append('synced')
                else:
                    tags.append(f"{tag_name}:{match}")
        
        return tags
    
    def write(self, entries: List[MemoryEntry], file_path: str, 
              backup: bool = True) -> bool:
        """
        Write entries back to MEMORY.md format.
        
        Args:
            entries: List of MemoryEntry objects
            file_path: Output file path
            backup: Create backup before writing (default: True)
            
        Returns:
            True if successful
        """
        if self.dry_run:
            logger.info(f"DRY RUN: Would write {len(entries)} entries to {file_path}")
            return True
        
        path = Path(file_path)
        
        # Backup if requested and file exists
        if backup and path.exists():
            backup_path = path.with_suffix(f".md.backup.{datetime.now():%Y%m%d_%H%M%S}")
            path.rename(backup_path)
            logger.info(f"Backup created: {backup_path}")
        
        # Generate content
        content = self._generate_content(entries)
        
        # Write file
        path.write_text(content, encoding='utf-8')
        logger.info(f"Written {len(entries)} entries to {file_path}")
        
        return True
    
    def _generate_content(self, entries: List[MemoryEntry]) -> str:
        """Generate MEMORY.md formatted content from entries."""
        lines = []
        
        # Group by section
        sections: Dict[str, List[MemoryEntry]] = {}
        for entry in entries:
            section = entry.section or "Uncategorized"
            if section not in sections:
                sections[section] = []
            sections[section].append(entry)
        
        # Generate output
        for section, section_entries in sections.items():
            lines.append(f"## {section}")
            lines.append("")
            
            for entry in section_entries:
                # Reconstruct entry line
                line = f"- [{entry.type}] {entry.content}"
                
                # Add tags back
                if 'synced' in entry.tags:
                    line += " [synced]"
                
                for tag in entry.tags:
                    if tag.startswith('REL:'):
                        line += f" REL: {tag[4:]}"
                    elif tag.startswith('CAUSED_BY:'):
                        line += f" CAUSED_BY {tag[10:]}"
                
                lines.append(line)
            
            lines.append("")
        
        return '\n'.join(lines)
    
    def validate(self, entries: List[MemoryEntry]) -> bool:
        """
        Validate parsed entries for data integrity.
        
        Args:
            entries: List of MemoryEntry objects
            
        Returns:
            True if valid
        """
        if not entries:
            logger.warning("No entries to validate")
            return False
        
        valid = True
        
        for i, entry in enumerate(entries):
            # Check required fields
            if not entry.type:
                logger.error(f"Entry {i}: Missing type")
                valid = False
            
            if not entry.content:
                logger.error(f"Entry {i}: Missing content")
                valid = False
            
            # Check for suspicious patterns
            if len(entry.content) < 5:
                logger.warning(f"Entry {i}: Very short content: {entry.content}")
        
        logger.info(f"Validation: {len(entries)} entries, valid={valid}")
        return valid
    
    def get_stats(self, entries: List[MemoryEntry]) -> Dict[str, Any]:
        """Get statistics about parsed entries."""
        stats = {
            'total_entries': len(entries),
            'by_type': {},
            'by_section': {},
            'with_dates': 0,
            'with_tags': 0,
            'date_range': {'min': None, 'max': None},
        }
        
        dates = []
        
        for entry in entries:
            # Count by type
            stats['by_type'][entry.type] = stats['by_type'].get(entry.type, 0) + 1
            
            # Count by section
            stats['by_section'][entry.section] = stats['by_section'].get(entry.section, 0) + 1
            
            # Count with dates
            if entry.date:
                stats['with_dates'] += 1
                dates.append(entry.date)
            
            # Count with tags
            if entry.tags:
                stats['with_tags'] += 1
        
        if dates:
            stats['date_range']['min'] = min(dates).isoformat()
            stats['date_range']['max'] = max(dates).isoformat()
        
        return stats


# Convenience functions
def parse_memory_md(file_path: str, dry_run: bool = True) -> List[MemoryEntry]:
    """Convenience function to parse MEMORY.md file."""
    parser = MemoryMDParser(dry_run=dry_run)
    return parser.parse(file_path)


def get_memory_stats(file_path: str) -> Dict[str, Any]:
    """Get statistics about a MEMORY.md file."""
    parser = MemoryMDParser(dry_run=True)
    entries = parser.parse(file_path)
    return parser.get_stats(entries)
