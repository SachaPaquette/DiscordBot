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
from Commands.Economy.finances import Finance
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
from Commands.Services.utility import Utility, EmbedMessage
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


@bot.event
async def on_ready():
    """
    Event handler that is triggered when the bot is ready.

    This function prints the bot's name and ID to the console.
    """
    try:
        await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name="depression"))
        guild = discord.Object(id=os.environ.get("TESTING_GUILD_ID"))
        # Instant sync to the testing guild
        bot.tree.copy_global_to(guild=guild)
        await bot.tree.sync(guild=guild)
        print(f'{bot.user} has connected to Discord!')
    except Exception as e:
        logger.error(f"Error in the on ready event: {e}")
        raise e


@bot.event
async def on_message(message):
    """
    Event handler for incoming messages.

    Parameters:
    - message: The message object representing the incoming message.

    Returns:
    - None

    Raises:
    - Exception: If an error occurs while processing the message.
    """
    try:
        # Ignore messages sent by the bot
        if message.author == bot.user:
            return

        # Create an instance of LinkMessage to handle messages that contain URLs
        #linkmessage = LinkMessage(bot)
        # Fetch the domain information from the message url and send it as a message
        #await linkmessage.on_message_command(message)

        profanity = Profanity(bot)
        # Check for profanity in the message
        await profanity.on_message_command(message)
    except Exception as e:
        logger.error(f"Error in the on message event: {e}")
        raise e


@bot.event
async def on_member_join(member):
    """
    Event handler that is triggered when a member joins the server.

    This function sends a welcome message to the member.

    Parameters:
    - member (discord.Member): The member that joined the server.

    Returns:
    None

    Raises:
    Exception: If an error occurs while sending the welcome message.
    """
    try:
        embed_message = EmbedMessage()
        channel = discord.utils.get(member.guild.text_channels, name=os.environ.get("GENERAL_CHANNEL_NAME"))
        if channel:
            await channel.send(embed=await embed_message.on_member_join_message(member))
        else:
            logger.error(f"General channel not found: {os.environ.get('GENERAL_CHANNEL_NAME')}")
    except Exception as e:
        logger.error(f"Error sending welcome message: {e}")


@bot.event
async def on_member_remove(member):
    """
    Event handler that is triggered when a member leaves the server.

    This function sends a goodbye message to the member.

    Parameters:
    - member (discord.Member): The member that left the server.

    Returns:
    None

    Raises:
    Exception: If an error occurs while sending the goodbye message.
    """
    try:
        embed_message = EmbedMessage()
        channel = discord.utils.get(member.guild.text_channels, name=os.environ.get("GENERAL_CHANNEL_NAME"))
        if channel:
            await channel.send(embed=await embed_message.on_member_leave_message(member))
        else:
            logger.error(f"General channel not found: {os.environ.get('GENERAL_CHANNEL_NAME')}")
    except Exception as e:
        logger.error(f"Error sending goodbye message: {e}")


@bot.tree.command(name='health', description='Display information about the bot.')
@commands.has_permissions(administrator=True)
async def health(interactions):
    """
    Check if the bot is alive and provide detailed health information.
    Used to sync the commands with the guild.
    """
    # Make sure the user has the correct permissions (by having the userid of the bot owner)
    if interactions.user.id != int(os.environ.get("BOT_OWNER_ID")):
        await interactions.response.send_message("You do not have permission to run this command.")
        return

    try:
        health_check = HealthCheck(bot)
        await health_check.health_command(interactions, bot)
        await bot.tree.sync()
    except Exception as e:
        print(f"Error in the health command: {e}")
        raise e


@bot.tree.command(name='join', description='Join the voice channel.')
async def join(interactions: discord.Interaction):
    """
    This command makes the bot join the voice channel of the user who sent the command.
    """
    try:
        await utility.join(interactions)
    except Exception as e:
        logger.error(
            f"An error occurred when trying to join the channel. {e}")
        raise e


@bot.tree.command(name='leave', description='Makes the bot leave the voice channel.')
async def leave(interactions):
    try:
        await utility.leave(interactions)
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


@bot.tree.command(name='skip', description='Skip the current song.')
async def skip(interactions):
    try:
        session = SongSession(interactions.guild, interactions)
        await session.skip(interactions)
    except Exception as e:
        logger.error(f"Error in the skip command: {e}")
        raise e


