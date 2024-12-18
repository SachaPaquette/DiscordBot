# Standard library imports
import asyncio
import os

# Third-party imports
import discord
from discord.ext import commands

# Commands import
from Commands.Economy.balance_command import Balance
from Commands.Games.blackjack_command import BlackJack
from Commands.Games.case_command import Case
from Commands.Games.capsule_command import Capsule
from Commands.Games.coinflip_command import CoinFlip
from Commands.Games.gambling_command import Gambling
from Commands.Economy.give_command import Give
from Commands.Information.health_command import HealthCheck
from Commands.Inventory.inventory_command import Inventory
from Commands.Inventory.leaderboard_command import Leaderboard
from Commands.Information.link_message_event import LinkMessage
from Commands.Music.lyrics_command import LyricsOperations
from Commands.Music.music import SongSession
from Commands.Music.nowplaying_command import NowPlaying
from Commands.Economy.portfolio_command import Portfolio
from Commands.Profanity.profanity_event import Profanity
from Commands.Music.queue_command import QueueOperations
from Commands.Games.roll_command import Roll
from Commands.Games.rockpaperscissors_command import RockPaperScissors, Choices
from Commands.Economy.stocks_command import Stocks, Options
from Commands.Information.user_info_command import UserInfo
from Commands.Services.utility import Utility, EmbedMessage, VoiceManager
from Commands.Economy.work_command import Work

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

# Create an instance of Utility to handle utility functions
utility = Utility()

voice_manager = VoiceManager()
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





@bot.tree.command(name='leave', description='Makes the bot leave the voice channel.')
async def leave(interactions):
    try:
        await voice_manager.leave(interactions)
    except Exception as e:
        logger.error(f"Error in the leave command: {e}")
        raise e


@bot.tree.command(name='ping', description='Pings a user.')
async def ping(interactions, username: discord.User):
    try:
        await interactions.response.send_message(f"Hello {username.mention}")
    except Exception as e:
        logger.error(f"Error in the ping command: {e}")
        raise e

@bot.tree.command(name="stocks", description="Buy or sell stocks.")
async def stocks(interactions, option: Options, stock: str, quantity: float):
    """
    Buy or sell stocks.

    Parameters:
    - interactions (Context): The context object representing the invocation context of the command.
    - option (Options): The option to buy or sell stocks.
    - stock (str): The stock to buy or sell.
    - quantity (int): The quantity of stocks to buy or sell.

    Returns:
    - None
    """
    try:
        stocks = Stocks()
        await stocks.stocks_command(interactions, option, stock, quantity)
    except Exception as e:
        logger.error(f"Error in the stocks command: {e}")
        raise e


@bot.tree.command(name='portfolio', description='Display your stock portfolio.')
async def portfolio(interactions):
    """
    Display the user's stock portfolio.

    Parameters:
    - interactions (Context): The context object representing the invocation context of the command.

    Returns:
    - None
    """
    try:
        portfolio = Portfolio()
        await portfolio.portfolio_command(interactions)
    except Exception as e:
        logger.error(f"Error in the portfolio command: {e}")
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

