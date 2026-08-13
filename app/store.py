from collections import Counter
from datetime import UTC, datetime
from uuid import uuid4

from app.domain import AuditEvent, CaseRecord, IntakeRequest, Metrics, ReviewRequest
from app.engine import analyze_transcript


class CaseStore:
    def __init__(self) -> None:
        self._cases: dict[str, CaseRecord] = {}

    def clear(self) -> None:
        self._cases.clear()

    def create(self, intake: IntakeRequest) -> CaseRecord:
        analysis = analyze_transcript(intake.transcript)
        now = datetime.now(UTC)
        case_id = f"OPS-{uuid4().hex[:8].upper()}"
        case = CaseRecord(
            id=case_id,
            source=intake.source,
            transcript=intake.transcript,
            category=str(analysis["category"]),
            priority=analysis["priority"],
            queue=str(analysis["queue"]),
            confidence=float(analysis["confidence"]),
            status="escalated" if analysis["priority"] == "critical" else "new",
            created_at=now,
            handoff_summary=str(analysis["handoff_summary"]),
            flags=list(analysis["flags"]),
            extracted_fields=dict(analysis["extracted_fields"]),
            estimated_minutes_saved=float(analysis["estimated_minutes_saved"]),
            audit_trail=[
                AuditEvent(
                    timestamp=now,
                    actor="Triage Engine",
                    action="case_created",
                    detail=f"Classified and routed with {float(analysis['confidence']):.0%} confidence.",
                )
            ],
        )
        self._cases[case_id] = case
        return case

    def list(self) -> list[CaseRecord]:
        return sorted(self._cases.values(), key=lambda case: case.created_at, reverse=True)

    def get(self, case_id: str) -> CaseRecord | None:
        return self._cases.get(case_id)

    def review(self, case_id: str, review: ReviewRequest) -> CaseRecord | None:
        case = self._cases.get(case_id)
        if case is None:
            return None

        detail_parts = [review.notes.strip()] if review.notes.strip() else []
        if review.corrected_queue and review.corrected_queue != case.queue:
            detail_parts.append(f"Queue changed from {case.queue} to {review.corrected_queue}.")
            case.queue = review.corrected_queue

        case.status = review.status
        case.audit_trail.append(
            AuditEvent(
                timestamp=datetime.now(UTC),
                actor=review.reviewer,
                action="human_review",
                detail=" ".join(detail_parts) or f"Status updated to {review.status}.",
            )
        )
        return case

    def metrics(self) -> Metrics:
        cases = self.list()
        total = len(cases)
        if total == 0:
            return Metrics(
                total_cases=0,
                automation_rate=0,
                average_confidence=0,
                high_priority_cases=0,
                human_review_rate=0,
                estimated_hours_saved=0,
                queue_distribution={},
                category_distribution={},
            )

        reviewed = sum(any(event.action == "human_review" for event in case.audit_trail) for case in cases)
        auto_routed = sum(case.confidence >= 0.7 and case.priority not in {"critical", "high"} for case in cases)
        return Metrics(
            total_cases=total,
            automation_rate=round(auto_routed / total, 3),
            average_confidence=round(sum(case.confidence for case in cases) / total, 3),
            high_priority_cases=sum(case.priority in {"critical", "high"} for case in cases),
            human_review_rate=round(reviewed / total, 3),
            estimated_hours_saved=round(sum(case.estimated_minutes_saved for case in cases) / 60, 1),
            queue_distribution=dict(Counter(case.queue for case in cases)),
            category_distribution=dict(Counter(case.category for case in cases)),
        )


store = CaseStore()
