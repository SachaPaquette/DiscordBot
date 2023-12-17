from collections import deque
# Random is used to shuffle the queue
import random
class QueueOperations:
    shared_queue = deque()  # Initialize the queue attribute
    def __init__(self, song_session=None):
        print("Initializing QueueOperations...")
        self.song_session = song_session
        self.queue = self.shared_queue

    def display_queue(self):
        print("Queue:")
        print(self.queue)
        # Clear the title queue
        # Return the queue of song titles
        # return only the titles in the queue list
        return [song["title"] for song in self.queue]
        
    def clear_queue(self):
        """
        Clears the queue and the title queue.
        """
        # Clear the queue
        self.queue.clear()
        
    def add_to_queue(self, youtube_source, title, vc, song_duration, thumbnail):
        """
        Add a song to the queue.

        Args:
            youtube_source (str): The source of the song (e.g., YouTube URL).
            title (str): The title of the song.
            vc (VoiceClient): The voice client object.

        Returns:
            None
        """
        try:
            # Add the source and title to the queue as a dictionary
            song_info = {"source": youtube_source, "title": title, "duration": song_duration, "thumbnail": thumbnail}
            print(f"Song info: {song_info}")
            # Append the song info to the queue
            self.queue.append(song_info)

            # Check if the bot is playing something
            if not vc.is_playing():
                # If not, play the next song
                self.song_session.play_next(vc)
                pass
        except Exception as e:
            print(f"Error while trying to add to queue in queue.py: {e}")
            return
        
    def return_queue(self):
        print("Returning queue...")
        print(f"Queue: {self.queue}")
        # Return the queue
        return len(self.queue)
    
    
    def check_queue_skipped_status(self, vc, skipped_status):
        # Check if the queue is empty or if the song was skipped
        if self.return_queue() == 0:
            print("No more songs in queue.")
        elif skipped_status:
            print("Song was skipped.")
        else:
            return
        # Stop the song's audio
        vc.stop()
            
    def get_next_song(self):
        try:
            print("Getting next song...")
            print(f"Queue: {self.queue}")
            # Check if the queue is empty
            if self.return_queue() == 0:
                return None, None
            
            # Get the next song from the queue
            next_song = self.queue.popleft()
            
            # Get the source and title of the next song
            next_source = next_song.get("source")
            next_title = next_song.get("title")
            next_song_duration = next_song.get("duration")
            next_song_thumbnail = next_song.get("thumbnail")
            
            if next_source is not None and next_title is not None and next_song_duration is not None and next_song_thumbnail is not None:
                return next_source, next_title, next_song_duration, next_song_thumbnail
            else:
                print("Source or title is None.")
                return None, None, None, None
        except Exception as e:
            print(f"Error in the get_next_song function in queue.py: {e}")
            return None, None, None, None


    def shuffle_queue(self):
        try:
            if self.return_queue() == 0:
                print("Queue is empty.")
                return    
            """
            Shuffles the queue.
            """
            # Shuffle the queue
            random.shuffle(self.queue)
        except Exception as e:
            print(f"Error in the shuffle_queue function in queue.py: {e}")
            return
        