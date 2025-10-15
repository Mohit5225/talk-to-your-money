import json
import logging
import re
from datetime import datetime
from typing import Dict, Any, List

 
from .calling_gemini import get_gemini_response_async

DATA_ENTRY_PROMPT_TEMPLATE = """
You are an expert financial data extraction API. Your sole purpose is to analyze a user's unstructured text and convert it into a structured JSON array of financial events.

**--- Step 1: Analyze and Identify Events ---**
Read the user's entire message. Identify every distinct financial event mentioned. An event could be a purchase, an investment, receiving income, taking on a loan, etc.

**--- Step 2: Structure Each Event into a JSON Object ---**
For each event you identify, create a JSON object with the following structure:
- `doc_type`: The fundamental type of the event.
- `payload`: An object containing the detailed information.

**--- Step 3: Follow These Rules for Each Field ---**

**1. `doc_type` (Required):**
   - Classify the event into ONE of the following types. This is the most important field.
   - Allowed values: `"transaction"`, `"investment"`, `"asset"`, `"liability"`

**2. `payload` (Required):**
   - This object contains the core data. It MUST have the following base fields:
     - `description`: A clean, short summary of the event (e.g., "Pizza Hut Dinner", "Investment in Tata Stocks").
     - `amount`: The numerical value of the event.
     - `currency`: The currency code, default to "INR".
     - `category`: Classify the event into a relevant category. Choose from this list: [Food & Drink, Shopping, Investment, Asset Purchase, Loan, Salary, Bills & Utilities, Groceries, Entertainment, Miscellaneous].
     - `type`: For transactions, specify if it was an "expense" or "income". For other types, this can be null.
     - `metadata`: A nested JSON object for special, category-specific details. If no special details exist, this MUST be `null`.

**3. `metadata` Object (Optional, inside `payload`):**
   - Use this to capture extra information that doesn't fit in the base fields.
   - **If the `category` is 'Investment' and it's a stock**, you MUST include: `{"asset_type": "stock", "ticker_symbol": "TICKER"}`.
   - **If the `category` is 'Asset Purchase' and it's a vehicle**, you could include: `{"asset_type": "vehicle", "make": "Honda", "model": "City"}`.
   - For most simple transactions (like Food & Drink), `metadata` will be `null`.

**--- Step 4: Format Your Final Output ---**
- Your entire response MUST be a single, valid JSON array `[...]`.
- Do NOT include any conversational text, explanations, apologies, or markdown formatting like ```json.

**--- Example ---**
**User Input:** "I SPENT 500 ON PIZZA, INVESTED 3000 ON STOCKS OF TATA ENERGY, and paid 300 for something I don't remember"

**Your JSON Array Response:**
[
  {
    "doc_type": "transaction",
    "payload": {
      "description": "Pizza",
      "amount": 500,
      "currency": "INR",
      "category": "Food & Drink",
      "type": "expense",
      "metadata": null
    }
  },
  {
    "doc_type": "transaction",
    "payload": {
      "description": "Investment in TATA ENERGY Stocks",
      "amount": 3000,
      "currency": "INR",
      "category": "Investment",
      "type": "expense",
      "metadata": {
        "asset_type": "stock",
        "ticker_symbol": "TATAENERGY"
      }
    }
  },
  {
    "doc_type": "transaction",
    "payload": {
      "description": "Unknown expense",
      "amount": 300,
      "currency": "INR",
      "category": "Miscellaneous",
      "type": "expense",
      "metadata": null
    }
  }
]

**--- User's Message to Analyze ---**
User Input: "{user_input}"

Your JSON Array Response:
"""





# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def extract_financial_events(user_input: str) -> List[Dict[str, Any]]:
    """
    Takes raw user text and uses an LLM to extract a structured list of financial events.
    This version is hardened against common LLM response formatting issues.
    """
    formatted_prompt = DATA_ENTRY_PROMPT_TEMPLATE.format(user_input=user_input)
    
    try:
        raw_response = await get_gemini_response_async(formatted_prompt)
        raw_response_str = str(raw_response)
        
        # --- THE CRITICAL FIX ---
        # Find the first '[' and the last ']' to extract the JSON array.
        # This is much more resilient to markdown and extra text.
        match = re.search(r'\[.*\]', raw_response_str, re.DOTALL)
        
        if not match:
            logger.warning("No JSON array found in the LLM response.")
            return []
            
        json_string = match.group(0)
        # --- END OF FIX ---

        extracted_json = json.loads(json_string)
        
        if isinstance(extracted_json, list):
            return extracted_json
        
        logger.warning("LLM response was valid JSON but not a list.")
        return []

    except json.JSONDecodeError:
        logger.error("Failed to decode JSON from the LLM's response.", exc_info=True)
        return []
    except Exception as e:
        logger.error(f"An unexpected error occurred in extract_financial_events: {e}", exc_info=True)
        return []
