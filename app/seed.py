from app.domain import IntakeRequest
from app.store import CaseStore


SYNTHETIC_CASES = (
    ("voice", "A caller reported a collision at the North Campus. One person says their shoulder is hurt. Incident INC-48291 needs immediate review."),
    ("chat", "I am locked out of my account and the verification code is not arriving. My email is jordan.lee@example.com."),
    ("email", "I was charged twice for invoice INV-77421 and need help reviewing the duplicate charge and refund options."),
    ("voice", "There is a fire near the service corridor at location Riverside Center. People are moving away and emergency services have been called."),
    ("web", "My package for order PKG-55281 was delivered to the wrong address and the delivery photo is not my home."),
    ("chat", "A vehicle hit my fence and caused property damage. Case CLM-90318. Nobody appears injured."),
    ("email", "Please update the contact name associated with ticket CUST-44018. This is not urgent."),
    ("voice", "A caller reported a threat during a customer interaction. They are safe now but requested a supervisor and incident documentation."),
    ("web", "The password reset link expires before I can use it. Account email is sam.rivera@example.com."),
    ("chat", "My late order arrived but one item is missing from package ORD-61773. Please advise on next steps."),
    ("email", "Question about payment terms on invoice INV-22190. No charge dispute, just need clarification."),
    ("voice", "I need general help finding the correct team for a policy question. Reference CASE-10293."),
)


def seed_store(case_store: CaseStore) -> None:
    if case_store.list():
        return
    for source, transcript in SYNTHETIC_CASES:
        case_store.create(IntakeRequest(source=source, transcript=transcript))
