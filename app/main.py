from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.domain import CaseRecord, IntakeRequest, Metrics, ReviewRequest
from app.seed import seed_store
from app.store import store


BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"


@asynccontextmanager
async def lifespan(_: FastAPI):
    seed_store(store)
    yield


app = FastAPI(
    title="AI Operations Triage & Quality Platform",
    description="Synthetic-data demonstration of intelligent intake, routing, handoffs, human review, and operational quality metrics.",
    version="0.1.0",
    lifespan=lifespan,
)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/", include_in_schema=False)
def dashboard() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "healthy", "service": "operations-triage"}


@app.get("/api/cases", response_model=list[CaseRecord])
def list_cases() -> list[CaseRecord]:
    return store.list()


@app.post("/api/cases", response_model=CaseRecord, status_code=201)
def create_case(intake: IntakeRequest) -> CaseRecord:
    return store.create(intake)


@app.get("/api/cases/{case_id}", response_model=CaseRecord)
def get_case(case_id: str) -> CaseRecord:
    case = store.get(case_id)
    if case is None:
        raise HTTPException(status_code=404, detail="Case not found")
    return case


@app.post("/api/cases/{case_id}/review", response_model=CaseRecord)
def review_case(case_id: str, review: ReviewRequest) -> CaseRecord:
    case = store.review(case_id, review)
    if case is None:
        raise HTTPException(status_code=404, detail="Case not found")
    return case


@app.get("/api/metrics", response_model=Metrics)
def get_metrics() -> Metrics:
    return store.metrics()


@app.post("/api/reset", response_model=list[CaseRecord])
def reset_demo() -> list[CaseRecord]:
    store.clear()
    seed_store(store)
    return store.list()

