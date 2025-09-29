from typing import Dict, Any
from clerk_backend_api.models import User as ClerkUser
 

def clerk_user_to_session_dict(clerk_user: ClerkUser) -> Dict[str, Any]:
    return {
        "sub": clerk_user.id,
        "first_name": clerk_user.first_name,
        "last_name": clerk_user.last_name,
        "primary_email_address": {
            "email_address": clerk_user.email_addresses[0].email_address
            if clerk_user.email_addresses else None
        },
    }