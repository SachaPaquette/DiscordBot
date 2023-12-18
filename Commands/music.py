import discord
import nacl
from dotenv import load_dotenv
from Config.config import conf
from Commands.queue import QueueOperations
# Load the .env file
load_dotenv()

class SongSession:
    def __init__(self, guild,  ctx) -> None:
        self.guild = guild
        vc = ctx.voice_client
        self.voice_client = vc
        self.skipped = False  # Initialize the skipped attribute
        self.queue_operations = QueueOperations(self)
        # Initialize the current song and song duration attributes
        self.current_song = None
        self.song_duration = None
        # Initialize the thumbnail attribute of the song
        self.thumbnail = None
        
    async def stop(self, vc):
        """
        Stop the currently playing song.

        Parameters:
        - vc: The voice client object.

        Returns:
        None
        """
        vc.stop()

    async def pause(self, vc):
        """
        Pause the song audio.

        Parameters:
        - vc: The voice client object.

        Returns:
        None
        """
        vc.pause()

    async def resume(self, vc):
        """
        Resumes the paused song audio.

        Parameters:
        - vc (object): The voice client object.

        Returns:
        None
        """
        vc.resume()

    def is_playing(self):
        """
        Check if the bot is currently playing audio.

        Returns:
            bool: True if the bot is playing audio, False otherwise.
        """
        return self.voice_client.is_playing()


                
    def skip_song(self, vc):
        try:
            # Set the skipped flag to True (this will be checked in play_next and after_playing to determine if the song was skipped or not -> after_playing will not play the next song if the song was skipped)
            self.skipped = True  
            # Play the next song
            self.play_next(vc)  
        except Exception as e:
            print(f"Error while trying to skip song in music.py: {e}")
            return
    
    def define_song_info(self, song_title, song_duration, song_thumbnail):
        # Define the current song object 
        self.current_song = song_title
        self.song_duration = song_duration
        self.thumbnail = song_thumbnail
        print(f"Removed {song_title} from the queue.")
    
    def play(self, source, vc, after=None, song_title=None, song_duration=None, thumbnail=None):
        try:
            # Define the song information such as the title and duration 
            self.define_song_info(song_title, song_duration, thumbnail)
            # Play the source 
            vc.play(discord.FFmpegPCMAudio(source, **conf.FFMPEG_OPTIONS), after=after)
        except Exception as e:
            print(f"Error at play function in music.py: {e}")
            return
    


    def play_next(self, vc):
        try:
            # Check if the queue is empty or if the song was skipped
            self.queue_operations.check_queue_skipped_status(vc, self.skipped)
            
            # Get the next song from the queue
            next_source, next_title, next_song_duration, next_song_thumbnail = self.queue_operations.get_next_song()
            
            # Check if the source and title are valid
            if next_source is None or next_title is None or next_song_duration is None or next_song_thumbnail is None:
                raise Exception("Song information is None.")
            
            # Play the next song
            self.play(next_source, vc, after=self.after_playing)
            
            # Reset the skipped flag to False
            self.skipped = False
            
            # Define the current song information 
            self.define_song_info(next_title, next_song_duration, next_song_thumbnail)
        except Exception as e:
            print(f"Error while trying to play next song in music.py: {e}")
            return

    def after_playing(self, error, vc):
        # Check if there was an error playing the song
        if error:
            print(f"Error at after_playing function in music.py: {error}")
        else:
            # Check if the skipped flag is False (if it is, the song ended naturally and was not skipped)
            if not self.skipped:
                # Play the next song in the queue
                self.play_next(vc)


    def get_song_title(self):
        try:
            # Return the current song
            return self.current_song
        except Exception as e:
            print(f"Error at get_song_title function in music.py: {e}")
            return None
            
            
            