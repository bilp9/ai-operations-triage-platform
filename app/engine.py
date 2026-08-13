import re
from dataclasses import dataclass

from app.domain import Priority


@dataclass(frozen=True)
class RouteRule:
    category: str
    queue: str
    keywords: tuple[str, ...]


ROUTE_RULES = (
    RouteRule(
        "safety_incident",
        "Safety & Escalations",
        ("injury", "hurt", "unsafe", "threat", "fire", "smoke", "evacuation", "weapon", "emergency", "collision", "sprain", "slipped"),
    ),
    RouteRule(
        "property_damage",
        "Claims Operations",
        ("property damage", "damaged", "broken", "hit my", "fence", "garage", "vehicle damage", "scraped", "mailbox", "gate"),
    ),
    RouteRule(
        "account_access",
        "Account Support",
        ("locked out", "login", "sign-in", "password", "access", "verification code", "two-factor", "authentication", "account"),
    ),
    RouteRule(
        "billing",
        "Billing Operations",
        ("charged", "invoice", "refund", "payment", "billing", "duplicate charge", "statement", "subscription", "renewal"),
    ),
    RouteRule(
        "delivery_issue",
        "Delivery Support",
        ("delivery", "package", "parcel", "driver", "missing item", "wrong address", "late order"),
    ),
)

CRITICAL_TERMS = ("fire", "smoke", "evacuation", "weapon", "unconscious", "life threatening", "immediate danger")
HIGH_TERMS = ("injury", "hurt", "threat", "collision", "unsafe", "property damage")


def _extract_fields(text: str) -> dict[str, str]:
    extracted: dict[str, str] = {}
    email_match = re.search(r"[\w.+-]+@[\w-]+\.[\w.-]+", text, re.IGNORECASE)
    case_match = re.search(r"\b(?:case|order|incident|ticket)[\s#:.-]*([A-Z0-9-]{5,})\b", text, re.IGNORECASE)
    location_match = re.search(
        r"\b(?:campus|location|facility)[\s#:.-]*([A-Za-z][A-Za-z ]{2,30}?)(?=[,.])",
        text,
        re.IGNORECASE,
    )

    if email_match:
        extracted["email"] = email_match.group(0)
    if case_match:
        extracted["reference"] = case_match.group(1).upper()
    if location_match:
        extracted["location"] = location_match.group(1).strip().title()
    return extracted


def _priority(text: str, category: str) -> Priority:
    if any(term in text for term in CRITICAL_TERMS):
        return "critical"
    if category in {"safety_incident", "property_damage"} or any(term in text for term in HIGH_TERMS):
        return "high"
    if category in {"account_access", "billing", "delivery_issue"}:
        return "medium"
    return "low"


def analyze_transcript(transcript: str) -> dict[str, object]:
    normalized = " ".join(transcript.lower().split())
    best_rule: RouteRule | None = None
    best_matches: list[str] = []

    for rule in ROUTE_RULES:
        matches = [keyword for keyword in rule.keywords if keyword in normalized]
        if len(matches) > len(best_matches):
            best_rule = rule
            best_matches = matches

    category = best_rule.category if best_rule else "general_support"
    queue = best_rule.queue if best_rule else "General Operations"
    priority = _priority(normalized, category)
    extracted_fields = _extract_fields(transcript)

    confidence = min(0.98, 0.56 + len(best_matches) * 0.1 + len(extracted_fields) * 0.04)
    if not best_rule:
        confidence = 0.52

    flags: list[str] = []
    if priority in {"critical", "high"}:
        flags.append("priority-review")
    if confidence < 0.7:
        flags.append("low-confidence")
    if priority == "critical":
        flags.append("immediate-escalation")

    field_phrase = ", ".join(f"{key}: {value}" for key, value in extracted_fields.items())
    context = field_phrase if field_phrase else "No structured identifiers detected"
    handoff_summary = (
        f"{priority.title()} priority {category.replace('_', ' ')} routed to {queue}. "
        f"{context}. Review the interaction context and confirm the recommended next action."
    )

    return {
        "category": category,
        "queue": queue,
        "priority": priority,
        "confidence": round(confidence, 2),
        "flags": flags,
        "extracted_fields": extracted_fields,
        "handoff_summary": handoff_summary,
        "estimated_minutes_saved": round(2.5 + len(extracted_fields) * 0.75 + len(best_matches) * 0.35, 1),
    }


def get_routing_rules() -> list[dict[str, object]]:
    return [
        {
            "category": rule.category,
            "queue": rule.queue,
            "keywords": list(rule.keywords),
            "requires_human_review": rule.category in {"safety_incident", "property_damage"},
        }
        for rule in ROUTE_RULES
    ] + [
        {
            "category": "general_support",
            "queue": "General Operations",
            "keywords": [],
            "requires_human_review": True,
        }
    ]
