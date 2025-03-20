from datetime import datetime

def create_message(timestamp: int, pph: int) -> str:
    human_date = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
    return f"At {human_date}, your packs per hour was {pph} / 100. Please fix and clean your instances and remove yourself from the blacklist."

