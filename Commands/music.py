import discord
import nacl
from dotenv import load_dotenv
from Config.config import conf

# Load the .env file
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
        # Stop the song audio
        vc.stop()

    def pause(self, vc):
        # Pause the song audio
        vc.pause()

    def resume(self, vc):
        # Resume the song audio
        vc.resume()

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
            # Set the skipped flag to True (this will be checked in play_next and after_playing to determine if the song was skipped or not -> after_playing will not play the next song if the song was skipped)
            self.skipped = True  
            # Play the next song
            self.play_next(vc)  
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
        
        
    def check_queue_skipped_status(self, vc):
        # Check if the queue is empty or if the song was skipped
        if len(self.queue) == 0 or self.skipped:
            print("No more songs in queue or song was skipped.")
            # Stop the song's audio
            vc.stop()
    def get_next_song(self):
        try:
            # Get the next song from the queue
            next_song = self.queue.pop(0)
            # Get the source of the next song
            next_source = next_song["source"]
            # Get the title of the next song
            next_title = next_song["title"]
            
            # Return the source and title of the next song
            if next_source and next_title:
                return next_source, next_title
        except Exception as e:
            print(f"Error: {e}")
            return None, None
    def play_next(self, vc):
        try:
            # Check if the queue is empty or if the song was skipped
            self.check_queue_skipped_status(vc)
            
            # Get the next song from the queue
            next_source, next_title = self.get_next_song()
            
            # Check if the source and title are valid
            if next_source is None or next_title is None:
                return
            
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
        # Check if there was an error playing the song
        if error:
            print(f"Error: {error}")
        else:
            # Check if the skipped flag is False (if it is, the song ended naturally and was not skipped)
            if not self.skipped:
                # Play the next song in the queue
                self.play_next(vc)


            
            
            