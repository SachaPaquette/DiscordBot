# Purpose: Contains the queue operations class and its methods.

from collections import deque
import random # Random is used to shuffle the queue


class QueueOperations:
    # Initialize the queue attribute
    shared_queue = deque()  
    
    def __init__(self, song_session=None):
        # Initialize the song session attribute
        self.song_session = song_session
        # Initialize the queue attribute
        self.queue = self.shared_queue

    def display_queue(self):
        """
        Returns a list of titles in the queue.

        Returns:
            list: A list of titles in the queue.
        """
        return [song["title"] for song in self.queue]
        
    async def display_queue_command(self, interactions, discord):
            """
            Displays the current queue of songs.

            Parameters:
            - interactions: The interaction object for sending messages.
            - discord: The discord module for creating embed messages.

            Returns:
            None
            """
            try:
                # Check if the queue is empty
                if self.return_queue() == 0:
                    await interactions.response.send_message("No songs in queue.")
                    return
                # Get the queue
                queue = self.display_queue()
                # Create an embed message that contains the queue
                embed = discord.Embed(title="Queue", description="\n".join(queue), color=discord.Color.green())
                # Send the embed
                await interactions.response.send_message(embed=embed)
            except Exception as e:
                print(f"An error occurred when trying to display the queue. {e}")
                raise e
        
    def clear_queue(self):
        """
        Clears the queue and the title queue.
        """
        try:
            # Clear the queue
            self.queue.clear()
        except Exception as e:
            print(f"Error while trying to clear the queue in queue.py: {e}")
            return
        
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
        """
        Returns the length of the queue.

        Returns:
            int: The length of the queue.
        """
        try:
            # Return the queue length
            return len(self.queue)
        except Exception as e:
            print(f"Error while trying to return the queue in queue.py: {e}")
            return
    
    def check_queue_skipped_status(self, vc, skipped_status):
        """
        Check the status of the queue and handle skipped songs.

        Args:
            vc (object): The voice client object.
            skipped_status (bool): Indicates if the song was skipped.

        Returns:
            None

        Raises:
            Exception: If an error occurs while checking the queue.

        """
        try:
            # Check if the queue is empty or if the song was skipped
            if self.return_queue() == 0:
                print("No more songs in queue.")
            elif skipped_status:
                print("Song was skipped.")
            else:
                return
            # Stop the song's audio
            vc.stop()
        except Exception as e:
            print(f"Error in the check_queue_skipped_status function in queue.py: {e}")
            return
        
    def get_next_song(self):
        """
        Retrieves the next song from the queue.

        Returns:
            A tuple containing the source, title, duration, and thumbnail of the next song.
            If the queue is empty or if any song information is missing, returns None for all values.
        """
        try:
            print("Getting next song.")
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
                print("Some song information is None.")
                return None, None, None, None
        except Exception as e:
            print(f"Error in the get_next_song function in queue.py: {e}")
            return None, None, None, None


    async def shuffle_queue_command(self, interactions):
            """
            Shuffles the music queue.

            Parameters:
            - interactions: The interaction object representing the user's command.

            Returns:
            None
            """
            try:
                # Check if the bot is playing something
                if interactions.guild.voice_client is None or not interactions.guild.voice_client.is_playing():
                    await interactions.response.send_message("No music is currently playing.")
                    return
                
                # Check if the queue contains music
                if self.return_queue() == 0:
                    await interactions.response.send_message("Queue is empty.")
                    return    
           
                # Shuffle the queue
                random.shuffle(self.queue)
                
                # Send a message that the queue was shuffled
                await interactions.response.send_message("Shuffled the queue.")
            except Exception as e:
                print(f"Error in the shuffle_queue_command function in queue.py: {e}")
                return
        
    
        
    async def clear_command(self, interactions):

        """
        This command clears the queue. It checks if the bot is currently playing music and if there are songs in the queue before calling the clear function from queue operations. 

        Parameters:
        - interactions (Context): The context object representing the invocation context of the command.

        Returns:
        None
        """
        try:
            # Get the voice client
            vc = interactions.voice_client
            # Check if the bot is playing something
            if vc is None or not vc.is_playing():
                await interactions.response.send_message("No music is currently playing.")
                return
            # Check if the queue is empty
            if self.return_queue() == 0:
                await interactions.response.send_message("No more songs in the queue to clear.")
                return
            # Clear the queue
            self.queue.clear()
            await interactions.response.send_message("Cleared the queue.")
        except Exception as e:
            print(f"An error occurred when trying to clear the queue. {e}")
            raise e