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
from Config.config import conf
load_dotenv()


        



class SongSession:
    def __init__(self, guild,  ctx) -> None:
        self.guild = guild
        
        vc = ctx.voice_client
        self.voice_client = vc
        self.queue = []  # Initialize the queue attribute
        self.title_queue = []
        self.skipped = False  # Initialize the skipped attribute

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
        # return only the titles in the queue list
        for song in self.queue:
            self.title_queue.append(song["title"])
        return self.title_queue
        #return self.title_queue

    def add_to_queue(self, youtube_source, title, vc):
        try:
            
            # Add the source and title to the queue as a dictionary
            song_info = {"source": youtube_source, "title": title}
            self.queue.append(song_info)
            print(f"Queue is now: {self.queue}")
            print(f"is playing: {vc.is_playing()}")

            # Check if the bot is playing something
            if not vc.is_playing():
                # If not, play the next song
                self.play_next(vc)
        except Exception as e:
            print(f"Error: {e}")
            return
                
    def skip(self, vc):
        try:
            
            print("Skipping song.")
            self.skipped = True  # Set the skipped flag to True
            self.play_next(vc)  # Play the next song
        except Exception as e:
            print(f"Error: {e}")
            return
            
    def play(self, source, vc, after=None):
        try:
            # Play the source 
            vc.play(discord.FFmpegPCMAudio(source, **conf.FFMPEG_OPTIONS), after=after)
        except Exception as e:
            print(f"Error: {e}")
            return

        
    #TODO fix this
    def play_next(self, vc):
        try:
            # Check if there are no more songs in the queue or it was skipped
            if len(self.queue) == 0 or self.skipped:
                print("No more songs in queue or song was skipped.")
                # Disconnect the bot
                vc.stop()
                

            # Get the next song from the queue 
            next_song = self.queue.pop(0)
            # Get the source of the next song
            next_source = next_song["source"]
            # Get the title of the next song
            next_title = next_song["title"]

            # Play the next song
            self.play(next_source, vc, after=self.after_playing)
            
            # Reset the skipped flag to False
            self.skipped = False
            
            print(f"Removed {next_title} from the queue.")
            print(f"Queue is now: {self.queue}")

        except Exception as e:
            print(f"Error: {e}")
            return

    def after_playing(self, error, vc):
        if error:
            print(f"Error: {error}")
        else:
            if not self.skipped:
                # Play the next song in the queue
                self.play_next(vc)


            
            
            