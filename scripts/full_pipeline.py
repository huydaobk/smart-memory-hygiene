#!/usr/bin/env python3
"""
Full pipeline runner for Smart Memory Hygiene.

Runs: Parse → Score → Deduplicate → Archive → Predict
Dry-run by default.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from src.parser.memory_md import MemoryMDParser
from src.scorer.composite import ImportanceScorer
from src.deduper.semantic import SemanticDeduplicator
from src.archiver.manager import ArchiveManager
from src.prediction.engine import PredictionEngine


def run_pipeline(memory_file: str, archive_dir: str, dry_run: bool = True) -> dict:
    parser = MemoryMDParser(dry_run=dry_run)
    entries = parser.parse(memory_file)

    scorer = ImportanceScorer()
    scored = []
    for entry in entries:
        imp = scorer.score(entry)
        if hasattr(entry, "importance"):
            entry.importance = imp
        scored.append(entry)

    deduper = SemanticDeduplicator(similarity_threshold=0.8)
    deduped = deduper.deduplicate(scored, importance_scorer=scorer)

    archiver = ArchiveManager(archive_dir=archive_dir)
    archived_ids = []
    if not dry_run:
        archived_ids = archiver.archive_entries(deduped)

    predictor = PredictionEngine(history_file=str(Path(archive_dir) / "access_history.json"))
    # Track synthetic accesses based on surviving entries to seed trends
    for i, entry in enumerate(deduped):
        content = entry.get("content", "") if hasattr(entry, "get") else getattr(entry, "content", "")
        entry_id = f"entry-{i}-{abs(hash(content)) % 100000}"
        predictor.track_access(entry_id)

    trends = predictor.get_trends(top_n=5)

    report = {
        "dry_run": dry_run,
        "input_entries": len(entries),
        "deduplicated_entries": len(deduped),
        "archived_entries": len(archived_ids),
        "top_trends": trends,
    }
    return report


def main():
    ap = argparse.ArgumentParser(description="Run full smart memory hygiene pipeline")
    ap.add_argument("memory_file", help="Path to MEMORY.md-like file")
    ap.add_argument("--archive-dir", default="./.memory-archive", help="Archive directory")
    ap.add_argument("--apply", action="store_true", help="Apply changes (default: dry-run)")
    args = ap.parse_args()

    dry_run = not args.apply
    report = run_pipeline(args.memory_file, args.archive_dir, dry_run=dry_run)

    print("=== Smart Memory Hygiene Full Pipeline ===")
    for k, v in report.items():
        print(f"{k}: {v}")


if __name__ == "__main__":
    main()
