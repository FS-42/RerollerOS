from firebase_admin import db  # Ensure we're using the same Firebase setup

def get_current_session(discord_id: str, firebase_db) -> str:
    user_ref = firebase_db.child('users').child(discord_id)
    user_data = user_ref.get()

    if not user_data or "history" not in user_data or not user_data["history"]:
        return f"No session data found for user {discord_id}."

    latest_entry = user_data["history"][0]  # Get the most recent session
    packs = latest_entry.get("Packs", 0)
    time = latest_entry.get("Time", 0)

    return f"Packs: `{packs}` - Time: `{time}` min"