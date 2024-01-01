import discord
class NowPlaying():    
    
    def create_embed_message(self, song_title, thumbnail, song_duration):
        """
        Create an embed message that contains the title of the song, the thumbnail, and the duration.

        Args:
            song_title (str): The title of the song.
            thumbnail (str): The URL of the thumbnail image.
            song_duration (str): The duration of the song.

        Returns:
            discord.Embed: The embed message containing the song information.
        """
        try:
            embed = discord.Embed(
                title="Now Playing", description=song_title, color=discord.Color.green())

            if thumbnail is not None:
                embed.set_thumbnail(url=thumbnail)
            if song_duration is not None:
                embed.add_field(name="Duration", value=song_duration)

            return embed
        except Exception as e:
            print(f"Error while trying to create an embed message in nowplaying.py: {e}")
            return
    
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
                embed = self.create_embed_message(song_title, session.thumbnail, session.song_duration)
                    
                # Send the embed
                await interactions.response.send_message(embed=embed)
            except Exception as e:
                print(f"An error occurred when trying to display the song. {e}")
                raise e
