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
        data = await loop.run_in_executor(
            None, lambda: ytdl.extract_info(url, download=False)
        )
        if "entries" in data:
            # take first item from a playlist
            data = data["entries"][0]
        filename = data["title"] if stream else ytdl.prepare_filename(data)
        return filename


class SongSession:
    def __init__(self, guild, url, ctx):
        self.guild = guild
        self.path = url
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

    def add_to_queue(self, youtube_source, vc):
        source = YTDLSource.from_url(youtube_source)
        self.queue.append(source)
        print(f"Added {source} to the queue.")
        print(f"Queue is now: {self.queue}")
        print(f"is playing: {vc.is_playing()}")
        if not vc.is_playing():
            self.play_next(vc)

    def play(self, source, options, vc):
        try:
            vc.play(discord.FFmpegPCMAudio(source, **options))
        except Exception as e:
            print(f"Error: {e}")
            return
        
    def play_next(self, vc):
        # If there are no more songs in the queue, disconnect the bot
        if len(self.queue) == 0:
            print("No more songs in queue.")
            return
        # Otherwise, get the next song and play it
        next_source = self.queue.pop(0)
        self.play(next_source, {}, vc)  # Adjust the options as needed
        print(f"Playing {next_source}")


class Bot(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.intents = discord.Intents.default()
        self.intents.message_content = True
        self.client = discord.Client(intents=self.intents)
        self.bot = commands.Bot(command_prefix="!", intents=self.intents)

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"Logged in as ")

    @commands.command()
    async def health(self, ctx):
        await ctx.send("I am alive!")

    @commands.command()
    async def join(self, ctx):
        channel = ctx.author.voice.channel
        await channel.connect()

    @commands.command()
    async def leave(self, ctx):
        await ctx.voice_client.disconnect()

    @commands.command()
    async def ping(self, ctx, username):
        # check if there is a @ in the username
        if "@" in username:
            await ctx.send(f"{username}")
        else:
            await ctx.send(f"@{username}")


    @commands.command()
    async def skip(self, queue, ctx):
        if len(queue) > 0:
            next_source = queue.pop(0)
            self.play(next_source, {}, ctx.voice_client)  # Adjust the options as needed
            
            
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


    @commands.command()
    async def play(self, ctx, url):
        try:
            session = SongSession(ctx.guild, url, ctx)  # Create an instance of SongSession
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
                session.add_to_queue(URL, vc)  # Use the instance to add to the queue
                await ctx.send(f"Added {info['title']} to the queue.")
            else:
                session.play(URL, FFMPEG_OPTIONS, vc)  # Use the instance to play the song

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


