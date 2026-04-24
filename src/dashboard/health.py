"""
Health Dashboard for Smart Memory Hygiene.

Computes memory health metrics, score, and alerts.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Dict, Any, Optional


@dataclass
class HealthThresholds:
    duplicate_ratio_warn: float = 0.2
    fragmentation_warn: float = 0.35
    archive_ratio_warn: float = 0.6
    min_health_score_warn: float = 0.6


class HealthDashboard:
    def __init__(self, thresholds: Optional[HealthThresholds] = None):
        self.thresholds = thresholds or HealthThresholds()
        self._cleanup_history: List[Dict[str, Any]] = []

    def record_cleanup(self, before_count: int, after_count: int, duplicates_removed: int) -> Dict[str, Any]:
        reduction = max(0, before_count - after_count)
        effectiveness = (reduction / before_count) if before_count else 0.0
        rec = {
            "before_count": before_count,
            "after_count": after_count,
            "duplicates_removed": duplicates_removed,
            "reduction": reduction,
            "effectiveness": round(effectiveness, 4),
        }
        self._cleanup_history.append(rec)
        return rec

    def get_metrics(self,
                    total_entries: int,
                    duplicate_entries: int,
                    archived_entries: int,
                    fragmented_sections: int,
                    total_sections: int) -> Dict[str, float]:
        duplicate_ratio = (duplicate_entries / total_entries) if total_entries else 0.0
        archive_ratio = (archived_entries / total_entries) if total_entries else 0.0
        fragmentation = (fragmented_sections / total_sections) if total_sections else 0.0

        cleanup_effectiveness = 0.0
        if self._cleanup_history:
            cleanup_effectiveness = sum(r["effectiveness"] for r in self._cleanup_history) / len(self._cleanup_history)

        return {
            "total_entries": float(total_entries),
            "duplicate_ratio": round(duplicate_ratio, 4),
            "archive_ratio": round(archive_ratio, 4),
            "fragmentation": round(fragmentation, 4),
            "cleanup_effectiveness": round(cleanup_effectiveness, 4),
        }

    def get_health_score(self, metrics: Dict[str, float]) -> float:
        # Higher duplicates/fragmentation/archive ratio reduce score; cleanup effectiveness improves score.
        score = 1.0
        score -= metrics.get("duplicate_ratio", 0.0) * 0.35
        score -= metrics.get("fragmentation", 0.0) * 0.30
        score -= metrics.get("archive_ratio", 0.0) * 0.20
        score += metrics.get("cleanup_effectiveness", 0.0) * 0.15
        return round(max(0.0, min(1.0, score)), 4)

    def check_alerts(self, metrics: Dict[str, float], health_score: Optional[float] = None) -> List[Dict[str, str]]:
        alerts: List[Dict[str, str]] = []
        score = self.get_health_score(metrics) if health_score is None else health_score

        if metrics.get("duplicate_ratio", 0.0) >= self.thresholds.duplicate_ratio_warn:
            alerts.append({"level": "warning", "type": "duplicates", "message": "High duplicate ratio detected"})

        if metrics.get("fragmentation", 0.0) >= self.thresholds.fragmentation_warn:
            alerts.append({"level": "warning", "type": "fragmentation", "message": "Memory fragmentation is high"})

        if metrics.get("archive_ratio", 0.0) >= self.thresholds.archive_ratio_warn:
            alerts.append({"level": "warning", "type": "archive", "message": "Archive ratio is high; active memory may be stale"})

        if score <= self.thresholds.min_health_score_warn:
            alerts.append({"level": "critical", "type": "health_score", "message": "Overall memory health score is low"})

        if not alerts:
            alerts.append({"level": "info", "type": "healthy", "message": "Memory health is within normal range"})

        return alerts
