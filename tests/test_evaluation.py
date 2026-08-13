from app.evaluation import evaluate_dataset


def test_dataset_is_balanced_and_reproducible() -> None:
    report = evaluate_dataset()

    assert report["dataset_size"] == 300
    assert set(report["dataset"]["categories"].values()) == {50}
    assert report["dataset"]["seed"] == 20260813


def test_evaluation_exposes_safety_and_quality_metrics() -> None:
    report = evaluate_dataset()

    assert 0.7 <= report["category_accuracy"] <= 1.0
    assert 0.7 <= report["macro_f1"] <= 1.0
    assert 0.0 <= report["critical_escalation_recall"] <= 1.0
    assert 0.0 <= report["false_automation_rate"] <= 1.0
    assert "safety_incident" in report["confusion_matrix"]