@bot.tree.command(name='play', description='Play a song.')
async def play(interactions, url: str):
    """
    Play a song.

    Parameters:
    - interactions (discord.ext.commands.Context): The context of the command.
    - url (str): The URL of the song to be played.

    Returns:
    None
    """
    try:
        global session
        # Get or create the singleton instance of SongSession
        session = SongSession(interactions.guild, interactions)

        # Call the play command on the session instance
        await session.play_command(interactions, url, bot.loop)

    except Exception as e:
        logger.error(f"An error occurred when trying to play the song. {e}")
        await interactions.response.send_message("An error occurred while processing your request.")
        raise e


@bot.tree.command(name='nowplaying', description='Display the current playing song.')
async def nowplaying(interactions):
    if utility.bot_check_session(session):
        try:
            playing_operations = NowPlaying()
            await playing_operations.nowplaying_command(interactions, session)
        except Exception as e:
            logger.error(
                f"An error occurred when trying to display the song. {e}")
            raise e
    else:
        await interactions.response.send_message("No song is currently playing.")


@bot.tree.command(name='lyrics', description='Display the lyrics of the current song.')
async def lyrics(interactions):
    if utility.bot_check_session(session):
        try:
            lyrics_operations = LyricsOperations(bot)
            await lyrics_operations.lyrics_command(interactions, session)
        except Exception as e:
            logger.error(
                f"An error occurred when trying to display the lyrics. {e}")
            raise e
    else:
        await interactions.response.send_message("No song is currently playing.")


@bot.tree.command(name='queue', description='Display the queue.')
async def queue(interactions):
    """
    Display the queue.

    This command displays the current queue of songs in the bot's session.

    Parameters:
    - interactions (Context): The context object representing the invocation context of the command.

    Returns:
    None
    """
    try:
        queue_operations = QueueOperations(session)
        # Call the queue function in QueueOperations
        await queue_operations.display_queue_command(interactions, discord)
    except Exception as e:
        logger.error(
            f"An error occurred when trying to display the queue. {e}")
        raise e


@bot.tree.command(name="clear", description="Clear the music queue.")
async def clear(interactions):
    """
    This command clears the queue. It checks if the bot is currently playing music and if there are songs in the queue before calling the clear function from queue operations. 

    Parameters:
    - interactions (Context): The context object representing the invocation context of the command.

    Returns:
    None
    """
    try:
        queue_operations = QueueOperations(session)
        queue_operations.clear_command(interactions)
    except Exception as e:
        logger.error(
            f"An error occurred when trying to clear the queue. {e}")
        raise e


@bot.tree.command(name='pause', description='Pause the current song.')
async def pause(interactions):
    """
    Pauses the current song.

    Parameters:
    - interactions (Context): The context of the command.

    Returns:
    None
    """
    if utility.bot_check_session(session):
        try:
            await session.pause_command(interactions)
        except Exception as e:
            logger.error(
                f"An error occurred when trying to pause the song. {e}")
            raise e
    else:
        await interactions.response.send_message("No song is currently playing.")


@bot.tree.command(name='resume', description='Resume the current song.')
async def resume(interactions):
    """
    Resumes the current song.

    This command is used to resume the current song if it is paused.
    If there is no music currently paused, it will display a message indicating that.
    If an error occurs while trying to resume the song, it will display an error message.

    Parameters:
    - interactions (Context): The context object representing the invocation context of the command.

    Returns:
    - None
    """
    if utility.bot_check_session(session):
        try:
            await session.resume_command(interactions)
        except Exception as e:
            logger.error(
                f"An error occurred when trying to resume the song. {e}")
            raise e
    else:
        await interactions.response.send_message("No song is currently paused.")


@bot.tree.command(name='shuffle', description='Shuffle the queue.')
async def shuffle(interactions):
    """
    Shuffles the queue.

    This command shuffles the songs in the queue if the conditions are met. It checks if the bot is currently playing music and if there are songs in the queue.

    Parameters:
    - interactions (Context): The context object representing the invocation context of the command.

    Raises:
    - Exception: If an error occurs while shuffling the queue.

    Returns:
    - None
    """
    try:
        queue_operations = QueueOperations(session)
        # Call the queue shuffle function in QueueOperations
        await queue_operations.shuffle_queue_command(interactions)
    except Exception as e:
        logger.error(f"Error in the shuffle command: {e}")
        raise e


