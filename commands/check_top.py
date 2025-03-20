import discord
import json
from discord import app_commands
from discord.ext import commands
from firebase_admin import db

# Load roles from roles.json
with open("roles.json", "r") as f:
    ROLES = json.load(f)

# Ensure all role IDs are stored as strings
REROLLER_ROLE_IDS = {str(role_id) for role_id in ROLES.get("rerollers", [])}  

class TopPacksLeaderboard(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="check_top", description="View the top 15 users with the most total packs.")
    async def check_top(self, interaction: discord.Interaction):
        user_id = str(interaction.user.id)  # Convert user ID to string
        user_roles = {str(role.id) for role in interaction.user.roles} 

        # Check if user has any of the allowed reroller roles
        if not user_roles.intersection(REROLLER_ROLE_IDS):
            await interaction.response.send_message("❌ You don't have permission to use this command.", ephemeral=True)
            return

        # Fetch all users from Firebase
        users_ref = db.reference().child('users')
        users_data = users_ref.get()

        if not users_data:
            await interaction.response.send_message("No user data available.", ephemeral=True)
            return

        # Sort users by total_packs in descending order and get the top 10
        sorted_users = sorted(
            users_data.items(),
            key=lambda item: item[1].get("total_packs", 0),
            reverse=True
        )[:15]

        if not sorted_users:
            await interaction.response.send_message("No users have collected any packs.", ephemeral=True)
            return

        # Format leaderboard message
        embed = discord.Embed(title="🏆 Top 15 Users by Total Packs", color=discord.Color.purple())
        rank_emojis = ["🥇", "🥈", "🥉"]

        leaderboard_text = ""
        for index, (user_id, user_data) in enumerate(sorted_users):
            total_packs = user_data.get("total_packs", 0)
            rank = rank_emojis[index] if index < 3 else f"{index + 1}."
            leaderboard_text += f"{rank} <@{user_id}> - `{total_packs}` packs\n"

        embed.description = leaderboard_text

        await interaction.response.send_message(embed=embed, ephemeral=False)

async def setup(bot):
    await bot.add_cog(TopPacksLeaderboard(bot))
