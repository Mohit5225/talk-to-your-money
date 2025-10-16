# app/api/agent/nodes.py
import logging
from .state import AgentState
# We import the intelligent parser function we created previously
from .intent_parser import parse_financial_intent
from .data_entry_node import extract_financial_events
from .storing_financial_events import save_financial_events

logger = logging.getLogger(__name__)

async def parse_intent_node(state: AgentState):
    """
    This is the first node that runs. It's the agent's "ears". It calls our
    LLM-based parser to understand the user's message and figure out what to do.
    """
    logger.info("=" * 80)
    logger.info("🎯 [PARSE_INTENT_NODE] Starting intent parsing...")
    logger.info(f"📝 [PARSE_INTENT_NODE] User input: '{state['user_input']}'")
    
    user_input = state["user_input"]

    # Here we call the intelligent parser we built.
    logger.info("🤖 [PARSE_INTENT_NODE] Calling Gemini LLM for intent extraction...")
    parsed_result = await parse_financial_intent(user_input)
    logger.info(f"✅ [PARSE_INTENT_NODE] LLM response received: {parsed_result}")

    # The agent's memory (state) is updated with the results of the parsing.
    state["intent"] = parsed_result.get("intent", "general_query")

    # FIXED: Extract ticker and date directly from parsed_result, not from entities wrapper
    if parsed_result.get("intent") == "prediction_request":
        # The LLM returns ticker and date directly, not wrapped in entities
        ticker = parsed_result.get("ticker")
        date = parsed_result.get("date")
        
        # Map 'ticker' to 'symbol' for consistency with your state
        state["symbol"] = ticker if ticker and ticker != "UNKNOWN" else None
        state["date_for_prediction"] = date
        
        logger.info(f"🎯 [PARSE_INTENT_NODE] Extracted ticker from LLM: '{ticker}'")
        logger.info(f"📅 [PARSE_INTENT_NODE] Extracted date from LLM: '{date}'")
    else:
        # For non-prediction intents, check if there's an entities object (backwards compatibility)
        entities = parsed_result.get("entities")
        if entities:
            state["symbol"] = entities.get("ticker")
            state["date_for_prediction"] = entities.get("date")

    logger.info(f"🎯 [PARSE_INTENT_NODE] Parsed Intent: '{state['intent']}'")
    logger.info(f"📊 [PARSE_INTENT_NODE] Extracted Symbol: '{state.get('symbol')}'")
    logger.info(f"📅 [PARSE_INTENT_NODE] Extracted Date: '{state.get('date_for_prediction')}'")
    logger.info("=" * 80)

    return state
async def get_prediction_node(state: AgentState):
    """
    This node is our specialized "tool". It is only called when the intent is to get a prediction.
    It uses the PredictionService object that was loaded when the server started.
    """
    logger.info("=" * 80)
    logger.info(f"🔮 [GET_PREDICTION_NODE] Starting prediction execution...")
    logger.info(f"📊 [GET_PREDICTION_NODE] Symbol: {state['symbol']}")
    logger.info(f"📅 [GET_PREDICTION_NODE] Target Date: {state.get('date_for_prediction')}")

    # Retrieve the pre-loaded service object and symbol from the agent's memory.
    service_instance = state["prediction_service"]
    symbol = state["symbol"]
    target_date = state.get("date_for_prediction")
    if target_date in {None, "", "UNKNOWN"}:
        target_date = None
        logger.info(f"📅 [GET_PREDICTION_NODE] No specific date provided, using default (next trading day)")

    try:
        # This is the direct Python function call to our loaded model service. NO HTTP.
        logger.info(f"🤖 [GET_PREDICTION_NODE] Calling ML model for prediction...")
        prediction_result, resolved_date = service_instance.predict(symbol, target_date)
        
        logger.info(f"✅ [GET_PREDICTION_NODE] Model prediction successful!")
        logger.info(f"📊 [GET_PREDICTION_NODE] Raw prediction array shape: {prediction_result.shape}")
        logger.info(f"💰 [GET_PREDICTION_NODE] Predicted values: High=${prediction_result[0][0]:.2f}, Low=${prediction_result[0][1]:.2f}, Close=${prediction_result[0][2]:.2f}")
        logger.info(f"📅 [GET_PREDICTION_NODE] Resolved prediction date: {resolved_date}")
        
        state["prediction_data"] = prediction_result
        state["date_for_prediction"] = resolved_date
    except Exception as e:
        logger.error(f"❌ [GET_PREDICTION_NODE] Error during model prediction for {symbol}: {e}")
        state["prediction_data"] = None # We mark it as failed so the next node can handle it.

    logger.info("=" * 80)
    return state

