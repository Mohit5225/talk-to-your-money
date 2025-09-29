# File: app/services/user_creation.py

from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import Dict, Any
from pymongo import ReturnDocument
from datetime import datetime, timezone

async def get_or_create_user_from_clerk(db: AsyncIOMotorDatabase, clerk_session: Dict[str, Any]) -> Dict:
    users_collection = db.get_collection("users")
    clerk_user_id = clerk_session.get("sub")
    
    if not clerk_user_id:
        raise ValueError("Clerk User ID (sub) not found in session")

    full_name = f"{clerk_session.get('first_name', '')} {clerk_session.get('last_name', '')}".strip()
    now_iso = datetime.now(timezone.utc).isoformat()

    user_data_to_set = {
        "email": clerk_session.get("primary_email"),
        "name": full_name,
        "updatedAt": now_iso,
    }
    
    # These fields are only set when a new document is created (inserted)
    data_on_insert = {
        "clerkUserId": clerk_user_id,
        "transactions": [],
        "liabilities": [],
        "investments": [],
        "epf_balances": [],
        "credit_scores": [],
        "assets": [],
        "conversations": [],
        "createdAt": now_iso
    }

    internal_user = await users_collection.find_one_and_update(
        {"clerkUserId": clerk_user_id},
        {"$set": user_data_to_set, "$setOnInsert": data_on_insert},
        upsert=True,
        return_document=ReturnDocument.AFTER
    )
    
    return internal_user