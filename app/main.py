from fastapi import FastAPI

from app.database.connection import Base, engine

# IMPORTANT:
# Import models so SQLAlchemy knows about them
from app.database import modal

from app.api.documents import router as documents_router
from app.api.chat import router as chat_router


app = FastAPI(
    title="Legalox API",
    description="AI Legal Intelligence API",
    version="1.0.0",
)


# Create database tables
Base.metadata.create_all(bind=engine)


# Register API router
app.include_router(documents_router)
app.include_router(chat_router)


@app.get("/")
def root():
    return {
        "message": "Legalox API is running"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }