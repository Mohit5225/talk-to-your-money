# app/api/router.py
from fastapi import APIRouter, HTTPException, Query, Depends
from fastapi import Request
from auth.auth import get_current_user
from mongo_db.db import get_database
from .graph import build_agent_graph
import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
from pathlib import Path
from typing import Optional
import pandas as pd
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
async def get_prediction(symbol: str, date: Optional[str] = Query(default=None, description="Target date in YYYY-MM-DD format")):
    """
    Endpoint to get stock prediction for a given symbol.
    If date is not provided, it will use the current date.
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

    # Parse and standardize the requested date (if provided)
    target_date_iso: Optional[str] = None
    if date:
        try:
            parsed_date = pd.to_datetime(date)
            # Normalize and drop timezone info for consistent downstream usage
            parsed_date = parsed_date.tz_localize(None).normalize()
            target_date_iso = parsed_date.strftime('%Y-%m-%d')
        except (ValueError, TypeError):
            raise HTTPException(
                status_code=400, 
                detail="Invalid date format. Please use YYYY-MM-DD."
            )

    try:
        try:
            # Log prediction request
            logger.info("\n" + "="*60)
            logger.info(f"📊 PREDICTING FOR {symbol} | Target Date: {target_date_iso or 'TODAY'}")
            logger.info("="*60)
            
            # Make the prediction - this internally calls _prepare_inference_data
            prediction, resolved_date = predictor.predict(symbol, target_date_iso)
            
            # Extract numeric values
            high_v = float(prediction[0][0])
            low_v = float(prediction[0][1])
            close_v = float(prediction[0][2])

            # Log prediction results in clean format
            logger.info(f"\n✅ PREDICTION RESULTS:")
            logger.info(f"🤖 Model Raw Output (Absolute Values):")
            logger.info(f"   Symbol: {symbol}")
            logger.info(f"   Date:   {resolved_date}")
            logger.info(f"   📈 High:  ${high_v:.2f}")
            logger.info(f"   📉 Low:   ${low_v:.2f}")
            logger.info(f"   💰 Close: ${close_v:.2f}")
            logger.info("="*60 + "\n")
            

            # Extract and format values for response
            return {
                 
                "symbol": symbol,
                "high": high_v,
                "low": low_v,
                "close": close_v,
                "date": resolved_date
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
    





@router.post("/chat")
async def chat_endpoint(
    payload: dict,
    clerk_session: dict = Depends(get_current_user),
    db = Depends(get_database),
):
    """
    Chat endpoint that runs the LangGraph agent and stores conversation messages.
    Expects JSON body: { "message": "..." }
    """
    user_input = payload.get("message") or payload.get("text")
    if not user_input or not user_input.strip():
        raise HTTPException(status_code=400, detail="`message` is required")

    user_id = clerk_session.get("sub")
    
    logger.info("=" * 100)
    logger.info(f"🌐 [CHAT_ENDPOINT] New chat request from user: {user_id[:8]}...")
    logger.info(f"💬 [CHAT_ENDPOINT] User message: '{user_input}'")
    
    # Save user message to database
    from mongo_db.message_storage import save_conversation_message
    try:
        user_msg_id = await save_conversation_message(db, user_id, "user", user_input)
        logger.info(f"✅ [CHAT_ENDPOINT] User message saved with ID: {user_msg_id}")
    except Exception as e:
        logger.error(f"❌ [CHAT_ENDPOINT] Failed to save user message: {e}")

    # Ensure prediction service loaded (used by agent prediction node)
    if not ml_models.get("stock_predictor"):
        logger.info("🔄 [CHAT_ENDPOINT] Initializing prediction service...")
        initialize_prediction_service()

    logger.info("🤖 [CHAT_ENDPOINT] Building agent graph...")
    agent = build_agent_graph()

    initial_state = {
        "user_input": user_input,
        "prediction_service": ml_models.get("stock_predictor"),
        "db_connection": db,
        "user_id": user_id,
        "intent": None,
        "symbol": None,
        "date_for_prediction": None,
        "prediction_data": None,
        "final_response": None
    }

    # Run the async agent
    logger.info("🚀 [CHAT_ENDPOINT] Invoking LangGraph agent...")
    result_state = await agent.ainvoke(initial_state)
    logger.info("✅ [CHAT_ENDPOINT] Agent execution completed")
    
    bot_response = result_state.get("final_response", {"type": "text", "content": "No response generated."})
    bot_content = bot_response.get("content", "No response")
    
    logger.info(f"📤 [CHAT_ENDPOINT] Bot response: '{bot_content[:100]}...'")
    
    # Save assistant message to database with metadata
    try:
        assistant_msg_id = await save_conversation_message(
            db, 
            user_id, 
            "assistant", 
            bot_content,
            metadata={
                "intent": result_state.get("intent"),
                "symbol": result_state.get("symbol"),
                "date": result_state.get("date_for_prediction")
            }
        )
        logger.info(f"✅ [CHAT_ENDPOINT] Assistant message saved with ID: {assistant_msg_id}")
    except Exception as e:
        logger.error(f"❌ [CHAT_ENDPOINT] Failed to save assistant message: {e}")

    logger.info("=" * 100)
    return bot_response