# app/api/agent/graph.py
import logging
from langgraph.graph import StateGraph, END
from .state import AgentState
from .nodes import (
    parse_intent_node,
    get_prediction_node,
    handle_portfolio_query_node,
    handle_general_query_node,
    format_response_node
)
logger = logging.getLogger(__name__)

def build_agent_graph():
    """
    This function assembles our agent's brain. It defines all possible paths
    a conversation can take and connects the action nodes together with logic.
    """
    workflow = StateGraph(AgentState)

    # Step 1: Register all our functions as nodes in the graph
    workflow.add_node("parse_intent", parse_intent_node)
    workflow.add_node("predict_stock", get_prediction_node)
    workflow.add_node("portfolio_query", handle_portfolio_query_node)
    workflow.add_node("general_query", handle_general_query_node)
    workflow.add_node("format_final_response", format_response_node)

    # Step 2: Define the starting point of every conversation
    workflow.set_entry_point("parse_intent")

    # Step 3: Define the routing logic. This is the core intelligence.
    def route_intent(state: AgentState):
        """This function reads the intent from the agent's memory and decides which node to run next."""
        intent = state.get("intent")
        logger.info(f"--- ROUTER: Deciding path for intent '{intent}' ---")
        
        if intent == "prediction_request":
            # If the parser couldn't find a valid ticker, we can't predict.
            return "predict_stock" if state.get("symbol") != "UNKNOWN" else "format_final_response"
        elif intent == "portfolio_query":
            return "portfolio_query"
        else: # This covers "general_query" and any other fallback.
            return "general_query"

    # Step 4: Connect the parser node to our router function
    workflow.add_conditional_edges(
        "parse_intent", # The source node
        route_intent,   # The function that makes the decision
        { # A map of the router's possible return values to the next node to execute
            "predict_stock": "predict_stock",
            "portfolio_query": "portfolio_query",
            "general_query": "general_query",
            "format_final_response": "format_final_response"
        }
    )

    # Step 5: Define the final connections
    workflow.add_edge("predict_stock", "format_final_response")
    
    # The placeholder nodes are dead-ends for now; they finish the conversation.
    workflow.add_edge("portfolio_query", END)
    workflow.add_edge("general_query", END)
    
    # The formatter is the final step for the prediction path.
    workflow.add_edge("format_final_response", END)

    # Step 6: Compile the graph into a runnable application
    logger.info("✅ Agent graph compiled successfully.")
    return workflow.compile()