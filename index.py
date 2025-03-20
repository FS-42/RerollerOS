import discord
from discord.ext import commands
from discord_variables import DISCORD_TOKEN
import os
import asyncio

# Set up intents
intents = discord.Intents.default()
intents.message_content = True
intents.reactions = True
intents.guilds = True
intents.members = True

# Initialize the bot
bot = commands.Bot(command_prefix="!", intents=intents)

async def load_cogs():
    """Loads all command cogs from the commands folder."""
    for filename in os.listdir('./commands'):
        if filename.endswith('.py'):
            try:
                await bot.load_extension(f'commands.{filename[:-3]}')
                print(f"✅ Successfully loaded {filename}")
            except Exception as e:
                print(f"❌ Error loading {filename}: {e}")

@bot.event
async def on_ready():
    """Runs when the bot connects to Discord."""
    print("🔥 on_ready() event fired!")  # Debugging print
    print(f'✅ Logged in as {bot.user} (ID: {bot.user.id})')
    print(f'🌍 Connected to {len(bot.guilds)} servers')

    # Sync global slash commands
    try:
        await bot.tree.sync()
        print("✅ Slash commands synced globally")
    except Exception as e:
        print(f"❌ Error syncing slash commands: {e}")

    # Debugging: Show loaded cogs
    print(f"🛠️ Loaded cogs: {list(bot.cogs.keys())}")

@bot.command()
async def check_perms(ctx):
    """Checks the bot's permissions in the current channel."""
    perms = ctx.channel.permissions_for(ctx.guild.me)
    
    perm_message = (
        f"🔍 **Bot Permissions in {ctx.channel.mention}**\n"
        f"✅ Read Messages: {perms.read_messages}\n"
        f"✅ Send Messages: {perms.send_messages}\n"
        f"✅ Add Reactions: {perms.add_reactions}\n"
        f"✅ Manage Messages: {perms.manage_messages}\n"
        f"✅ Read Message History: {perms.read_message_history}\n"
    )
    
    await ctx.send(perm_message)

@bot.command()
async def sync(ctx):
    """Manually syncs slash commands (use this if commands are not showing)."""
    await bot.tree.sync()
    await ctx.send("✅ Slash commands synced!")

async def main():
    """Handles bot startup properly with async."""
    print("🔄 Starting bot...")
    
    # Debugging: Check if token is loaded
    if not DISCORD_TOKEN:
        print("❌ ERROR: DISCORD_TOKEN is missing!")
        return
    
    async with bot:
        await load_cogs()
        await bot.start(DISCORD_TOKEN)

# Ensure proper bot startup
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("❌ Bot manually stopped.")
    except Exception as e:
        print(f"❌ Fatal error: {e}")
