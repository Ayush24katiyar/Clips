from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from ..controllers.job_controller import JobController
from ..core.events import bus
from ..db.session import get_db
from ..schemas.job import CreateJobRequest, JobRead

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.post("", response_model=JobRead, status_code=status.HTTP_202_ACCEPTED)
def create_job(payload: CreateJobRequest, db: Session = Depends(get_db)) -> JobRead:
    job = JobController(db).create(payload)
    return JobRead.model_validate(job, from_attributes=True)


@router.get("", response_model=list[JobRead])
def list_jobs(db: Session = Depends(get_db)) -> list[JobRead]:
    return [JobRead.model_validate(job, from_attributes=True) for job in JobController(db).list()]


@router.get("/{job_id}", response_model=JobRead)
def get_job(job_id: str, db: Session = Depends(get_db)) -> JobRead:
    job = JobController(db).get(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    return JobRead.model_validate(job, from_attributes=True)


@router.get("/{job_id}/events")
async def job_events(job_id: str) -> StreamingResponse:
    async def generate():
        async for event in bus.stream(job_id):
            yield f"data: {event}\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")