async def handle_portfolio_query_node(state: AgentState):
    """
    This is a placeholder for a future feature. It shows how we can easily add
    new tools to our agent.
    """
    logger.info("--- NODE: Handling Portfolio Query (Placeholder) ---")
    state["final_response"] = {
        "type": "text",
        "content": "This feature is coming soon! I'll be able to connect to your portfolio and give you updates."
    }
    return state

async def handle_general_query_node(state: AgentState):
    """
    This is the fallback node for when the intent is not a specific tool call.
    """
    logger.info("--- NODE: Handling General Query (Placeholder) ---")
    state["final_response"] = {
        "type": "text",
        "content": "I am a specialized financial agent. I can provide stock predictions for major tech companies. How can I help?"
    }
    return state

async def format_response_node(state: AgentState):
    """
    This node takes raw prediction data and generates a natural language response using Gemini LLM.
    It converts numeric predictions into conversational, human-friendly text.
    """
    logger.info("=" * 80)
    logger.info("📝 [FORMAT_RESPONSE_NODE] Starting response formatting...")

    if state.get("prediction_data") is not None:
        # If prediction was successful, generate natural language response
        prediction_values = state["prediction_data"][0].tolist()
        symbol = state["symbol"]
        date = state["date_for_prediction"]
        
        high, low, close = prediction_values
        
        logger.info(f"💰 [FORMAT_RESPONSE_NODE] Processing prediction data:")
        logger.info(f"   Symbol: {symbol}")
        logger.info(f"   Date: {date}")
        logger.info(f"   High: ${high:.2f}")
        logger.info(f"   Low: ${low:.2f}")
        logger.info(f"   Close: ${close:.2f}")
        
        # Create prompt for LLM to generate natural response
        nl_prompt = f"""You are a friendly financial assistant. Convert this stock prediction into a natural, conversational response.

Stock Symbol: {symbol}
Prediction Date: {date}
Predicted High: ${high:.2f}
Predicted Low: ${low:.2f}
Predicted Close: ${close:.2f}

Generate a brief, friendly message (2-3 sentences) explaining these predictions to the user. Be conversational and helpful, not robotic. Start with something like "Based on my analysis..." or "Here's what I predict...". Make it sound natural and easy to understand."""
        
        # Call LLM to generate natural language response
        logger.info("🤖 [FORMAT_RESPONSE_NODE] Calling Gemini LLM to generate natural language response...")
        from .calling_gemini import get_gemini_response_async
        nl_response = await get_gemini_response_async(nl_prompt)
        
        if nl_response:
            logger.info(f"✅ [FORMAT_RESPONSE_NODE] Generated natural language response: {nl_response[:100]}...")
            state["final_response"] = {
                "type": "text",
                "content": nl_response
            }
        else:
            logger.warning("⚠️ [FORMAT_RESPONSE_NODE] LLM failed to generate response, using fallback")
            state["final_response"] = {
                "type": "text",
                "content": f"Based on my analysis, here's what I predict for {symbol} on {date}: The stock should reach a high of ${high:.2f}, a low of ${low:.2f}, and close around ${close:.2f}."
            }
    else:
        # If prediction failed or wasn't requested, create a fallback text response.
        logger.info("⚠️ [FORMAT_RESPONSE_NODE] No prediction data available, using fallback response")
        if state.get("final_response") is None:
             state["final_response"] = {
                "type": "text",
                "content": "I wasn't able to get a prediction for that stock. It might not be one I track, or there might be insufficient data available."
            }

    logger.info(f"✅ [FORMAT_RESPONSE_NODE] Final response ready: {state['final_response']}")
    logger.info("=" * 80)
    return state



# in nodes.py
async def handle_data_entry_node(state: AgentState):
    """Process financial data entry and save to database"""
    logger.info("--- NODE: Processing Data Entry ---")
    user_input = state["user_input"]
    db = state["db_connection"]
    user_id = state["user_id"]

    # Extract structured data
    extracted_events = await extract_financial_events(user_input)
    
    if not extracted_events:
        state["final_response"] = {
            "type": "text",
            "content": "I couldn't extract any financial data from your message."
        }
        return state
        
    try:
        # Save extracted data to database
        await save_financial_events(db, user_id, extracted_events)
        
        # Prepare summary for response
        categories = set(event["payload"]["category"] for event in extracted_events 
                        if "payload" in event and "category" in event["payload"])
        
        state["final_response"] = {
            "type": "text",
            "content": f"I've recorded {len(extracted_events)} financial entries in these categories: {', '.join(categories)}."
        }
    except Exception as e:
        logger.error(f"Error saving financial events: {e}")
        state["final_response"] = {
            "type": "text",
            "content": "I had trouble saving your financial data. Please try again later."
        }
    
    return state