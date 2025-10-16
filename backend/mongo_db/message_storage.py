# File: mongo_db/message_storage.py

from motor.motor_asyncio import AsyncIOMotorDatabase
from datetime import datetime, timezone
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

async def save_conversation_message(
    db: AsyncIOMotorDatabase,
    user_id: str,
    role: str,  # "user" or "assistant"
    content: str,
    metadata: Optional[Dict[str, Any]] = None
) -> str:
    """
    Save a single conversation message to the messages collection.
    
    Args:
        db: MongoDB database instance
        user_id: Clerk user ID
        role: Either "user" or "assistant"
        content: The message content
        metadata: Optional metadata (intent, symbol, date, etc.)
    
    Returns:
        The inserted message ID as a string
    """
    try:
        logger.info(f"💾 [MESSAGE_STORAGE] Saving {role} message for user {user_id[:8]}...")
        
        message_doc = {
            "userId": user_id,
            "role": role,
            "content": content,
            "metadata": metadata or {},
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        result = await db.messages.insert_one(message_doc)
        message_id = str(result.inserted_id)
        
        logger.info(f"✅ [MESSAGE_STORAGE] Successfully saved {role} message with ID: {message_id}")
        return message_id
        
    except Exception as e:
        logger.error(f"❌ [MESSAGE_STORAGE] Error saving message: {str(e)}")
        raise
