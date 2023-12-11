# Discord bot for the server
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

        # Stop the current playing song
        self.session.stop(vc)

        # Play the next song in the queue
        self.session.play_next(vc)

        await ctx.send("Skipped to the next song.")


        
            
            
    async def joinChannel(self, ctx):
        try:
            channel = ctx.author.voice.channel
        except Exception as e:
            await ctx.send(ctx.author.mention + " is not in a voice channel.")
            return False

        vc = ctx.voice_client
        if vc and vc.channel == channel:
            return True  # Bot is already in the correct channel, no need to reconnect

        if vc:
            await vc.move_to(channel)
        else:
            await channel.connect()

        return True


    @commands.command(name='play', brief='Play a song.', usage='<url>', help='This command plays a song.')
    async def play(self, ctx, url):
        try:
            if not self.session:
                self.session = SongSession(ctx.guild, ctx)  # Create an instance of SongSession
            
            data = await self.joinChannel(ctx)  # Use the instance to call joinChannel
            if data is False:
                return

            YDL_OPTIONS = {"format": "bestaudio", "noplaylist": "True"}
            FFMPEG_OPTIONS = {
                "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
                "options": "-vn",
            }

            URL, song_title = await YTDLSource.from_url(url, loop=self.bot.loop, stream=True)  # Use the classmethod to get the URL
            vc = ctx.voice_client
            if vc.is_playing():
                await self.session.add_to_queue(URL,song_title, vc)  # Use the instance to add to the queue
                await ctx.send(f"Added {song_title} to the queue.")
            else:
                self.session.play(URL, FFMPEG_OPTIONS, vc)  # Use the instance to play the song

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
        await ctx.send(f"Queue: {queue}")


async def main():
    # Get the token from the .env file
    token = os.environ.get("DISCORD_TOKEN")  
    # Create an instance of the bot
    intents = discord.Intents.default()
    # Make sure the bot can read messages
    intents.message_content = True
    # Create the command prefix and pass in the intents parameter 
    bot = commands.Bot(command_prefix="!", intents=intents)
    # Await the coroutine
    await bot.add_cog(Bot(bot))  
    # Create a new event loop
    loop = asyncio.new_event_loop()
    # Set the event loop
    asyncio.set_event_loop(loop)
    # Start the bot
    try:
        await bot.start(token)
    except Exception as e:
        print(f"Error: {e}")
        exit()

# Run the main coroutine
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"Error: {e}")
        exit()


