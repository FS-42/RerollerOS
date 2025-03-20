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


# Load roles from roles.json
with open("roles.json", "r") as f:
    ROLES = json.load(f)

# Ensure all role IDs are stored as strings
MOD_ROLE_IDS = {str(role_id) for role_id in ROLES.get("mods", [])}

class DensityPlotCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="density", description="Generates a density plot for the top users in the past X days.")
    async def density(self, interaction: discord.Interaction, time_range_days: int):
        """Generates and sends a density plot for the top users in the past X days."""
        await interaction.response.defer() 
        user_id = str(interaction.user.id)
        user_roles = {str(role.id) for role in interaction.user.roles}

        # Check if user has any of the allowed mod roles
        if not user_roles.intersection(MOD_ROLE_IDS):
            await interaction.response.send_message("❌ You don't have permission to use this command.", ephemeral=True)
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

        # Create a list of all PPH values for the density plot
        all_pph = [pph for user_pph in sorted_pph for pph in user_pph]

        # Plot the density plot
        plt.figure(figsize=(10, 6))
        sns.kdeplot(all_pph, fill=True, color='blue', alpha=0.5)

        # Add grid, labels, and title
        plt.xlabel('Packs per Hour')
        plt.ylabel('Density')
        plt.title(f'Density Plot of Packs per Hour (Last {time_range_days} Days)')
        plt.grid(True)

        # Save the plot
        image_path = "pph_density_plot.png"
        plt.tight_layout()  # Ensure proper spacing
        plt.savefig(image_path)
        plt.close()

        # Send the image
        await interaction.followup.send(file=discord.File(image_path))

        # Clean up
        os.remove(image_path)

async def setup(bot):
    await bot.add_cog(DensityPlotCog(bot))
