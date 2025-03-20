import time
import discord
from discord.ext import tasks, commands
from firebase import firebase_db, remove_rerolling_user
from helper.create_reroller_list import create_reroller_list

CHECK_INTERVAL = 60
INACTIVITY_LIMIT = 1850  # Remove users inactive for more than 30 minutes and 50 seconds

class SendMessageList(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.check_users.start()

    def cog_unload(self):
        self.check_users.cancel()

    @tasks.loop(seconds=CHECK_INTERVAL)
    async def check_users(self):
        
        current_time = int(time.time())
        rerolling_users = firebase_db.child("rerollingUsers").get() or {}

        # Remove users who have been inactive for more than 30 minutes and 50 seconds
        for discord_id, data in list(rerolling_users.items()):
            timestamp = data.get("Timestamp", 0)
            if current_time - timestamp > INACTIVITY_LIMIT:
                print(f"Removing inactive user: {discord_id}")
                remove_rerolling_user(discord_id)

        # Call create_reroller_list to update the message
        await create_reroller_list(self.bot)  # 🔹 Pass the bot instance

    @check_users.before_loop
    async def before_check_users(self):
        await self.bot.wait_until_ready()

async def setup(bot):
    await bot.add_cog(SendMessageList(bot))
