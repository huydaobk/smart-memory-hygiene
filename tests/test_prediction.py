from datetime import datetime, timedelta

from src.prediction.engine import PredictionEngine


def test_track_access_creates_and_updates_record(tmp_path):
    hist = tmp_path / "history.json"
    engine = PredictionEngine(history_file=str(hist))

    engine.track_access("entry-1", timestamp=datetime.now() - timedelta(days=2))
    rec = engine.track_access("entry-1")

    assert rec["access_count"] == 2
    assert len(rec["accesses"]) == 2
    assert hist.exists()


def test_predict_relevance_unknown_entry():
    engine = PredictionEngine()
    pred = engine.predict_relevance("missing")

    assert pred["trend"] == "unknown"
    assert 0.0 <= pred["predicted_relevance"] <= 1.0
    assert 0.0 <= pred["confidence"] <= 1.0


def test_predict_relevance_and_trends():
    engine = PredictionEngine()
    base = datetime.now() - timedelta(days=30)

    # increasing activity in recent window
    for d in [25, 20, 15, 10, 5, 3, 1]:
        engine.track_access("e-hot", timestamp=base + timedelta(days=d))

    pred = engine.predict_relevance("e-hot")
    assert pred["trend"] in {"rising", "stable", "declining"}
    assert pred["predicted_relevance"] > 0.3
    assert pred["confidence"] > 0.2


def test_get_trends_sorted():
    engine = PredictionEngine()
    now = datetime.now()

    for _ in range(5):
        engine.track_access("e1", now)
    for _ in range(2):
        engine.track_access("e2", now)

    trends = engine.get_trends(top_n=2)
    assert len(trends) == 2
    assert trends[0]["predicted_relevance"] >= trends[1]["predicted_relevance"]
