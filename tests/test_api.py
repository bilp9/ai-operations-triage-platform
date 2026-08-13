from fastapi.testclient import TestClient

from app.main import app


def test_dashboard_and_metrics() -> None:
    with TestClient(app) as client:
        dashboard = client.get("/")
        metrics = client.get("/api/metrics")

    assert dashboard.status_code == 200
    assert "AI Operations" in dashboard.text
    assert metrics.status_code == 200
    assert metrics.json()["total_cases"] >= 10


def test_create_and_review_case() -> None:
    with TestClient(app) as client:
        created = client.post(
            "/api/cases",
            json={
                "source": "chat",
                "transcript": "A customer reports a duplicate charge on invoice INV-88991 and requests a refund.",
            },
        )
        case_id = created.json()["id"]
        reviewed = client.post(
            f"/api/cases/{case_id}/review",
            json={"reviewer": "Demo Analyst", "status": "resolved", "notes": "Routing confirmed."},
        )

    assert created.status_code == 201
    assert created.json()["queue"] == "Billing Operations"
    assert reviewed.status_code == 200
    assert reviewed.json()["status"] == "resolved"
    assert reviewed.json()["audit_trail"][-1]["action"] == "human_review"

