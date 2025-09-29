# api/main.py
from fastapi import FastAPI, HTTPException
from contextlib import asynccontextmanager
from pathlib import Path
from .prediction_service import PredictionService
import numpy as np

# This dictionary will hold our loaded service
ml_models = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
     
    print("🚀 Server starting up...")
    model_dir = Path("models/saved")
    model_path = model_dir / "multi_stock_model.keras"
    feature_scaler_path = model_dir / "multi_stock_feature_scaler.pkl"
    target_scaler_path = model_dir / "multi_stock_target_scaler.pkl"
    
    # Initialize our prediction service
    ml_models["stock_predictor"] = PredictionService(
        model_path=model_path,
        feature_scaler_path=feature_scaler_path,
        target_scaler_path=target_scaler_path
    )
    yield
    # This code runs ONCE when the server shuts down.
    ml_models.clear()
    print("🌙 Server shutting down...")

app = FastAPI(lifespan=lifespan)

@app.get("/")
def read_root():
    return {"message": "Grumpy's Stock Prediction API is awake. Now what?"}

@app.post("/predict/{symbol}")
async def get_prediction(symbol: str):
    """
    This is the endpoint LangGraph will call.
    """
    predictor = ml_models.get("stock_predictor")
    if not predictor:
        raise HTTPException(status_code=503, detail="Model is not loaded yet.")

    # Convert symbol to uppercase to match our config
    symbol = symbol.upper()
    if symbol not in predictor.config.data.stock_identifier_mapping:
        raise HTTPException(status_code=404, detail=f"Stock symbol '{symbol}' not supported.")

    try:
        prediction = predictor.predict(symbol)
        # The prediction is a 2D array, e.g., [[150.5, 148.2, 149.9]]
        # Let's format it nicely for the response.
        prediction_values = prediction[0].tolist()
        
        return {
            "symbol": symbol,
            "prediction": {
                "High": prediction_values[0],
                "Low": prediction_values[1],
                "Close": prediction_values[2]
            }
        }
    except Exception as e:
        # Catch any errors during fetching or prediction
        raise HTTPException(status_code=500, detail=str(e))