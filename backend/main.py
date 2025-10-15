# File: main.py

import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Configure basic logging so module-level logger.info() calls are visible
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Import the refactored DB logic and the routers
from mongo_db.db import database, lifespan
from auth.auth import router as auth_router
from app.api.router import router as prediction_router

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
# Expose the prediction/chat router under /api so frontend can call /api/chat
app.include_router(prediction_router, prefix="/api")

@app.get("/")
async def root():
    return { "message": "Talk To Your Money API is running" }

@app.get("/health")
async def health_check():
    db_status = "connected" if database is not None else "disconnected"
    return {"status": "healthy", "database": db_status}


