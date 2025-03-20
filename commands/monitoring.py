import discord
import re
import logging
from firebase_admin import db
from firebase import update_rerolling_user
from discord.ext import commands
from discord_variables import MONITOR_ID
from helper.calculate_difference import calculate_difference

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

firebase_db = db.reference()

# Match the webhook message
message_pattern = re.compile(r"""
    <(?P<discord_id>\d+)(?:-\d+)?>  # Capture Discord ID (with optional -0 suffix)
    (?:\s*\S+)?  # Ignore any extra words (e.g., usernames) after the ID
    \s*Online:\s(?P<online>.*?)\s*[.,]?  # Capture online instances (until period or comma, optional)
    \s*Offline:\s(?P<offline>.*?)\s*[.,]?  # Capture offline instances (until period or comma, optional)
    \s*Time:\s(?P<time>\d+)m  # Capture time in minutes
    \s*Packs:\s(?P<packs>\d+)  # Capture number of packs
""", re.VERBOSE | re.DOTALL)

async def setup(bot):
    @bot.event
    async def on_message(message):
        if int(message.channel.id) != int(MONITOR_ID):
            return

        match = message_pattern.search(message.content)
        if not match:
            return

        # Extract and normalize Discord ID
        raw_discord_id = match.group('discord_id')
        discord_id = raw_discord_id.split('-')[0] if '-' in raw_discord_id else raw_discord_id


        # Extract other details
        online_raw = match.group('online')
        offline_raw = match.group('offline')
        time = int(match.group('time'))
        packs = int(match.group('packs'))

        # Normalize "none." to 0 instances
        online = len(re.findall(r'\d+', online_raw)) if "none" not in online_raw.lower() else 0
        offline = len(re.findall(r'\d+', offline_raw)) if "none" not in offline_raw.lower() else 0

        # Create new session data
        new_entry = {
            "Online": online,
            "Offline": offline,
            "Time": time,
            "Packs": packs,
            "Timestamp": int(message.created_at.timestamp()),
        }
        # Calculate PPH
        pph = 0 if time == 0 else calculate_difference(discord_id, 'Packs', packs, firebase_db) * 2
        update_rerolling_user(discord_id, online, offline, time, packs, pph)

        # Fetch or create user data in Firebase
        user_ref = firebase_db.child('users').child(discord_id)
        user_data = user_ref.get()

        if user_data:
            current_data = user_data
            history = current_data.get('history', [])

            # Calculate total stats
            time_difference = calculate_difference(discord_id, 'Time', time, firebase_db)
            packs_difference = calculate_difference(discord_id, 'Packs', packs, firebase_db)

            history.insert(0, new_entry)  # Add new entry to history

            total_time = current_data.get('total_time', 0) + (time_difference if time > 0 else 0)
            total_packs = current_data.get('total_packs', 0) + (packs_difference if packs > 0 else 0)

            # Update Firebase
            user_ref.update({
                'history': history,
                'total_time': total_time,
                'total_packs': total_packs
            })
        else:
            # New user entry
            user_ref.update({
                'history': [new_entry],
                'total_time': time if time > 0 else 0,
                'total_packs': packs if packs > 0 else 0
            })

        # Update the reroller list message
        send_message_list = bot.get_cog("SendMessageList")
        if send_message_list:
            await send_message_list.check_users()
        else:
            logger.warning("⚠️ SendMessageList cog not found!")

        await bot.process_commands(message)
