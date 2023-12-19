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
        # Create an instance of QueueOperations
        self.queue_operations = QueueOperations(self.session)
        # Create an instance of CustomHelpCommand 
        self.help_command = CustomHelpCommand()

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
            # Get the voice channel of the user who sent the command
            channel = ctx.author.voice.channel
        except AttributeError:
            await ctx.send(ctx.author.mention + " is not in a voice channel.")
            return
        try:
            # Create a voice client variable
            vc = ctx.voice_client
            # Check if the bot is already in the correct channel
            if vc and vc.channel == channel:
                await ctx.send("I'm already in your channel.")
                return

            # Check if the bot is already in a channel
            if vc:
                # Move the bot to the correct channel
                await vc.move_to(channel)
            else:
                # Connect to the voice channel
                await channel.connect()
            # Return True to indicate that the bot is in the correct channel
            await ctx.send(f"Joined {channel}")
        except Exception as e:
            print(f"An error occurred when trying to join the channel. {e}")
            raise e
        
    @commands.command(name='leave', aliases=['disconnect'], brief='Leave the voice channel.', usage='', help='This command disconnects the bot from the voice channel.')
    async def leave(self, ctx):
        try:
            # Check if the bot is in a voice channel
            if ctx.voice_client is None:
                await ctx.send("I'm not in a voice channel.")
                return
            # Send a message that the bot is leaving
            await ctx.send("Leaving voice channel.")
            # Disconnect the bot from the voice channel
            await ctx.voice_client.disconnect()
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
            vc = ctx.voice_client
            
            if vc is None or not vc.is_playing():
                await ctx.send("No music is currently playing to skip.")
                return
            print(f"Queue length before: {self.queue_operations.return_queue()}")
            # Check if the queue is empty 
            if self.queue_operations.return_queue() == 0:
                await ctx.send("No more songs in the queue to skip.")
                return
            else:
                print(f"Queue length before: {self.queue_operations.return_queue()}")
                # Call the skip function in the SongSession instance to skip the song
                self.session.skip_song(vc)
                print(f"Queue length before: {self.queue_operations.return_queue()}")
                await ctx.send("Skipped to the next song.")
        except Exception as e:
            print(f"Error in the skip command: {e}")
            raise e
            
    async def joinChannel(self, ctx):
        try:
            # Check if the user is in a voice channel
            try:
                # Get the voice channel of the user who sent the command
                channel = ctx.author.voice.channel
            except Exception as e:
                # Send a message that the user is not in a voice channel
                await ctx.send(ctx.author.mention + " is not in a voice channel.")
                # Return False to indicate that the user is not in a voice channel
                return False

            # Create a voice client variable
            vc = ctx.voice_client
            # Check if the bot is already in the correct channel
            if vc and vc.channel == channel:
                return True  # Bot is already in the correct channel, no need to reconnect
            # Check if the bot is already in a channel
            if vc:
                # Move the bot to the correct channel
                await vc.move_to(channel)
            else:
                # Connect to the voice channel
                await channel.connect()
            # Return True to indicate that the bot is in the correct channel
            return True
        except Exception as e:
            print(f"An error occurred when trying to join the channel. {e}")
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
            # Check if the URL is valid (i.e. it is a YouTube URL)
            if not CommandErrorHandler.check_url_correct(url):
                await ctx.send("Please enter a valid YouTube URL, such as https://www.youtube.com/watch?v=dQw4w9WgXcQ")
                return
            # Check if the bot is already in the correct channel
            if not self.session:
                # Create an instance of SongSession
                self.session = SongSession(ctx.guild, ctx)
                
            # Check if the bot is already in the correct channel
            if await self.joinChannel(ctx) is False:
                return
   
            
            # Get the URL and the title of the song
            URL, song_title, song_duration, thumbnail = await YTDLSource.from_url(url, loop=self.bot.loop, stream=True)
            
            # This will return False if the URL or song_title is invalid
            if not CommandErrorHandler.check_url_song_correct(URL, song_title): 
                await ctx.send("No song found.")
                return
            
            # Declare a voice client variable
            vc = ctx.voice_client
            # Check if the bot is playing something
            if vc.is_playing():
                # Use the instance to add to the queue
                self.queue_operations.add_to_queue(URL, song_title, vc, song_duration, thumbnail)
                await ctx.send(f"Added {song_title} to the queue.")
            else:
                # Use the instance to play the song
                self.session.play(URL, vc, None, song_title, song_duration, thumbnail)

        except Exception as e:
            # Leave the channel if an error occurs
            await self.leave(ctx)
            print(f"An error occurred when trying to play the song. {e}")
            raise e

    @commands.command(name='nowplaying', aliases=['np'], brief='Display the current song.', usage='', help='This command displays the current song.')
    async def nowplaying(self, ctx):
        try:
            # Get the voice client
            vc = ctx.voice_client
            # Check if the bot is playing something
            if vc is None or not vc.is_playing():
                await ctx.send("No music is currently playing.")
                return
            # Get the title of the song
            song_title = self.session.get_song_title()
            if song_title is None:
                await ctx.send("No music is currently playing.")
                return
            
            # Create an embed message that contains the title of the song, the thumbnail, and the duration
            embed = discord.Embed(title="Now Playing", description=song_title, color=discord.Color.green())
            # Add the thumbnail if available and the song duration
            if self.session.thumbnail is not None:
                embed.set_thumbnail(url=self.session.thumbnail)
            if self.session.song_duration is not None:
                embed.add_field(name="Duration", value=self.session.song_duration)
                
            # Add more information to the embed if available
            if vc.source:
                # Get the duration of the song
                pass

            # Send the embed
            await ctx.send(embed=embed)
        except Exception as e:
            print(f"An error occurred when trying to display the song. {e}")
            raise e
    
    
    @commands.command(name='queue', brief='Display the queue.', usage='', help='This command displays the queue.')
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
            # Get the voice client
            vc = ctx.voice_client
            # Check if the bot is playing something
            if vc is None or not vc.is_playing():
                await ctx.send("No music is currently playing.")
                return
            # Check if the queue is empty
            if self.queue_operations.return_queue() == 0:
                await ctx.send("No more songs in the queue.")
                return

            # Send a message with the queue
            await ctx.send(f"Queue: {self.queue_operations.display_queue()}")
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
            # Get the voice client
            vc = ctx.voice_client
            # Check if the bot is playing something
            if vc is None or not vc.is_playing():
                await ctx.send("No music is currently playing.")
                return
            # Check if the queue is empty
            if self.queue_operations.return_queue() == 0:
                await ctx.send("No more songs in the queue to clear.")
                return
            # Clear the queue
            self.queue_operations.queue.clear()
            await ctx.send("Cleared the queue.")
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
            # Declare a voice client variable
            vc = ctx.voice_client
            # Check if the bot is playing something
            if vc is None or not vc.is_playing():
                await ctx.send("No music is currently playing to pause.")
                return
            # Pause the song
            await self.session.pause(vc)
            # Send a message that the song was paused
            await ctx.send("Paused the current song.")
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
            # Declare a voice client variable
            vc = ctx.voice_client
            # Check if the bot is playing something or if the bot is paused
            if vc is None or not vc.is_paused():
                await ctx.send("No music is currently paused to resume.")
                return
            # Resume the song
            await self.session.resume(vc)
            # Send a message that the song was resumed
            await ctx.send("Resumed the current song.")
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
            # Get the voice client
            vc = ctx.voice_client
            # Check if the bot is playing something
            if vc is None or not vc.is_playing():
                await ctx.send("No music is currently playing.")
                return
            # Check if the queue is empty
            if self.queue_operations.return_queue() == 0:
                await ctx.send("No songs in the queue to suffle.")
                return
            # Call the queue shuffle function in QueueOperations
            self.queue_operations.shuffle_queue()
            await ctx.send("Suffled the queue.")
        except Exception as e:
            print(f"Error in the shuffle command: {e}")
            raise e            
            
    @commands.command(name="userinfo", aliases=["ui", "whois"], brief="Display user information.", usage="<member>", help="This command displays information about a user.")
    async def user_information(self, ctx, *, member: discord.Member = None):
        try:
            embed = await UserInfo.fetch_user_information(self, ctx, member=member)
            # Send the embed
            await ctx.send(embed=embed)
        except Exception as e:
            print(f"Error: {e}")
            raise e
        
