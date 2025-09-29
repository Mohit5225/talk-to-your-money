import json
import logging
from datetime import datetime
from typing import Dict, Any

 
from calling_gemini import get_gemini_response_async

logger = logging.getLogger(__name__)

# --- The Finalized Prompt Template ---
INTENT_PARSING_PROMPT_TEMPLATE = """
```json
{
    "user_input": "{user_input}",
    "current_date": "{current_date}"
}
You are an expert intent and entity extraction system for a Financial AI Agent.
Your task is to analyze the user's message and extract three key pieces of information:
1.  The user's intent.
2.  The stock ticker they are interested in.
3.  The date they are asking about.

**--- Step 1: Classify the Intent ---**
Categorize the user's request into ONE of the following intents:
- **prediction_request**: The user is asking for a future stock price prediction.
- **portfolio_query**: The user is asking a question about their personal investments, holdings, or portfolio performance.
- **general_query**: The user is asking a general financial question or a question that doesn't fit the other categories.

**--- Step 2: Extract Entities for "prediction_request" ---**
If, and only if, the intent is `prediction_request`, you MUST extract the following entities:

**1. Ticker:**
   - The user will provide a company name. You MUST map it to its official stock ticker using this table.
   - If the name is not on this list, do not guess. Set the ticker to "UNKNOWN".

   **Ticker Lookup Table:**
   - "apple": "AAPL"
   - "tesla": "TSLA"
   - "microsoft": "MSFT"
   - "nvidia": "NVDA"
   - "google": "GOOGL"
   - "alphabet": "GOOGL"
   - "amd": "AMD"
   - "meta": "META"
   - "facebook": "META"

**2. Date:**
   - Find the date the user is asking about.
   - You MUST format it as **YYYY-MM-DD**.
   - **If the user does not specify a date or says "today" or "tomorrow", use today's date which is: {current_date}**

**--- Step 3: Format Your Response ---**
You MUST respond with ONLY a valid JSON object. Do not add any conversational text, explanations, or markdown formatting like ```json.

**Example for a prediction request:**
User Input: "what do you think apple stock will do tomorrow"
Your Response:
{{
    "intent": "prediction_request",
    "entities": {{
        "ticker": "AAPL",
        "date": "{current_date}"
    }}
}}

**Example for a portfolio query:**
User Input: "how are my investments doing?"
Your Response:
{{
    "intent": "portfolio_query",
    "entities": null
}}

**--- User's Message to Analyze ---**
User Input: "{user_input}"

Your JSON Response:
"""

async def parse_financial_intent(user_input: str) -> Dict[str, Any]:
    """
    Uses the Gemini LLM to parse intent and entities from a user's financial query.
    
    This function is designed to be robust, handling potential errors from the LLM
    by falling back to a safe default state.

    Args:
        user_input: The raw text message from the user.

    Returns:
        A dictionary containing the parsed intent and any extracted entities.
    """
    current_date = datetime.now().strftime('%Y-%m-%d')
    prompt = INTENT_PARSING_PROMPT_TEMPLATE.format(
        user_input=user_input,
        current_date=current_date
    )

    try:
        # Call the LLM function you provided
        response_str = await get_gemini_response_async(prompt)
        
        if not response_str:
            raise ValueError("LLM returned an empty or None response.")
        
        # Clean the response string in case the LLM wraps it in markdown
        cleaned_response_str = response_str.strip().replace('```json', '').replace('```', '').strip()
            
        # Parse the JSON string from the LLM into a Python dictionary
        parsed_response = json.loads(cleaned_response_str)
        logger.info(f"✅ LLM successfully parsed intent: {parsed_response}")
        return parsed_response

    except (json.JSONDecodeError, ValueError, TypeError) as e:
        logger.error(f"❌ Failed to parse LLM response into JSON. Error: {e}. Response was: '{response_str}'")
        # Fallback to a safe default if the LLM response is garbage or fails
        return {
            "intent": "general_query",
            "entities": None
        }

# --- This block allows you to test this file directly ---
if __name__ == '__main__':
    import asyncio

    async def main():
        print("--- Testing Intent Parser ---")
        
        test_inputs = [
            "what do you think microsoft stock will do on 2025-10-20?",
            "can you predict tesla for me",
            "how is my portfolio looking?",
            "what is a stock?"
        ]
        
        for text in test_inputs:
            print(f"\n---> Testing input: '{text}'")
            result = await parse_financial_intent(text)
            print(f"<--- Parsed result: {result}")
            
    asyncio.run(main())