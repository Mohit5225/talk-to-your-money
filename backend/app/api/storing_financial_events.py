from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import List, Dict, Any
from datetime import datetime, timezone
import logging

__all__ = ["save_financial_events"]

logger = logging.getLogger(__name__)

async def save_financial_events(db: AsyncIOMotorDatabase, clerk_user_id: str, events: List[Dict[str, Any]]):
    """Save extracted financial events to the database."""
    
    # Get the user by their clerk ID
    user = await db.users.find_one({"clerkUserId": clerk_user_id})
    if not user:
        raise ValueError(f"User with clerk ID {clerk_user_id} not found")
        
    for event in events:
        doc_type = event.get("doc_type")
        payload = event.get("payload", {})
        
        if doc_type == "transaction":
            # Create a new transaction record
            transaction = {
                "userId": user["_id"],
                "description": payload.get("description", "Unknown"),
                "amount": payload.get("amount", 0),
                "category": payload.get("category", "Miscellaneous"),
                "type": payload.get("type", "expense"),
                "currency": payload.get("currency", "INR"),
                "metadata": payload.get("metadata"),
                "createdAt": datetime.now(timezone.utc).isoformat()
            }
            
            # Insert the transaction
            result = await db.transactions.insert_one(transaction)
            
            # Add transaction reference to user
            await db.users.update_one(
                {"_id": user["_id"]},
                {"$push": {"transactions": result.inserted_id}}
            )