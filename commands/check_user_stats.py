import discord
import json
import logging
from discord import app_commands
from discord.ext import commands
from firebase_admin import db
from helper.get_current_session import get_current_session
from helper.get_longest_session import get_longest_session

# Set up logging
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

# Load roles from roles.json
with open("roles.json", "r") as f:
    ROLES = json.load(f)

# Ensure all role IDs are stored as strings
MOD_ROLE_IDS = {str(role_id) for role_id in ROLES.get("mods", [])}

class Stats(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="check_user", description="Check session stats for another user.")
    @app_commands.describe(user="The user to check stats for.")
    async def check_user(self, interaction: discord.Interaction, user: discord.Member):
        user_id = str(interaction.user.id)  
        user_roles = {str(role.id) for role in interaction.user.roles} 

        # Check if user has any of the allowed mod roles
        if not user_roles.intersection(MOD_ROLE_IDS):
            await interaction.response.send_message("❌ You don't have permission to use this command.", ephemeral=True)
            return

        try:
            discord_id = str(user.id) 
            display_name = user.display_name 

            # Get current session
            current_session = get_current_session(discord_id, db.reference()) or "No data available."

            # Get longest session
            longest_session = get_longest_session(discord_id, db.reference()) or "No data available."

            # Fetch total packs and total time
            user_ref = db.reference().child('users').child(discord_id)
            user_data = user_ref.get()

            total_packs = user_data.get("total_packs", 0) if user_data else 0
            total_time = user_data.get("total_time", 0) if user_data else 0
            pack_tests = user_data.get("test", 0) if user_data else 0

            # Format response
            embed = discord.Embed(title=f"📊 Stats for {display_name}", color=discord.Color.gold())
            
            # First row
            embed.add_field(name="⏱ Current Session", value=current_session, inline=True)
            embed.add_field(name="\u200b", value="\u200b", inline=True)
            embed.add_field(name="🏆 Longest Session", value=longest_session, inline=True)
            # Second row
            embed.add_field(name="\u200b", value="\u200b", inline=False)  # Spacer to create new row
            embed.add_field(name="📦 Total Packs", value=f"`{total_packs}`", inline=True)
            embed.add_field(name="⏳ Total Time", value=f"`{total_time} minutes`", inline=True)
            embed.add_field(name="🧪 Pack Tests", value=f"`{pack_tests}`", inline=True)

            await interaction.response.send_message(embed=embed, ephemeral=False)

        except Exception as e:
            logger.error(f"Error in /check_user command: {e}", exc_info=True)
            await interaction.response.send_message("⚠️ An error occurred while fetching user stats. Please try again later.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Stats(bot))
