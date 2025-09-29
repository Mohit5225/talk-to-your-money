import logging
import asyncio
import os
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables from .env file
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)
genai.configure(api_key=GOOGLE_API_KEY)

async def get_gemini_response_async(prompt: str) -> str:
    LLM_MODEL_NAME = "gemini-1.5-flash"
    if not GOOGLE_API_KEY or "YOUR_KEY" in GOOGLE_API_KEY:
        logger.error("Invalid API key configuration")
        return None
    
    model = genai.GenerativeModel(LLM_MODEL_NAME)
    
    try:
        logger.info(f"Sending prompt to Gemini: {prompt[:100]}...")
        response = await model.generate_content_async(
            contents=[{"parts": [{"text": prompt}]}],
            generation_config={
                "temperature": 0.1,
                "max_output_tokens": 2048
            }
        )
        
        if hasattr(response, 'text'):
            return response.text
        else:
            logger.error("Response missing text attribute")
            return None
    
    except Exception as e:
        logger.error(f"Error calling Gemini: {str(e)}")
        return None