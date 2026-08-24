from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_redoc_html
from fastapi.responses import JSONResponse

from app.api.router import api_router
from app.config import settings
from app.db.mongodb import close_mongo_connection, connect_to_mongo


@asynccontextmanager
async def lifespan(app: FastAPI):
    connect_to_mongo()
    yield
    close_mongo_connection()


app = FastAPI(
    title="Vettora API",
    description="AI-Powered Resume Screening API",
    version="1.0.0",
    redoc_url=None,
    lifespan=lifespan,
)

origins = [settings.frontend_url] if settings.frontend_url else ["http://localhost:5173"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)



@app.get("/redoc", include_in_schema=False)
async def redoc_html():
    return get_redoc_html(
        openapi_url=app.openapi_url,
        title=f"{app.title} - ReDoc",
        redoc_js_url="https://cdn.jsdelivr.net/npm/redoc@2.2.0/bundles/redoc.standalone.js",
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": getattr(exc, "error_code", "http_error"),
            "message": exc.detail,
        },
    )

