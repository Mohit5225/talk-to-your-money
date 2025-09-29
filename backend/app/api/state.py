# app/api/agent/state.py
from typing import TypedDict, Optional, Any
# Adjust this import path if your PredictionService is located elsewhere
from app.api.prediction_service import PredictionService

class AgentState(TypedDict):
    """
    This defines the structure of our agent's shared memory.
    Every piece of information the agent discovers or uses during a run is stored here.
    """
    # --- Inputs from the user and server ---
    user_input: str
    prediction_service: PredictionService # The pre-loaded model service object

    # --- Information discovered by the agent's nodes ---
    intent: Optional[str]
    symbol: Optional[str]
    date_for_prediction: Optional[str]
    prediction_data: Optional[Any] # This will hold the numpy array from the model

    # --- The final, formatted output for the frontend ---
    final_response: Optional[dict]