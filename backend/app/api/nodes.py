# app/api/agent/nodes.py
import logging
from .state import AgentState
# We import the intelligent parser function we created previously
from .intent_parser import parse_financial_intent

logger = logging.getLogger(__name__)

async def parse_intent_node(state: AgentState):
    """
    This is the first node that runs. It's the agent's "ears". It calls our
    LLM-based parser to understand the user's message and figure out what to do.
    """
    logger.info("--- NODE: Parsing User Intent ---")
    user_input = state["user_input"]

    # Here we call the intelligent parser we built.
    parsed_result = await parse_financial_intent(user_input)

    # The agent's memory (state) is updated with the results of the parsing.
    state["intent"] = parsed_result.get("intent", "general_query")

    entities = parsed_result.get("entities")
    if entities:
        state["symbol"] = entities.get("ticker")
        state["date_for_prediction"] = entities.get("date")

    logger.info(f"Intent='{state['intent']}', Symbol='{state.get('symbol')}', Date='{state.get('date_for_prediction')}'")

    return state

async def get_prediction_node(state: AgentState):
    """
    This node is our specialized "tool". It is only called when the intent is to get a prediction.
    It uses the PredictionService object that was loaded when the server started.
    """
    logger.info(f"--- NODE: Executing Prediction for {state['symbol']} ---")

    # Retrieve the pre-loaded service object and symbol from the agent's memory.
    service_instance = state["prediction_service"]
    symbol = state["symbol"]
    target_date = state.get("date_for_prediction")
    if target_date in {None, "", "UNKNOWN"}:
        target_date = None

    try:
        # This is the direct Python function call to our loaded model service. NO HTTP.
        prediction_result, resolved_date = service_instance.predict(symbol, target_date)
        state["prediction_data"] = prediction_result
        state["date_for_prediction"] = resolved_date
        logger.info(f"Successfully ran prediction model for {symbol}")
    except Exception as e:
        logger.error(f"Error during model prediction for {symbol}: {e}")
        state["prediction_data"] = None # We mark it as failed so the next node can handle it.

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
    This node is the final step for the prediction path. It takes the raw prediction
    numbers and formats them into the specific JSON our frontend needs to render a graph.
    """
    logger.info("--- NODE: Formatting Final Response ---")

    if state.get("prediction_data") is not None:
        # If prediction was successful, build the graph JSON
        prediction_values = state["prediction_data"][0].tolist()
        symbol = state["symbol"]
        date = state["date_for_prediction"]

        chart_data = {
            "title": f"{symbol} Price Prediction for {date}",
            "labels": ["High", "Low", "Close"],
            "datasets": [{
                "label": "Predicted Price ($)",
                "data": prediction_values,
                "backgroundColor": ["rgba(75, 192, 192, 0.6)", "rgba(255, 99, 132, 0.6)", "rgba(54, 162, 235, 0.6)"]
            }]
        }
        state["final_response"] = {
            "type": "graph",
            "text_summary": f"Based on my analysis, here is the prediction for {symbol} on {date}:",
            "chart_data": chart_data
        }
    else:
        # If prediction failed or wasn't requested, create a fallback text response.
        if state.get("final_response") is None:
             state["final_response"] = {
                "type": "text",
                "content": "I wasn't able to get a prediction for that stock. It might not be one I track."
            }

    return state