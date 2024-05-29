import discord
from discord.ext import commands
from dotenv import load_dotenv
from discord import app_commands
from Commands.music import SongSession
from Commands.lyrics import LyricsOperations
from Commands.queue import QueueOperations
from Commands.userinfo import UserInfo
from Commands.linkmessage import LinkMessage
from Commands.utility import Utility
from Commands.nowplaying import NowPlaying
from Commands.health import HealthCheck
from Commands.gambling import Gambling
from Config.config import conf

# Import logging
from Config.logging import setup_logging


# Create a logger for this file
logger = setup_logging("bot.py", conf.LOGS_PATH)

# Load the .env file
load_dotenv()

import os


intents = discord.Intents.all()
#intents.message_content = True
# Create a discord client instance and give it the intents 
#client = discord.Client(intents=intents)
#tree = app_commands.CommandTree(client)
bot = commands.Bot(command_prefix='!', intents=intents)

session = None
# Create an instance of QueueOperations to handle the music queue
queue_operations = QueueOperations(session)

# Create an instance of LinkMessage to handle messages that contain URLs
linkmessage = LinkMessage(bot)
# Create an instance of Utility to handle utility commands
utility = Utility()
# Create an instance of NowPlaying to handle the nowplaying command
playing_operations = NowPlaying()
# Create an instance of HealthCheck to handle the health command
health_check = HealthCheck(bot)

lyrics_operations = LyricsOperations(bot)
@bot.event
async def on_ready():
    """
    Event handler that is triggered when the bot is ready.

    This function prints the bot's name and ID to the console.
    """
    try:
        print(f'{bot.user} has connected to Discord!')
        # Change the bot's status to "Listening to /help"
        await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name="/help"))
        
        # Synchornize the bot's commands with the Discord API
        await bot.tree.sync()
       
    except Exception as e:
        logger.error(f"Error in the on ready event: {e}")
        raise e

@bot.event
async def on_message(message):
    """
    Event handler that is triggered when a message is sent in a channel.

    This function checks if the message contains a URL. If it does, it will fetch the domain information and send it as a message.

    Parameters:
    - message (discord.Message): The message object that was sent.

    Returns:
    None

    Raises:
    Exception: If an error occurs while fetching the domain information.

    Examples:
    https://www.youtube.com/watch?v=vJwKKKd2ZYE&list=RDMMvrQWhFysPKY&index=3 ->

    Origin: US
    Creation Date: 2005-02-15 05:13:12
    Name Servers: NS1.GOOGLE.COM, NS2.GOOGLE.COM, NS3.GOOGLE.COM, NS4.GOOGLE.COM, ns2.google.com, ns1.google.com, ns4.google.com, ns3.google.com
    Name Domain: YOUTUBE.COM, youtube.com
    Organization: Google LLC
    """
    try:
        # Fetch the domain information from the message url and send it as a message
        await linkmessage.on_message_command(message)
    except Exception as e:
        logger.error(f"Error in the on message event: {e}")
        raise e

@bot.tree.command(name='health', description='Displays all the available commands.')
async def health(interactions):
    """
    Check if the bot is alive and provide detailed health information.
    """
    try:
        await health_check.health_command(interactions, bot)
        
    except Exception as e:
        print(f"Error in the health command: {e}")
        raise e


    
@bot.tree.command(name='join', description='Join the voice channel.')
async def join(interactions: discord.Interaction):
    """
    Join the voice channel.

    This command makes the bot join the voice channel of the user who sent the command.
    If the bot is already in the correct channel, it will send a message indicating that it is already in the channel.
    If the bot is in a different channel, it will move to the correct channel.
    If the bot is not in any channel, it will connect to the voice channel.
    """

    try:
        await utility.join(interactions)
    except Exception as e:
        logger.error(
            f"An error occurred when trying to join the channel. {e}")
        raise e

@bot.tree.command(name='leave', description='Makes the bot leave the voice channel.')
async def leave( interactions):
    try:
        await utility.leave(interactions)
    except Exception as e:
        logger.error(f"Error in the leave command: {e}")
        raise e

@bot.tree.command(name='ping', description='Ping a user.')
async def ping(interactions, username: discord.User):
    try:
        # check if there is a @ in the username
        await interactions.response.send_message(f"Hello {username.mention}")
    except Exception as e:
        logger.error(f"Error in the ping command: {e}")
        raise e

@bot.tree.command(name='skip', description='Skip the current song.')
async def skip( interactions):
    try:
        # Call the skip function in SongSession
        await session.skip(interactions)
    except Exception as e:
        logger.error(f"Error in the skip command: {e}")
        raise e

