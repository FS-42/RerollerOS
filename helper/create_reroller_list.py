import time
import discord
from firebase import firebase_db
from discord_variables import DESTINATION_ID, MINIMUM_PPH
from flags import BLACKLIST_WARNING_TIME
from helper.blacklist_helper import blacklist_helper
from helper.create_message import create_message

latest_sent_message = None  

async def create_reroller_list(bot):
    """Fetches all rerolling users from Firebase and sends an update message in Discord."""
    global latest_sent_message

    print("Starting reroller list update...")  # Logging start of the process

    # Get the channel using the bot instance
    channel = bot.get_channel(int(DESTINATION_ID))
    if not channel:
        print(f"❌ Error: Channel {DESTINATION_ID} not found. Check if bot has access.")
        return

    message_list = []
    current_time = int(time.time())

    print("Fetching rerolling users from Firebase...")  # Logging Firebase fetch
    # Fetch all rerolling users from Firebase
    rerolling_users = firebase_db.child("rerollingUsers").get()
    last_warning_time = firebase_db.child("lastWarningTimes").get() or {}  # Retrieve stored warning times

    if rerolling_users is None:
        print("⚠️ No 'rerollingUsers' node found in Firebase. Creating an empty node.")
        try:
            current_time = int(time.time())
            dummy_data = {
                "dummy_user_id": {
                    "Online": 0,
                    "Offline": 0,
                    "Time": 0,
                    "Packs": 0,
                    "PPH": 0,
                    "Timestamp": current_time
                }
            }
            firebase_db.child("rerollingUsers").set(dummy_data)
            print("The 'rerollingUsers' node was created with dummy data.")
        except Exception as e:
            print(f"Error creating 'rerollingUsers' node: {e}")
        rerolling_users = {}

    total_online = 0
    total_pph = 0

    if not rerolling_users:
        message_content = "## No active rerolling users."
    else:
        sorted_users = sorted(
            rerolling_users.items(),
            key=lambda x: x[1].get("Timestamp", 0),
            reverse=True
        )

        for discord_id, data in sorted_users:
            online = data.get("Online", 0)
            offline = data.get("Offline", 0)
            time_spent = data.get("Time", 0)
            packs = data.get("Packs", 0)
            pph = data.get("PPH", 0)
            timestamp = data.get("Timestamp", 0)

            time_diff_minutes = (current_time - timestamp) // 60
            relative_time = f"{time_diff_minutes}m" if time_diff_minutes > 0 else "Now"

            total_online += online
            total_pph += pph

            warning_needed = pph >= 0 and pph < MINIMUM_PPH and time_spent > 0
            warning_emoji = "⚠️" if warning_needed else ""

            # Get last warning time from Firebase
            last_warning = last_warning_time.get(str(discord_id), 0)

            if warning_needed and (current_time - last_warning >= BLACKLIST_WARNING_TIME):
                helper_message = create_message(timestamp, pph)
                await blacklist_helper(bot, discord_id, helper_message)
                
                # Update Firebase with the new warning time
                last_warning_time[str(discord_id)] = current_time
                firebase_db.child("lastWarningTimes").set(last_warning_time)
                print(f'user {discord_id} warned')

            username_display = f"{warning_emoji} <@{discord_id}>" if warning_emoji else f"<@{discord_id}>"

            line = f"{username_display} | {online} / {offline} | {time_spent}m | PPH: {round(pph)} | {relative_time}"
            message_list.append(line)

        header = f"# Active Rerollers ({len(sorted_users)})\n**Instances: {total_online} | Total PPH: {round(total_pph)}**\n"
        message_content = header + "\n".join(message_list)

    # Try sending or editing the message
    try:
        if latest_sent_message:
            await latest_sent_message.edit(content=message_content)
        else:
            latest_sent_message = await channel.send(message_content, allowed_mentions=discord.AllowedMentions.none())
            print(f"Message sent to channel {DESTINATION_ID}.")  # Log successful send
    except discord.errors.HTTPException as e:
        print(f"Error sending/editing message: {e}")
    except Exception as e:
        print(f"Unexpected error while sending message: {e}")
