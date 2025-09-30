# api/main.py
from fastapi import FastAPI, HTTPException
from contextlib import asynccontextmanager
from pathlib import Path
from .prediction_service import PredictionService
import numpy as np
import pandas as pd

# This dictionary will hold our loaded service

app = FastAPI()

# Add CORS middleware
from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Grumpy's Stock Prediction API is awake. Now what?"}

