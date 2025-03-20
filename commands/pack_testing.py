import discord
import json
import logging
from discord.ext import commands
from firebase import update_test_count
from discord_variables import SPECIFIC_EMOJI, SUCCESS_EMOJI

# Load moderator roles from roles.json
with open("roles.json", "r") as f:
    roles_data = json.load(f)
MOD_ROLES = {int(role_id) for role_id in roles_data["mods"]}

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("PackTesting")

class PackTesting(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def send_error_message(self, channel, error_message):
        """Send an error message to the channel."""
        try:
            await channel.send(f"⚠️ **Error:** {error_message}")
        except discord.Forbidden:
            logger.error("⛔ Bot lacks permission to send messages in this channel.")

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        """Triggered when a reaction is added."""
        if user.bot or str(reaction.emoji) != SPECIFIC_EMOJI:
            return

        # Fetch member to check roles
        try:
            member = await reaction.message.guild.fetch_member(user.id)
        except (discord.NotFound, discord.Forbidden):
            return

        # Check if user has a moderator role
        if not any(role.id in MOD_ROLES for role in member.roles):
            return

        # Add SUCCESS_EMOJI reaction
        try:
            await reaction.message.add_reaction(SUCCESS_EMOJI)
        except discord.Forbidden:
            logger.error("⛔ Bot lacks permission to add reactions.")
            await self.send_error_message(reaction.message.channel, "I don't have permission to add reactions.")

        # Update Firebase test count
        update_test_count(str(reaction.message.author.id), 1)

    @commands.Cog.listener()
    async def on_reaction_remove(self, reaction, user):
        """Triggered when a reaction is removed."""
        if str(reaction.emoji) != SPECIFIC_EMOJI:
            return

        # Fetch member to check roles
        try:
            member = await reaction.message.guild.fetch_member(user.id)
        except (discord.NotFound, discord.Forbidden):
            return

        # Check if user has a moderator role
        if not any(role.id in MOD_ROLES for role in member.roles):
            return

        # Update Firebase test count
        update_test_count(str(reaction.message.author.id), -1)

        # Remove SUCCESS_EMOJI reaction
        try:
            await reaction.message.remove_reaction(SUCCESS_EMOJI, self.bot.user)
        except discord.Forbidden:
            logger.error("⛔ Bot lacks permission to remove reactions.")
            await self.send_error_message(reaction.message.channel, "I don't have permission to remove reactions.")

async def setup(bot):
    """Asynchronous setup function to add the cog."""
    await bot.add_cog(PackTesting(bot))
