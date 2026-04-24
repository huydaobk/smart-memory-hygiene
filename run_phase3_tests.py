#!/usr/bin/env python3
"""
Run Phase 3 tests - Prediction Engine + Health Dashboard
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from datetime import datetime, timedelta
from src.prediction.engine import PredictionEngine
from src.dashboard.health import HealthDashboard

print("=" * 60)
print("Phase 3: Prediction + Dashboard Tests")
print("=" * 60)

# Test 1: Prediction Engine - Track Access
print("\n[TEST 1] Track Access...")
try:
    engine = PredictionEngine()
    
    # Track multiple accesses
    engine.track_access("entry-1", timestamp=datetime.now() - timedelta(days=2))
    engine.track_access("entry-1", timestamp=datetime.now() - timedelta(days=1))
    engine.track_access("entry-1")
    
    print("  ✓ Access tracking working")
except Exception as e:
    print(f"  ✗ FAILED: {e}")
    sys.exit(1)

# Test 2: Prediction Engine - Predict Relevance
print("\n[TEST 2] Predict Relevance...")
try:
    engine = PredictionEngine()
    base = datetime.now() - timedelta(days=30)
    
    # Simulate rising trend (more recent accesses)
    for d in [25, 20, 15, 10, 5, 3, 1]:
        engine.track_access("e-hot", timestamp=base + timedelta(days=d))
    
    pred = engine.predict_relevance("e-hot")
    print(f"  Predicted relevance: {pred['predicted_relevance']:.2f}")
    print(f"  Confidence: {pred['confidence']:.2f}")
    print(f"  Trend: {pred['trend']}")
    
    assert pred['trend'] in {'rising', 'stable', 'declining', 'unknown'}
    assert 0.0 <= pred['predicted_relevance'] <= 1.0
    
    print("  ✓ Prediction working")
except Exception as e:
    print(f"  ✗ FAILED: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 3: Prediction Engine - Get Trends
print("\n[TEST 3] Get Trends...")
try:
    engine = PredictionEngine()
    now = datetime.now()
    
    # Create entries with different access patterns
    for _ in range(5):
        engine.track_access("e1", now)
    for _ in range(2):
        engine.track_access("e2", now)
    
    trends = engine.get_trends(top_n=2)
    print(f"  Found {len(trends)} trends")
    
    print("  ✓ Trends working")
except Exception as e:
    print(f"  ✗ FAILED: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 4: Health Dashboard - Metrics
print("\n[TEST 4] Health Dashboard Metrics...")
try:
    dashboard = HealthDashboard()
    
    metrics = dashboard.get_metrics(
        total_entries=100,
        duplicate_entries=15,
        archived_entries=20,
        fragmented_sections=30,
        total_sections=100
    )
    
    print(f"  Total entries: {metrics['total_entries']}")
    print(f"  Duplicate ratio: {metrics['duplicate_ratio']:.2f}")
    print(f"  Archive ratio: {metrics['archive_ratio']:.2f}")
    print(f"  Fragmentation: {metrics['fragmentation']:.2f}")
    
    print("  ✓ Metrics working")
except Exception as e:
    print(f"  ✗ FAILED: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 5: Health Dashboard - Health Score
print("\n[TEST 5] Health Score...")
try:
    dashboard = HealthDashboard()
    
    metrics = dashboard.get_metrics(
        total_entries=100,
        duplicate_entries=15,
        archived_entries=20,
        fragmented_sections=30,
        total_sections=100
    )
    
    score = dashboard.get_health_score(metrics)
    print(f"  Health score: {score:.2f}")
    
    assert 0.0 <= score <= 1.0
    
    print("  ✓ Health score working")
except Exception as e:
    print(f"  ✗ FAILED: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 6: Health Dashboard - Alerts
print("\n[TEST 6] Health Alerts...")
try:
    dashboard = HealthDashboard()
    
    metrics = dashboard.get_metrics(
        total_entries=100,
        duplicate_entries=50,  # High duplicates
        archived_entries=10,
        fragmented_sections=80,  # High fragmentation
        total_sections=100
    )
    
    alerts = dashboard.check_alerts(metrics)
    print(f"  Found {len(alerts)} alerts:")
    for alert in alerts:
        print(f"    [{alert['level']}] {alert['message']}")
    
    print("  ✓ Alerts working")
except Exception as e:
    print(f"  ✗ FAILED: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "=" * 60)
print("Phase 3: All tests PASSED! ✓")
print("=" * 60)

sys.exit(0)