@bot.tree.command(name='volume', description="Change the music's volume.")
async def volume(interactions, volume: int):
    """
    Change the volume.

    This command changes the volume of the bot if the conditions are met. It checks if the bot is currently playing music and if the volume is between 0 and 100.

    Parameters:
    - interactions (Context): The context object representing the invocation context of the command.
    - volume (int): The volume to set the bot to.

    Raises:
    - Exception: If an error occurs while changing the volume.

    Returns:
    - None
    """
    if utility.bot_check_session(session):
        try:
            # Call the change volume function in SongSession
            await session.change_volume(volume, interactions)
        except Exception as e:
            logger.error(f"Error in the volume command: {e}")
            raise e
    else:
        await interactions.response.send_message("No song is currently playing.")


@bot.tree.command(name="userinfo", description="Get information about a user.")
async def user_information(interactions, *, member: discord.Member = None):
    """
    Fetches and displays information about a user.

    Parameters:
    - interactions (discord.Context): The context of the command.
    - member (discord.Member, optional): The member to fetch information about. Defaults to None.

    Raises:
    - Exception: If there is an error in fetching the user information.

    Examples:
    ` /userinfo @user -> 
        User Information - Chencho
        Username
        discordusername
        User ID
        0000000000
        Joined Server On
        2017-02-26 20:37:34
        Account Created On
        2017-02-18 04:04:35 `

    Returns:
    - None
    """
    try:
        user_info = UserInfo()
        # Create the embed message that will display the user information (username, ID, join date, account creation date)
        await user_info.fetch_user_information(interactions=interactions, member=member)
    except Exception as e:
        logger.error(f"Error in the user info command: {e}")
        raise e


@bot.tree.command(name='gamble', description='Gamble your money.')
async def gamble(interactions, amount: int):
    """
    Allows a user to gamble a certain amount of money.

    Parameters:
    - interactions (Context): The context object representing the invocation context of the command.
    - amount (int): The amount of money to gamble.

    Returns:
    - None
    """
    try:
        gambling = Gambling(interactions.guild.id)
        # Call the gamble function in Gambling
        await gambling.gamble(interactions, amount)
    except Exception as e:
        logger.error(f"Error in the gamble command: {e}")
        raise e


@bot.tree.command(name='leaderboard', description='Display the leaderboard.')
async def leaderboard(interactions):
    """
    Display the leaderboard.

    Parameters:
    - interactions (Context): The context object representing the invocation context of the command.

    Returns:
    - None
    """
    try:

        leaderboard = Leaderboard()
        # Call the leaderboard function in Leaderboard
        await leaderboard.leaderboard_command(interactions)
    except Exception as e:
        logger.error(f"Error in the leaderboard command: {e}")
        raise e


@bot.tree.command(name='rank', description='Display your rank.')
async def rank(interactions):
    """
    Display the user's rank.

    Parameters:
    - interactions (Context): The context object representing the invocation context of the command.

    Returns:
    - None
    """
    try:
        leaderboard = Leaderboard()
        # Call the rank function in Gambling
        await leaderboard.rank_command(interactions)
    except Exception as e:
        logger.error(f"Error in the rank command: {e}")
        raise e


@bot.tree.command(name='work', description='Work to earn money.')
async def work(interactions):
    """
    Allows a user to work to earn money.

    Parameters:
    - interactions (Context): The context object representing the invocation context of the command.

    Returns:
    - None
    """
    try:
        work = Work()
        await work.work_command(interactions)
    except Exception as e:
        logger.error(f"Error in the work command: {e}")
        raise e


@bot.tree.command(name='balance', description='Display your bank balance.')
async def balance(interactions):
    """
    Display the user's bank balance.

    Parameters:
    - interactions (Context): The context object representing the invocation context of the command.

    Returns:
    - None
    """
    try:
        balance = Balance()
        await balance.balance_command(interactions)
    except Exception as e:
        logger.error(f"Error in the balance command: {e}")
        raise e


@bot.tree.command(name="give", description="Give money to another user.")
async def give(interactions, member: discord.Member, amount: int):
    """
    Give money to another user.

    Parameters:
    - interactions (Context): The context object representing the invocation context of the command.
    - amount (int): The amount of money to give.
    - member (discord.Member): The member to give the money to.

    Returns:
    - None
    """
    try:
        give = Give()
        await give.give_command(interactions, member, amount)
    except Exception as e:
        logger.error(f"Error in the give command: {e}")
        raise e