@bot.tree.command(name='play', description='Play a song.')
async def play( interactions, url: str):
    """
    Play a song.

    Parameters:
    - interactions (discord.ext.commands.Context): The context of the command.
    - url (str): The URL of the song to be played.

    Returns:
    None
    """
    try:
        # Create a global session variable to store the SongSession instance
        global session
        # Check if a music session instance was already created
        if not session:
            # Create an instance of SongSession
            session = SongSession(interactions.guild, interactions)

        await session.play_command(interactions, url, bot.loop)

    except Exception as e:
        # Leave the channel if an error occurs
        logger.error(
            f"An error occurred when trying to play the song. {e}")
        raise e

@bot.tree.command(name='nowplaying', description='Display the current playing song.')
async def nowplaying( interactions):
    try:
        await playing_operations.nowplaying_command(interactions, session)
    except Exception as e:
        logger.error(
            f"An error occurred when trying to display the song. {e}")
        raise e

# TODO - Add a command to display the lyrics of the current song
@bot.tree.command(name='lyrics', description='Display the lyrics of the current song.')
async def lyrics( interactions):
    try:
        await lyrics_operations.lyrics_command(interactions, session)
    except Exception as e:
        logger.error(
            f"An error occurred when trying to display the lyrics. {e}")
        raise e

@bot.tree.command(name='queue', description='Display the queue.')
async def queue( interactions):
    """
    Display the queue.

    This command displays the current queue of songs in the bot's session.

    Parameters:
    - interactions (Context): The context object representing the invocation context of the command.

    Returns:
    None
    """
    try:
        # Call the queue function in QueueOperations
        await queue_operations.display_queue_command(interactions, discord)
    except Exception as e:
        logger.error(
            f"An error occurred when trying to display the queue. {e}")
        raise e

@bot.tree.command(name="clear", description="Clear the music queue.")
async def clear( interactions):

    """
    This command clears the queue. It checks if the bot is currently playing music and if there are songs in the queue before calling the clear function from queue operations. 

    Parameters:
    - interactions (Context): The context object representing the invocation context of the command.

    Returns:
    None
    """
    try:
        queue_operations.clear_command(interactions)
    except Exception as e:
        logger.error(
            f"An error occurred when trying to clear the queue. {e}")
        raise e

@bot.tree.command(name='pause', description='Pause the current song.')
async def pause( interactions):
    """
    Pauses the current song.

    Parameters:
    - interactions (Context): The context of the command.

    Returns:
    None
    """
    try:
        await session.pause_command(interactions)
    except Exception as e:
        logger.error(
            f"An error occurred when trying to pause the song. {e}")
        raise e

@bot.tree.command(name='resume', description='Resume the current song.')
async def resume( interactions):
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
    try:
        await session.resume_command(interactions)
    except Exception as e:
        logger.error(
            f"An error occurred when trying to resume the song. {e}")
        raise e

@bot.tree.command(name='shuffle', description='Shuffle the queue.')
async def shuffle( interactions):
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
        # Call the queue shuffle function in QueueOperations
        await queue_operations.shuffle_queue_command(interactions)
    except Exception as e:
        logger.error(f"Error in the shuffle command: {e}")
        raise e

@bot.tree.command(name='volume', description="Change the music's volume.")
async def volume( interactions, volume: int):
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
    try:
        # Call the change volume function in SongSession
        await session.change_volume(volume, interactions)
    except Exception as e:
        logger.error(f"Error in the volume command: {e}")
        raise e

@bot.tree.command(name="userinfo", description="Get information about a user.")
async def user_information( interactions,*, member: discord.Member = None):
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
async def gamble( interactions, amount: int):
    """
    Allows a user to gamble a certain amount of money.

    Parameters:
    - interactions (Context): The context object representing the invocation context of the command.
    - amount (int): The amount of money to gamble.

    Returns:
    - None
    """
    try:
        gambling = Gambling()
        # Call the gamble function in Gambling
        await gambling.gamble(interactions, amount)
    except Exception as e:
        logger.error(f"Error in the gamble command: {e}")
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
        gambling = Gambling()
        # Call the work function in Gambling
        await gambling.work(interactions)
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
        gambling = Gambling()
        # Call the balance function in Gambling
        await gambling.balance(interactions)
    except Exception as e:
        logger.error(f"Error in the balance command: {e}")
        raise e


def main():
    """
    Main function that runs the bot.
    """
    try:
        token = os.environ.get("DISCORD_TOKEN")
        if token is None:
            raise Exception("No token found in the environment variables.")
        # Run the bot
        bot.run(token)
    except Exception as e:
        logger.error(f"Error in the main function: {e}")
        raise e




