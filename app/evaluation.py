import csv
from collections import Counter, defaultdict
from pathlib import Path

from app.engine import analyze_transcript


DATASET_PATH = Path(__file__).resolve().parents[1] / "data" / "synthetic_interactions.csv"


def _safe_ratio(numerator: int, denominator: int) -> float:
    return numerator / denominator if denominator else 0.0


def _classification_metrics(expected: list[str], predicted: list[str]) -> tuple[dict[str, dict[str, float]], float]:
    labels = sorted(set(expected) | set(predicted))
    per_class: dict[str, dict[str, float]] = {}
    f1_scores: list[float] = []
    for label in labels:
        true_positive = sum(left == label and right == label for left, right in zip(expected, predicted))
        false_positive = sum(left != label and right == label for left, right in zip(expected, predicted))
        false_negative = sum(left == label and right != label for left, right in zip(expected, predicted))
        precision = _safe_ratio(true_positive, true_positive + false_positive)
        recall = _safe_ratio(true_positive, true_positive + false_negative)
        f1 = _safe_ratio(2 * precision * recall, precision + recall)
        f1_scores.append(f1)
        per_class[label] = {
            "precision": round(precision, 3),
            "recall": round(recall, 3),
            "f1": round(f1, 3),
            "support": expected.count(label),
        }
    return per_class, round(sum(f1_scores) / len(f1_scores), 3)


def evaluate_dataset(path: Path = DATASET_PATH) -> dict[str, object]:
    with path.open(encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))

    expected_categories: list[str] = []
    predicted_categories: list[str] = []
    expected_priorities: list[str] = []
    predicted_priorities: list[str] = []
    confusion: dict[str, Counter[str]] = defaultdict(Counter)
    critical_total = 0
    critical_captured = 0
    safe_to_automate = 0
    false_automations = 0

    for row in rows:
        result = analyze_transcript(row["transcript"])
        expected_category = row["expected_category"]
        predicted_category = str(result["category"])
        expected_priority = row["expected_priority"]
        predicted_priority = str(result["priority"])
        expected_categories.append(expected_category)
        predicted_categories.append(predicted_category)
        expected_priorities.append(expected_priority)
        predicted_priorities.append(predicted_priority)
        confusion[expected_category][predicted_category] += 1

        if expected_priority == "critical":
            critical_total += 1
            critical_captured += predicted_priority == "critical"

        if float(result["confidence"]) >= 0.7 and predicted_priority not in {"critical", "high"}:
            safe_to_automate += 1
            false_automations += predicted_category != expected_category or expected_priority in {"critical", "high"}

    per_class, macro_f1 = _classification_metrics(expected_categories, predicted_categories)
    correct_categories = sum(left == right for left, right in zip(expected_categories, predicted_categories))
    correct_priorities = sum(left == right for left, right in zip(expected_priorities, predicted_priorities))
    return {
        "dataset_size": len(rows),
        "category_accuracy": round(_safe_ratio(correct_categories, len(rows)), 3),
        "priority_accuracy": round(_safe_ratio(correct_priorities, len(rows)), 3),
        "macro_f1": macro_f1,
        "critical_escalation_recall": round(_safe_ratio(critical_captured, critical_total), 3),
        "false_automation_rate": round(_safe_ratio(false_automations, safe_to_automate), 3),
        "automated_decisions": safe_to_automate,
        "per_class": per_class,
        "confusion_matrix": {label: dict(counts) for label, counts in sorted(confusion.items())},
        "dataset": {
            "type": "synthetic",
            "seed": 20260813,
            "categories": dict(Counter(expected_categories)),
            "channels": dict(Counter(row["channel"] for row in rows)),
        },
    }
