import discord
from Commands.utility import Utility
from Config.logging import setup_logging
from Config.config import conf
# Create a logger for this file
logger = setup_logging("nowplaying.py", conf.LOGS_PATH)
class NowPlaying():    
    async def nowplaying_command(self, interactions, session):
            """
            Retrieves and displays the currently playing song information.

            Parameters:
            - interactions: The interaction object representing the user's command.
            - session: The session object containing the song information.

            Returns:
            None
            """
            try:
                # Get the voice client
                vc = interactions.guild.voice_client
                
                # Check if the bot is playing something
                if vc is None or not vc.is_playing():
                    await interactions.response.send_message("No music is currently playing.")
                    return
                
                # Get the title of the song
                song_title = session.get_song_title()
                
                # Check if the song title is None
                if song_title is None:
                    await interactions.response.send_message("No music is currently playing.")
                    return

                # Create an embed message that contains the title of the song, the thumbnail, and the duration
                embed = Utility.now_playing_song_embed(song_title, session.thumbnail, session.song_duration)
                    
                # Send the embed
                await interactions.response.send_message(embed=embed)
            except Exception as e:
                logger.error(f"An error occurred when trying to display the song. {e}")
                raise e
