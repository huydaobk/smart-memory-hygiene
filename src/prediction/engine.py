"""
Prediction Engine for Smart Memory Hygiene.

Tracks access patterns and predicts future relevance of memory entries.
"""

from __future__ import annotations

import json
import math
from datetime import datetime
from pathlib import Path
from statistics import mean
from typing import Dict, List, Optional, Any


class PredictionEngine:
    """
    Learns from access history and predicts future relevance.

    Features:
    - Access pattern tracking over time
    - Relevance prediction with confidence score
    - Trend analysis (rising/stable/declining)
    """

    def __init__(self, history_file: Optional[str] = None):
        self.history_file = Path(history_file) if history_file else None
        self.history: Dict[str, Dict[str, Any]] = {}

        if self.history_file and self.history_file.exists():
            self._load_history()

    def _load_history(self) -> None:
        try:
            self.history = json.loads(self.history_file.read_text(encoding="utf-8"))
        except Exception:
            self.history = {}

    def _save_history(self) -> None:
        if not self.history_file:
            return
        self.history_file.parent.mkdir(parents=True, exist_ok=True)
        self.history_file.write_text(json.dumps(self.history, indent=2), encoding="utf-8")

    def track_access(self, entry_id: str, timestamp: Optional[datetime] = None) -> Dict[str, Any]:
        """Record an access event for an entry."""
        ts = (timestamp or datetime.now()).isoformat()

        if entry_id not in self.history:
            self.history[entry_id] = {
                "access_count": 0,
                "first_access": ts,
                "last_access": ts,
                "accesses": [],
            }

        record = self.history[entry_id]
        record["access_count"] += 1
        record["last_access"] = ts
        record["accesses"].append(ts)

        # Keep bounded history to avoid unbounded growth
        if len(record["accesses"]) > 200:
            record["accesses"] = record["accesses"][-200:]

        self._save_history()
        return record

    def predict_relevance(self, entry_id: str) -> Dict[str, float | str]:
        """
        Predict future relevance for an entry.

        Returns:
            {
              "predicted_relevance": float (0-1),
              "confidence": float (0-1),
              "trend": "rising|stable|declining|unknown"
            }
        """
        if entry_id not in self.history:
            return {
                "predicted_relevance": 0.2,
                "confidence": 0.1,
                "trend": "unknown",
            }

        rec = self.history[entry_id]
        accesses = [datetime.fromisoformat(x) for x in rec.get("accesses", [])]
        count = rec.get("access_count", 0)

        if not accesses:
            return {
                "predicted_relevance": 0.2,
                "confidence": 0.1,
                "trend": "unknown",
            }

        now = datetime.now()
        days_since_last = max(0.0, (now - max(accesses)).total_seconds() / 86400.0)

        # Frequency component
        freq_score = min(1.0, math.log1p(count) / math.log1p(30))

        # Recency component (half-life ≈ 14 days)
        recency_score = math.exp(-days_since_last / 14.0)

        # Cadence consistency: lower stdev between intervals => better predictability
        intervals = []
        sorted_acc = sorted(accesses)
        for i in range(1, len(sorted_acc)):
            intervals.append((sorted_acc[i] - sorted_acc[i - 1]).total_seconds() / 86400.0)

        if len(intervals) >= 2:
            avg = mean(intervals)
            variance = mean([(x - avg) ** 2 for x in intervals])
            stdev = math.sqrt(variance)
            consistency = 1.0 / (1.0 + stdev)
        else:
            consistency = 0.5

        predicted = (freq_score * 0.45) + (recency_score * 0.4) + (consistency * 0.15)
        predicted = max(0.0, min(1.0, predicted))

        trend = self._compute_trend(accesses)
        confidence = self._compute_confidence(count=count, consistency=consistency)

        return {
            "predicted_relevance": round(predicted, 4),
            "confidence": round(confidence, 4),
            "trend": trend,
        }

    def _compute_trend(self, accesses: List[datetime]) -> str:
        if len(accesses) < 4:
            return "stable"

        now = datetime.now()
        window_recent = now.timestamp() - (14 * 86400)
        window_prev = now.timestamp() - (28 * 86400)

        recent = sum(1 for a in accesses if a.timestamp() >= window_recent)
        previous = sum(1 for a in accesses if window_prev <= a.timestamp() < window_recent)

        if recent > previous * 1.25:
            return "rising"
        if recent < previous * 0.8:
            return "declining"
        return "stable"

    def _compute_confidence(self, count: int, consistency: float) -> float:
        sample_strength = min(1.0, math.log1p(count) / math.log1p(50))
        return max(0.0, min(1.0, (sample_strength * 0.7) + (consistency * 0.3)))

    def get_trends(self, top_n: int = 10) -> List[Dict[str, Any]]:
        """Return top entries with predictions and trend data."""
        rows: List[Dict[str, Any]] = []
        for entry_id in self.history.keys():
            pred = self.predict_relevance(entry_id)
            rows.append({"entry_id": entry_id, **pred})

        rows.sort(key=lambda x: (x["predicted_relevance"], x["confidence"]), reverse=True)
        return rows[:top_n]
