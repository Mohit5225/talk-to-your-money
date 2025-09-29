# File: main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import the refactored DB logic and the new auth router
from mongo_db.db import database, lifespan
from auth.auth import router as auth_router

app = FastAPI(
    title="Talk To Your Money API",
    description="AI-powered financial insights and stock predictions",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"], # Added your other port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/api") # Prefixed with /api for good practice

@app.get("/")
async def root():
    return { "message": "Talk To Your Money API is running" }

@app.get("/health")
async def health_check():
    db_status = "connected" if database is not None else "disconnected"
    return {"status": "healthy", "database": db_status}