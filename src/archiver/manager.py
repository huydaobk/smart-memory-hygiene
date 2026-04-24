"""
Archive Manager for Smart Memory Hygiene.

Manages archiving of low-importance entries to cold storage.
Supports retrieval and lifecycle management.
"""

import json
import shutil
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional, Any
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ArchiveManager:
    """
    Manages archive lifecycle for memory entries.
    
    Archive rules:
    - Entries with importance < threshold → archive
    - Entries older than max_age → archive
    - Promoted blocks > 30 days → archive
    """
    
    DEFAULT_IMPORTANCE_THRESHOLD = 0.3
    DEFAULT_MAX_AGE_DAYS = 90
    DEFAULT_PROMOTED_BLOCK_AGE = 30
    
    def __init__(self, 
                 archive_dir: str,
                 importance_threshold: float = DEFAULT_IMPORTANCE_THRESHOLD,
                 max_age_days: int = DEFAULT_MAX_AGE_DAYS,
                 promoted_block_age: int = DEFAULT_PROMOTED_BLOCK_AGE):
        """
        Initialize archive manager.
        
        Args:
            archive_dir: Directory to store archived entries
            importance_threshold: Entries below this score get archived
            max_age_days: Entries older than this get archived
            promoted_block_age: Promoted blocks older than this get archived
        """
        self.archive_dir = Path(archive_dir)
        self.importance_threshold = importance_threshold
        self.max_age_days = max_age_days
        self.promoted_block_age = promoted_block_age
        
        # Ensure archive directory exists
        self.archive_dir.mkdir(parents=True, exist_ok=True)
        
        # Archive index file
        self.index_file = self.archive_dir / "archive_index.json"
        self._load_index()
        
        # Save initial index if it doesn't exist
        if not self.index_file.exists():
            self._save_index()
    
    def _load_index(self):
        """Load archive index from disk."""
        if self.index_file.exists():
            with open(self.index_file, 'r') as f:
                self.index = json.load(f)
        else:
            self.index = {
                'version': '1.0',
                'created': datetime.now().isoformat(),
                'entries': []
            }
    
    def _save_index(self):
        """Save archive index to disk."""
        self.index_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.index_file, 'w') as f:
            json.dump(self.index, f, indent=2, default=str)
    
    def should_archive(self, entry) -> tuple[bool, str]:
        """
        Determine if an entry should be archived.
        
        Returns:
            (should_archive, reason)
        """
        # Extract attributes
        importance = self._get_importance(entry)
        entry_date = self._get_date(entry)
        entry_type = self._get_type(entry)
        
        # Check importance
        if importance < self.importance_threshold:
            return True, f"importance {importance:.3f} < {self.importance_threshold}"
        
        # Check age
        if entry_date:
            age_days = (datetime.now() - entry_date).days
            if age_days > self.max_age_days:
                return True, f"age {age_days} days > {self.max_age_days}"
        
        # Check promoted blocks
        if entry_type == 'promoted' or 'Promoted' in str(entry):
            if entry_date:
                age_days = (datetime.now() - entry_date).days
                if age_days > self.promoted_block_age:
                    return True, f"promoted block age {age_days} days > {self.promoted_block_age}"
        
        return False, ""
    
    def archive_entry(self, entry) -> Optional[str]:
        """
        Archive a single entry.
        
        Returns:
            Archive ID if successful, None otherwise
        """
        should, reason = self.should_archive(entry)
        if not should:
            return None
        
        # Generate archive ID
        archive_id = self._generate_archive_id(entry)
        
        # Prepare archive record
        archive_record = {
            'id': archive_id,
            'archived_at': datetime.now().isoformat(),
            'reason': reason,
            'entry': self._entry_to_dict(entry)
        }
        
        # Save to archive file
        archive_file = self.archive_dir / f"{archive_id}.json"
        with open(archive_file, 'w') as f:
            json.dump(archive_record, f, indent=2, default=str)
        
        # Update index
        self.index['entries'].append({
            'id': archive_id,
            'archived_at': archive_record['archived_at'],
            'reason': reason,
            'type': archive_record['entry'].get('type', 'unknown'),
            'date': archive_record['entry'].get('date')
        })
        self._save_index()
        
        logger.info(f"Archived entry {archive_id}: {reason}")
        return archive_id
    
    def archive_entries(self, entries: List) -> List[str]:
        """
        Archive multiple entries.
        
        Returns:
            List of archive IDs
        """
        archived_ids = []
        for entry in entries:
            archive_id = self.archive_entry(entry)
            if archive_id:
                archived_ids.append(archive_id)
        
        return archived_ids
    
    def retrieve_entry(self, archive_id: str) -> Optional[Dict]:
        """
        Retrieve an archived entry.
        
        Args:
            archive_id: ID of archived entry
            
        Returns:
            Entry dict if found, None otherwise
        """
        archive_file = self.archive_dir / f"{archive_id}.json"
        if not archive_file.exists():
            return None
        
        with open(archive_file, 'r') as f:
            record = json.load(f)
        
        return record['entry']
    
    def search_archives(self, query: str, limit: int = 10) -> List[Dict]:
        """
        Search archived entries.
        
        Args:
            query: Search query (matches type, content, tags)
            limit: Max results to return
            
        Returns:
            List of matching archive records
        """
        results = []
        query_lower = query.lower()
        
        for entry_info in self.index['entries']:
            archive_id = entry_info['id']
            entry = self.retrieve_entry(archive_id)
            
            if entry:
                # Check content
                content = entry.get('content', '').lower()
                entry_type = entry.get('type', '').lower()
                tags = ' '.join(entry.get('tags', [])).lower()
                
                if (query_lower in content or 
                    query_lower in entry_type or
                    query_lower in tags):
                    results.append({
                        'id': archive_id,
                        'archived_at': entry_info.get('archived_at'),
                        'reason': entry_info.get('reason'),
                        'entry': entry
                    })
                    
                    if len(results) >= limit:
                        break
        
        return results
    
    def get_stats(self) -> Dict[str, Any]:
        """Get archive statistics."""
        total_archived = len(self.index['entries'])
        
        # Count by type
        type_counts = {}
        for entry_info in self.index['entries']:
            entry_type = entry_info.get('type', 'unknown')
            type_counts[entry_type] = type_counts.get(entry_type, 0) + 1
        
        # Count by reason
        reason_counts = {}
        for entry_info in self.index['entries']:
            reason = entry_info.get('reason', 'unknown')
            # Extract main reason (before any details)
            main_reason = reason.split(':')[0] if ':' in reason else reason
            reason_counts[main_reason] = reason_counts.get(main_reason, 0) + 1
        
        return {
            'total_archived': total_archived,
            'archive_dir': str(self.archive_dir),
            'index_file': str(self.index_file),
            'by_type': type_counts,
            'by_reason': reason_counts,
            'thresholds': {
                'importance': self.importance_threshold,
                'max_age_days': self.max_age_days,
                'promoted_block_age': self.promoted_block_age
            }
        }
    
    def restore_entry(self, archive_id: str, restore_dir: str) -> Optional[Path]:
        """
        Restore an archived entry to a file.
        
        Args:
            archive_id: ID of entry to restore
            restore_dir: Directory to restore to
            
        Returns:
            Path to restored file if successful
        """
        entry = self.retrieve_entry(archive_id)
        if not entry:
            return None
        
        restore_path = Path(restore_dir) / f"restored_{archive_id}.json"
        restore_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(restore_path, 'w') as f:
            json.dump(entry, f, indent=2, default=str)
        
        return restore_path
    
    def _generate_archive_id(self, entry) -> str:
        """Generate unique archive ID for entry."""
        import hashlib
        
        content = self._get_content(entry)
        date_str = str(self._get_date(entry))
        
        text = f"{date_str}:{content[:50]}:{datetime.now().isoformat()}"
        return hashlib.md5(text.encode()).hexdigest()[:16]
    
    def _entry_to_dict(self, entry) -> Dict:
        """Convert entry to dictionary."""
        if isinstance(entry, dict):
            return entry
        
        # Convert object to dict
        return {
            'type': self._get_type(entry),
            'date': self._get_date(entry).isoformat() if self._get_date(entry) else None,
            'content': self._get_content(entry),
            'tags': self._get_tags(entry),
            'importance': self._get_importance(entry)
        }
    
    def _get_importance(self, entry) -> float:
        """Extract importance from entry."""
        if isinstance(entry, dict):
            return entry.get('importance', 0.0)
        return getattr(entry, 'importance', 0.0)
    
    def _get_date(self, entry):
        """Extract date from entry."""
        if isinstance(entry, dict):
            date_val = entry.get('date')
            if isinstance(date_val, str):
                try:
                    return datetime.fromisoformat(date_val)
                except ValueError:
                    return None
            return date_val
        return getattr(entry, 'date', None)
    
    def _get_type(self, entry) -> str:
        """Extract type from entry."""
        if isinstance(entry, dict):
            return entry.get('type', 'unknown')
        return getattr(entry, 'type', 'unknown')
    
    def _get_content(self, entry) -> str:
        """Extract content from entry."""
        if isinstance(entry, dict):
            return entry.get('content', '')
        return getattr(entry, 'content', '')
    
    def _get_tags(self, entry) -> List[str]:
        """Extract tags from entry."""
        if isinstance(entry, dict):
            return entry.get('tags', [])
        return getattr(entry, 'tags', [])


# Convenience functions
def archive_low_importance_entries(entries: List, 
                                   archive_dir: str,
                                   threshold: float = 0.3) -> List[str]:
    """Archive entries below importance threshold."""
    manager = ArchiveManager(
        archive_dir=archive_dir,
        importance_threshold=threshold
    )
    return manager.archive_entries(entries)


def search_archive(archive_dir: str, query: str, limit: int = 10) -> List[Dict]:
    """Search archived entries."""
    manager = ArchiveManager(archive_dir=archive_dir)
    return manager.search_archives(query, limit)
