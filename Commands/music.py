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
load_dotenv()


        



class SongSession:
    def __init__(self, guild,  ctx) -> None:
        self.guild = guild
        
        vc = ctx.voice_client
        self.voice_client = vc
        self.queue = []  # Initialize the queue attribute
        self.title_queue = []

    def stop(self, vc):
        vc.stop()

    def pause(self):
        self.voice_client.pause()

    def resume(self):
        self.voice_client.resume()

    def is_playing(self):
        return self.voice_client.is_playing()

    def display_queue(self):
        # Return the queue of song titles
        return self.title_queue

    async def add_to_queue(self, youtube_source,title, vc):
        # Add the source to the queue
        self.queue.append(youtube_source)
        self.title_queue.append(title)

        print(f"Queue is now: {self.title_queue}")
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
        self.title_queue.pop(0) # Remove the song title from the queue
        