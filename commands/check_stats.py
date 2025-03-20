import discord
import logging
from discord import app_commands
from discord.ext import commands
from firebase_admin import db
from helper.get_current_session import get_current_session
from helper.get_longest_session import get_longest_session

# Set up logging
logging.basicConfig(level=logging.INFO)  # Change to DEBUG if needed
logger = logging.getLogger(__name__)

class PersonalStats(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        print("✅ check_stats.py loaded successfully!")

    @app_commands.command(name="my_stats", description="Check your personal session stats.")
    async def my_stats(self, interaction: discord.Interaction):
        """Fetch and display user stats."""
        try:
            discord_id = str(interaction.user.id)
            print(f"🔍 Fetching stats for user: {interaction.user.display_name} ({discord_id})")

            # Ensure Firebase is initialized
            if not db.reference():
                raise RuntimeError("Firebase database is not initialized!")

            # Get current session
            current_session = get_current_session(discord_id, db.reference()) or "No data available."

            # Get longest session
            longest_session = get_longest_session(discord_id, db.reference()) or "No data available."

            # Fetch total packs and total time
            user_ref = db.reference().child('users').child(discord_id)
            user_data = user_ref.get()

            if not user_data:
                print(f"❌ No data found for {interaction.user.display_name} in the database.")
                await interaction.response.send_message("❌ No data found for you in the database.", ephemeral=True)
                return

            total_packs = user_data.get("total_packs", 0)
            total_time = user_data.get("total_time", 0)
            pack_tests = user_data.get("test", 0)

            # Format response
            embed = discord.Embed(title=f"📊 Stats for {interaction.user.display_name}", color=discord.Color.blue())
            embed.add_field(name="⏱ Current Session", value=current_session, inline=True)
            embed.add_field(name="🏆 Longest Session", value=longest_session, inline=True)
            embed.add_field(name="\u200b", value="\u200b", inline=False)  # Spacer for better formatting
            embed.add_field(name="📦 Total Packs", value=f"`{total_packs}`", inline=True)
            embed.add_field(name="⏳ Total Time", value=f"`{total_time} minutes`", inline=True)
            embed.add_field(name="🧪 Pack Tests", value=f"`{pack_tests}`", inline=True)

            await interaction.response.send_message(embed=embed, ephemeral=False)

        except Exception as e:
            logger.error(f"❌ Error in /my_stats command: {e}", exc_info=True)
            await interaction.response.send_message("⚠️ An error occurred while fetching your stats. Please try again later.", ephemeral=True)

async def setup(bot):
    try:
        await bot.add_cog(PersonalStats(bot))
    except Exception as e:
        print(f"❌ Error adding PersonalStats cog: {e}")
