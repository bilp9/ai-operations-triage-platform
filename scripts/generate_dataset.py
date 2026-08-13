import csv
import random
from pathlib import Path


SEED = 20260813
OUTPUT = Path(__file__).resolve().parents[1] / "data" / "synthetic_interactions.csv"
CHANNELS = ("voice", "chat", "email", "web")
LOCATIONS = ("North Campus", "Riverside Center", "West Annex", "Building C", "Harbor Office")

CATEGORY_SPECS = {
    "safety_incident": {
        "queue": "Safety & Escalations",
        "templates": (
            ("high", "A caller reported a collision at the {location}. One person is hurt and incident {reference} needs review."),
            ("high", "The caller says the area is unsafe after a threat near location {location}. Ticket {reference} was opened."),
            ("critical", "There is a fire at location {location}, and people may be in immediate danger. Incident {reference}."),
            ("critical", "A weapon was reported near facility {location}. This is an emergency linked to case {reference}."),
            ("high", "A staff member slipped and may have a sprain at the {location}. Please escalate report {reference}."),
            ("critical", "Heavy smoke is spreading through the service corridor at {location}; evacuation is underway for report {reference}."),
        ),
    },
    "property_damage": {
        "queue": "Claims Operations",
        "templates": (
            ("high", "A vehicle hit my fence and caused property damage. Case {reference}; nobody is injured."),
            ("high", "A service vehicle damaged the garage at location {location}. Claim case {reference}."),
            ("high", "My gate was broken during the stop. Order {reference} is connected to the report."),
            ("high", "The courier scraped a parked car and left visible damage. Reference {reference}."),
            ("high", "A mailbox was knocked over during delivery for order {reference}. No one was hurt."),
        ),
    },
    "account_access": {
        "queue": "Account Support",
        "templates": (
            ("medium", "I am locked out of my account and the verification code is not arriving at {email}."),
            ("medium", "My password reset link fails every time. Account email: {email}. Ticket {reference}."),
            ("medium", "I cannot login after changing phones. Please restore access for {email}."),
            ("medium", "The sign-in page loops back to verification and never lets me continue. Contact {email}."),
            ("medium", "Two-factor authentication rejects every code for user {email}; case {reference}."),
        ),
    },
    "billing": {
        "queue": "Billing Operations",
        "templates": (
            ("medium", "I was charged twice for invoice {reference} and need a refund for the duplicate charge."),
            ("medium", "Payment for invoice {reference} shows pending even though the bank approved it."),
            ("medium", "Please explain the billing terms on invoice {reference}. Contact me at {email}."),
            ("medium", "The amount on statement {reference} is incorrect and I need an adjustment."),
            ("medium", "A subscription renewal posted unexpectedly under reference {reference}."),
        ),
    },
    "delivery_issue": {
        "queue": "Delivery Support",
        "templates": (
            ("medium", "My package for order {reference} was delivered to the wrong address."),
            ("medium", "One missing item was not included in delivery {reference}."),
            ("medium", "The driver marked order {reference} complete, but nothing arrived."),
            ("medium", "My late order {reference} has not moved for three days."),
            ("medium", "The parcel for order {reference} went to a neighbor and the photo confirms it."),
        ),
    },
    "general_support": {
        "queue": "General Operations",
        "templates": (
            ("low", "I need help understanding the policy connected with case {reference}."),
            ("low", "Please update the contact name on ticket {reference}. This is not urgent."),
            ("low", "Where can I find the current service hours for location {location}?"),
            ("low", "I have a general question and would like someone to contact me at {email}."),
            ("low", "Please confirm who owns follow-up for reference {reference}."),
        ),
    },
}


def build_rows() -> list[dict[str, str]]:
    random.seed(SEED)
    rows: list[dict[str, str]] = []
    for category, spec in CATEGORY_SPECS.items():
        for index in range(50):
            priority, template = spec["templates"][index % len(spec["templates"])]
            serial = len(rows) + 1
            reference = f"SYN-{serial:05d}"
            location = LOCATIONS[serial % len(LOCATIONS)]
            email = f"demo.user{serial:03d}@example.com"
            transcript = template.format(reference=reference, location=location, email=email)
            if index % 7 == 0:
                transcript = f"For context, this started earlier today. {transcript} Please document the next action."
            rows.append(
                {
                    "interaction_id": f"EVAL-{serial:04d}",
                    "channel": CHANNELS[serial % len(CHANNELS)],
                    "transcript": transcript,
                    "expected_category": category,
                    "expected_queue": spec["queue"],
                    "expected_priority": priority,
                    "expected_escalation": str(priority in {"critical", "high"}).lower(),
                    "synthetic": "true",
                    "generation_seed": str(SEED),
                }
            )
    random.shuffle(rows)
    return rows


def main() -> None:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    rows = build_rows()
    with OUTPUT.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=rows[0].keys(), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    print(f"Wrote {len(rows)} labeled synthetic interactions to {OUTPUT}")


if __name__ == "__main__":
    main()
