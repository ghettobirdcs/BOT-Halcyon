"""
Bot Halcyon - CS2 League Discord Bot
Main bot initialization and setup
"""

import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
import config

# Load environment variables from .env file
load_dotenv()

# Get bot token from environment
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')

if not DISCORD_TOKEN:
    raise ValueError("DISCORD_TOKEN not found in .env file")

# Set up bot intents
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True

# Initialize bot with slash command support
bot = commands.Bot(
    command_prefix=config.BOT_PREFIX,
    intents=intents,
    help_command=None  # Disable default help command if using slash commands
)

# Bot event handlers
@bot.event
async def on_ready():
    """Called when the bot has successfully connected to Discord"""
    print(f'\n{bot.user} is now running!')
    print(f'Bot ID: {bot.user.id}')  # pyright: ignore
    print(f'Discord.py version: {discord.__version__}')
    print(f'Syncing slash commands...\n')
    try:
        synced = await bot.tree.sync()
        print(f'Synced {len(synced)} command(s)')
    except Exception as e:
        print(f'Failed to sync commands: {e}')

@bot.event
async def on_error(event, *args, **kwargs):
    """Error handler for bot events"""
    print(f'Error in {event}:', args, kwargs)

# Load cogs (command modules)
async def load_cogs():
    """Load all cog modules from the cogs directory"""
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py') and not filename.startswith('__'):
            try:
                await bot.load_extension(f'cogs.{filename[:-3]}')
                print(f'Loaded cog: {filename[:-3]}')
            except Exception as e:
                print(f'Failed to load cog {filename}: {e}')

# Run the bot
async def main():
    """Main entry point for the bot"""
    print('Starting Bot Halcyon...')
    await load_cogs()
    await bot.start(DISCORD_TOKEN)  # pyright: ignore

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
