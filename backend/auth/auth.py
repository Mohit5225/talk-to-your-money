# File: app/api/endpoints/auth.py

from fastapi import APIRouter, Depends, HTTPException, Request
from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import Dict, Any
import os
import logging
from dotenv import load_dotenv
import uuid
import traceback
from fastapi.responses import JSONResponse

from clerk_backend_api import Clerk, AuthenticateRequestOptions
from auth.clerk_adaptor import clerk_user_to_session_dict
from services.user_creation import get_or_create_user_from_clerk
from mongo_db.db import get_database
from backend_models.backend_models import User as UserResponseModel


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - [%(funcName)s] - %(message)s'
)
logger = logging.getLogger("auth")
load_dotenv()

secret = os.environ.get("CLERK_SECRET_KEY")
jwt_key = os.environ.get("JWT_KEY")
if not secret or not jwt_key:
    raise RuntimeError("CLERK_SECRET_KEY and JWT_KEY must be set")

clerk = Clerk(bearer_auth=secret)
router = APIRouter()


# --- Dependencies ---
async def get_current_user(request: Request) -> Dict[str, Any]:
    trace_id = uuid.uuid4()
    logger.info(f"trace_id={trace_id} -- 🔐 Starting authentication attempt...")

    try:
        options = AuthenticateRequestOptions(jwt_key=jwt_key)
        request_state = clerk.authenticate_request(request, options)

        if not request_state.is_signed_in:
            logger.warning(f"trace_id={trace_id} -- ⚠️ Not signed in.")
            raise HTTPException(status_code=401, detail="Not signed in")

        user_id = request_state.payload.get("sub")
        if not user_id:
            logger.error(f"trace_id={trace_id} -- ❌ No 'sub' in token.")
            raise HTTPException(status_code=401, detail="Invalid token: User ID missing.")

        logger.info(f"trace_id={trace_id} -- ✅ Token validated for clerk_user_id='{user_id}'.")
        clerk_user = clerk.users.get(user_id=user_id)

        session_dict = clerk_user_to_session_dict(clerk_user)
        session_dict['trace_id'] = str(trace_id)

        return session_dict

    except Exception as e:
        logger.error(f"trace_id={trace_id} -- ❌ Authentication failed: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=401, detail="Authentication failed")


from svix.webhooks import Webhook, WebhookVerificationError

CLERK_WEBHOOK_SECRET = os.environ.get("CLERK_WEBHOOK_SECRET")
if not CLERK_WEBHOOK_SECRET:
    raise RuntimeError("CLERK_WEBHOOK_SECRET must be set")

@router.post("/webhooks/clerk", tags=["Authentication"])
async def clerk_webhook(
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    """Webhook endpoint to handle Clerk events (user.created, etc.)."""
    trace_id = uuid.uuid4()
    try:
        payload = await request.body()  # raw bytes
        headers = request.headers

        # Verify signature using svix
        wh = Webhook(CLERK_WEBHOOK_SECRET)
        try:
            body = wh.verify(payload, headers)
        except WebhookVerificationError as e:
            logger.error(f"trace_id={trace_id} -- ❌ Webhook signature verification failed: {e}")
            raise HTTPException(status_code=400, detail="Invalid webhook signature")

        event_type = body.get("type")
        data = body.get("data")

        logger.info(f"trace_id={trace_id} -- 📩 Verified webhook event='{event_type}'")

        if event_type == "user.created":
            clerk_user_id = data.get("id")
            logger.info(f"trace_id={trace_id} -- 👤 New Clerk user created: {clerk_user_id}")
            
            # Build session_dict directly from webhook data (dict)
            session_dict = {
                "sub": data.get("id"),
                "first_name": data.get("first_name"),
                "last_name": data.get("last_name"),
                "primary_email": data.get("email_addresses", [{}])[0].get("email_address") if data.get("email_addresses") else None
            }
            await get_or_create_user_from_clerk(db, session_dict)
            
            logger.info(f"trace_id={trace_id} -- ✅ User created in DB for clerk_user_id='{clerk_user_id}'")

    except Exception as e:
        logger.error(f"trace_id={trace_id} -- ❌ Webhook error: {str(e)}")
        logger.error(traceback.format_exc())
        return JSONResponse({"status": "error", "detail": str(e)}, status_code=500)

@router.get("/users/me", response_model=UserResponseModel, tags=["Authentication"])
async def read_users_me(
    clerk_session: Dict[str, Any] = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    trace_id = clerk_session.get('trace_id', 'N/A')
    clerk_user_id = clerk_session.get('sub')

    logger.info(f"trace_id={trace_id} -- 👤 Endpoint /users/me for clerk_user_id='{clerk_user_id}'")

    try:
        # Now just fetch (user already created via webhook)
        internal_user = await get_or_create_user_from_clerk(db, clerk_session)

        db_user_id = internal_user.get('_id')
        logger.info(f"trace_id={trace_id} -- ✅ Returning internal user. db_id='{db_user_id}'")
        return internal_user

    except Exception as e:
        logger.error(f"trace_id={trace_id} -- ❌ Failed fetching user: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail="Error processing user data.")
