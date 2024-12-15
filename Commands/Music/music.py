import discord
import nacl
from dotenv import load_dotenv
from Config.config import conf
from Commands.Music.queue_command import QueueOperations
from Commands.ErrorHandling.handling import CommandErrorHandler
from Commands.Music.ytdl import YTDLSource
from Commands.Services.utility import Utility, EmbedMessage
import asyncio
# Load the .env file
load_dotenv()

class SongSession:
    _instance = None
    
    def __new__(cls, guild, interactions):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.__initialized = False
        return cls._instance
    
    def __init__(self, guild, interactions):
        if self.__initialized:
            return
        self.__initialized = True
        
        """
        Initializes a music session object.

        Parameters:
        - guild (str): The guild associated with the Music object.
        - interactions (object): The context object containing information about the command invocation.

        Attributes:
        - guild (str): The guild associated with the Music object.
        - voice_client (object): The voice client associated with the Music object.
        - skipped (bool): Indicates whether a song has been skipped or not.
        - queue_operations (object): The queue operations object associated with the Music object.
        - current_song (str): The currently playing song.
        - song_duration (str): The duration of the currently playing song.
        - thumbnail (str): The thumbnail of the currently playing song.
        """
        self.guild = guild
        self.voice_client = interactions.guild.voice_client
        self.skipped = False
        self.queue_operations = QueueOperations(self)
        self.current_song = None
        self.song_duration = None
        self.thumbnail = None
        self.utility = Utility()
        self.embedMessage = EmbedMessage()
        self.source = None

    async def stop(self, vc):
        """
        Stop the currently playing song.

        Parameters:
        - vc: The voice client object.

        Returns:
        None
        """
        try:
            # Check if the voice client is playing audio
            if vc and vc.is_playing():
                # Stop the audio
                vc.stop()
        except Exception as e:
            print(f"Error at stop function in music.py: {e}")
            return


        
    async def pause_command(self, interactions):
        """
        Pauses the current song.

        Parameters:
        - interactions (Context): The context of the command.

        Returns:
        None
        """
        try:
            # Check if the bot is playing something
            if interactions.guild.voice_client is None or not interactions.guild.voice_client.is_playing():
                await interactions.response.send_message("No music is currently playing to pause.")
                return
            # Pause the song
            interactions.guild.voice_client.pause()
            # Send a message that the song was paused
            await interactions.response.send_message("Paused the current song.")
        except Exception as e:
            print(f"An error occurred when trying to pause the song. {e}")
            raise e



    async def resume_command(self, interactions):
        """
        Resumes the paused song audio.

        Parameters:
        - interactions (Context): The context of the command.

        Returns:
        None
        """
        try:
            # Check if the bot is playing something
            if interactions.guild.voice_client is None or not interactions.guild.voice_client.is_paused():
                await interactions.response.send_message("No music is currently paused to resume.")
                return
            
            # Resume the song
            interactions.guild.voice_client.resume()
            
            # Send a message that the song was resumed
            await interactions.response.send_message("Resumed the current song.")
        except Exception as e:
            print(f"An error occurred when trying to resume the song. {e}")
            raise e

        
    def is_playing(self):
        """
        Check if the bot is currently playing audio.

        Returns:
            bool: True if the bot is playing audio, False otherwise.
        """
        try:
            # Return whether the voice client is playing audio
            return self.voice_client.is_playing()
        except Exception as e:
            print(f"Error at is_playing function in music.py: {e}")
            return False


    async def skip(self, interactions):
        try:
            # Check if the bot is playing something
            if interactions.guild.voice_client is None:
                await interactions.response.send_message("The bot is not in a voice channel.")
                return

            # Check if the queue is empty
            if self.queue_operations.return_queue() == 0:
                await interactions.response.send_message("No more songs in the queue to skip.")
                # Stop the audio
                await self.stop(interactions.guild.voice_client)
                return
            
            else:
                # Set the skipped flag to True (this will be checked in play_next and after_playing to determine if the song was skipped or not -> after_playing will not play the next song if the song was skipped)
                self.skipped = True
                # Play the next song
                await self.play_next()
                
                # Send a message saying that the song was skipped
                await interactions.response.send_message("Skipped to the next song.")
        except Exception as e:
            print(f"Error in the skip command: {e}")
            raise e

    def define_song_info(self, song_title, song_duration, song_thumbnail):
        """
        Defines the information for the current song.

        Args:
            song_title (str): The title of the song.
            song_duration (int): The duration of the song in seconds.
            song_thumbnail (str): The URL of the song's thumbnail.

        Returns:
            None
        """
        try:
            # Define the current song object
            self.current_song = song_title
            # Define the song duration object
            self.song_duration = song_duration
            # Define the song thumbnail object
            self.thumbnail = song_thumbnail
        except Exception as e:
            print(f"Error at define_song_info function in music.py: {e}")
            return

    async def play(self, source, song_title=None, song_duration=None, thumbnail=None):
        """
        Play a song in the voice channel.

        Args:
            source (str): The source of the song to be played.
            song_title (str, optional): The title of the song. Defaults to None.
            song_duration (str, optional): The duration of the song. Defaults to None.
            thumbnail (str, optional): The thumbnail of the song. Defaults to None.
        """
        try:
            # Define the song information such as the title and duration
            self.define_song_info(song_title, song_duration, thumbnail)
            

            # Play the source
            self.source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(
                source, **conf.FFMPEG_OPTIONS))
            self.voice_client.play(self.source, after=self.after_playing_callback)
            
        except Exception as e:
            print(f"Error in play function in music.py: {e}")

    def after_playing_callback(self):
        try:
            # Run the after_playing function
            asyncio.run(self.after_playing(self.voice_client))
        except Exception as e:
            print(f"Error at after_playing_callback function in music.py: {e}")
            return
        
    async def play_command(self, interactions, url, loop):
        """
        Play a song.

        Parameters:
        - interactions (discord.ext.commands.Context): The context of the command.
        - url (str): The URL of the song to be played.

        Returns:
        None
        """
        try:
            # Send a message that the bot is trying to play the song
            await interactions.response.send_message("Trying to play the song...")
            # Get the original response message
            result_message = await interactions.original_response()
            # Check if the URL is valid (i.e. it is a YouTube URL)
            if not CommandErrorHandler.check_url_correct(url):
                # Send a follow-up message to the user
                
                await result_message.edit(content="Please enter a valid YouTube URL, such as https://www.youtube.com/watch?v=dQw4w9WgXcQ")
                return

            # Check if the bot is already in the correct channel
            if await self.utility.join(interactions, result_message) is False:
                return

            # Extract information from the URL
            try:
                URL, song_title, song_duration, thumbnail = await YTDLSource.extract_info_from_url(url, loop=loop, stream=True)
            except Exception as e:
                print(f"Error extracting info from URL: {e}")
                return

            # Check if the URL and song title are valid
            if not CommandErrorHandler.check_url_song_correct(URL, song_title):
                await result_message.edit(content="No song found.")
                return

            self.voice_client = interactions.guild.voice_client
            if interactions.guild.voice_client is None:
                await result_message.edit(content="The bot is not in a voice channel.")
                return
        
            # Check if the bot is already playing something
            if interactions.guild.voice_client.is_playing():
                # Add the song to the queue
                self.queue_operations.add_to_queue(URL, song_title, interactions.guild.voice_client, song_duration, thumbnail)
                await result_message.edit(content=f"Added {song_title} to the queue.")
            else:
