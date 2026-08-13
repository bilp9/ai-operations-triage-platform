from app.engine import analyze_transcript


def test_safety_incident_routes_to_escalations() -> None:
    result = analyze_transcript("A collision caused an injury at location North Campus. Incident INC-48291.")

    assert result["category"] == "safety_incident"
    assert result["queue"] == "Safety & Escalations"
    assert result["priority"] == "high"
    assert "priority-review" in result["flags"]
    assert result["extracted_fields"]["location"] == "North Campus"


def test_critical_language_forces_immediate_escalation() -> None:
    result = analyze_transcript("There is a fire and people may be in immediate danger at location Riverside Center.")

    assert result["priority"] == "critical"
    assert "immediate-escalation" in result["flags"]


def test_unknown_request_enters_low_confidence_review() -> None:
    result = analyze_transcript("I have a question and would like someone to contact me about the policy details.")

    assert result["category"] == "general_support"
    assert result["confidence"] < 0.7
    assert "low-confidence" in result["flags"]
