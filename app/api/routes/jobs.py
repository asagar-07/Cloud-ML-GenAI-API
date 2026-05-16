from fastapi import APIRouter ,HTTPException

from app.services.job_store import get_job

router = APIRouter(prefix="/jobs", tags=["Jobs"])

@router.get("/{job_id}")
async def get_job_status(job_id: str):
    job = get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    return job