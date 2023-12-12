import discord
from yt_dlp import YoutubeDL
from dotenv import load_dotenv
import asyncio


class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)
        self.data = data
        self.title = data.get("title")
        self.url = ""

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        # Set the options for YoutubeDL
        YDL_OPTIONS = {"format": "bestaudio", "noplaylist": "True"}
        # Create a YoutubeDL instance with the options 
        with YoutubeDL(YDL_OPTIONS) as ydl:
            # Extract the info from the URL
            info = ydl.extract_info(url, download=False)
        # Get the URL of the song
        URL = info["url"] 
        # Return the URL and the title of the song
        return URL, info['title']