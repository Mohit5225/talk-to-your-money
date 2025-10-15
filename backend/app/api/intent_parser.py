import json
import logging
from datetime import datetime
from typing import Dict, Any

 
from .calling_gemini import get_gemini_response_async

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
- **data_entry**: The user is providing financial data to be recorded if user tells you where did he spent its money or where did he get its money classify it as data_entry.

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