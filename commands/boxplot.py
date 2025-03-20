import discord
import json
from discord.ext import commands
from discord import app_commands
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import os

from firebase import get_user_history
from user_dict import discord_friends

# Merge specific users under one name, FILL THIS IN IF MULTI PC USERS
MERGE_USERS = {""}

# Load roles from roles.json
with open("roles.json", "r") as f:
    ROLES = json.load(f)

MOD_ROLE_IDS = {str(role_id) for role_id in ROLES.get("mods", [])}

class BoxPlotCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="boxplot", description="Generates a boxplot for the top users in the past X days.")
    async def boxplot(self, interaction: discord.Interaction, time_range_days: int):
        """Generates and sends a boxplot for the top users in the past X days."""
        await interaction.response.defer() 
        user_id = str(interaction.user.id)  
        user_roles = {str(role.id) for role in interaction.user.roles}  

        # Check if user has any of the allowed mod roles
        if not user_roles.intersection(MOD_ROLE_IDS):
            await interaction.followup.send("❌ You don't have permission to use this command.", ephemeral=True)
            return

        # Fetch history data
        user_data = get_user_history(time_range_days)

        processed_data = {}

        for user_id, history in user_data.items():
            username = discord_friends.get(user_id, user_id)  # Fallback to ID if name is missing
            pph = [entry["Packs"] / (entry["Time"] / 60) for entry in history if entry["Time"] > 0]

            if pph:
                if user_id in MERGE_USERS:
                    processed_data.setdefault("LukedIn", []).extend(pph)
                else:
                    processed_data[username] = pph

        if not processed_data:
            await interaction.followup.send("No valid data available for this time range.")
            return

        # Sort users by the mean PPH (Packs per Hour) in descending order
        sorted_data = sorted(processed_data.items(), key=lambda x: np.mean(x[1]), reverse=True)
        sorted_users, sorted_pph = zip(*sorted_data)

        
        plt.figure(figsize=(12, 6))
        sns.boxplot(data=sorted_pph, showfliers=False, palette="turbo")

        # Add vertical lines for each boxplot with offset (thinner and no overlap)
        for i in range(len(sorted_users)):
            # Adjust the vertical line position slightly to avoid overlapping with boxes
            plt.axvline(x=i, color='black', linestyle='-', lw=0.25)

        # Adjust x-ticks and rotation for better spacing
        plt.xticks(range(len(sorted_users)), sorted_users, rotation=45, ha="right")

        # Add grid for better readability
        plt.grid(True, axis="y", linestyle="--", alpha=0.7)

        # Add labels and title
        plt.ylabel("Packs Per Hour (PPH)")
        plt.title(f"PPH Distribution (Last {time_range_days} Days)")

        # Save the plot
        image_path = "pph_boxplot.png"
        plt.tight_layout()
        plt.savefig(image_path)
        plt.close()

        # Send the image
        await interaction.followup.send(file=discord.File(image_path))

        # Clean up
        os.remove(image_path)

async def setup(bot):
    await bot.add_cog(BoxPlotCog(bot))
