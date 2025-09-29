# File: app/core/db.py

import os
from contextlib import asynccontextmanager
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from fastapi import HTTPException

mongo_client: AsyncIOMotorClient = None
database: AsyncIOMotorDatabase = None

@asynccontextmanager
async def lifespan(app):
    """Application startup and shutdown events"""
    global mongo_client, database
    print("🚀 Server starting up...")
    
    mongodb_uri = os.getenv("MONGODB_URI")
    if mongodb_uri:
        mongo_client = AsyncIOMotorClient(mongodb_uri)
        database = mongo_client.get_database("talk_to_your_money")
        print("✅ MongoDB connected")
    else:
        print("⚠️ MongoDB URI not found, running without database")
    
    yield
    
    print("🔒 Closing MongoDB connection...")
    mongo_client.close()

# Dependency to get database
def get_database() -> AsyncIOMotorDatabase:
    if database is None:
        raise HTTPException(status_code=503, detail="Database not available")
    return database