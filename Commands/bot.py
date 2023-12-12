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
load_dotenv()


class Bot(commands.Cog):
    def __init__(self, bot):
        self.intents = discord.Intents.default()
        self.intents.message_content = True
        self.client = discord.Client(intents=self.intents)
        self.bot = commands.Bot(command_prefix="!", intents=self.intents)
        self.session = None  # Create an instance of SongSession

        self.help_command = CustomHelpCommand()

    @commands.Cog.listener()
    async def on_ready(self):
        await self.bot.change_presence(activity=discord.Game(name="!help"))

    @commands.command(name='health', brief='Check if the bot is alive.', usage='', help='This command checks the bot\'s latency.')
    async def health(self, ctx):
        # Send a message that the bot is alive as a health check
        await ctx.send("I am alive!")

    @commands.command()
    async def join(self, ctx):
        # Get the voice channel of the user who sent the command
        channel = ctx.author.voice.channel
        # Connect to the voice channel
        await channel.connect()

    @commands.command(name='leave', aliases=['disconnect'], brief='Leave the voice channel.', usage='', help='This command disconnects the bot from the voice channel.')
    async def leave(self, ctx):
        # Send a message that the bot is leaving
        await ctx.send("Leaving voice channel.")
        # Disconnect the bot from the voice channel
        await ctx.voice_client.disconnect()

    @commands.command(name='ping', brief='Ping a user.', usage='<username>', help='This command pings a user.')
    async def ping(self, ctx, username):
        # check if there is a @ in the username
        if "@" in username:
            await ctx.send(f"{username}")
        else:
            await ctx.send(f"@{username}")

    @commands.command(name='skip', brief='Skip the current song.', usage='', help='This command skips the current song.')
    async def skip(self, ctx):
        vc = ctx.voice_client
        
        if vc is None or not vc.is_playing():
            await ctx.send("No music is currently playing to skip.")
            return

        if len(self.session.queue) == 0:
            await ctx.send("No more songs in the queue to skip.")
            return
        
        self.session.skip(vc)
        await ctx.send("Skipped to the next song.")

    async def joinChannel(self, ctx):
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

    @commands.command(name='play', brief='Play a song.', usage='<url>', help='This command plays a song.')
    async def play(self, ctx, url):
        try:
            if not self.session:
                # Create an instance of SongSession
                self.session = SongSession(ctx.guild, ctx)

            # Use the instance to call joinChannel
            data = await self.joinChannel(ctx)
            if data is False:
                return

            YDL_OPTIONS = {"format": "bestaudio", "noplaylist": "True"}
            

            # Use the classmethod to get the URL
            URL, song_title = await YTDLSource.from_url(url, loop=self.bot.loop, stream=True)
            vc = ctx.voice_client
            if vc.is_playing():
                # Use the instance to add to the queue
                await self.session.add_to_queue(URL, song_title, vc)
                await ctx.send(f"Added {song_title} to the queue.")
            else:
                # Use the instance to play the song
                self.session.play(URL, vc)

        except Exception as e:
            print(f"Error: {e}")
            await ctx.send(f"An error occurred: {e}")
            await self.leave(ctx)

    @commands.command(name='queue', brief='Display the queue.', usage='', help='This command displays the queue.')
    async def queue(self, ctx):
        # Get the voice client
        vc = ctx.voice_client
        # Check if the bot is playing something
        if vc is None or not vc.is_playing():
            await ctx.send("No music is currently playing.")
            return
        # Check if the queue is empty
        if len(self.session.queue) == 0:
            await ctx.send("No more songs in the queue.")
            return
        # Get the queue from the instance
        queue = self.session.display_queue()

        # Send a message with the queue
        await ctx.send(f"Queue: {queue}")