# Run this in your Python environment to actually see what methods exist
from clerk_backend_api import Clerk
import os
from dotenv import load_dotenv

load_dotenv()
secret = os.environ.get("CLERK_SECRET_KEY")
clerk = Clerk(bearer_auth=secret)

print("🔍 ============ CLERK SDK EXPLORATION ============")
print(f"🔍 Clerk object type: {type(clerk)}")
print(f"🔍 Available attributes:")

# Get all non-private attributes
attrs = [attr for attr in dir(clerk) if not attr.startswith('_')]
for attr in attrs:
    attr_obj = getattr(clerk, attr)
    print(f"  - {attr}: {type(attr_obj)}")
    
    # If it's a resource, explore its methods too
    if hasattr(attr_obj, '__dict__') and not callable(attr_obj):
        sub_attrs = [sub_attr for sub_attr in dir(attr_obj) if not sub_attr.startswith('_')]
        for sub_attr in sub_attrs[:5]:  # Limit to first 5 to avoid spam
            print(f"    └─ {sub_attr}")
        if len(sub_attrs) > 5:
            print(f"    └─ ... and {len(sub_attrs) - 5} more")

print("\n🔍 Sessions resource methods (if exists):")
if hasattr(clerk, 'sessions'):
    sessions_methods = [method for method in dir(clerk.sessions) if not method.startswith('_')]
    print(f"Available sessions methods: {sessions_methods}")

print("\n🔍 Users resource methods (if exists):")
if hasattr(clerk, 'users'):
    users_methods = [method for method in dir(clerk.users) if not method.startswith('_')]
    print(f"Available users methods: {users_methods}")

# Check for JWT verification methods
print("\n🔍 Looking for JWT/Token verification methods...")
potential_methods = ['verify_token', 'verify_session', 'validate_token', 'decode_token', 'authenticate']
for method_name in potential_methods:
    if hasattr(clerk, method_name):
        print(f"✅ Found: clerk.{method_name}")
    elif hasattr(clerk, 'sessions') and hasattr(clerk.sessions, method_name):
        print(f"✅ Found: clerk.sessions.{method_name}")
    else:
        print(f"❌ Not found: {method_name}")