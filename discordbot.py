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
    def __init__(self, guild, path, ctx):
        self.guild = guild
        self.path = path
        self.voice_client = ctx.voice_client

    def stop(self):
        self.voice_client.stop()

    def pause(self):
        self.voice_client.pause()

    def resume(self):
        self.voice_client.resume()

    def is_playing(self):
        return self.voice_client.is_playing()

    def display_queue(self):
        return self.queue

    def add_to_queue(self, youtube_source):
        source = YTDLSource.from_url(youtube_source)
        self.queue.append(source)
        if self.voice_client.is_playing():
            return

    def play(self, source, options):
        self.voice_client.play(discord.FFmpegPCMAudio(source, **options))

    def play_next(self):
        if len(self.queue) > 0:
            self.play(self.queue.pop(0))


intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)
bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")


@bot.command()
async def health(ctx):
    await ctx.send("I am alive!")


@bot.command()  # command prefix
async def join(ctx):
    channel = ctx.author.voice.channel  # gets the channel of the user
    await channel.connect()  # joins the voice channel


@bot.command()
async def leave(ctx):
    await ctx.voice_client.disconnect()  # leaves the voice channel


@bot.command()
async def ping(ctx, username):  # function to ping someone in the server
    await ctx.send(f"@{username}")


async def joinChannel(ctx):
    try:
        channel = ctx.author.voice.channel
    except Exception as e:
        await ctx.send(ctx.author.mention + " is not in a voice channel.")
        return False
    vc = ctx.voice_client
    if vc is None:
        await channel.connect()
    return True


ytdl_format_options = {
    "format": "bestaudio/best",
    "outtmpl": "%(extractor)s-%(id)s-%(title)s.%(ext)s",
    "restrictfilenames": True,
    "noplaylist": True,
    "nocheckcertificate": True,
    "ignoreerrors": False,
    "logtostderr": False,
    "quiet": True,
    "no_warnings": True,
    "default_search": "auto",
    "source_address": "0.0.0.0",  # bind to ipv4 since ipv6 addresses cause issues sometimes
}
ffmpeg_options = {"options": "-vn"}

ytdl = YoutubeDL(ytdl_format_options)


def endSong(guild, path):
    os.remove(path)


async def get_youtube_dl_output(url):
    import subprocess

    process = await asyncio.create_subprocess_exec(
        "youtube-dl", url, "--verbose", stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    stdout, stderr = await process.communicate()
    return stdout.decode() + stderr.decode()


@bot.command()
async def play(ctx, url):
    try:
        SongSession(ctx.guild, url, ctx)
        # Join the voice channel of the user who requested the song
        data = await joinChannel(ctx)
        # Check if the user is in a voice channel
        if data is False:
            return
        # Create the stream options
        YDL_OPTIONS = {"format": "bestaudio", "noplaylist": "True"}
        # Create the FFMPEG options
        FFMPEG_OPTIONS = {
            "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
            "options": "-vn",
        }
        # Get the info of the song from the url
        with YoutubeDL(YDL_OPTIONS) as ydl:
            info = ydl.extract_info(url, download=False)

        # Get the url of the song
        URL = info["url"]
        #   Get the voice client
        vc = ctx.voice_client
        # Check if the bot is already playing a song
        if vc.is_playing():
            # Add the song to the queue
            SongSession.add_to_queue(URL)
        SongSession.play(URL, FFMPEG_OPTIONS)

    except Exception as e:
        print(f"Error: {e}")
        await ctx.send(f"An error occurred: {e}")
        await leave(ctx)


def main():
    token = os.environ.get("DISCORD_TOKEN")  # Get the token from the .env file
    bot.run(token)  # Run the bot


if __name__ == "__main__":
    main()
