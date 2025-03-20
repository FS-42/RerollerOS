from firebase_admin import db

def get_longest_session(discord_id: str, firebase_db) -> str:
    user_ref = firebase_db.child('users').child(discord_id)
    user_data = user_ref.get()

    if not user_data or "history" not in user_data or not user_data["history"]:
        return f"No session data found for user {discord_id}."

    # Find the session with the longest time
    longest_session = max(user_data["history"], key=lambda session: session.get("Time", 0))

    packs = longest_session.get("Packs", 0)
    time = longest_session.get("Time", 0)

    return f"Packs: `{packs}` - Time: `{time}` min"
