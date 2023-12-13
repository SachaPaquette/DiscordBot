from collections import deque
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
        
    def add_to_queue(self, youtube_source, title, vc):
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
            song_info = {"source": youtube_source, "title": title}
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
        print(f"Checking queue skipped status... {self.return_queue()}")
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
            
            if next_source is not None and next_title is not None:
                return next_source, next_title
            else:
                print("Source or title is None.")
                return None, None
        except Exception as e:
            print(f"Error in the get_next_song function in queue.py: {e}")
            return None, None
