from fastapi import APIRouter
from app.api.routes import health, jobs, resumes, screening

api_router = APIRouter()
api_router.include_router(health.router, tags=["Health"])
api_router.include_router(jobs.router, tags=["Jobs"])
api_router.include_router(resumes.router, tags=["Resumes"])
api_router.include_router(screening.router, tags=["Screening"])
