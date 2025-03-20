def calculate_difference(discord_id, key, current_value, firebase_db):
    """
    Utility function to calculate the difference between the current value
    and the previous value stored in Firebase.

    Parameters:
    - discord_id: The user's Discord ID
    - key: The key to compare ('time' or 'packs')
    - current_value: The new current value to compare with the last value
    - firebase_db: The Firebase database reference to fetch user data
    
    Returns:
    - The difference between the previous and current values
    """
    user_ref = firebase_db.child('users').child(discord_id)
    user_data = user_ref.get()

    if user_data:
        history = user_data.get('history', [])
        if history:
            previous_record = history[0]  # Latest record is always in the front
            
            previous_value = previous_record.get(key, 0)
            
            difference = current_value - previous_value
            return difference
        else:
            return current_value
    else:
        return current_value