@bot.tree.command(name="case", description="Open a Counter-Strike case.")
async def case(interactions):
    """
    Open a Counter-Strike case.

    Parameters:
    - interactions (Context): The context object representing the invocation context of the command.

    Returns:
    - None
    """
    try:
        case = Case(interactions.guild.id)
        # Call the case function in Gambling
        await case.open_case(interactions)
    except Exception as e:
        logger.error(f"Error in the case command: {e}")
        raise e


@bot.tree.command(name="sticker", description="Open a Counter-Strike sticker capsule.")
async def capsule(interactions):
    """
    Open a Counter-Strike sticker capsule.

    Parameters:
    - interactions (Context): The context object representing the invocation context of the command.

    Returns:
    - None
    """
    try:
        sticker = Capsule(interactions.guild.id)
        # Call the capsule function in Gambling
        await sticker.open_capsule(interactions)
    except Exception as e:
        logger.error(f"Error in the capsule command: {e}")
        raise e


@bot.tree.command(name="inventory", description="Display your inventory.")
async def inventory(interactions):
    """
    Display the user's inventory.

    Parameters:
    - interactions (Context): The context object representing the invocation context of the command.

    Returns:
    - None
    """
    try:
        inventory = Inventory(interactions.guild.id)
        # Call the inventory function in Gambling
        await inventory.display_inventory(interactions)
    except Exception as e:
        logger.error(f"Error in the inventory command: {e}")
        raise e


@bot.tree.command(name="rps", description="Play rock, paper, scissors.")
async def rps(interactions, bet: float,  choice: Choices):
    """
    Play rock, paper, scissors.

    Parameters:
    - interactions (Context): The context object representing the invocation context of the command.
    - choice (Choices): The choice of rock, paper, or scissors.

    Returns:
    - None
    """
    try:
        rps = RockPaperScissors()
        # Call the rps function in RockPaperScissors
        await rps.rockpaperscissors_command(interactions, bet, choice)
    except Exception as e:
        logger.error(f"Error in the rps command: {e}")
        raise e


@bot.tree.command(name='roll', description='Roll a dice between 1-100.')
async def roll(interactions, bet: int, number: int):
    """
    Roll a dice between 1-100.

    Parameters:
    - interactions (Context): The context object representing the invocation context of the command.

    Returns:
    - None
    """
    try:
        roll = Roll()
        await roll.roll_command(interactions, bet, number)
    except Exception as e:
        logger.error(f"Error in the roll command: {e}")
        raise e


@bot.tree.command(name='blackjack', description='Play blackjack.')
async def blackjack(interactions, bet: int):
    """
    Play blackjack.

    Parameters:
    - interactions (Context): The context object representing the invocation context of the command.

    Returns:
    - None
    """
    try:
        blackjack = BlackJack()
        await blackjack.blackjack_command(interactions, bet)
    except Exception as e:
        logger.error(f"Error in the blackjack command: {e}")
        raise e


@bot.tree.command(name='coinflip', description='Flip a coin.')
async def coinflip(interactions, bet: float, user: discord.Member):
    """
    Flip a coin.

    Parameters:
    - interactions (Context): The context object representing the invocation context of the command.

    Returns:
    - None
    """
    try:
        coinflip = CoinFlip()
        await coinflip.coinflip_command(interactions, bet, user)
    except Exception as e:
        logger.error(f"Error in the coinflip command: {e}")
        raise e


@bot.tree.command(name='finance', description='Get the live price of a stock.')
async def finance(interactions, stock: str):
    """
    Get the live price of a stock.

    Parameters:
    - interactions (Context): The context object representing the invocation context of the command.

    Returns:
    - None
    """
    try:
        finance = Finance()
        await finance.finance_command(interactions, stock)
    except Exception as e:
        logger.error(f"Error in the finance command: {e}")
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

async def run_bot(token):
    while True:
        try:
            await bot.start(token, reconnect=True)
        except ConnectionResetError as e:
            print(f"Connection error: {e}")
            await asyncio.sleep(5)  # Wait for 5 seconds before reconnecting
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            await asyncio.sleep(5)  # Wait for 5 seconds before reconnecting


def main():
    """
    Main function that runs the bot.
    """
    try:
        if os.environ.get("DISCORD_TOKEN") is None:
            raise Exception("No token found in the environment variables.")
        asyncio.get_event_loop().run_until_complete(
            run_bot(os.environ.get("DISCORD_TOKEN")))
    except KeyboardInterrupt:
        print("\nBot stopped by user.")
        return
    except Exception as e:
        print(f"Error in the main function: {e}")
        raise e
