# AI Operations Triage & Quality Platform

An end-to-end, human-in-the-loop portfolio project demonstrating how operational interactions can move from unstructured intake to structured decisions, traceable routing, analyst handoffs, and measurable quality controls.

> This project uses synthetic records only. It does not contain employer data, proprietary workflows, customer information, or production integrations.

![AI Operations dashboard preview](docs/dashboard.png)

## Why This Project Exists

Operations teams often treat the customer interaction and the resulting analyst work as separate events. That creates missing context, repeated questions, inconsistent routing, and weak accountability.

This platform demonstrates a better operating model:

1. Capture an interaction from voice, chat, email, or web.
2. Extract structured identifiers and operational context.
3. Classify category, urgency, confidence, and destination queue.
4. Generate a standardized handoff for the receiving analyst.
5. Escalate critical or low-confidence cases for human review.
6. Preserve an auditable decision trail.
7. Measure automation, confidence, review demand, and estimated time savings.

## Product Preview

The dashboard includes:

- Executive-ready operational metrics
- Priority and low-confidence review queues
- Explainable routing decisions
- Structured field extraction
- Standardized analyst handoffs
- Human confirmation and correction
- Full audit history
- Queue-level workload distribution

## Architecture

```mermaid
flowchart LR
    A["Voice, chat, email, or web intake"] --> B["Structured intake API"]
    B --> C["Classification and extraction engine"]
    C --> D{"Confidence and safety gate"}
    D -->|"High confidence"| E["Recommended operations queue"]
    D -->|"Critical or uncertain"| F["Human review queue"]
    E --> G["Standardized handoff and task record"]
    F --> G
    G --> H["Audit trail and quality metrics"]
```

## Technical Highlights

- **FastAPI:** Typed REST endpoints and automatically generated OpenAPI documentation.
- **Pydantic:** Validated intake, review, case, audit, and metric models.
- **Explainable routing:** Deterministic rules expose why each recommendation was made.
- **Human-in-the-loop controls:** Critical and uncertain cases are flagged instead of silently automated.
- **Synthetic dataset:** Twelve representative interactions spanning safety, claims, billing, access, delivery, and general operations.
- **Evaluation layer:** Automation rate, confidence, human review demand, queue distribution, and estimated time savings.
- **Responsive dashboard:** Dependency-free HTML, CSS, and JavaScript served directly by FastAPI.
- **Automated tests:** Coverage for routing, safety escalation, low-confidence review, API intake, and analyst review.

## API

| Method | Endpoint | Purpose |
| --- | --- | --- |
| `GET` | `/api/health` | Service health |
| `GET` | `/api/cases` | List decision records |
| `POST` | `/api/cases` | Analyze and route a new interaction |
| `GET` | `/api/cases/{case_id}` | Inspect one interaction |
| `POST` | `/api/cases/{case_id}/review` | Record a human review or correction |
| `GET` | `/api/metrics` | Operational and quality metrics |
| `POST` | `/api/reset` | Restore the synthetic demo dataset |

Interactive API documentation is available at `/docs` when the service is running.

## Run Locally

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
uvicorn app.main:app --reload
```

Open `http://127.0.0.1:8000`.

## Test

```bash
pytest
```

## Design Principles

- Automate recommendations, not accountability.
- Route uncertainty to people instead of hiding it.
- Keep customer context attached to operational work.
- Make quality measurable and decisions auditable.
- Demonstrate business impact alongside technical capability.

## Roadmap

- Provider-agnostic LLM structured-output adapter
- Evaluation dataset with expected classifications and confusion matrix
- Persistent PostgreSQL storage
- Role-based review queues
- Webhook and task-management integrations
- Prompt and routing version comparisons
- Containerized cloud deployment

## Author

Built by [Billy Pierre](https://github.com/bilp9), an operations leader and AI automation builder focused on practical systems that improve workflow quality, speed, and accountability.
