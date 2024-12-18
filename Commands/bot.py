# Standard library imports
import asyncio
import os

# Third-party imports
import discord
from discord.ext import commands

# Config imports
from Config.config import conf
from Config.logging import setup_logging

# Load the .env file
from dotenv import load_dotenv
load_dotenv()

# Create a logger for this file
logger = setup_logging("bot.py", conf.LOGS_PATH)

# Create a bot instance
bot = commands.Bot(command_prefix='/', intents=discord.Intents.all())

async def load_cogs():
    """Load all command cogs."""
    cogs = [
        "Commands.events",
        "Commands.Music.music_cog",
        "Commands.Economy.economy_cog",
        "Commands.Games.games_cog",
        "Commands.Information.information_cog",]
    for cog in cogs:
        try:
            await bot.load_extension(cog)
        except Exception as e:
            logger.error(f"Error loading cog {cog}: {e}")
            raise e

async def run_bot():
    try:
        
        token = os.environ.get("DISCORD_TOKEN")
        if not token:
            raise Exception("DISCORD_TOKEN not found in environment variables.")
        await load_cogs()
        await bot.start(token)

    except Exception as e:
        logger.error(f"Error in run_bot function: {e}")
        raise e

def main():
    try:
        asyncio.run(run_bot()) 
    except KeyboardInterrupt:
        print("\nBot stopped by user.")
    except Exception as e:
        logger.error(f"Error in main function: {e}")