import discord
import json
from discord import app_commands
from discord.ext import commands
from firebase_admin import db

# Load roles from roles.json
with open("roles.json", "r") as f:
    ROLES = json.load(f)

# Ensure all role IDs are stored as strings
MOD_ROLE_IDS = {str(role_id) for role_id in ROLES.get("rerollers", [])}  

class TesterLeaderboard(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="check_testers", description="View the leaderboard for test counts.")
    async def check_testers(self, interaction: discord.Interaction):
        user_id = str(interaction.user.id)  
        user_roles = {str(role.id) for role in interaction.user.roles}  

        # Check if user has any of the allowed mod roles
        if not user_roles.intersection(MOD_ROLE_IDS):
            await interaction.response.send_message("❌ You don't have permission to use this command.", ephemeral=True)
            return

        # Fetch all users from Firebase
        users_ref = db.reference().child('users')
        users_data = users_ref.get()

        if not users_data:
            await interaction.response.send_message("No user data available.", ephemeral=True)
            return

        # Filter users who have at least 1 test and sort them in descending order
        valid_users = [(user_id, data.get("test", 0)) for user_id, data in users_data.items() if data.get("test", 0) > 0]
        sorted_users = sorted(valid_users, key=lambda item: item[1], reverse=True)

        if not sorted_users:
            await interaction.response.send_message("No users have conducted any tests.", ephemeral=True)
            return

        # Format leaderboard message
        embed = discord.Embed(title="🏆 Testers Leaderboard", color=discord.Color.gold())
        rank_emojis = ["🥇", "🥈", "🥉"]  # Only top 3 get emojis

        leaderboard_text = ""
        for index, (user_id, test_count) in enumerate(sorted_users):
            rank = rank_emojis[index] if index < 3 else f"{index + 1}."
            leaderboard_text += f"{rank} <@{user_id}> - `{test_count}`\n"

        embed.description = leaderboard_text

        await interaction.response.send_message(embed=embed, ephemeral=False)

async def setup(bot):
    await bot.add_cog(TesterLeaderboard(bot))
