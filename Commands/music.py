import discord
import nacl
from dotenv import load_dotenv
from Config.config import conf
from Commands.queue import QueueOperations
from Commands.ErrorHandling.handling import CommandErrorHandler
from Commands.ytdl import YTDLSource
from Commands.utility import Utility
import asyncio
# Load the .env file
load_dotenv()

class SongSession:
    def __init__(self, guild,  interactions) -> None:
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
        # Define the guild attribute
        self.guild = guild
        # Define the voice client object
        vc = interactions.guild.voice_client
        # Assign the voice client to the voice_client attribute
        self.voice_client = vc
        # Initialize the skipped attribute
        self.skipped = False  
        # Initialize the queue operations object 
        self.queue_operations = QueueOperations(self)
        # Initialize the current song and song duration attributes
        self.current_song = None
        self.song_duration = None
        # Initialize the thumbnail attribute of the song
        self.thumbnail = None
        
        self.utility = Utility()
        
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
            # Declare a voice client variable
            vc = interactions.guild.voice_client
            # Check if the bot is playing something
            if vc is None or not vc.is_playing():
                await interactions.response.send_message("No music is currently playing to pause.")
                return
            # Pause the song
            vc.pause()
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
            # Declare a voice client variable
            vc = interactions.guild.voice_client
            
            # Check if the bot is playing something
            if vc is None or not vc.is_paused():
                await interactions.response.send_message("No music is currently paused to resume.")
                return
            
            # Resume the song
            vc.resume()
            
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
            # Declare a voice client variable
            vc = interactions.guild.voice_client
            
            # Check if the bot is playing something
            if vc is None or not vc.is_playing():
                await interactions.response.send_message("No music is currently playing to skip.")
                return

            # Check if the queue is empty
            if self.queue_operations.return_queue() == 0:
                await interactions.response.send_message("No more songs in the queue to skip.")
                return
            
            else:
                # Set the skipped flag to True (this will be checked in play_next and after_playing to determine if the song was skipped or not -> after_playing will not play the next song if the song was skipped)
                self.skipped = True
                # Play the next song
                await self.play_next(vc)
                
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
            vc (discord.VoiceChannel): The voice channel to play the song in.
            after (Callable, optional): A function to be called after the song finishes playing. Defaults to None.
            song_title (str, optional): The title of the song. Defaults to None.
            song_duration (str, optional): The duration of the song. Defaults to None.
            thumbnail (str, optional): The thumbnail of the song. Defaults to None.
        """
        try:
            # Define the song information such as the title and duration
            self.define_song_info(song_title, song_duration, thumbnail)
            # Play the source
            await self.voice_client.play(discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(
                source, **conf.FFMPEG_OPTIONS)), after=self.after_playing_callback)
            self.source = discord.PCMVolumeTransformer(self.voice_client.source)
        except Exception as e:
            print(f"Error at play function in music.py: {e}")
            return

    def after_playing_callback(self, error):
        asyncio.run(self.after_playing(self.voice_client))

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
                await interactions.foll
                await result_message.edit(content="Please enter a valid YouTube URL, such as https://www.youtube.com/watch?v=dQw4w9WgXcQ")
                return

            # Check if the bot is already in the correct channel
            if await self.utility.join(interactions) is False:
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

            # Get the voice client
            vc = interactions.guild.voice_client
            self.voice_client = interactions.guild.voice_client
            if vc is None:
                await result_message.edit(content="The bot is not in a voice channel.")
                return
            
            
            
            # Check if the bot is already playing something
            if vc.is_playing():
                # Add the song to the queue
                self.queue_operations.add_to_queue(URL, song_title, vc, song_duration, thumbnail)
                await result_message.edit(content=f"Added {song_title} to the queue.")
            else:
                # Send the now playing message
                embed = Utility.now_playing_song_embed(song_title, thumbnail, song_duration)
                await result_message.edit(embed=embed, content=None)
                # Play the song
                await self.play(source=URL, song_title=song_title, song_duration=song_duration, thumbnail=thumbnail)
                # Asynchronously play the next song
        except Exception as e:
            # Handle any errors gracefully
            print(f"An error occurred when trying to play the song: {e}")
            # Leave the channel if an error occurs
            await self.utility.leave(interactions)
            raise e


    async def play_next(self, vc):
        """
        Plays the next song in the queue.

        Args:
            vc (VoiceClient): The voice client object.

        Returns:
            None
        """
        try:
            # Check if the queue is empty or if the song was skipped
            self.queue_operations.check_queue_skipped_status(vc, self.skipped)

            # Get the next song from the queue
            next_source, next_title, next_song_duration, next_song_thumbnail = self.queue_operations.get_next_song()

            # Check if the source and title are valid
            if next_source is None or next_title is None or next_song_duration is None or next_song_thumbnail is None:
                raise Exception("Song information is None.")

            if not vc:
                raise Exception("Voice client is None.")
            
            # Play the next song
            await self.play(next_source, next_title, next_song_duration, next_song_thumbnail)

            # Reset the skipped flag to False
            self.skipped = False

            # Define the current song information
            self.define_song_info(
                next_title, next_song_duration, next_song_thumbnail)
        except Exception as e:
            print(f"Error while trying to play next song in music.py: {e}")
            return

    async def after_playing(self, vc):
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
            if not self.skipped:
                # Play the next song in the queue
                await self.play_next(vc)
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

        Returns:
            None
        """
        try:
            # Check if the volume is valid
            if volume < 0 or volume > 100:
                await interactions.response.send_message("Please enter a valid volume between 0 and 100.")
                return
            
            # Put the volume in the correct range (0.0 - 1.0)
            volume = float(volume) / 100
            
            # Change the volume of the bot
            interactions.guild.voice_client.source.volume = volume
            
            # Send a message that the volume was changed
            await interactions.response.send_message(f"Changed the volume to {volume * 100}%")
        except Exception as e:
            print(f"Error at change_volume function in music.py: {e}")
            return

