# app/api/agent/state.py
from typing import TypedDict, Optional, Any
# Adjust this import path if your PredictionService is located elsewhere
from app.api.prediction_service import PredictionService
from motor.motor_asyncio import AsyncIOMotorDatabase

class AgentState(TypedDict):
    """
    This defines the structure of our agent's shared memory.
    Every piece of information the agent discovers or uses during a run is stored here.
    """
    user_input: str
    prediction_service: PredictionService
    db_connection: AsyncIOMotorDatabase  # Add this
    user_id: str  # Add this (clerk user ID)
    intent: Optional[str]
    symbol: Optional[str]
    date_for_prediction: Optional[str]
    prediction_data: Optional[Any]
    final_response: Optional[dict]