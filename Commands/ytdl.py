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
        
        YDL_OPTIONS = {"format": "bestaudio", "noplaylist": "True"}
        with YoutubeDL(YDL_OPTIONS) as ydl:
            info = ydl.extract_info(url, download=False)
        URL = info["url"] 
        print(URL)
        return URL, info['title']