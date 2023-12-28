import discord
from discord.ext import commands
from discord.utils import get
from discord.voice_client import VoiceClient
import youtube_dl
from yt_dlp import YoutubeDL

import nacl
import os
from dotenv import load_dotenv
import asyncio
from Commands.help import CustomHelpCommand
from Commands.ytdl import YTDLSource
from Commands.music import SongSession
from Commands.ErrorHandling.handling import CommandErrorHandler
from Commands.queue import QueueOperations
from Commands.userinfo import UserInfo
from Commands.linkmessage import LinkMessage
from Commands.utility import Utility
from Commands.nowplaying import NowPlaying
# Import logging
from Config.config import conf
from Config.logging import setup_logging

# Create a logger for this file
Logger = setup_logging("bot.py", conf.LOGS_PATH)

# Load the .env file
load_dotenv()


class Bot(commands.Cog):
    def __init__(self, bot):
        # Create an instance of the intents class
        self.intents = discord.Intents.default()
        # Make sure the bot can read messages
        self.intents.message_content = True
        # Create the client
        self.client = discord.Client(intents=self.intents)
        # Assign the bot instance to the bot variable
        self.bot = bot
        # Create an instance of SongSession
        self.session = None
        # Create an instance of QueueOperations to handle the music queue
        self.queue_operations = QueueOperations(self.session)
        # Create an instance of CustomHelpCommand to handle the help command
        self.help_command = CustomHelpCommand()
        # Create an instance of LinkMessage to handle messages that contain URLs
        self.linkmessage = LinkMessage(bot)
        # Create an instance of Utility to handle utility commands
        self.utility = Utility(bot)
        # Create an instance of NowPlaying to handle the nowplaying command
        self.playing_operations = NowPlaying()

    @commands.Cog.listener()
    async def on_ready(self):
        """
        Event handler that is triggered when the bot is ready to start receiving events.

        This function changes the status of the bot to "Playing !help" when it is ready.
        """
        try:
            # Check if the bot is ready
            if self.bot:
                # Change the status of the bot to "Playing !help"
                await self.bot.change_presence(activity=discord.Game(name="!help"))
        except Exception as e:
            print(f"Error in on_ready: {e}")
            raise e

    @commands.Cog.listener()
    async def on_message(self, message):
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
            await self.linkmessage.on_message_command(message)
        except Exception as e:
            print(f"Error in the on message event: {e}")
            raise e


    @commands.command(name='health', brief='Check if the bot is alive.', usage='', help='This command checks the bot\'s latency.')
    async def health(self, ctx):
        """
        Check if the bot is alive.

        This command checks the bot's latency by sending a message "I am alive!".
        """
        try:
            # Send a message that the bot is alive as a health check
            await ctx.send("I am alive!")
        except Exception as e:
            print(f"Error in the health command: {e}")
            raise e

    @commands.command(name='join', brief='Join the voice channel.', usage='', help='This command makes the bot join the voice channel.')
    async def join(self, ctx):
        """
        Join the voice channel.

        This command makes the bot join the voice channel of the user who sent the command.
        If the bot is already in the correct channel, it will send a message indicating that it is already in the channel.
        If the bot is in a different channel, it will move to the correct channel.
        If the bot is not in any channel, it will connect to the voice channel.
        """

        try:
            await self.utility.join(ctx)
        except Exception as e:
            print(f"An error occurred when trying to join the channel. {e}")
            raise e

    @commands.command(name='leave', aliases=['disconnect'], brief='Leave the voice channel.', usage='', help='This command disconnects the bot from the voice channel.')
    async def leave(self, ctx):
        try:
            await self.utility.leave(ctx)
        except Exception as e:
            print(f"Error in the leave command: {e}")
            raise e

    @commands.command(name='ping', brief='Ping a user.', usage='<username>', help='This command pings a user.')
    async def ping(self, ctx, username):
        try:
            # check if there is a @ in the username
            if "@" in username:
                await ctx.send(f"{username}")
            else:
                await ctx.send(f"@{username}")
        except Exception as e:
            print(f"Error in the ping command: {e}")
            raise e

    @commands.command(name='skip', brief='Skip the current song.', usage='', help='This command skips the current song.')
    async def skip(self, ctx):
        try:
            # Call the skip function in SongSession
            await self.session.skip(ctx)
        except Exception as e:
            print(f"Error in the skip command: {e}")
            raise e



    @commands.command(name='play', brief='Play a song.', usage='<url>', help='This command plays a song.')
    async def play(self, ctx, url):
        """
        Play a song.

        Parameters:
        - ctx (discord.ext.commands.Context): The context of the command.
        - url (str): The URL of the song to be played.

        Returns:
        None
        """
        try:
            # Check if a music session instance was already created
            if not self.session:
                # Create an instance of SongSession
                self.session = SongSession(ctx.guild, ctx)
                
            await self.session.play_command(ctx, url, self.bot.loop)

        except Exception as e:
            # Leave the channel if an error occurs
            print(f"An error occurred when trying to play the song. {e}")
            raise e

    @commands.command(name='nowplaying', aliases=['np', 'playing'], brief='Display the current song.', usage='', help='This command displays the current song.')
    async def nowplaying(self, ctx):
        try:
            await self.playing_operations.nowplaying_command(ctx, self.session)
        except Exception as e:
            print(f"An error occurred when trying to display the song. {e}")
            raise e

    # TODO - Add a command to display the lyrics of the current song
    @commands.command(name='lyrics', brief='Display the lyrics of the current song.', usage='', help='This command displays the lyrics of the current song.')
    async def lyrics(self, ctx):
        try:
           pass
        except Exception as e:
            print(f"An error occurred when trying to display the lyrics. {e}")
            raise e

    @commands.command(name='queue', aliases=["q"], brief='Display the queue.', usage='', help='This command displays the queue.')
    async def queue(self, ctx):
        """
        Display the queue.

        This command displays the current queue of songs in the bot's session.

        Parameters:
        - ctx (Context): The context object representing the invocation context of the command.

        Returns:
        None
        """
        try:
            # Call the queue function in QueueOperations
            await self.queue_operations.display_queue_command(ctx, discord)
        except Exception as e:
            print(f"An error occurred when trying to display the queue. {e}")
            raise e

    @commands.command(name="clear", brief="Clear the queue.", usage="", help="This command clears the queue.")
    async def clear(self, ctx):

        """
        This command clears the queue. It checks if the bot is currently playing music and if there are songs in the queue before calling the clear function from queue operations. 

        Parameters:
        - ctx (Context): The context object representing the invocation context of the command.

        Returns:
        None
        """
        try:
            self.queue_operations.clear_command(ctx)
        except Exception as e:
            print(f"An error occurred when trying to clear the queue. {e}")
            raise e

    @commands.command(name='pause', brief='Pause the current song.', usage='', help='This command pauses the current song.')
    async def pause(self, ctx):
        """
        Pauses the current song.

        Parameters:
        - ctx (Context): The context of the command.

        Returns:
        None
        """
        try:
            await self.session.pause_command(ctx)
        except Exception as e:
            print(f"An error occurred when trying to pause the song. {e}")
            raise e

    @commands.command(name='resume', brief='Resume the current song.', usage='', help='This command resumes the current song.')
    async def resume(self, ctx):
        """
        Resumes the current song.

        This command is used to resume the current song if it is paused.
        If there is no music currently paused, it will display a message indicating that.
        If an error occurs while trying to resume the song, it will display an error message.

        Parameters:
        - ctx (Context): The context object representing the invocation context of the command.

        Returns:
        - None
        """
        try:
            await self.session.resume_command(ctx)
        except Exception as e:
            print(f"An error occurred when trying to resume the song. {e}")
            raise e

    @commands.command(name='shuffle', brief='Suffle the queue.', usage='', help='This command suffles the queue.')
    async def shuffle(self, ctx):
        """
        Shuffles the queue.

        This command shuffles the songs in the queue. It checks if the bot is currently playing music and if there are songs in the queue.
        If the conditions are met, it calls the shuffle_queue function in QueueOperations to shuffle the songs.

        Parameters:
        - ctx (Context): The context object representing the invocation context of the command.

        Raises:
        - Exception: If an error occurs while shuffling the queue.

        Returns:
        - None
        """
        try:
            # Call the queue shuffle function in QueueOperations
            await self.queue_operations.shuffle_queue_command(ctx)
        except Exception as e:
            print(f"Error in the shuffle command: {e}")
            raise e

    @commands.command(name="userinfo", aliases=["ui", "whois"], brief="Display user information.", usage="<member>", help="This command displays information about a user.")
    async def user_information(self, ctx, *, member: discord.Member = None):
        try:
            # Create the embed message that will display the user information (username, ID, join date, account creation date)
            await UserInfo.fetch_user_information(self, ctx, member=member)
        except Exception as e:
            print(f"Error in the user info command: {e}")
            raise e


                