PREDICTION_INSIDE_BOT_PROMPT_TEMPLATE = """
The user is asking for a future stock price prediction.
**--- Step 1 : you are 
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

