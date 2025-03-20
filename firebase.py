import time
import firebase_admin
from datetime import datetime, timedelta
from firebase_admin import credentials, db
from discord_variables import FIREBASE_URL

# Initialize Firebase
if not firebase_admin._apps:
    cred = credentials.Certificate('./firebase_credentials.json')
    firebase_admin.initialize_app(cred, {'databaseURL': FIREBASE_URL})

firebase_db = db.reference()

# Updates testing field
def update_test_count(user_id: str, increment: int):
    """Updates the test count for a user in Firebase."""
    ref = db.reference(f"users/{user_id}/test")
    
    current_value = ref.get()  # Fetch existing value
    if current_value is None:
        ref.set(1 if increment > 0 else 0)  # Set to 1 or 0 if removing
    else:
        new_value = max(0, current_value + increment)  # Ensure no negatives
        ref.set(new_value)

# Updates list of rerollers
def update_rerolling_user(discord_id: str, online: int, offline: int, time_spent: int, packs: int, pph : int):
    ref = firebase_db.child("rerollingUsers")
    # Create user data object
    user_data = {
        "Online": online,
        "Offline": offline,
        "Time": time_spent,
        "Packs": packs,
        "PPH": pph,
        "Timestamp": int(time.time())
    }

    ref.child(discord_id).set(user_data)

def remove_rerolling_user(discord_id: str):
    ref = firebase_db.child("rerollingUsers")
    print(f"Removed rerolling user {discord_id}")
    # Check if the user exists before deleting
    if ref.child(discord_id).get() is not None:
        ref.child(discord_id).delete()

def get_user_history(days: int):
    """Fetch user history from Firebase within the given time range (in days)."""
    ref = db.reference("users")
    users_data = ref.get()

    if not users_data:
        return {}

    # Get timestamp range
    time_threshold = int((datetime.utcnow() - timedelta(days=days)).timestamp())

    user_history = {}

    for user_id, user_info in users_data.items():
        history = user_info.get("history", [])
        
        # Filter by timestamp
        filtered_history = [entry for entry in history if entry.get("Timestamp", 0) >= time_threshold]
        
        if filtered_history:
            user_history[user_id] = filtered_history

    return user_history