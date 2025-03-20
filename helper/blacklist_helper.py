import flags
import discord_variables
import discord

async def blacklist_helper(bot, discord_id: int, message: str):
    """Handles blacklisting of a user and sends a message to the bot spam channel only work with Live Bot."""

    # Check if blacklisting is disabled or if the user is whitelisted
    if not getattr(flags, "BLACKLIST", True) or discord_id in getattr(flags, "WHITELIST", []):
        return

    # Construct the blacklist message
    blacklist_message = f"{getattr(discord_variables, 'BLACKLIST_COMMAND', None)} {discord_id} {message}"

    # Get the bot spam channel ID and convert it to an integer
    try:
        bot_spam_channel_id = int(getattr(discord_variables, "BOT_SPAM", 0))
    except ValueError:
        print("⚠️ Error: BOT_SPAM channel ID is invalid in discord_variables.")
        return

    if not bot_spam_channel_id:
        print("⚠️ Error: BOT_SPAM channel ID is not set in discord_variables.")
        return

    bot_spam_channel = bot.get_channel(bot_spam_channel_id)
    
    if not bot_spam_channel:
        print(f"❌ Error: Could not find BOT_SPAM channel ({bot_spam_channel_id}).")
        return

    # Send the blacklist message
    try:
        await bot_spam_channel.send(blacklist_message)
    except discord.errors.HTTPException as e:
        print(f"❌ Error sending blacklist message: {e}")
