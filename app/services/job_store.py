from datetime import datetime, timezone
from typing import Any, Dict, Optional

job_store: Dict[str, Dict[str, Any]] = {}

def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def create_job(job_id: str, payload: dict) -> dict:
    job_store[job_id] = {
        "job_id": job_id,
        "status": "QUEUED",
        "created_at": utc_now_iso(),
        "updated_at": utc_now_iso(),
        "payload": payload,
        "result": None,
        "error": None,
    }
    return job_store[job_id]


def update_job_status(job_id: str, status: str) -> Optional[dict]:
    if job_id not in job_store:
        return None

    job_store[job_id]["status"] = status
    job_store[job_id]["updated_at"] = utc_now_iso()
    return job_store[job_id]


def complete_job(job_id: str, result: dict) -> Optional[dict]:
    if job_id not in job_store:
        return None

    job_store[job_id]["status"] = "COMPLETED"
    job_store[job_id]["result"] = result
    job_store[job_id]["updated_at"] = utc_now_iso()
    return job_store[job_id]


def fail_job(job_id: str, error: str) -> Optional[dict]:
    if job_id not in job_store:
        return None

    job_store[job_id]["status"] = "FAILED"
    job_store[job_id]["error"] = error
    job_store[job_id]["updated_at"] = utc_now_iso()
    return job_store[job_id]


def get_job(job_id: str) -> Optional[dict]:
    return job_store.get(job_id)