<<<<<<< HEAD:Commands/music.py
                embed = Utility.now_playing_song_embed(song_title, thumbnail, song_duration)
                print(embed)
                await interactions.response.send_message(embed)
                # Use the instance to play the song
                await self.play(URL, vc, None, song_title,
                                  song_duration, thumbnail)
                
=======
                # Send the now playing message
                embed = self.embedMessage.now_playing_song_embed(song_title, thumbnail, song_duration)
                await result_message.edit(embed=embed, content=None)
                # Play the song
                await self.play(source=URL, song_title=song_title, song_duration=song_duration, thumbnail=thumbnail)
>>>>>>> 222dc3a057e0e82b87f8d3925bf948b0f4d329f7:Commands/Music/music.py
        except Exception as e:
            # Handle any errors gracefully
            print(f"An error occurred when trying to play the song: {e}")
            # Leave the channel if an error occurs
            await self.utility.leave(interactions)
            raise e

    async def play_next(self):
        """
        Plays the next song in the queue.

        Args:
            vc (VoiceClient): The voice client object.

        Returns:
            None
        """
        try:
            # Check if the queue is empty or if the song was skipped
            self.queue_operations.check_queue_skipped_status(self.voice_client, self.skipped)

            # Get the next song from the queue
            next_source, next_title, next_song_duration, next_song_thumbnail = self.queue_operations.get_next_song()
            if not self.voice_client:
                raise Exception("Voice client is None.")
            # Define the current song information
            self.define_song_info(next_title, next_song_duration, next_song_thumbnail)
            # Play the next song
            await self.play(next_source, next_title, next_song_duration, next_song_thumbnail)

            # Reset the skipped flag to False
            self.skipped = False
        except Exception as e:
            print(f"Error while trying to play next song in music.py: {e}")
            return

    async def after_playing(self):
        """
        Callback function called after a song finishes playing.

        Args:
            error (Exception): The error that occurred while playing the song, if any.
            vc (VoiceClient): The voice client associated with the song.

        Returns:
            None
        """
        try:
            # Check if the skipped flag is False (if it is, the song ended naturally and was not skipped)
            if not self.skipped and self.voice_client is not None and self.voice_client.is_playing() is False and self.queue_operations.return_queue() > 0: 
                # Play the next song in the queue
                await self.play_next()
                pass
        except Exception as e:
            print(f"Error at after_playing function in music.py: {e}")
            return
        
    def get_song_title(self):
        """
        Returns the title of the current song.

        Returns:
            str: The title of the current song.
            None: If there is an error retrieving the song title.
        """
        try:
            # Return the current song
            return self.current_song
        except Exception as e:
            print(f"Error at get_song_title function in music.py: {e}")
            return None
    
    async def change_volume(self, volume, interactions):
        """
        Changes the volume of the bot.

        Args:
            volume (float): The volume to change to.
            interactions: The interaction context.

        Returns:
            None
        """
        try:
            # Validate volume range
            if not 0 <= volume <= 100:
                await interactions.response.send_message("Please enter a valid volume between 0 and 100.")
                return
            
            # Adjust volume to correct range (0.0 - 1.0)
            adjusted_volume = volume / 100
            
            # Check if the voice client and source are available
            voice_client = interactions.guild.voice_client
            if not voice_client or not voice_client.source:
                await interactions.response.send_message("Voice client or source not available.")
                return

            # Change the volume
            voice_client.source.volume = adjusted_volume
            
            # Send a confirmation message
            await interactions.response.send_message(f"Changed the volume to {volume}%.")
        except Exception as e:
            print(f"Error at change_volume function in music.py: {e}")
            await interactions.response.send_message("An error occurred while changing the volume.")
