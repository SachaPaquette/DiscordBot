import discord
from yt_dlp import YoutubeDL
from dotenv import load_dotenv
import asyncio


class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)
        # Set the data attribute
        self.data = data
        # Set the title attribute
        self.title = data.get("title")

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        """
        Extracts information from a given URL using YoutubeDL.

        Args:
            url (str): The URL of the video or audio to extract information from.
            loop (asyncio.AbstractEventLoop, optional): The event loop to use for asynchronous operations. Defaults to None.
            stream (bool, optional): Whether to stream the audio instead of downloading it. Defaults to False.

        Returns:
            tuple: A tuple containing the URL, title, duration, and thumbnail of the song.
                   If an error occurs during extraction, returns (None, None).
        """
        try:
            # Set the options for YoutubeDL
            YDL_OPTIONS = {"format": "bestaudio", "noplaylist": "True"}
            # Create a YoutubeDL instance with the options 
            with YoutubeDL(YDL_OPTIONS) as ydl:
                # Extract the info from the URL
                info = ydl.extract_info(url, download=False)
            
            # Get the URL of the song
            URL = info["url"]
            song_title = info["title"] 
            song_duration = info["duration_string"]
            thumbnail = info["thumbnails"][0]["url"]
            # Return the URL and the title of the song
            return URL, song_title, song_duration, thumbnail 
        except Exception as e:
            print(f"Error: {e}")
            return None, None