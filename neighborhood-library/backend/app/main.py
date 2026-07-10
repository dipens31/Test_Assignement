from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.v1 import books, loans, members, members_loans
from app.core.config import settings
from app.core.logging import get_logger, setup_logging

# Initialize logging
setup_logging()
logger = get_logger(__name__)

app = FastAPI(
    title="Neighborhood Library Service",
    description=(
        "REST API for managing books, members, and lending operations "
        "for a neighborhood library."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", tags=["Health"], summary="Health check")
def health_check():
    logger.info("Health check endpoint called")
    return {"status": "ok"}


app.include_router(books.router, prefix="/api/v1")
app.include_router(members.router, prefix="/api/v1")
app.include_router(members_loans.router, prefix="/api/v1")
app.include_router(loans.router, prefix="/api/v1")
