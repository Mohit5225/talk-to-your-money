# app/api/router.py
from fastapi import APIRouter, HTTPException
from pathlib import Path
import pandas as pd
import numpy as np
from .prediction_service import PredictionService

# This dictionary will hold our loaded service
ml_models = {}

router = APIRouter(tags=["predictions"])

# Initialize the prediction service
def initialize_prediction_service():
    # Use absolute path to the model files from the original location
    model_path = Path(r"C:\Users\mohit\Desktop\python\FinancialAgent\LJ_Hackathon\backend\models\saved\multi_stock_model.keras")
    feature_scaler_path = Path(r"C:\Users\mohit\Desktop\python\FinancialAgent\LJ_Hackathon\backend\models\saved\multi_stock_feature_scaler.pkl")
    target_scaler_path = Path(r"C:\Users\mohit\Desktop\python\FinancialAgent\LJ_Hackathon\backend\models\saved\multi_stock_target_scaler.pkl")
    
    # Check if model files exist
    for file_path, file_desc in [
        (model_path, "Model file"),
        (feature_scaler_path, "Feature scaler"),
        (target_scaler_path, "Target scaler")
    ]:
        if not file_path.exists():
            print(f"⚠️ Warning: {file_desc} not found at {file_path}")
        else:
            print(f"✅ Found {file_desc} at {file_path}")
            
    # Initialize our prediction service
    try:
        ml_models["stock_predictor"] = PredictionService(
            model_path=model_path,
            feature_scaler_path=feature_scaler_path,
            target_scaler_path=target_scaler_path
        )
        print("✅ Successfully loaded model and scalers")
    except Exception as e:
        print(f"❌ Error initializing prediction service: {str(e)}")


@router.post("/predict/{symbol}")
@router.get("/predict/{symbol}")
async def get_prediction(symbol: str):
    """
    Endpoint to get stock prediction for a given symbol
    """
    if not ml_models.get("stock_predictor"):
        initialize_prediction_service()
        
    predictor = ml_models.get("stock_predictor")
    if not predictor:
        raise HTTPException(status_code=503, detail="Model is not loaded yet.")

    # Convert symbol to uppercase to match our config
    symbol = symbol.upper()
    if symbol not in predictor.config.data.stock_identifier_mapping:
        raise HTTPException(status_code=404, detail=f"Stock symbol '{symbol}' not supported.")

    try:
        try:
            # Make the prediction - this internally calls _prepare_inference_data
            prediction = predictor.predict(symbol)
            
            # Extract and format values for response
            return {
                "symbol": symbol,
                "high": float(prediction[0][0]),
                "low": float(prediction[0][1]),
                "close": float(prediction[0][2]),
                "date": pd.Timestamp.now().strftime('%Y-%m-%d')
            }
        except ValueError as ve:
            # Handle specific value errors like not enough data
            print(f"Value Error in prediction: {str(ve)}")
            if "Not enough recent data" in str(ve):
                raise HTTPException(
                    status_code=422, 
                    detail=f"Insufficient data available for {symbol}. We need at least 30 days of market data to make a prediction."
                )
            raise ve
    except Exception as e:
        # Catch any other errors during fetching or prediction
        print(f"Error making prediction: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))