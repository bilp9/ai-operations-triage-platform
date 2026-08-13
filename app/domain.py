from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


Source = Literal["voice", "chat", "email", "web"]
Priority = Literal["critical", "high", "medium", "low"]
CaseStatus = Literal["new", "in_review", "resolved", "escalated"]


class IntakeRequest(BaseModel):
    source: Source
    transcript: str = Field(min_length=20, max_length=5000)


class ReviewRequest(BaseModel):
    reviewer: str = Field(min_length=2, max_length=80)
    status: CaseStatus
    notes: str = Field(default="", max_length=1000)
    corrected_queue: str | None = Field(default=None, max_length=80)


class AuditEvent(BaseModel):
    timestamp: datetime
    actor: str
    action: str
    detail: str


class CaseRecord(BaseModel):
    id: str
    source: Source
    transcript: str
    category: str
    priority: Priority
    queue: str
    confidence: float
    status: CaseStatus
    created_at: datetime
    handoff_summary: str
    flags: list[str]
    extracted_fields: dict[str, str]
    estimated_minutes_saved: float
    audit_trail: list[AuditEvent]


class Metrics(BaseModel):
    total_cases: int
    automation_rate: float
    average_confidence: float
    high_priority_cases: int
    human_review_rate: float
    estimated_hours_saved: float
    queue_distribution: dict[str, int]
    category_distribution: dict[str, int]

