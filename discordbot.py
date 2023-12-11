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
load_dotenv()



class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)
        self.data = data
        self.title = data.get("title")
        self.url = ""

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        YDL_OPTIONS = {"format": "bestaudio", "noplaylist": "True"}
        with YoutubeDL(YDL_OPTIONS) as ydl:
            info = ydl.extract_info(url, download=False)
        URL = info["url"] 
        print(URL)
        return URL
        



class SongSession:
    def __init__(self, guild,  ctx) -> None:
        self.guild = guild
        
        vc = ctx.voice_client
        self.voice_client = vc
        self.queue = []  # Initialize the queue attribute

    def stop(self, vc):
        vc.stop()

    def pause(self):
        self.voice_client.pause()

    def resume(self):
        self.voice_client.resume()

    def is_playing(self):
        return self.voice_client.is_playing()

    def display_queue(self):
        return self.queue

    async def add_to_queue(self, youtube_source, vc):
        # Add the source to the queue
        self.queue.append(youtube_source)
        print(f"Added {youtube_source} to the queue.")
        print(f"Queue is now: {self.queue}")
        print(f"is playing: {vc.is_playing()}")
        # Check if the bot is playing something
        if not vc.is_playing():
            # If not, play the next song
            self.play_next(vc)

    def play(self, source, options, vc):
        def after_playing(error):
            if error:
                print(f"Error: {error}")
            else:
                self.play_next(vc)
                
        try:
            # Play the source 
            vc.play(discord.FFmpegPCMAudio(source, **options), after=after_playing)
        except Exception as e:
            print(f"Error: {e}")
            return
        
    def play_next(self, vc):
        # If there are no more songs in the queue, disconnect the bot
        if len(self.queue) == 0:
            print("No more songs in queue.")
            # Disconnect the bot
            vc.stop()
        
        # Otherwise, get the next song and play it
        next_source = self.queue.pop(0)
        self.play(next_source, {}, vc)  # Play the next song
        
     

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

            with YoutubeDL(YDL_OPTIONS) as ydl:
                info = ydl.extract_info(url, download=False)
            URL = info["url"]
            vc = ctx.voice_client
            if vc.is_playing():
                await self.session.add_to_queue(URL, vc)  # Use the instance to add to the queue
                await ctx.send(f"Added {info['title']} to the queue.")
            else:
                self.session.play(URL, FFMPEG_OPTIONS, vc)  # Use the instance to play the song

        except Exception as e:
            print(f"Error: {e}")
            await ctx.send(f"An error occurred: {e}")
            await self.leave(ctx)




async def main():
    token = os.environ.get("DISCORD_TOKEN")  # Get the token from the .env file
    intents = discord.Intents.default()
    intents.message_content = True
    bot = commands.Bot(command_prefix="!", intents=intents)
    await bot.add_cog(Bot(bot))  # Await the coroutine

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

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


