from src.dashboard.health import HealthDashboard


def test_metrics_and_health_score():
    dash = HealthDashboard()
    dash.record_cleanup(before_count=100, after_count=80, duplicates_removed=15)

    metrics = dash.get_metrics(
        total_entries=100,
        duplicate_entries=15,
        archived_entries=20,
        fragmented_sections=3,
        total_sections=10,
    )

    assert metrics["duplicate_ratio"] == 0.15
    assert metrics["archive_ratio"] == 0.2
    assert metrics["fragmentation"] == 0.3
    assert metrics["cleanup_effectiveness"] == 0.2

    score = dash.get_health_score(metrics)
    assert 0.0 <= score <= 1.0


def test_alerts_triggered():
    dash = HealthDashboard()
    metrics = dash.get_metrics(
        total_entries=100,
        duplicate_entries=30,
        archived_entries=70,
        fragmented_sections=5,
        total_sections=10,
    )
    score = dash.get_health_score(metrics)
    alerts = dash.check_alerts(metrics, health_score=score)

    types = {a["type"] for a in alerts}
    assert "duplicates" in types
    assert "fragmentation" in types
    assert "archive" in types


def test_healthy_alert_when_no_issues():
    dash = HealthDashboard()
    metrics = dash.get_metrics(
        total_entries=100,
        duplicate_entries=2,
        archived_entries=5,
        fragmented_sections=1,
        total_sections=20,
    )
    score = dash.get_health_score(metrics)
    alerts = dash.check_alerts(metrics, health_score=score)
    assert any(a["type"] == "healthy" for a in alerts)
